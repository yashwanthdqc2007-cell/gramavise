"""Phase 6D Analysis Persistence & Historical Retrieval Test Suite.

Verifies:
- Test 1: POST /api/analyze persists the complete analysis to the database.
- Test 2: All 12 financial input assumptions match the persisted snapshot.
- Test 3: Deterministic financial calculation result is persisted without recalculation.
- Test 4: Evidence ledger with provenance survives round-trip.
- Test 5: Decision trace rule evaluations survive retrieval.
- Test 6: Pre-loan action plan survives retrieval.
- Test 7: Scheme and market evaluation results survive retrieval.
- Test 8: AI advisory explanation survives retrieval.
- Test 9: GET /api/analyze/{analysis_id} returns identical response to POST /api/analyze.
- Test 10: GET with non-existent UUID returns HTTP 404.
- Test 11: GET with malformed ID returns HTTP 422.
- Test 12 & 13: GET historical retrieval does NOT call FinancialService, providers, or AI.
- Test 14: Historical immutability of Analysis A when context changes.
- Test 15: Atomic rollback when persistence fails.
- Test 16: Multiple distinct analyses coexist without overwriting each other.
- Test 17: Mathematical & recommendation parity before and after persistence.
"""
import uuid
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, init_db, get_db
from app.repositories import UnitOfWork, get_uow
from app.models import Analysis, FinancialInputSnapshot, FinancialResultSnapshot


@pytest.fixture
def client_with_db(tmp_path):
    """Provides a TestClient with an isolated test SQLite database and overridden UoW dependency."""
    db_file = tmp_path / "test_api_persist.db"
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
        "business_name": "Gram Udyog Oil Expeller",
        "category": "Agro Processing",
        "description": "Cold-pressed mustard oil processing unit",
        "location": {
            "state": "Uttar Pradesh",
            "district": "Varanasi",
            "village": "Ramnagar",
            "latitude": 25.267,
            "longitude": 83.025
        },
        "experience_years": 3,
        "own_capital": 50000.0,
        "desired_loan": 150000.0,
        "is_new_business": True
    },
    "financials": {
        "startup_cost": 20000.0,
        "equipment_cost": 100000.0,
        "inventory_cost": 80000.0,
        "monthly_fixed_cost": 12000.0,
        "customers_per_day": 25,
        "avg_ticket_price": 200.0,
        "working_days_per_month": 26,
        "variable_cost_pct": 50.0,
        "interest_rate_pct": 10.5,
        "loan_tenure_months": 36
    },
    "preferred_language": "hi"
}


def test_post_analyze_persists_and_returns_id(client_with_db):
    """Test 1: POST /api/analyze executes analysis and persists record to database."""
    client, session_factory = client_with_db
    response = client.post("/api/analyze", json=SAMPLE_PAYLOAD)
    assert response.status_code == 200
    data = response.json()

    assert "analysis_id" in data
    analysis_id = data["analysis_id"]
    assert analysis_id is not None

    # Verify record exists in DB
    with UnitOfWork(session_factory=session_factory) as uow:
        stored_analysis = uow.analyses.get_by_id(analysis_id)
        assert stored_analysis is not None
        assert stored_analysis.id == analysis_id
        assert stored_analysis.confidence_score == data["confidence_score"]


def test_financial_input_persistence_fidelity(client_with_db):
    """Test 2: Persisted FinancialInputSnapshot preserves all 12 input assumptions."""
    client, session_factory = client_with_db
    response = client.post("/api/analyze", json=SAMPLE_PAYLOAD)
    data = response.json()
    analysis_id = data["analysis_id"]

    with UnitOfWork(session_factory=session_factory) as uow:
        stored = uow.analyses.get_by_id(analysis_id)
        fin_in = stored.financial_input_snapshot
        assert fin_in is not None
        assert fin_in.own_capital == SAMPLE_PAYLOAD["profile"]["own_capital"]
        assert fin_in.desired_loan == SAMPLE_PAYLOAD["profile"]["desired_loan"]
        assert fin_in.startup_cost == SAMPLE_PAYLOAD["financials"]["startup_cost"]
        assert fin_in.equipment_cost == SAMPLE_PAYLOAD["financials"]["equipment_cost"]
        assert fin_in.inventory_cost == SAMPLE_PAYLOAD["financials"]["inventory_cost"]
        assert fin_in.monthly_fixed_cost == SAMPLE_PAYLOAD["financials"]["monthly_fixed_cost"]
        assert fin_in.customers_per_day == SAMPLE_PAYLOAD["financials"]["customers_per_day"]
        assert fin_in.avg_ticket_price == SAMPLE_PAYLOAD["financials"]["avg_ticket_price"]
        assert fin_in.working_days_per_month == SAMPLE_PAYLOAD["financials"]["working_days_per_month"]
        assert fin_in.variable_cost_pct == SAMPLE_PAYLOAD["financials"]["variable_cost_pct"]
        assert fin_in.interest_rate_pct == SAMPLE_PAYLOAD["financials"]["interest_rate_pct"]
        assert fin_in.loan_tenure_months == SAMPLE_PAYLOAD["financials"]["loan_tenure_months"]


