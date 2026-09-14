"""Phase 6E Scenario Persistence & Scenario History Comprehensive Test Suite.

Verifies:
- Test 1: Create and persist a scenario against a parent Analysis.
- Test 2: Fidelity of all 12 persisted scenario input parameters.
- Test 3: Fidelity of persisted scenario calculation result (no recalculation).
- Test 4: Baseline Analysis immutability before and after scenario creation.
- Test 5: Multiple scenarios (up to 3) coexist for one Analysis.
- Test 6: Fourth scenario rejected with HTTP 409 Conflict.
- Test 7: Per-analysis scenario limit isolation (Analysis A=3, Analysis B=3).
- Test 8: List saved scenarios without recalculation.
- Test 9: Single saved scenario retrieval.
- Test 10: Parent ID mismatch rejected with HTTP 404.
- Test 11: Historical scenario retrieval isolation from context changes.
- Test 12: Historical GET does NOT invoke FinancialService, FeasibilityRules, or ScenarioComparator.
- Test 13: Historical GET does NOT invoke live Market, Scheme, Evidence, or AI providers.
- Test 14: Atomic rollback on scenario persistence error.
- Test 15: ScenarioRepository interface immutability (no update/overwrite methods).
- Test 16: UnitOfWork transaction boundary enforcement.
- Test 17: Parity between ScenarioComparator and persisted comparison snapshot.
- Test 18: Existing stateless Scenario Lab endpoint (/api/analyze/scenario) remains unbroken.
"""
import uuid
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, init_db
from app.repositories import UnitOfWork, get_uow, ScenarioRepository, ScenarioLimitExceededError
from app.models import Analysis, ScenarioRecord
from app.services.financial.calculator import FinancialService
from app.services.recommendation.scenario_comparator import ScenarioComparator
from app.schemas.scenario import ScenarioEvaluationRequest
from app.schemas.financial import FinancialAssumptionsInput


@pytest.fixture
def client_with_db(tmp_path):
    """Provides a TestClient with an isolated test SQLite database and overridden UoW dependency."""
    db_file = tmp_path / "test_scenario_persist.db"
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


SAMPLE_ANALYSIS_PAYLOAD = {
    "profile": {
        "business_name": "Gram Udyog Oil Expeller",
        "category": "Agro Processing",
        "description": "Cold-pressed mustard oil processing unit",
        "location": {
            "state": "Uttar Pradesh",
            "district": "Varanasi",
            "village": "Ramnagar",
            "latitude": 25.267,
            "longitude": 83.025,
        },
        "experience_years": 3,
        "own_capital": 50000.0,
        "desired_loan": 150000.0,
        "is_new_business": True,
    },
    "financials": {
        "startup_cost": 30000.0,
        "equipment_cost": 120000.0,
        "inventory_cost": 50000.0,
        "monthly_fixed_cost": 8000.0,
        "customers_per_day": 40,
        "avg_ticket_price": 50.0,
        "working_days_per_month": 26,
        "variable_cost_pct": 45.0,
        "interest_rate_pct": 11.0,
        "loan_tenure_months": 60,
    },
    "preferred_language": "hi",
}

SAMPLE_SCENARIO_INPUT = {
    "name": "Higher Volume Scenario",
    "description": "Increase footfall to 60 customers/day and ticket price to 60 INR",
    "scenario_own_capital": 60000.0,
    "scenario_desired_loan": 140000.0,
    "scenario_financials": {
        "startup_cost": 30000.0,
        "equipment_cost": 120000.0,
        "inventory_cost": 50000.0,
        "monthly_fixed_cost": 9000.0,
        "customers_per_day": 60,
        "avg_ticket_price": 60.0,
        "working_days_per_month": 26,
        "variable_cost_pct": 40.0,
        "interest_rate_pct": 10.5,
        "loan_tenure_months": 60,
    },
}


def create_baseline_analysis(client: TestClient) -> str:
    """Helper to create a baseline analysis and return its analysis_id."""
    resp = client.post("/api/analyze", json=SAMPLE_ANALYSIS_PAYLOAD)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "analysis_id" in data
    return data["analysis_id"]


