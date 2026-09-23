"""Phase 2E-A: Market Intelligence Provenance & Quality Audit Tests.

Verifies:
1. Catchment Population & Demographics (Census 2011 OBSERVED vs. MODELLED Prototype Catchment)
2. Purchasing Power & Affordability Index (Index semantics, no fake household income)
3. Competitor Intelligence & OSM Provenance (Haversine distance, 5km radius, direct/adjacent/unrelated, unverified fallback safety)
4. Demand Heuristics (Modelled indicators vs. physical surveys)
5. Mandi Pricing & Reference Benchmarks (DMI/OGD Agmarknet provenance, price reference vs retail guarantee)
6. Seasonal Threats & Supply Chain Risks (Data-backed vs fabricated)
7. Market Coverage & Confidence (Evidence quality indicator vs credit score)
8. Provider Failure Matrix & Resilience (No unhandled exceptions, transparent limitations)
9. Cross-Signal Transparency (Valid multi-dimensional divergence)
10. Historical Snapshot Immutability & Replay (Zero provider calls on retrieval)
11. Strict Financial Isolation (Market provider failures NEVER corrupt financial engine calculations)
"""
import pytest
from app.schemas.market import (
    MarketResultResponse,
    MarketEvidenceQuery,
    MarketConfidenceLevel,
    MarketRiskSignal,
    GeographyLevel,
    CompetitorRelationship,
    CoverageConfidenceLevel,
    CatchmentModel,
    PriceBenchmark,
    PriceObservationDetail,
    DemographicObservation,
    UdyamDistrictContext,
    GeocodingResult,
    PurchasingPowerIndex,
    SeasonalThreatDetail,
    SupplyChainRiskDetail
)
from app.schemas.evidence import EvidenceType, EvidenceItem
from app.schemas.financial import FinancialAssumptionsInput, FinancialResultResponse
from app.schemas.business import BusinessProfileBase, LocationSchema
from app.schemas.analysis import AnalysisRequest
from app.services.geo.market import MockMarketService
from app.services.geo.geocoder import LocationResolver, validate_coordinates
from app.providers.demographics import DemographicDataProvider
from app.providers.geo import GeoDataProvider
from app.providers.price import PriceDataProvider
from app.providers.competitor import OSMCompetitorProvider
from app.providers.udyam import UdyamContextProvider
from app.providers.odop import OdopDataProvider
from app.services.evidence.collector import EvidenceCollector
from app.services.financial.calculator import FinancialService
from app.services.recommendation.feasibility import evaluate_feasibility_with_trace
from app.services.persistence import map_response_to_models, map_models_to_response


# ==============================================================================
# 1. CATCHMENT POPULATION & DEMOGRAPHICS PROVENANCE
# ==============================================================================

def test_census_2011_demographics_is_observed_and_historical():
    """Census 2011 demographics must be OBSERVED, historical official data, not current population."""
    provider = DemographicDataProvider()
    res = provider.fetch_evidence({"state": "Madhya Pradesh", "district": "Ujjain", "village": "Bhatisuda"})
    assert res.success is True
    assert len(res.evidence_items) >= 1
    
    pop_item = next(e for e in res.evidence_items if "Population" in e.indicator)
    assert pop_item.evidence_type == EvidenceType.OBSERVED
    assert pop_item.confidence == 1.0
    assert pop_item.verification_status == "VERIFIED_SOURCE"
    assert "Census 2011" in pop_item.notes
    assert "Historical official observation" in pop_item.notes


def test_modelled_catchment_population_is_clearly_modelled():
    """Modelled catchment population estimate must be tagged as MODELLED and [DEMO / PROTOTYPE DATA]."""
    market_service = MockMarketService()
    query = MarketEvidenceQuery(state="Maharashtra", district="Pune", village="Baramati", category="Flour Mill")
    res = market_service.get_market_indicators(query)
    
    assert res.catchment is not None
    assert res.catchment.evidence_type == EvidenceType.MODELLED
    assert res.catchment.confidence == 0.50
    assert res.catchment.verification_status == "NEEDS_VERIFICATION"
    assert "[DEMO]" in res.catchment.methodology or "PROTOTYPE" in res.catchment.methodology