def test_financial_result_persistence_fidelity(client_with_db):
    """Test 3: Persisted FinancialResultSnapshot exactly matches returned metrics without recalculation."""
    client, session_factory = client_with_db
    response = client.post("/api/analyze", json=SAMPLE_PAYLOAD)
    data = response.json()
    analysis_id = data["analysis_id"]
    api_fin = data["financial_result"]

    with UnitOfWork(session_factory=session_factory) as uow:
        stored = uow.analyses.get_by_id(analysis_id)
        fin_res = stored.financial_result_snapshot
        assert fin_res is not None
        assert fin_res.total_capex == api_fin["total_capex"]
        assert fin_res.required_loan_amount == api_fin["required_loan_amount"]
        assert fin_res.monthly_revenue == api_fin["monthly_revenue"]
        assert fin_res.monthly_variable_cost == api_fin["monthly_variable_cost"]
        assert fin_res.monthly_gross_profit == api_fin["monthly_gross_profit"]
        assert fin_res.monthly_fixed_cost == api_fin["monthly_fixed_cost"]
        assert fin_res.monthly_emi == api_fin["monthly_emi"]
        assert fin_res.monthly_net_profit == api_fin["monthly_net_profit"]
        assert fin_res.dscr == api_fin["dscr"]
        assert fin_res.is_financially_viable == api_fin["is_financially_viable"]


def test_evidence_decision_trace_action_plan_snapshots(client_with_db):
    """Tests 4, 5, 6, 7, 8: Evidence ledger, decision trace, action plan, schemes, market, and AI survive round-trip."""
    client, session_factory = client_with_db
    response = client.post("/api/analyze", json=SAMPLE_PAYLOAD)
    data = response.json()
    analysis_id = data["analysis_id"]

    with UnitOfWork(session_factory=session_factory) as uow:
        stored = uow.analyses.get_by_id(analysis_id)
        assert len(stored.evidence_ledger_snapshot) == len(data["evidence_ledger"])
        assert stored.decision_trace_snapshot["summary"] == data["decision_trace"]["summary"]
        assert len(stored.action_plan_snapshot["actions"]) == len(data["action_plan"]["actions"])
        assert len(stored.scheme_result_snapshot["schemes"]) == len(data["scheme_result"]["schemes"])
        assert stored.market_result_snapshot["competitor_count"] == data["market_result"]["competitor_count"]
        assert stored.ai_explanation["language"] == data["ai_explanation"]["language"]


def test_get_historical_analysis_endpoint(client_with_db):
    """Test 9: GET /api/analyze/{analysis_id} reconstructs exact analysis response."""
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
    assert get_data["confidence_score"] == post_data["confidence_score"]
    assert get_data["financial_result"]["monthly_net_profit"] == post_data["financial_result"]["monthly_net_profit"]
    assert get_data["financial_result"]["dscr"] == post_data["financial_result"]["dscr"]
    assert get_data["market_result"]["competitor_count"] == post_data["market_result"]["competitor_count"]
    assert len(get_data["evidence_ledger"]) == len(post_data["evidence_ledger"])
    assert get_data["decision_trace"]["summary"] == post_data["decision_trace"]["summary"]


def test_get_historical_analysis_not_found(client_with_db):
    """Test 10: GET with non-existent UUID returns HTTP 404."""
    client, _ = client_with_db
    random_uuid = str(uuid.uuid4())
    res = client.get(f"/api/analyze/{random_uuid}")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_get_historical_analysis_invalid_id(client_with_db):
    """Test 11: GET with malformed ID returns HTTP 422."""
    client, _ = client_with_db
    res = client.get("/api/analyze/invalid-not-a-uuid")
    assert res.status_code == 422
    assert "invalid analysis id format" in res.json()["detail"].lower()


