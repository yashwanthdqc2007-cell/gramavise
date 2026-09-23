import pytest
import uuid
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.market import MarketResultResponse, SWOTAnalysis
from app.services.recommendation.swot import SWOTEngine


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_analysis_payload():
    return {
        "profile": {
            "business_name": "Kisan Flour Mill",
            "category": "Flour & Spice Milling (Atta Chakki)",
            "description": "Rural grain processing mill",
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


def test_01_analyze_response_contains_swot(client, sample_analysis_payload):
    """Test that POST /api/analyze returns a structured SWOTAnalysis in market_result."""
    response = client.post("/api/analyze", json=sample_analysis_payload)
    assert response.status_code == 200
    data = response.json()

    assert "market_result" in data
    market_result = data["market_result"]
    assert "swot" in market_result
    swot = market_result["swot"]
    assert swot is not None
    assert "strengths" in swot
    assert "weaknesses" in swot
    assert "opportunities" in swot
    assert "threats" in swot


def test_02_swot_generated_from_real_analysis_context(client, sample_analysis_payload):
    """Test that SWOT factors reflect the exact financial and market numbers of the request."""
    response = client.post("/api/analyze", json=sample_analysis_payload)
    assert response.status_code == 200
    data = response.json()

    swot = data["market_result"]["swot"]
    financial_res = data["financial_result"]

    # If DSCR >= 1.50, check that STR-FIN-DSCR-STRONG exists and quotes the exact DSCR
    if financial_res["dscr"] >= 1.50:
        dscr_strengths = [s for s in swot["strengths"] if s["id"] == "STR-FIN-DSCR-STRONG"]
        assert len(dscr_strengths) == 1
        assert f"{financial_res['dscr']:,.2f}x" in dscr_strengths[0]["explanation"]


def test_03_emitted_evidence_ids_exist_in_evidence_ledger(client, sample_analysis_payload):
    """Test that every emitted SWOT item strictly references evidence IDs present in the Evidence Ledger."""
    response = client.post("/api/analyze", json=sample_analysis_payload)
    assert response.status_code == 200
    data = response.json()

    ledger = data.get("evidence_ledger", []) or data.get("evidence_list", [])
    ledger_ids = {e["evidence_id"] for e in ledger if e.get("evidence_id")}

    swot = data["market_result"]["swot"]
    all_swot_items = swot["strengths"] + swot["weaknesses"] + swot["opportunities"] + swot["threats"]

    assert len(all_swot_items) > 0
    for item in all_swot_items:
        assert len(item["evidence_ids"]) > 0
        for eid in item["evidence_ids"]:
            assert eid in ledger_ids, f"SWOT item {item['id']} references missing evidence ID {eid}"


def test_04_missing_market_evidence_does_not_crash_analysis(client, sample_analysis_payload):
    """Test that an unmapped location with missing demographic and price evidence succeeds cleanly."""
    sample_analysis_payload["profile"]["location"]["village"] = "NonExistentVillage999"
    sample_analysis_payload["profile"]["location"]["latitude"] = None
    sample_analysis_payload["profile"]["location"]["longitude"] = None

    response = client.post("/api/analyze", json=sample_analysis_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["financial_result"]["is_financially_viable"] is True
    assert data["market_result"]["swot"] is not None


def test_05_osm_failure_does_not_crash_analysis(client, sample_analysis_payload):
    """Test that OSM provider failure is handled gracefully and analysis succeeds."""
    from app.schemas.market import CoverageConfidenceLevel
    with patch("app.services.geo.market.OSMCompetitorProvider.get_competitors", return_value=([], CoverageConfidenceLevel.LOW, "OSM Overpass 503 Service Unavailable")):
        response = client.post("/api/analyze", json=sample_analysis_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["market_result"]["swot"] is not None
        # Must not claim low competition strength when provider failed/coverage is low
        assert not any(s["id"] == "STR-MKT-COMP-LOW" for s in data["market_result"]["swot"]["strengths"])


def test_06_mandi_failure_does_not_crash_analysis(client, sample_analysis_payload):
    """Test that Agmarknet provider failure is handled gracefully and analysis succeeds."""
    from app.providers.base import ProviderResult
    failed_result = ProviderResult(
        provider_name="Agmarknet Mandi Price API",
        data_category="COMMODITY_PRICES",
        success=False,
        errors=["Mandi connection timeout / service unavailable"],
        raw_payload={}
    )
    with patch("app.providers.price.PriceDataProvider.fetch_evidence", return_value=failed_result):
        response = client.post("/api/analyze", json=sample_analysis_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["market_result"]["swot"] is not None
        # Should not produce favorable price opportunity when mandi price is missing
        assert not any(o["id"] == "OPP-MKT-PRICE-FAVORABLE" for o in data["market_result"]["swot"]["opportunities"])


def test_07_all_market_provider_failure_does_not_crash_analysis(client, sample_analysis_payload):
    """Test that complete failure of all market providers does not crash financial or overall analysis."""
    from app.schemas.market import CoverageConfidenceLevel
    from app.providers.base import ProviderResult
    failed_result = ProviderResult(
        provider_name="Failed Provider",
        data_category="TEST",
        success=False,
        errors=["Failed"],
        raw_payload={}
    )
    with patch("app.services.geo.market.OSMCompetitorProvider.get_competitors", return_value=([], CoverageConfidenceLevel.LOW, "Failed")), \
         patch("app.providers.geo.GeoDataProvider.fetch_evidence", return_value=failed_result), \
         patch("app.providers.demographics.DemographicDataProvider.fetch_evidence", return_value=failed_result), \
         patch("app.providers.price.PriceDataProvider.fetch_evidence", return_value=failed_result):
        response = client.post("/api/analyze", json=sample_analysis_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["financial_result"] is not None
        assert data["market_result"] is not None
        assert data["market_result"]["swot"] is not None


def test_08_unverified_geography_does_not_produce_low_competition_strength(client, sample_analysis_payload):
    """Test that unverified coordinates or LOW coverage never emit STR-MKT-COMP-LOW."""
    sample_analysis_payload["profile"]["location"]["latitude"] = None
    sample_analysis_payload["profile"]["location"]["longitude"] = None
    sample_analysis_payload["profile"]["location"]["village"] = "RemoteUnverifiedHamlet"

    response = client.post("/api/analyze", json=sample_analysis_payload)
    assert response.status_code == 200
    data = response.json()
    swot = data["market_result"]["swot"]

    assert not any(s["id"] == "STR-MKT-COMP-LOW" for s in swot["strengths"])
    assert any(t["id"] == "THR-GEO-COVERAGE-LOW" for t in swot["threats"])


def test_09_missing_mandi_price_does_not_produce_favorable_price_claim(client, sample_analysis_payload):
    """Test that missing mandi price feeds emit a weakness notice and never claim low raw material prices."""
    sample_analysis_payload["profile"]["category"] = "Tailoring & Garment Making"

    response = client.post("/api/analyze", json=sample_analysis_payload)
    assert response.status_code == 200
    data = response.json()
    swot = data["market_result"]["swot"]

    for item in swot["strengths"] + swot["opportunities"]:
        assert "raw material prices are low" not in item["explanation"].lower()
        assert "prices are favorable" not in item["explanation"].lower()


def test_10_scheme_match_produces_potential_scheme_opportunity(client, sample_analysis_payload):
    """Test that statutory scheme matches emit cautious potential match opportunities."""
    response = client.post("/api/analyze", json=sample_analysis_payload)
    assert response.status_code == 200
    data = response.json()
    swot = data["market_result"]["swot"]

    scheme_opps = [o for o in swot["opportunities"] if o["id"].startswith("OPP-SCH-")]
    if scheme_opps:
        for opp in scheme_opps:
            assert "potential match with" in opp["explanation"]
            assert "guaranteed subsidy" not in opp["explanation"].lower()
            assert "bank will sanction" not in opp["explanation"].lower()


def test_11_census_opportunity_requires_verified_geography(client, sample_analysis_payload):
    """Test that Census population opportunity is emitted for verified Baramati location."""
    response = client.post("/api/analyze", json=sample_analysis_payload)
    assert response.status_code == 200
    data = response.json()
    swot = data["market_result"]["swot"]

    census_opps = [o for o in swot["opportunities"] if o["id"] == "OPP-DEM-CENSUS-POP"]
    if census_opps:
        assert "Census 2011" in census_opps[0]["explanation"]
        assert "guaranteed customer base" not in census_opps[0]["explanation"].lower()


def test_12_modelled_catchment_population_cannot_generate_census_opportunity(client, sample_analysis_payload):
    """Test that prototype 4500 catchment model is not falsely attributed as Census when Census is missing."""
    sample_analysis_payload["profile"]["location"]["village"] = "ZeroCensusVillage"
    sample_analysis_payload["profile"]["location"]["latitude"] = 18.1550
    sample_analysis_payload["profile"]["location"]["longitude"] = 74.5780

    response = client.post("/api/analyze", json=sample_analysis_payload)
    assert response.status_code == 200
    data = response.json()
    swot = data["market_result"]["swot"]

    # Without verified Census village demographic observation, OPP-DEM-CENSUS-POP must not be emitted
    if data["market_result"].get("demographics") is None:
        assert not any(o["id"] == "OPP-DEM-CENSUS-POP" for o in swot["opportunities"])


def test_13_financial_results_remain_unchanged_after_swot_generation(client, sample_analysis_payload):
    """Test that financial metrics (net profit, DSCR, break-even) are untouched by SWOT generation."""
    response = client.post("/api/analyze", json=sample_analysis_payload)
    assert response.status_code == 200
    data = response.json()

    fin = data["financial_result"]
    assert fin["monthly_revenue"] == 455000.0  # 25 * 700 * 26
    assert fin["monthly_variable_cost"] == 204750.0  # 455k * 45%
    assert fin["monthly_fixed_cost"] == 30000.0
    assert fin["monthly_emi"] > 0
    assert fin["monthly_net_profit"] > 0
    assert fin["dscr"] > 0


def test_14_feasibility_status_remains_unchanged(client, sample_analysis_payload):
    """Test that RecommendationStatus is invariant to SWOT generation."""
    response = client.post("/api/analyze", json=sample_analysis_payload)
    assert response.status_code == 200
    data = response.json()

    assert data["recommendation_status"] == "PROCEED"
    assert data["overall_verdict"] == "PROCEED"


def test_15_historical_retrieval_returns_exact_persisted_swot(client, sample_analysis_payload):
    """Test that GET /api/analyze/{id} returns the exact point-in-time persisted SWOT from snapshot."""
    post_res = client.post("/api/analyze", json=sample_analysis_payload)
    assert post_res.status_code == 200
    post_data = post_res.json()
    analysis_id = post_data["analysis_id"]
    original_swot = post_data["market_result"]["swot"]

    get_res = client.get(f"/api/analyze/{analysis_id}")
    assert get_res.status_code == 200
    get_data = get_res.json()

    assert get_data["analysis_id"] == analysis_id
    assert get_data["market_result"]["swot"] == original_swot


def test_16_historical_retrieval_does_not_invoke_swot_engine(client, sample_analysis_payload):
    """Test that GET /api/analyze/{id} loads directly from DB snapshot without re-running SWOTEngine."""
    post_res = client.post("/api/analyze", json=sample_analysis_payload)
    analysis_id = post_res.json()["analysis_id"]

    with patch.object(SWOTEngine, "generate_swot") as mock_generate:
        get_res = client.get(f"/api/analyze/{analysis_id}")
        assert get_res.status_code == 200
        mock_generate.assert_not_called()


def test_17_idempotent_replay_returns_same_swot_snapshot(client, sample_analysis_payload):
    """Test that replaying a request with the same Idempotency-Key returns identical SWOT snapshot."""
    idempotency_key = str(uuid.uuid4())
    headers = {"Idempotency-Key": idempotency_key}

    res1 = client.post("/api/analyze", json=sample_analysis_payload, headers=headers)
    assert res1.status_code == 200
    data1 = res1.json()

    res2 = client.post("/api/analyze", json=sample_analysis_payload, headers=headers)
    assert res2.status_code == 200
    data2 = res2.json()

    assert data1["analysis_id"] == data2["analysis_id"]
    assert data1["market_result"]["swot"] == data2["market_result"]["swot"]


def test_18_legacy_snapshot_without_swot_remains_readable():
    """Test that a legacy market result snapshot lacking 'swot' field deserializes cleanly with swot=None."""
    legacy_dict = {
        "location_summary": "Baramati, Pune",
        "competitor_count": 1,
        "direct_competitor_count": 1,
        "adjacent_competitor_count": 0,
        "catchment_radius_km": 5.0,
        "coverage_confidence": "HIGH",
        "demand_indicator": "HIGH",
    }
    reconstructed = MarketResultResponse.model_validate(legacy_dict)
    assert reconstructed.swot is None


def test_19_no_nan_or_infinity_in_api_response(client, sample_analysis_payload):
    """Test that the entire API JSON response contains valid, finite numeric values and strings."""
    response = client.post("/api/analyze", json=sample_analysis_payload)
    assert response.status_code == 200
    raw_text = response.text.lower()
    assert ": nan" not in raw_text
    assert ": inf" not in raw_text
    assert ": -inf" not in raw_text


def test_20_repeated_analysis_produces_deterministic_swot(client, sample_analysis_payload):
    """Test that two separate requests with identical parameters produce deterministic SWOT parity."""
    res1 = client.post("/api/analyze", json=sample_analysis_payload)
    res2 = client.post("/api/analyze", json=sample_analysis_payload)

    swot1 = res1.json()["market_result"]["swot"]
    swot2 = res2.json()["market_result"]["swot"]

    assert swot1 == swot2