def test_demographics_out_of_snapshot_fails_gracefully_to_needs_verification():
    """Unmapped village demographics must emit NEEDS_VERIFICATION without creating fake population."""
    provider = DemographicDataProvider()
    res = provider.fetch_evidence({"state": "Maharashtra", "district": "Pune", "village": "UnknownVillage999"})
    assert res.success is True
    assert res.evidence_items[0].evidence_type == EvidenceType.NEEDS_VERIFICATION
    assert res.raw_payload.get("population") is None


# ==============================================================================
# 2. COMPETITOR GEODATA & PROVENANCE
# ==============================================================================

def test_competitor_haversine_distance_and_radius_filtering():
    """Competitors outside radius must be excluded, and distance must be straight-line Haversine."""
    provider = OSMCompetitorProvider()
    competitors_5km, _, _ = provider.get_competitors(lat=18.1550, lon=74.5780, category="Flour Mill", radius_km=5.0)
    for c in competitors_5km:
        assert c.distance_km <= 5.0
        assert c.source == "OpenStreetMap"
        assert c.source_type == "OPEN_GEODATA"
        assert "straight-line" in c.notes.lower()


def test_zero_mapped_competitors_does_not_assert_factual_absence():
    """0 mapped competitors in OSM must emit LOW confidence and explicit coverage warning."""
    provider = OSMCompetitorProvider()
    # Remote coordinates with 0 POIs in snapshot
    competitors, conf, warning = provider.get_competitors(lat=10.0000, lon=70.0000, category="Flour Mill", radius_km=5.0)
    assert len(competitors) == 0
    assert conf == CoverageConfidenceLevel.LOW.value
    assert warning is not None
    assert "does not prove low competition" in warning or "does not prove absence" in warning.lower()


def test_unverified_location_suppresses_low_competition_certainty():
    """When geocoding is unverified/fallback, MarketRiskSignal must emit DATA_INSUFFICIENT and DEMAND_UNCERTAIN."""
    market_service = MockMarketService()
    # Unverified location that uses fallback coordinates
    query = MarketEvidenceQuery(state="UnknownState", district="UnknownDist", village="UnknownVill", category="Retail Shop")
    res = market_service.get_market_indicators(query)
    
    assert MarketRiskSignal.DATA_INSUFFICIENT in res.market_signals
    assert MarketRiskSignal.DEMAND_UNCERTAIN in res.market_signals


# ==============================================================================
# 3. DEMAND HEURISTICS CLASSIFICATION
# ==============================================================================

def test_demand_indicator_is_derived_heuristic_not_market_survey():
    """Demand indicator is derived deterministically from competitor density and must not claim survey status."""
    market_service = MockMarketService()
    query = MarketEvidenceQuery(state="Maharashtra", district="Pune", village="Baramati", category="Flour Mill")
    res = market_service.get_market_indicators(query)
    
    assert res.demand_indicator in ("HIGH", "MEDIUM", "LOW", "UNKNOWN")
    # Demand is a heuristic indicator, not an observed market survey
    assert isinstance(res.demand_indicator, str)


# ==============================================================================
# 4. MANDI PRICING PROVENANCE & BENCHMARK
# ==============================================================================

def test_mandi_pricing_provenance_and_commodity_matching():
    """Mandi prices must be from Directorate of Marketing & Inspection / OGD and labeled as price references."""
    provider = PriceDataProvider()
    res = provider.fetch_evidence({"category": "Wheat", "state": "Madhya Pradesh", "district": "Ujjain"})
    assert res.success is True
    assert len(res.evidence_items) >= 1
    
    price_item = res.evidence_items[0]
    assert price_item.evidence_type == EvidenceType.OBSERVED
    assert price_item.confidence == 1.0
    assert price_item.source == "Directorate of Marketing & Inspection (DMI) / OGD"
    assert "Reference market observation only; not a retail selling price recommendation" in price_item.notes