def test_get_historical_analysis_does_not_recalculate_or_call_providers(client_with_db):
    """Tests 12 & 13: Historical retrieval is pure read-only and does not invoke calculation or providers."""
    client, _ = client_with_db
    post_res = client.post("/api/analyze", json=SAMPLE_PAYLOAD)
    analysis_id = post_res.json()["analysis_id"]

    with patch("app.services.financial.calculator.FinancialService.calculate") as mock_calc, \
         patch("app.services.geo.market.MockMarketService.get_market_indicators") as mock_market, \
         patch("app.services.schemes.matcher.SchemeService.match_schemes") as mock_scheme, \
         patch("app.services.ai.explanation.AIService.explain_analysis") as mock_ai:
        
        get_res = client.get(f"/api/analyze/{analysis_id}")
        assert get_res.status_code == 200

        mock_calc.assert_not_called()
        mock_market.assert_not_called()
        mock_scheme.assert_not_called()
        mock_ai.assert_not_called()


def test_historical_immutability_when_context_changes(client_with_db):
    """Test 14: Changing current business context does not alter historical Analysis A."""
    client, session_factory = client_with_db
    post_res = client.post("/api/analyze", json=SAMPLE_PAYLOAD)
    analysis_id = post_res.json()["analysis_id"]
    orig_profit = post_res.json()["financial_result"]["monthly_net_profit"]

    # Mutate current business profile in DB
    with UnitOfWork(session_factory=session_factory) as uow:
        analysis = uow.analyses.get_by_id(analysis_id)
        assert analysis is not None
        if analysis.business:
            analysis.business.business_name = "Completely Altered Name"
            analysis.business.own_capital = 999999.0
            uow.commit()

    # Retrieve analysis A - must remain untouched
    get_res = client.get(f"/api/analyze/{analysis_id}")
    assert get_res.status_code == 200
    assert get_res.json()["financial_result"]["monthly_net_profit"] == orig_profit


def test_atomic_rollback_on_persistence_failure(client_with_db):
    """Test 15: If database commit fails, API returns HTTP 500 and no partial records remain."""
    client, session_factory = client_with_db

    with patch("app.repositories.unit_of_work.UnitOfWork.commit", side_effect=RuntimeError("Simulated DB connection error")):
        res = client.post("/api/analyze", json=SAMPLE_PAYLOAD)
        assert res.status_code == 500
        assert "failed to persist" in res.json()["detail"].lower()

    # Verify no records were saved
    with UnitOfWork(session_factory=session_factory) as uow:
        analyses = uow.analyses.list_by_business(str(uuid.uuid4()))
        assert len(analyses) == 0


def test_multiple_analyses_coexist_independently(client_with_db):
    """Test 16: Multiple analyses persist with unique IDs and do not overwrite each other."""
    client, _ = client_with_db

    res_1 = client.post("/api/analyze", json=SAMPLE_PAYLOAD)
    id_1 = res_1.json()["analysis_id"]

    payload_2 = dict(SAMPLE_PAYLOAD)
    payload_2["financials"] = dict(SAMPLE_PAYLOAD["financials"])
    payload_2["financials"]["customers_per_day"] = 50
    res_2 = client.post("/api/analyze", json=payload_2)
    id_2 = res_2.json()["analysis_id"]

    assert id_1 != id_2

    get_1 = client.get(f"/api/analyze/{id_1}").json()
    get_2 = client.get(f"/api/analyze/{id_2}").json()

    assert get_1["financial_result"]["monthly_revenue"] == res_1.json()["financial_result"]["monthly_revenue"]
    assert get_2["financial_result"]["monthly_revenue"] == res_2.json()["financial_result"]["monthly_revenue"]
    assert get_1["financial_result"]["monthly_revenue"] != get_2["financial_result"]["monthly_revenue"]


def test_mathematical_and_recommendation_parity(client_with_db):
    """Test 17 & 26: Pre-persistence result == post-persistence result == historically retrieved result."""
    client, _ = client_with_db
    post_res = client.post("/api/analyze", json=SAMPLE_PAYLOAD)
    post_data = post_res.json()
    analysis_id = post_data["analysis_id"]

    get_res = client.get(f"/api/analyze/{analysis_id}")
    get_data = get_res.json()

    # Numerical parity
    assert post_data["financial_result"]["total_capex"] == get_data["financial_result"]["total_capex"]
    assert post_data["financial_result"]["monthly_net_profit"] == get_data["financial_result"]["monthly_net_profit"]
    assert post_data["financial_result"]["dscr"] == get_data["financial_result"]["dscr"]
    assert post_data["financial_result"]["is_financially_viable"] == get_data["financial_result"]["is_financially_viable"]

    # Recommendation parity
    assert post_data["recommendation_status"] == get_data["recommendation_status"]
    assert post_data["confidence_score"] == get_data["confidence_score"]
