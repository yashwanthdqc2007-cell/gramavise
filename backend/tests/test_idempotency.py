"""Phase 6G Tests: Persistence-Backed Idempotency & Duplicate-Request Protection."""
import uuid
import pytest
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, init_db
from app.models import Analysis, ScenarioRecord, IdempotencyRecord
from app.repositories import UnitOfWork, get_uow
from app.utils.fingerprint import compute_request_fingerprint


@pytest.fixture
def client_with_db(tmp_path):
    """Provides a TestClient with an isolated test SQLite database and overridden UoW dependency."""
    db_file = tmp_path / "test_idempotency.db"
    test_engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    init_db(target_engine=test_engine)
    test_session_factory = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)

    def override_get_uow():
        with UnitOfWork(session_factory=test_session_factory) as uow:
            yield uow

    app.dependency_overrides[get_uow] = override_get_uow
    client = TestClient(app)
    try:
        yield client, test_session_factory
    finally:
        app.dependency_overrides.clear()
        test_engine.dispose()


@pytest.fixture
def sample_analysis_payload():
    return {
        "profile": {
            "business_name": "Rural Mustard Oil Mill",
            "category": "Oil Extraction & Processing",
            "description": "Mustard oil expeller unit",
            "location": {
                "state": "Rajasthan",
                "district": "Bharatpur",
                "village": "Kumher",
                "latitude": 27.32,
                "longitude": 77.38
            },
            "experience_years": 4,
            "own_capital": 100000.0,
            "desired_loan": 300000.0,
            "is_new_business": True
        },
        "financials": {
            "startup_cost": 50000.0,
            "equipment_cost": 300000.0,
            "inventory_cost": 50000.0,
            "monthly_fixed_cost": 12000.0,
            "customers_per_day": 20,
            "avg_ticket_price": 150.0,
            "working_days_per_month": 26,
            "variable_cost_pct": 35.0,
            "interest_rate_pct": 10.0,
            "loan_tenure_months": 36
        },
        "preferred_language": "hi"
    }


# ==============================================================================
# TEST 1: First and Repeated POST /api/analyze with Same Idempotency-Key
# ==============================================================================
def test_01_analyze_idempotent_creation_and_replay(client_with_db, sample_analysis_payload):
    """First request creates analysis + idempotency record; second request replays same result."""
    client, session_factory = client_with_db
    idempotency_key = "idemp-test-analyze-001"

    # 1. First execution
    resp1 = client.post("/api/analyze", json=sample_analysis_payload, headers={"Idempotency-Key": idempotency_key})
    assert resp1.status_code == 200
    data1 = resp1.json()
    analysis_id_1 = data1["analysis_id"]

    # 2. Replay with identical key and payload
    resp2 = client.post("/api/analyze", json=sample_analysis_payload, headers={"Idempotency-Key": idempotency_key})
    assert resp2.status_code == 200
    data2 = resp2.json()
    analysis_id_2 = data2["analysis_id"]

    # Must be exact same persisted analysis
    assert analysis_id_1 == analysis_id_2
    assert data1["financial_result"]["monthly_net_profit"] == data2["financial_result"]["monthly_net_profit"]
    assert data1["recommendation_status"] == data2["recommendation_status"]

    # Verify only ONE analysis was created in the database
    with UnitOfWork(session_factory=session_factory) as uow:
        count = uow.session.scalar(select(func.count(Analysis.id)))
        assert count == 1

        idemp_rec = uow.idempotency.get(idempotency_key, "ANALYSIS")
        assert idemp_rec is not None
        assert idemp_rec.resource_id == analysis_id_1
        assert idemp_rec.status == "COMPLETED"