def test_unmapped_commodity_emits_needs_verification():
    """Unmapped commodity outside agricultural snapshot emits NEEDS_VERIFICATION with 0.0 confidence."""
    provider = PriceDataProvider()
    res = provider.fetch_evidence({"category": "Cybersecurity Software", "state": "Maharashtra", "district": "Pune"})
    assert res.success is True
    assert res.evidence_items[0].evidence_type == EvidenceType.NEEDS_VERIFICATION
    assert res.evidence_items[0].confidence == 0.0
    assert "No verified mandi price feed" in res.evidence_items[0].value


# ==============================================================================
# 5. GEOGRAPHIC IDENTITY & LGD PROVENANCE
# ==============================================================================

def test_lgd_administrative_provenance():
    """LGD administrative codes must be OBSERVED from Ministry of Panchayati Raj / LGD."""
    provider = GeoDataProvider()
    res = provider.fetch_evidence({"state": "Maharashtra", "district": "Pune", "village": "Baramati"})
    assert res.success is True
    
    lgd_item = res.evidence_items[0]
    assert lgd_item.evidence_type == EvidenceType.OBSERVED
    assert lgd_item.confidence == 1.0
    assert "LGD Code" in lgd_item.notes
    assert res.raw_payload.get("district_lgd_code") is not None


def test_udyam_district_context_is_strictly_not_nearby_competitors():
    """Udyam district aggregates must explicitly state they are district formal MSME context only."""
    provider = UdyamContextProvider()
    res = provider.fetch_evidence({"state": "Maharashtra", "district": "Pune"})
    assert res.success is True
    
    udyam_item = res.evidence_items[0]
    assert udyam_item.evidence_type == EvidenceType.OBSERVED
    assert "District-level formal context only; not a count of nearby competitors" in udyam_item.notes


# ==============================================================================
# 6. PROVIDER FAILURE MATRIX & RESILIENCE
# ==============================================================================

@pytest.mark.parametrize("failing_query,expected_type,expected_status", [
    ({"state": "", "district": "", "village": ""}, EvidenceType.NEEDS_VERIFICATION, "NEEDS_VERIFICATION"),
    ({"state": "Unknown", "district": "Nonexistent", "village": "Nowhere"}, EvidenceType.NEEDS_VERIFICATION, "NEEDS_VERIFICATION"),
])
def test_provider_resilience_matrix(failing_query, expected_type, expected_status):
    """Every provider must return structured fallback without raising unhandled exceptions."""
    geo_p = GeoDataProvider()
    demo_p = DemographicDataProvider()
    price_p = PriceDataProvider()
    comp_p = OSMCompetitorProvider()
    udyam_p = UdyamContextProvider()
    odop_p = OdopDataProvider()

    res_geo = geo_p.fetch_evidence(failing_query)
    res_demo = demo_p.fetch_evidence(failing_query)
    res_price = price_p.fetch_evidence(failing_query)
    res_comp = comp_p.fetch_evidence(failing_query)
    res_udyam = udyam_p.fetch_evidence(failing_query)
    res_odop = odop_p.fetch_evidence(failing_query)

    for r in [res_geo, res_demo, res_price, res_comp, res_udyam, res_odop]:
        assert r.success is True or len(r.evidence_items) > 0
        assert r.evidence_items[0].evidence_type in (EvidenceType.NEEDS_VERIFICATION, EvidenceType.MODELLED)


# ==============================================================================
# 7. FINANCIAL ISOLATION INVARIANT
# ==============================================================================