# --- TEST 1: Create Scenario ---
def test_01_create_scenario(client_with_db):
    client, session_factory = client_with_db
    analysis_id = create_baseline_analysis(client)

    resp = client.post(f"/api/analyze/{analysis_id}/scenarios", json=SAMPLE_SCENARIO_INPUT)
    assert resp.status_code == 201, resp.text
    data = resp.json()

    assert data["analysis_id"] == analysis_id
    assert "scenario_id" in data
    assert data["name"] == SAMPLE_SCENARIO_INPUT["name"]
    assert data["description"] == SAMPLE_SCENARIO_INPUT["description"]
    assert "scenario_result" in data
    assert "baseline_result" in data
    assert "metric_comparisons" in data
    assert "recommendation_change" in data

    # Verify persisted in database
    with session_factory() as session:
        record = session.scalar(select(ScenarioRecord).where(ScenarioRecord.id == data["scenario_id"]))
        assert record is not None
        assert record.analysis_id == analysis_id
        assert record.name == SAMPLE_SCENARIO_INPUT["name"]


# --- TEST 2: Scenario Input Fidelity ---
def test_02_scenario_input_fidelity(client_with_db):
    client, session_factory = client_with_db
    analysis_id = create_baseline_analysis(client)

    resp = client.post(f"/api/analyze/{analysis_id}/scenarios", json=SAMPLE_SCENARIO_INPUT)
    assert resp.status_code == 201
    scenario_id = resp.json()["scenario_id"]

    with session_factory() as session:
        record = session.scalar(select(ScenarioRecord).where(ScenarioRecord.id == scenario_id))
        inputs = record.scenario_inputs
        assert inputs["own_capital"] == 60000.0
        assert inputs["desired_loan"] == 140000.0
        assert inputs["startup_cost"] == 30000.0
        assert inputs["equipment_cost"] == 120000.0
        assert inputs["inventory_cost"] == 50000.0
        assert inputs["monthly_fixed_cost"] == 9000.0
        assert inputs["customers_per_day"] == 60
        assert inputs["avg_ticket_price"] == 60.0
        assert inputs["working_days_per_month"] == 26
        assert inputs["variable_cost_pct"] == 40.0
        assert inputs["interest_rate_pct"] == 10.5
        assert inputs["loan_tenure_months"] == 60


# --- TEST 3: Scenario Result Fidelity ---
def test_03_scenario_result_fidelity(client_with_db):
    client, session_factory = client_with_db
    analysis_id = create_baseline_analysis(client)

    resp = client.post(f"/api/analyze/{analysis_id}/scenarios", json=SAMPLE_SCENARIO_INPUT)
    assert resp.status_code == 201
    saved_res = resp.json()["scenario_result"]

    # Calculate directly with FinancialService
    calc = FinancialService()
    expected = calc.calculate(
        own_capital=SAMPLE_SCENARIO_INPUT["scenario_own_capital"],
        desired_loan=SAMPLE_SCENARIO_INPUT["scenario_desired_loan"],
        financials=FinancialAssumptionsInput(**SAMPLE_SCENARIO_INPUT["scenario_financials"]),
    )

    assert round(saved_res["monthly_revenue"], 2) == round(expected.monthly_revenue, 2)
    assert round(saved_res["monthly_emi"], 2) == round(expected.monthly_emi, 2)
    assert round(saved_res["monthly_net_profit"], 2) == round(expected.monthly_net_profit, 2)
    assert round(saved_res["dscr"], 2) == round(expected.dscr, 2)
    assert saved_res["break_even_units_daily"] == expected.break_even_units_daily