# ==============================================================================
# TEST 2: POST /api/analyze with Same Key but Modified Payload -> HTTP 409
# ==============================================================================
def test_02_analyze_payload_mismatch_conflict(client_with_db, sample_analysis_payload):
    """Reusing an idempotency key with a changed payload returns HTTP 409 Conflict."""
    client, session_factory = client_with_db
    idempotency_key = "idemp-test-analyze-002"

    # 1. First execution
    resp1 = client.post("/api/analyze", json=sample_analysis_payload, headers={"Idempotency-Key": idempotency_key})
    assert resp1.status_code == 200

    # 2. Replay with SAME key but MODIFIED payload
    modified_payload = dict(sample_analysis_payload)
    modified_payload["financials"] = dict(sample_analysis_payload["financials"])
    modified_payload["financials"]["monthly_fixed_cost"] = 99999.0

    resp2 = client.post("/api/analyze", json=modified_payload, headers={"Idempotency-Key": idempotency_key})
    assert resp2.status_code == 409
    assert "different request payload" in resp2.json()["detail"]


# ==============================================================================
# TEST 3: Scenario Idempotency Replay (Does NOT consume extra slot)
# ==============================================================================
def test_03_scenario_idempotent_replay(client_with_db, sample_analysis_payload):
    """Replaying a scenario save with same key returns existing scenario without consuming slots."""
    client, session_factory = client_with_db

    # 1. Create baseline analysis
    resp_base = client.post("/api/analyze", json=sample_analysis_payload)
    assert resp_base.status_code == 200
    analysis_id = resp_base.json()["analysis_id"]

    scenario_payload = {
        "name": "Higher Volume Scenario",
        "description": "Testing demand shock",
        "scenario_own_capital": 100000.0,
        "scenario_desired_loan": 300000.0,
        "scenario_financials": {
            "startup_cost": 50000.0,
            "equipment_cost": 300000.0,
            "inventory_cost": 50000.0,
            "monthly_fixed_cost": 12000.0,
            "customers_per_day": 35,
            "avg_ticket_price": 150.0,
            "working_days_per_month": 26,
            "variable_cost_pct": 35.0,
            "interest_rate_pct": 10.0,
            "loan_tenure_months": 36
        }
    }

    scen_key = "idemp-test-scenario-001"

    # 2. First scenario save
    resp_scen_1 = client.post(
        f"/api/analyze/{analysis_id}/scenarios",
        json=scenario_payload,
        headers={"Idempotency-Key": scen_key}
    )
    assert resp_scen_1.status_code == 201
    scen_id_1 = resp_scen_1.json()["scenario_id"]

    # 3. Second scenario save with same key and payload
    resp_scen_2 = client.post(
        f"/api/analyze/{analysis_id}/scenarios",
        json=scenario_payload,
        headers={"Idempotency-Key": scen_key}
    )
    assert resp_scen_2.status_code == 200 or resp_scen_2.status_code == 201
    scen_id_2 = resp_scen_2.json()["scenario_id"]

    assert scen_id_1 == scen_id_2

    # Verify database has exactly 1 scenario record
    with UnitOfWork(session_factory=session_factory) as uow:
        count = uow.scenarios.count_by_analysis(analysis_id)
        assert count == 1


# ==============================================================================
# TEST 4: Scenario Idempotency Payload Mismatch -> HTTP 409
# ==============================================================================
def test_04_scenario_payload_mismatch_conflict(client_with_db, sample_analysis_payload):
    """Reusing scenario idempotency key with modified scenario payload returns HTTP 409."""
    client, session_factory = client_with_db

    # 1. Create baseline analysis
    resp_base = client.post("/api/analyze", json=sample_analysis_payload)
    analysis_id = resp_base.json()["analysis_id"]

    scen_key = "idemp-test-scenario-002"
    scenario_payload = {
        "name": "Scenario A",
        "scenario_own_capital": 100000.0,
        "scenario_desired_loan": 300000.0,
        "scenario_financials": sample_analysis_payload["financials"]
    }

    resp1 = client.post(
        f"/api/analyze/{analysis_id}/scenarios",
        json=scenario_payload,
        headers={"Idempotency-Key": scen_key}
    )
    assert resp1.status_code == 201

    # Modified scenario payload
    modified_scen = dict(scenario_payload)
    modified_scen["name"] = "Scenario Modified"
    modified_scen["scenario_own_capital"] = 200000.0

    resp2 = client.post(
        f"/api/analyze/{analysis_id}/scenarios",
        json=modified_scen,
        headers={"Idempotency-Key": scen_key}
    )
    assert resp2.status_code == 409
    assert "different scenario payload" in resp2.json()["detail"]


