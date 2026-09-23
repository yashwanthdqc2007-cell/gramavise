"""Phase 2D-D: Immutability, Historical Retrieval, and Scenario Boundary Audit Tests for SWOT Engine.

Verifies:
1. Complete structural roundtrip persistence and retrieval of SWOT output.
2. Historical GET requests are 100% read-only (zero provider calls, zero recalculations).
3. Stored SWOT snapshots remain strictly immutable after creation.
4. Idempotency replay and payload mismatch conflict guarantees.
5. Scenario Lab creates scenarios without mutating baseline SWOT or analysis snapshots.
6. Legacy historical analysis snapshots without SWOT deserialize cleanly without crashing or fabricating items.
7. Financial metrics and recommendation status invariance.
"""

import pytest
import uuid
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.market import MarketResultResponse, SWOTAnalysis
from app.services.recommendation.swot import SWOTEngine
from app.services.financial.calculator import FinancialService
from app.services.geo.market import MockMarketService
from app.services.schemes.matcher import SchemeService
from app.database import SessionLocal
from app.models.analysis import Analysis, RecommendationStatusEnum
from app.models.financial_snapshot import FinancialInputSnapshot, FinancialResultSnapshot
from app.models.business import BusinessProfile


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def standard_analysis_payload():
    return {
        "profile": {
            "business_name": "Kisan Flour Mill",
            "category": "Flour & Spice Milling (Atta Chakki)",
            "description": "Rural grain processing enterprise",
            "location": {
                "state": "Maharashtra",
                "district": "Pune",
                "village": "Baramati",
                "pincode": "413102",
                "latitude": 18.1550,
                "longitude": 74.5780,
            },
            "experience_years": 3,
            "own_capital": 150000.0,
            "desired_loan": 150000.0,
            "business_stage": "NEW",
        },
        "financials": {
            "startup_cost": 50000.0,
            "equipment_cost": 200000.0,
            "inventory_cost": 50000.0,
            "monthly_fixed_cost": 30000.0,
            "customers_per_day": 25,
            "avg_ticket_price": 700.0,
            "working_days_per_month": 26,
            "variable_cost_pct": 45.0,
            "interest_rate_pct": 10.5,
            "loan_tenure_months": 36,
        },
        "preferred_language": "en",
    }


# =============================================================================
# 1. SNAPSHOT ROUNDTRIP VERIFICATION
# =============================================================================
def test_swot_snapshot_roundtrip_structural_fidelity(client, standard_analysis_payload):
    """Verify that every field of every SWOT item is persisted and retrieved with 100% structural fidelity."""
    post_res = client.post("/api/analyze", json=standard_analysis_payload)
    assert post_res.status_code == 200
    post_data = post_res.json()
    analysis_id = post_data["analysis_id"]

    original_swot = post_data["market_result"]["swot"]
    assert original_swot is not None

    get_res = client.get(f"/api/analyze/{analysis_id}")
    assert get_res.status_code == 200
    get_data = get_res.json()
    retrieved_swot = get_data["market_result"]["swot"]

    # Structural fidelity comparison across all 4 quadrants
    for quadrant in ["strengths", "weaknesses", "opportunities", "threats"]:
        orig_items = original_swot[quadrant]
        retr_items = retrieved_swot[quadrant]
        assert len(orig_items) == len(retr_items), f"Mismatch in {quadrant} item count"

        for orig_item, retr_item in zip(orig_items, retr_items):
            assert orig_item["id"] == retr_item["id"]
            assert orig_item["title"] == retr_item["title"]
            assert orig_item["explanation"] == retr_item["explanation"]
            assert orig_item["category"] == retr_item["category"]
            assert orig_item["importance"] == retr_item["importance"]
            assert orig_item["evidence_type"] == retr_item["evidence_type"]
            assert orig_item["confidence"] == retr_item["confidence"]
            assert orig_item["source"] == retr_item["source"]
            assert orig_item["evidence_ids"] == retr_item["evidence_ids"]

    assert original_swot["confidence"] == retrieved_swot["confidence"]
    assert original_swot["verification_status"] == retrieved_swot["verification_status"]
    assert original_swot["notes"] == retrieved_swot["notes"]


# =============================================================================
# 2. PROVE HISTORICAL RETRIEVAL IS 100% READ-ONLY
# =============================================================================
def test_historical_retrieval_does_not_call_any_computation_or_providers(client, standard_analysis_payload):
    """Prove using instrumented spies that historical GET never calls SWOTEngine, providers, or financial service."""
    post_res = client.post("/api/analyze", json=standard_analysis_payload)
    assert post_res.status_code == 200
    analysis_id = post_res.json()["analysis_id"]

    with patch.object(SWOTEngine, "generate_swot") as mock_swot, \
         patch.object(FinancialService, "calculate") as mock_fin, \
         patch.object(MockMarketService, "get_market_indicators") as mock_mkt, \
         patch.object(SchemeService, "match_schemes") as mock_sch:

        get_res = client.get(f"/api/analyze/{analysis_id}")
        assert get_res.status_code == 200
        get_data = get_res.json()

        # Assert zero invocations across all analytical engines
        mock_swot.assert_not_called()
        mock_fin.assert_not_called()
        mock_mkt.assert_not_called()
        mock_sch.assert_not_called()

        assert get_data["market_result"]["swot"] is not None