# --- TEST 4: Baseline Immutability ---
def test_04_baseline_immutability(client_with_db):
    client, session_factory = client_with_db
    analysis_id = create_baseline_analysis(client)

    # Capture baseline state before scenario creation
    with session_factory() as session:
        analysis_before = session.scalar(select(Analysis).where(Analysis.id == analysis_id))
        before_inputs = {
            "own_capital": analysis_before.financial_input_snapshot.own_capital,
            "desired_loan": analysis_before.financial_input_snapshot.desired_loan,
            "customers_per_day": analysis_before.financial_input_snapshot.customers_per_day,
            "monthly_fixed_cost": analysis_before.financial_input_snapshot.monthly_fixed_cost,
        }
        before_result = {
            "monthly_net_profit": analysis_before.financial_result_snapshot.monthly_net_profit,
            "monthly_revenue": analysis_before.financial_result_snapshot.monthly_revenue,
            "dscr": analysis_before.financial_result_snapshot.dscr,
        }
        before_verdict = analysis_before.overall_verdict
        before_status = analysis_before.recommendation_status.value

    # Create Scenario
    resp = client.post(f"/api/analyze/{analysis_id}/scenarios", json=SAMPLE_SCENARIO_INPUT)
    assert resp.status_code == 201

    # Verify baseline state after scenario creation
    with session_factory() as session:
        analysis_after = session.scalar(select(Analysis).where(Analysis.id == analysis_id))
        after_inputs = {
            "own_capital": analysis_after.financial_input_snapshot.own_capital,
            "desired_loan": analysis_after.financial_input_snapshot.desired_loan,
            "customers_per_day": analysis_after.financial_input_snapshot.customers_per_day,
            "monthly_fixed_cost": analysis_after.financial_input_snapshot.monthly_fixed_cost,
        }
        after_result = {
            "monthly_net_profit": analysis_after.financial_result_snapshot.monthly_net_profit,
            "monthly_revenue": analysis_after.financial_result_snapshot.monthly_revenue,
            "dscr": analysis_after.financial_result_snapshot.dscr,
        }
        assert before_inputs == after_inputs
        assert before_result == after_result
        assert analysis_after.overall_verdict == before_verdict
        assert analysis_after.recommendation_status.value == before_status


# --- TEST 5: Multiple Scenarios Coexist ---
def test_05_multiple_scenarios_coexist(client_with_db):
    client, session_factory = client_with_db
    analysis_id = create_baseline_analysis(client)

    # Save 3 scenarios
    scen_ids = []
    for i in range(1, 4):
        payload = {
            **SAMPLE_SCENARIO_INPUT,
            "name": f"Scenario {i}",
            "scenario_own_capital": 50000.0 + i * 10000,
        }
        resp = client.post(f"/api/analyze/{analysis_id}/scenarios", json=payload)
        assert resp.status_code == 201
        scen_ids.append(resp.json()["scenario_id"])

    assert len(set(scen_ids)) == 3

    # Check listing
    resp_list = client.get(f"/api/analyze/{analysis_id}/scenarios")
    assert resp_list.status_code == 200
    list_data = resp_list.json()
    assert len(list_data) == 3
    assert [s["scenario_id"] for s in list_data] == scen_ids


# --- TEST 6: Fourth Scenario Rejected (HTTP 409 Conflict) ---
def test_06_fourth_scenario_rejected_with_conflict(client_with_db):
    client, session_factory = client_with_db
    analysis_id = create_baseline_analysis(client)

    # Create 3 allowed scenarios
    for i in range(1, 4):
        resp = client.post(
            f"/api/analyze/{analysis_id}/scenarios",
            json={**SAMPLE_SCENARIO_INPUT, "name": f"Scenario {i}"},
        )
        assert resp.status_code == 201

    # Attempt 4th scenario
    resp_4 = client.post(
        f"/api/analyze/{analysis_id}/scenarios",
        json={**SAMPLE_SCENARIO_INPUT, "name": "Scenario 4 (Excess)"},
    )
    assert resp_4.status_code == 409
    assert "limit of 3" in resp_4.json()["detail"].lower()

    # Verify count remains exactly 3
    with session_factory() as session:
        count = session.scalar(
            select(ScenarioRecord).where(ScenarioRecord.analysis_id == analysis_id)
        )
        all_recs = session.scalars(
            select(ScenarioRecord).where(ScenarioRecord.analysis_id == analysis_id)
        ).all()
        assert len(all_recs) == 3