# ==============================================================================
# TEST 5: Operation Scope Isolation
# ==============================================================================
def test_05_operation_scope_isolation(client_with_db, sample_analysis_payload):
    """Same key string used across different scopes (ANALYSIS vs SCENARIO) operates independently."""
    client, session_factory = client_with_db
    shared_key = "shared-idempotency-key-007"

    # 1. Create Analysis with shared_key
    resp_ana = client.post("/api/analyze", json=sample_analysis_payload, headers={"Idempotency-Key": shared_key})
    assert resp_ana.status_code == 200
    analysis_id = resp_ana.json()["analysis_id"]

    # 2. Create Scenario with same shared_key (scope SCENARIO)
    scenario_payload = {
        "name": "Scenario In Scope",
        "scenario_own_capital": 100000.0,
        "scenario_desired_loan": 300000.0,
        "scenario_financials": sample_analysis_payload["financials"]
    }
    resp_scen = client.post(
        f"/api/analyze/{analysis_id}/scenarios",
        json=scenario_payload,
        headers={"Idempotency-Key": shared_key}
    )
    assert resp_scen.status_code == 201

    with UnitOfWork(session_factory=session_factory) as uow:
        rec_ana = uow.idempotency.get(shared_key, "ANALYSIS")
        rec_scen = uow.idempotency.get(shared_key, "SCENARIO")
        assert rec_ana is not None
        assert rec_scen is not None
        assert rec_ana.resource_id == analysis_id
        assert rec_scen.resource_id == resp_scen.json()["scenario_id"]


# ==============================================================================
# TEST 6: Fingerprint Determinism
# ==============================================================================
def test_06_fingerprint_determinism():
    """Verify dictionary key ordering does not alter SHA-256 request fingerprint."""
    dict_a = {"a": 1, "b": {"x": 10, "y": 20}, "c": [1, 2, 3]}
    dict_b = {"c": [1, 2, 3], "b": {"y": 20, "x": 10}, "a": 1}

    fp_a = compute_request_fingerprint(dict_a)
    fp_b = compute_request_fingerprint(dict_b)

    assert fp_a == fp_b
    assert len(fp_a) == 64


# ==============================================================================
# TEST 7: No Recalculation on Idempotent Replay
# ==============================================================================
def test_07_no_recalculation_on_idempotent_replay(client_with_db, sample_analysis_payload, monkeypatch):
    """Replay does not invoke FinancialService.calculate."""
    client, session_factory = client_with_db
    idempotency_key = "idemp-no-recalc-001"

    resp1 = client.post("/api/analyze", json=sample_analysis_payload, headers={"Idempotency-Key": idempotency_key})
    assert resp1.status_code == 200

    def mock_fail(*args, **kwargs):
        raise AssertionError("FinancialService.calculate MUST NOT be called on idempotent replay")

    monkeypatch.setattr("app.services.financial.calculator.FinancialService.calculate", mock_fail)

    # Second call should succeed via idempotency cache/replay
    resp2 = client.post("/api/analyze", json=sample_analysis_payload, headers={"Idempotency-Key": idempotency_key})
    assert resp2.status_code == 200
    assert resp2.json()["analysis_id"] == resp1.json()["analysis_id"]


# ==============================================================================
# TEST 8: Request without Idempotency-Key Functions Normally
# ==============================================================================
def test_08_request_without_idempotency_key_succeeds(client_with_db, sample_analysis_payload):
    """Requests without Idempotency-Key proceed normally and persist each time."""
    client, session_factory = client_with_db

    resp1 = client.post("/api/analyze", json=sample_analysis_payload)
    resp2 = client.post("/api/analyze", json=sample_analysis_payload)

    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp1.json()["analysis_id"] != resp2.json()["analysis_id"]
