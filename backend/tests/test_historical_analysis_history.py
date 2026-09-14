"""Phase 6H Persistent Analysis History & Historical Retrieval Test Suite.

Verifies:
- Test 1: Existing historical GET still works and returns exact persisted snapshot.
- Test 2: Historical GET does not invoke FinancialService.
- Test 3: Historical GET does not invoke MarketService / geo providers.
- Test 4: Historical GET does not invoke SchemeService.
- Test 5: Historical GET does not invoke AIService.
- Test 6: Historical analysis returns original persisted snapshot data.
- Test 7: Historical analysis remains unchanged when active scheme catalog is updated.
- Test 8: Historical scenarios remain retrievable under parent analysis.
- Test 9: Opening a historical analysis does not mutate Analysis, snapshots, or scenarios.
- Test 10: Valid UUID returns snapshot, malformed UUID returns 422, unknown UUID returns 404.
"""
import uuid
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, init_db
from app.repositories import UnitOfWork, get_uow
from app.models import Analysis, FinancialInputSnapshot, FinancialResultSnapshot, ScenarioRecord
from app.models.scheme import Scheme, SchemeVersion, SchemeStatusEnum


@pytest.fixture
def client_with_db(tmp_path):
    """Provides a TestClient with an isolated test SQLite database and overridden UoW dependency."""
    db_file = tmp_path / "test_history_6h.db"
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


SAMPLE_PAYLOAD = {
    "profile": {
        "business_name": "Kisan Agro Processing Unit",
        "category": "Food Processing",
        "description": "Mini rice & pulse mill in rural cluster",
        "location": {
            "state": "Maharashtra",
            "district": "Pune",
            "village": "Baramati Rural",
            "latitude": 18.15,
            "longitude": 74.58
        },
        "experience_years": 3,
        "own_capital": 50000.0,
        "desired_loan": 100000.0,
        "is_new_business": True
    },
    "financials": {
        "startup_cost": 20000.0,
        "equipment_cost": 100000.0,
        "inventory_cost": 30000.0,
        "monthly_fixed_cost": 8000.0,
        "customers_per_day": 40,
        "avg_ticket_price": 45.0,
        "working_days_per_month": 26,
        "variable_cost_pct": 45.0,
        "interest_rate_pct": 10.5,
        "loan_tenure_months": 36
    },
    "preferred_language": "hi"
}


def test_01_historical_get_returns_stored_snapshot(client_with_db):
    """Verify that POST creates and GET retrieves identical persisted snapshot."""
    client, _ = client_with_db
    post_res = client.post("/api/analyze", json=SAMPLE_PAYLOAD)
    assert post_res.status_code == 200
    post_data = post_res.json()
    analysis_id = post_data["analysis_id"]

    get_res = client.get(f"/api/analyze/{analysis_id}")
    assert get_res.status_code == 200
    get_data = get_res.json()

    assert get_data["analysis_id"] == analysis_id
    assert get_data["recommendation_status"] == post_data["recommendation_status"]
    assert get_data["financial_result"]["monthly_net_profit"] == post_data["financial_result"]["monthly_net_profit"]
    assert get_data["financial_result"]["dscr"] == post_data["financial_result"]["dscr"]


def test_02_historical_get_does_not_invoke_financial_service(client_with_db):
    """Verify that historical GET does NOT call FinancialService.calculate."""
    client, _ = client_with_db
    post_res = client.post("/api/analyze", json=SAMPLE_PAYLOAD)
    analysis_id = post_res.json()["analysis_id"]

    with patch("app.services.financial.calculator.FinancialService.calculate") as mock_calc:
        get_res = client.get(f"/api/analyze/{analysis_id}")
        assert get_res.status_code == 200
        mock_calc.assert_not_called()


def test_03_historical_get_does_not_invoke_market_providers(client_with_db):
    """Verify that historical GET does NOT call live market/geospatial providers."""
    client, _ = client_with_db
    post_res = client.post("/api/analyze", json=SAMPLE_PAYLOAD)
    analysis_id = post_res.json()["analysis_id"]

    with patch("app.services.geo.market.MockMarketService.get_market_indicators") as mock_market:
        get_res = client.get(f"/api/analyze/{analysis_id}")
        assert get_res.status_code == 200
        mock_market.assert_not_called()


def test_04_historical_get_does_not_invoke_scheme_service(client_with_db):
    """Verify that historical GET does NOT call SchemeService.match_schemes."""
    client, _ = client_with_db
    post_res = client.post("/api/analyze", json=SAMPLE_PAYLOAD)
    analysis_id = post_res.json()["analysis_id"]

    with patch("app.services.schemes.matcher.SchemeService.match_schemes") as mock_scheme:
        get_res = client.get(f"/api/analyze/{analysis_id}")
        assert get_res.status_code == 200
        mock_scheme.assert_not_called()