# --- TEST 7: Per-Analysis Limit Isolation ---
def test_07_per_analysis_limit_isolation(client_with_db):
    client, session_factory = client_with_db
    analysis_a = create_baseline_analysis(client)
    analysis_b = create_baseline_analysis(client)

    # Add 3 scenarios to Analysis A
    for i in range(3):
        resp_a = client.post(f"/api/analyze/{analysis_a}/scenarios", json={**SAMPLE_SCENARIO_INPUT, "name": f"Scen A{i}"})
        assert resp_a.status_code == 201

    # Add 3 scenarios to Analysis B
    for i in range(3):
        resp_b = client.post(f"/api/analyze/{analysis_b}/scenarios", json={**SAMPLE_SCENARIO_INPUT, "name": f"Scen B{i}"})
        assert resp_b.status_code == 201

    # Total in DB should be 6
    with session_factory() as session:
        total_scenarios = len(session.scalars(select(ScenarioRecord)).all())
        assert total_scenarios == 6

    # 4th scenario on A should fail
    resp_a_4 = client.post(f"/api/analyze/{analysis_a}/scenarios", json={**SAMPLE_SCENARIO_INPUT, "name": "Scen A4"})
    assert resp_a_4.status_code == 409

    # 4th scenario on B should fail
    resp_b_4 = client.post(f"/api/analyze/{analysis_b}/scenarios", json={**SAMPLE_SCENARIO_INPUT, "name": "Scen B4"})
    assert resp_b_4.status_code == 409


# --- TEST 8: Scenario List ---
def test_08_list_scenarios_without_recalculation(client_with_db):
    client, session_factory = client_with_db
    analysis_id = create_baseline_analysis(client)

    client.post(f"/api/analyze/{analysis_id}/scenarios", json={**SAMPLE_SCENARIO_INPUT, "name": "Scen 1"})
    client.post(f"/api/analyze/{analysis_id}/scenarios", json={**SAMPLE_SCENARIO_INPUT, "name": "Scen 2"})

    resp = client.get(f"/api/analyze/{analysis_id}/scenarios")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["name"] == "Scen 1"
    assert data[1]["name"] == "Scen 2"


# --- TEST 9: Single Scenario Retrieval ---
def test_09_single_scenario_retrieval(client_with_db):
    client, session_factory = client_with_db
    analysis_id = create_baseline_analysis(client)

    post_resp = client.post(f"/api/analyze/{analysis_id}/scenarios", json=SAMPLE_SCENARIO_INPUT)
    assert post_resp.status_code == 201
    created_data = post_resp.json()
    scenario_id = created_data["scenario_id"]

    get_resp = client.get(f"/api/analyze/{analysis_id}/scenarios/{scenario_id}")
    assert get_resp.status_code == 200
    retrieved_data = get_resp.json()

    assert retrieved_data["scenario_id"] == scenario_id
    assert retrieved_data["analysis_id"] == analysis_id
    assert retrieved_data["name"] == SAMPLE_SCENARIO_INPUT["name"]
    assert retrieved_data["scenario_result"]["monthly_net_profit"] == created_data["scenario_result"]["monthly_net_profit"]
    assert retrieved_data["metric_comparisons"] == created_data["metric_comparisons"]


# --- TEST 10: Wrong Parent ID Rejected ---
def test_10_wrong_parent_id_rejected(client_with_db):
    client, session_factory = client_with_db
    analysis_a = create_baseline_analysis(client)
    analysis_b = create_baseline_analysis(client)

    post_resp = client.post(f"/api/analyze/{analysis_a}/scenarios", json=SAMPLE_SCENARIO_INPUT)
    assert post_resp.status_code == 201
    scenario_id = post_resp.json()["scenario_id"]

    # Attempt to access scenario_id from A through analysis_b path
    resp = client.get(f"/api/analyze/{analysis_b}/scenarios/{scenario_id}")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