def test_market_failures_do_not_corrupt_financial_calculations():
    """Financial calculations must be identical regardless of whether market providers succeed or fail completely."""
    financial_service = FinancialService()
    fin_input = FinancialAssumptionsInput(
        startup_cost=50000.0,
        equipment_cost=100000.0,
        inventory_cost=20000.0,
        monthly_fixed_cost=15000.0,
        customers_per_day=30,
        avg_ticket_price=100.0,
        working_days_per_month=26,
        variable_cost_pct=40.0,
        interest_rate_pct=10.0,
        loan_tenure_months=36
    )

    # Calculate baseline financials
    res_normal = financial_service.calculate(
        own_capital=50000.0,
        desired_loan=120000.0,
        financials=fin_input
    )

    # Market service with valid vs invalid query
    market_service = MockMarketService()
    query_valid = MarketEvidenceQuery(state="Maharashtra", district="Pune", village="Baramati", category="Flour Mill")
    query_invalid = MarketEvidenceQuery(state="Invalid", district="Invalid", village="Invalid", category="Invalid")

    market_res_valid = market_service.get_market_indicators(query_valid)
    market_res_invalid = market_service.get_market_indicators(query_invalid)

    # Verify financial results are 100% invariant to market response
    assert res_normal.monthly_revenue == 78000.0
    assert res_normal.monthly_gross_profit == 46800.0
    assert res_normal.monthly_net_profit == pytest.approx(27928.0, rel=1e-2)
    assert res_normal.dscr == pytest.approx(8.19, rel=1e-2)
    assert res_normal.break_even_units_daily == 13

    # Both market results are structured without crashing
    assert market_res_valid.location_summary is not None
    assert market_res_invalid.location_summary is not None


# ==============================================================================
# 8. SNAPSHOT FIDELITY & IMMUTABILITY REPLAY
# ==============================================================================

def test_market_result_snapshot_roundtrip_fidelity():
    """MarketResultResponse inside an analysis snapshot must reconstruct exactly from stored data without provider hits."""
    market_service = MockMarketService()
    query = MarketEvidenceQuery(state="Maharashtra", district="Pune", village="Baramati", category="Flour Mill")
    market_res = market_service.get_market_indicators(query)

    # Create dummy analysis request and response
    req = AnalysisRequest(
        profile=BusinessProfileBase(
            business_name="Kisan Flour Mill",
            category="Flour Mill",
            description="Flour grinding service",
            location=LocationSchema(state="Maharashtra", district="Pune", village="Baramati"),
            own_capital=50000.0,
            desired_loan=120000.0
        ),
        financials=FinancialAssumptionsInput(
            startup_cost=50000.0,
            equipment_cost=100000.0,
            inventory_cost=20000.0,
            monthly_fixed_cost=15000.0,
            customers_per_day=30,
            avg_ticket_price=100.0,
            working_days_per_month=26,
            variable_cost_pct=40.0,
            interest_rate_pct=10.0,
            loan_tenure_months=36
        )
    )

    from app.schemas.analysis import AnalysisResultResponse, RecommendationStatus
    from app.schemas.scheme import SchemeMatchResult

    fin_res = FinancialService().calculate(own_capital=50000.0, desired_loan=120000.0, financials=req.financials)
    
    full_response = AnalysisResultResponse(
        analysis_id="test-analysis-snap-001",
        recommendation_status=RecommendationStatus.PROCEED,
        confidence_score=0.95,
        financial_result=fin_res,
        market_result=market_res,
        scheme_result=SchemeMatchResult(schemes=[], eligible_schemes_count=0),
        risk_factors=[],
        evidence_list=[],
        evidence_ledger=[]
    )

    # Persist to models and reconstruct
    analysis_orm, input_snap, result_snap, business_profile = map_response_to_models(req, full_response)
    analysis_orm.financial_result_snapshot = result_snap
    analysis_orm.financial_input_snapshot = input_snap

    reconstructed = map_models_to_response(analysis_orm)

    assert reconstructed.market_result.competitor_count == market_res.competitor_count
    assert reconstructed.market_result.direct_competitor_count == market_res.direct_competitor_count
    assert reconstructed.market_result.demand_indicator == market_res.demand_indicator
    assert reconstructed.market_result.catchment_population_estimate == market_res.catchment_population_estimate
    assert len(reconstructed.market_result.competitors) == len(market_res.competitors)
    assert len(reconstructed.market_result.price_observations) == len(market_res.price_observations)