# =============================================================================
# 3. SNAPSHOT IMMUTABILITY UNDER CONTEXT CHANGES
# =============================================================================
def test_snapshot_immutability_when_provider_context_changes(client, standard_analysis_payload):
    """Verify that modifying current external provider responses does not alter already-persisted historical SWOT."""
    post_res = client.post("/api/analyze", json=standard_analysis_payload)
    assert post_res.status_code == 200
    analysis_id = post_res.json()["analysis_id"]
    original_swot = post_res.json()["market_result"]["swot"]

    # Even if market service would now return 10 competitors and different indicators:
    with patch.object(MockMarketService, "get_market_indicators", side_effect=Exception("Market service changed")):
        get_res = client.get(f"/api/analyze/{analysis_id}")
        assert get_res.status_code == 200
        get_data = get_res.json()

        # Historical snapshot is unchanged and unaffected
        assert get_data["market_result"]["swot"] == original_swot


# =============================================================================
# 4. IDEMPOTENCY REPLAY AND CONFLICT VERIFICATION
# =============================================================================
def test_idempotency_replay_preserves_swot_without_recalculation(client, standard_analysis_payload):
    """Verify that repeated requests with same Idempotency-Key return the exact persisted SWOT snapshot."""
    idempotency_key = str(uuid.uuid4())
    headers = {"Idempotency-Key": idempotency_key}

    res1 = client.post("/api/analyze", json=standard_analysis_payload, headers=headers)
    assert res1.status_code == 200
    data1 = res1.json()
    analysis_id1 = data1["analysis_id"]
    swot1 = data1["market_result"]["swot"]

    # Replay with same key & payload
    with patch.object(SWOTEngine, "generate_swot") as mock_swot:
        res2 = client.post("/api/analyze", json=standard_analysis_payload, headers=headers)
        assert res2.status_code == 200
        data2 = res2.json()

        # Proves no recalculation on replay
        mock_swot.assert_not_called()
        assert data2["analysis_id"] == analysis_id1
        assert data2["market_result"]["swot"] == swot1


def test_idempotency_conflict_preserves_original_swot(client, standard_analysis_payload):
    """Verify that re-using an Idempotency-Key with different payload raises 409 and leaves original SWOT intact."""
    idempotency_key = str(uuid.uuid4())
    headers = {"Idempotency-Key": idempotency_key}

    res1 = client.post("/api/analyze", json=standard_analysis_payload, headers=headers)
    assert res1.status_code == 200
    data1 = res1.json()
    analysis_id1 = data1["analysis_id"]
    swot1 = data1["market_result"]["swot"]

    # Mismatched payload with same key
    modified_payload = dict(standard_analysis_payload)
    modified_payload["financials"] = dict(standard_analysis_payload["financials"])
    modified_payload["financials"]["customers_per_day"] = 999

    res2 = client.post("/api/analyze", json=modified_payload, headers=headers)
    assert res2.status_code == 409

    # Verify original persisted record is completely un-mutated
    get_res = client.get(f"/api/analyze/{analysis_id1}")
    assert get_res.status_code == 200
    assert get_res.json()["market_result"]["swot"] == swot1


# =============================================================================
# 5. SCENARIO LAB BASELINE ISOLATION
# =============================================================================
def test_scenario_creation_does_not_mutate_baseline_swot(client, standard_analysis_payload):
    """Verify that saving what-if scenarios in Scenario Lab preserves baseline SWOT immutability."""
    # 1. Create Baseline Analysis
    post_res = client.post("/api/analyze", json=standard_analysis_payload)
    assert post_res.status_code == 200
    base_data = post_res.json()
    analysis_id = base_data["analysis_id"]
    baseline_swot_before = base_data["market_result"]["swot"]

    # 2. Save Scenario 1: Cost stress override
    scenario_1_payload = {
        "scenario_name": "Conservative Input Costs",
        "scenario_own_capital": 150000.0,
        "scenario_desired_loan": 150000.0,
        "scenario_financials": dict(standard_analysis_payload["financials"]),
    }
    scenario_1_payload["scenario_financials"]["variable_cost_pct"] = 60.0
    res_s1 = client.post(f"/api/analyze/{analysis_id}/scenarios", json=scenario_1_payload)
    assert res_s1.status_code == 201

    # 3. Save Scenario 2: Footfall drop override
    scenario_2_payload = {
        "scenario_name": "Low Footfall",
        "scenario_own_capital": 150000.0,
        "scenario_desired_loan": 150000.0,
        "scenario_financials": dict(standard_analysis_payload["financials"]),
    }
    scenario_2_payload["scenario_financials"]["customers_per_day"] = 12
    res_s2 = client.post(f"/api/analyze/{analysis_id}/scenarios", json=scenario_2_payload)
    assert res_s2.status_code == 201

    # 4. Save Scenario 3: Debt-free expansion override
    scenario_3_payload = {
        "scenario_name": "Debt-Free Self-Funded",
        "scenario_own_capital": 300000.0,
        "scenario_desired_loan": 0.0,
        "scenario_financials": dict(standard_analysis_payload["financials"]),
    }
    res_s3 = client.post(f"/api/analyze/{analysis_id}/scenarios", json=scenario_3_payload)
    assert res_s3.status_code == 201

    # 5. Verify 4th scenario is rejected with 409
    scenario_4_payload = {
        "scenario_name": "4th Scenario Over Limit",
        "scenario_own_capital": 150000.0,
        "scenario_desired_loan": 150000.0,
        "scenario_financials": dict(standard_analysis_payload["financials"]),
    }
    res_s4 = client.post(f"/api/analyze/{analysis_id}/scenarios", json=scenario_4_payload)
    assert res_s4.status_code == 409

    # 6. Retrieve Baseline Analysis and verify SWOT is 100% untouched
    get_res = client.get(f"/api/analyze/{analysis_id}")
    assert get_res.status_code == 200
    baseline_swot_after = get_res.json()["market_result"]["swot"]
    assert baseline_swot_after == baseline_swot_before