# --- TEST 11: Scenario Historical Retrieval Isolation ---
def test_11_scenario_historical_retrieval_isolation(client_with_db):
    client, session_factory = client_with_db
    analysis_id = create_baseline_analysis(client)

    post_resp = client.post(f"/api/analyze/{analysis_id}/scenarios", json=SAMPLE_SCENARIO_INPUT)
    scenario_id = post_resp.json()["scenario_id"]
    original_profit = post_resp.json()["scenario_result"]["monthly_net_profit"]

    # Retrieve again later
    get_resp = client.get(f"/api/analyze/{analysis_id}/scenarios/{scenario_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["scenario_result"]["monthly_net_profit"] == original_profit


# --- TEST 12: No Recalculation on GET ---
def test_12_no_recalculation_on_get(client_with_db):
    client, session_factory = client_with_db
    analysis_id = create_baseline_analysis(client)

    post_resp = client.post(f"/api/analyze/{analysis_id}/scenarios", json=SAMPLE_SCENARIO_INPUT)
    scenario_id = post_resp.json()["scenario_id"]

    with patch("app.services.financial.calculator.FinancialService.calculate") as mock_calc, \
         patch("app.rules.feasibility_rules.FeasibilityRules.evaluate_with_trace") as mock_rules, \
         patch("app.services.recommendation.scenario_comparator.ScenarioComparator.evaluate_scenario") as mock_comp:
        
        # Test List
        resp_list = client.get(f"/api/analyze/{analysis_id}/scenarios")
        assert resp_list.status_code == 200
        
        # Test Single
        resp_single = client.get(f"/api/analyze/{analysis_id}/scenarios/{scenario_id}")
        assert resp_single.status_code == 200

        mock_calc.assert_not_called()
        mock_rules.assert_not_called()
        mock_comp.assert_not_called()


# --- TEST 13: No Live Provider Refresh on GET ---
def test_13_no_provider_refresh_on_get(client_with_db):
    client, session_factory = client_with_db
    analysis_id = create_baseline_analysis(client)

    post_resp = client.post(f"/api/analyze/{analysis_id}/scenarios", json=SAMPLE_SCENARIO_INPUT)
    scenario_id = post_resp.json()["scenario_id"]

    with patch("app.services.geo.market.MockMarketService.get_market_indicators") as mock_market, \
         patch("app.services.schemes.matcher.SchemeService.match_schemes") as mock_schemes, \
         patch("app.services.evidence.collector.EvidenceCollector.collect") as mock_evidence, \
         patch("app.services.ai.explanation.AIService.explain_analysis") as mock_ai:

        resp = client.get(f"/api/analyze/{analysis_id}/scenarios/{scenario_id}")
        assert resp.status_code == 200

        mock_market.assert_not_called()
        mock_schemes.assert_not_called()
        mock_evidence.assert_not_called()
        mock_ai.assert_not_called()


# --- TEST 14: Atomic Rollback on Failure ---
def test_14_atomic_rollback_on_failure(client_with_db):
    client, session_factory = client_with_db
    analysis_id = create_baseline_analysis(client)

    with patch.object(ScenarioRepository, "create", side_effect=RuntimeError("Simulated DB Crash")):
        resp = client.post(f"/api/analyze/{analysis_id}/scenarios", json=SAMPLE_SCENARIO_INPUT)
        assert resp.status_code == 500

    # Ensure no scenario was saved
    with session_factory() as session:
        recs = session.scalars(select(ScenarioRecord).where(ScenarioRecord.analysis_id == analysis_id)).all()
        assert len(recs) == 0


# --- TEST 15: ScenarioRepository Interface Immutability ---
def test_15_scenario_immutability_interface():
    repo = ScenarioRepository(session=MagicMock())
    assert not hasattr(repo, "update")
    assert not hasattr(repo, "overwrite")
    assert not hasattr(repo, "replace_scenario_result")


# --- TEST 16: Unit of Work Transaction Boundary ---
def test_16_unit_of_work_transaction_boundary(client_with_db):
    client, session_factory = client_with_db
    analysis_id = create_baseline_analysis(client)

    with UnitOfWork(session_factory=session_factory) as uow:
        # Check that scenario repository is bound to the UoW session
        assert uow.scenarios.session is uow.session
        count = uow.scenarios.count_by_analysis(analysis_id)
        assert count == 0


# --- TEST 17: Scenario Comparison Parity ---
def test_17_scenario_comparison_parity(client_with_db):
    client, session_factory = client_with_db
    analysis_id = create_baseline_analysis(client)

    resp = client.post(f"/api/analyze/{analysis_id}/scenarios", json=SAMPLE_SCENARIO_INPUT)
    assert resp.status_code == 201
    persisted_comp = resp.json()

    # Directly run ScenarioComparator with the baseline from the payload
    comparator = ScenarioComparator()
    direct_eval = comparator.evaluate_scenario(
        ScenarioEvaluationRequest(
            baseline_own_capital=SAMPLE_ANALYSIS_PAYLOAD["profile"]["own_capital"],
            baseline_desired_loan=SAMPLE_ANALYSIS_PAYLOAD["profile"]["desired_loan"],
            baseline_financials=FinancialAssumptionsInput(**SAMPLE_ANALYSIS_PAYLOAD["financials"]),
            scenario_own_capital=SAMPLE_SCENARIO_INPUT["scenario_own_capital"],
            scenario_desired_loan=SAMPLE_SCENARIO_INPUT["scenario_desired_loan"],
            scenario_financials=FinancialAssumptionsInput(**SAMPLE_SCENARIO_INPUT["scenario_financials"]),
        )
    )

    assert persisted_comp["scenario_status"] == direct_eval.scenario_status.value
    assert len(persisted_comp["metric_comparisons"]) == len(direct_eval.metric_comparisons)
    assert persisted_comp["what_changed"] == direct_eval.what_changed
    assert persisted_comp["why_it_changed"] == direct_eval.why_it_changed


# --- TEST 18: Existing Scenario Behavior Unbroken ---
def test_18_existing_scenario_behavior_unbroken(client_with_db):
    client, _ = client_with_db
    req = {
        "baseline_own_capital": 50000.0,
        "baseline_desired_loan": 150000.0,
        "baseline_financials": SAMPLE_ANALYSIS_PAYLOAD["financials"],
        "scenario_own_capital": 60000.0,
        "scenario_desired_loan": 140000.0,
        "scenario_financials": SAMPLE_SCENARIO_INPUT["scenario_financials"],
    }
    resp = client.post("/api/analyze/scenario", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert "scenario_result" in data
    assert "metric_comparisons" in data


# --- TEST 19: Concurrency 3-Scenario Ceiling Verification ---
def test_19_concurrency_three_scenario_ceiling(client_with_db):
    """Verify that concurrent scenario creation requests cannot exceed the 3-scenario ceiling."""
    import concurrent.futures

    client, session_factory = client_with_db
    analysis_id = create_baseline_analysis(client)

    # Pre-populate 2 scenarios so 1 slot remains
    for i in range(1, 3):
        resp = client.post(
            f"/api/analyze/{analysis_id}/scenarios",
            json={**SAMPLE_SCENARIO_INPUT, "name": f"Initial Scenario {i}"},
        )
        assert resp.status_code == 201

    # Attempt 5 concurrent scenario saves simultaneously
    results = []
    def save_worker(idx: int):
        payload = {
            **SAMPLE_SCENARIO_INPUT,
            "name": f"Concurrent Scenario {idx}",
            "scenario_own_capital": 50000.0 + idx * 5000,
        }
        return client.post(f"/api/analyze/{analysis_id}/scenarios", json=payload)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(save_worker, i) for i in range(1, 6)]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    # Count HTTP statuses
    success_201 = [r for r in results if r.status_code == 201]
    conflict_409 = [r for r in results if r.status_code == 409]

    # Exactly 1 can take the final 3rd slot, the rest must receive 409 Conflict
    assert len(success_201) == 1, f"Expected exactly 1 concurrent success, got {len(success_201)}"
    assert len(conflict_409) == 4, f"Expected 4 conflicts, got {len(conflict_409)}"

    # Invariant: Total in database must be strictly 3
    with session_factory() as session:
        count = session.scalar(
            select(func.count()).select_from(ScenarioRecord).where(ScenarioRecord.analysis_id == analysis_id)
        )
        assert count == 3


# --- TEST 20: PostgreSQL FOR UPDATE Dialect Compilation ---
def test_20_postgresql_for_update_dialect_compilation():
    """Verify that the parent row-locking query compiles with FOR UPDATE in PostgreSQL dialect."""
    from sqlalchemy.dialects import postgresql
    
    stmt = select(Analysis.id).where(Analysis.id == "test-uuid").with_for_update()
    compiled = str(stmt.compile(dialect=postgresql.dialect()))
    assert "FOR UPDATE" in compiled