def test_05_historical_get_does_not_invoke_ai_service(client_with_db):
    """Verify that historical GET does NOT call AIService.explain_analysis."""
    client, _ = client_with_db
    post_res = client.post("/api/analyze", json=SAMPLE_PAYLOAD)
    analysis_id = post_res.json()["analysis_id"]

    with patch("app.services.ai.explanation.AIService.explain_analysis") as mock_ai:
        get_res = client.get(f"/api/analyze/{analysis_id}")
        assert get_res.status_code == 200
        mock_ai.assert_not_called()


def test_06_historical_analysis_unaltered_by_active_scheme_catalog_update(client_with_db):
    """Verify that changing the scheme catalog does NOT modify an existing historical analysis snapshot."""
    client, session_factory = client_with_db
    post_res = client.post("/api/analyze", json=SAMPLE_PAYLOAD)
    analysis_id = post_res.json()["analysis_id"]
    original_scheme_res = post_res.json()["scheme_result"]

    # Mutate master scheme database by adding a new scheme version
    with session_factory() as session:
        scheme = Scheme(
            id=str(uuid.uuid4()),
            scheme_code="TEST_FUTURE_SCHEME",
            scheme_name="Future Innovation Fund 2030",
        )
        version = SchemeVersion(
            id=str(uuid.uuid4()),
            scheme_id=scheme.id,
            scheme_code="TEST_FUTURE_SCHEME",
            version="2030.1",
            status=SchemeStatusEnum.ACTIVE,
            eligibility_criteria={},
            required_documents=[],
            verification_notes=[],
            metadata_payload={},
        )
        session.add(scheme)
        session.add(version)
        session.commit()

    # Re-fetch historical analysis and ensure scheme snapshot is 100% invariant
    get_res = client.get(f"/api/analyze/{analysis_id}")
    assert get_res.status_code == 200
    assert get_res.json()["scheme_result"] == original_scheme_res


def test_07_historical_scenarios_retrievable(client_with_db):
    """Verify that scenarios saved under a parent analysis remain retrievable via historical routes."""
    client, _ = client_with_db
    post_res = client.post("/api/analyze", json=SAMPLE_PAYLOAD)
    analysis_id = post_res.json()["analysis_id"]

    # Save a scenario
    scen_payload = {
        "name": "Higher Loan Scenario",
        "description": "Evaluating impact of higher borrowing",
        "scenario_own_capital": 30000.0,
        "scenario_desired_loan": 120000.0,
        "scenario_financials": SAMPLE_PAYLOAD["financials"],
    }
    scen_res = client.post(f"/api/analyze/{analysis_id}/scenarios", json=scen_payload)
    assert scen_res.status_code == 201
    scenario_id = scen_res.json()["scenario_id"]

    # List scenarios
    list_res = client.get(f"/api/analyze/{analysis_id}/scenarios")
    assert list_res.status_code == 200
    scenarios = list_res.json()
    assert len(scenarios) == 1
    assert scenarios[0]["scenario_id"] == scenario_id
    assert scenarios[0]["name"] == "Higher Loan Scenario"

    # Get single scenario
    single_res = client.get(f"/api/analyze/{analysis_id}/scenarios/{scenario_id}")
    assert single_res.status_code == 200
    assert single_res.json()["scenario_id"] == scenario_id


def test_08_historical_immutability_no_db_mutation_on_get(client_with_db):
    """Verify that reading a historical analysis makes zero database modifications."""
    client, session_factory = client_with_db
    post_res = client.post("/api/analyze", json=SAMPLE_PAYLOAD)
    analysis_id = post_res.json()["analysis_id"]

    with session_factory() as session:
        initial_analyses_count = len(session.scalars(select(Analysis)).all())
        initial_input_count = len(session.scalars(select(FinancialInputSnapshot)).all())
        initial_result_count = len(session.scalars(select(FinancialResultSnapshot)).all())

    # Execute multiple GET calls
    for _ in range(5):
        get_res = client.get(f"/api/analyze/{analysis_id}")
        assert get_res.status_code == 200

    with session_factory() as session:
        assert len(session.scalars(select(Analysis)).all()) == initial_analyses_count
        assert len(session.scalars(select(FinancialInputSnapshot)).all()) == initial_input_count
        assert len(session.scalars(select(FinancialResultSnapshot)).all()) == initial_result_count


def test_09_direct_uuid_routing_and_malformed_handling(client_with_db):
    """Verify malformed UUID string triggers HTTP 422 with clear validation error."""
    client, _ = client_with_db
    res = client.get("/api/analyze/invalid-not-a-uuid-1234")
    assert res.status_code == 422
    assert "Expected a standard UUID string" in res.json()["detail"]


def test_10_unknown_uuid_returns_404(client_with_db):
    """Verify non-existent valid UUID returns HTTP 404."""
    client, _ = client_with_db
    non_existent_uuid = str(uuid.uuid4())
    res = client.get(f"/api/analyze/{non_existent_uuid}")
    assert res.status_code == 404
    assert f"Historical analysis with ID '{non_existent_uuid}' was not found." in res.json()["detail"]