# =============================================================================
# 6. LEGACY SNAPSHOT COMPATIBILITY
# =============================================================================
def test_legacy_snapshot_without_swot_in_database_loads_cleanly(client):
    """Verify that a legacy Analysis record created without SWOT loads without crashing or fabricating items."""
    from app.repositories import get_uow
    analysis_uuid = str(uuid.uuid4())
    business_uuid = str(uuid.uuid4())

    legacy_market_snapshot = {
        "location_summary": "Legacy Village, Wardha, Maharashtra",
        "competitor_count": 0,
        "direct_competitor_count": 0,
        "adjacent_competitor_count": 0,
        "catchment_radius_km": 5.0,
        "coverage_confidence": "LOW",
        "demand_indicator": "HIGH",
        # NOTE: No "swot" key in legacy JSON
    }

    biz = BusinessProfile(
        id=business_uuid,
        business_name="Legacy Kirana Store",
        category="Kirana & General Store",
        state="Maharashtra",
        district="Wardha",
        village="Legacy Village",
        own_capital=50000.0,
        desired_loan=50000.0,
        is_new_business=True,
    )

    analysis = Analysis(
        id=analysis_uuid,
        business_id=business_uuid,
        recommendation_status=RecommendationStatusEnum.PROCEED,
        overall_verdict="PROCEED",
        confidence_score=0.85,
        schema_version="1.0.0",
        rules_version="1.0.0",
        business_input_snapshot={},
        market_result_snapshot=legacy_market_snapshot,
        scheme_result_snapshot={"schemes": [], "eligible_schemes_count": 0},
        evidence_ledger_snapshot=[],
        decision_trace_snapshot={},
        action_plan_snapshot={},
        bank_readiness_snapshot={},
        risk_factors=[],
        ai_explanation={},
    )

    fin_res = FinancialResultSnapshot(
        analysis_id=analysis_uuid,
        total_capex=100000.0,
        required_loan_amount=50000.0,
        monthly_revenue=80000.0,
        monthly_variable_cost=40000.0,
        monthly_gross_profit=40000.0,
        monthly_fixed_cost=15000.0,
        monthly_emi=1600.0,
        monthly_net_profit=23400.0,
        net_profit_margin_pct=29.25,
        break_even_revenue_monthly=33200.0,
        break_even_units_daily=10,
        dscr=15.6,
        is_financially_viable=True,
        explanations={},
    )

    uow_gen = app.dependency_overrides[get_uow]()
    uow = next(uow_gen)
    try:
        uow.business_profiles.create(biz)
        uow.analyses.create(analysis, input_snapshot=None, result_snapshot=fin_res)
        uow.commit()
    finally:
        try:
            next(uow_gen)
        except StopIteration:
            pass

    # Query the legacy analysis via GET /api/analyze/{id}
    res = client.get(f"/api/analyze/{analysis_uuid}")
    assert res.status_code == 200
    data = res.json()

    assert data["analysis_id"] == analysis_uuid
    assert data["financial_result"]["monthly_revenue"] == 80000.0
    assert data["market_result"]["swot"] is None  # Cleanly None, no crash, no fabricated data


# =============================================================================
# 7. FINANCIAL INVARIANCE VERIFICATION
# =============================================================================
def test_swot_does_not_mutate_financial_calculator_math(client, standard_analysis_payload):
    """Verify that all financial metrics and recommendation status are completely invariant to SWOT."""
    post_res = client.post("/api/analyze", json=standard_analysis_payload)
    assert post_res.status_code == 200
    data = post_res.json()

    fin = data["financial_result"]
    assert fin["monthly_revenue"] == 455000.0
    assert fin["monthly_variable_cost"] == 204750.0
    assert fin["monthly_gross_profit"] == 250250.0
    assert fin["monthly_fixed_cost"] == 30000.0
    assert fin["monthly_net_profit"] == pytest.approx(215374.63, 0.01)
    assert fin["is_financially_viable"] is True
    assert data["recommendation_status"] == "PROCEED"
    assert data["overall_verdict"] == "PROCEED"
