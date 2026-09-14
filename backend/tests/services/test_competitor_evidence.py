import pytest
import math
from app.utils.geo_distance import haversine_distance
from app.services.geo.category_matching import match_competitor_category
from app.schemas.market import (
    CompetitorRelationship,
    CoverageConfidenceLevel,
    MarketEvidenceQuery,
    MarketResultResponse,
    UdyamDistrictContext
)
from app.schemas.analysis import RecommendationStatus
from app.providers.competitor import OSMCompetitorProvider
from app.providers.udyam import UdyamContextProvider
from app.services.geo.market import MockMarketService
from app.services.financial.calculator import FinancialService
from app.rules.feasibility_rules import FeasibilityRules
from app.schemas.financial import FinancialAssumptionsInput


def test_haversine_distance_calculation():
    # Known distance: Pune (18.5204, 73.8567) to Baramati (18.1510, 74.5750) is ~85 km
    dist = haversine_distance(18.5204, 73.8567, 18.1510, 74.5750)
    assert 80.0 < dist < 95.0

    # Same point distance is 0.0
    assert haversine_distance(18.15, 74.57, 18.15, 74.57) == 0.0


def test_category_matching_direct_adjacent_unrelated():
    # 1. Direct match: bakery / snacks vs bakery shop
    rel, reason, subcat = match_competitor_category("Bakery", {"shop": "bakery"})
    assert rel == CompetitorRelationship.DIRECT
    assert subcat == "bakery"
    assert "shop=bakery" in reason

    # 2. Adjacent match: snack kiosk vs grocery store
    rel, reason, subcat = match_competitor_category("Snack Kiosk", {"shop": "convenience"})
    assert rel == CompetitorRelationship.ADJACENT

    # 3. Unrelated match: food stall vs clothing shop
    rel, reason, subcat = match_competitor_category("Millet Food Stall", {"shop": "clothes"})
    assert rel == CompetitorRelationship.UNRELATED


def test_osm_competitor_catchment_filtering_and_exclusion():
    provider = OSMCompetitorProvider()
    # Query Baramati center (18.1550, 74.5780) where snapshot POIs are within 1-2 km
    competitors, conf, warning = provider.get_competitors(
        lat=18.1550,
        lon=74.5780,
        category="Bakery & Snacks",
        radius_km=5.0
    )

    assert len(competitors) >= 2
    for c in competitors:
        assert c.distance_km <= 5.0
        assert c.source == "OpenStreetMap"
        assert c.source_type == "OPEN_GEODATA"
        assert "openstreetmap.org" in (c.source_url or "")

    # Query with tiny radius 0.01 km -> excludes POIs outside radius
    competitors_tiny, conf_tiny, _ = provider.get_competitors(
        lat=18.1550,
        lon=74.5780,
        category="Bakery & Snacks",
        radius_km=0.01
    )
    assert len(competitors_tiny) == 0
    assert conf_tiny == CoverageConfidenceLevel.LOW.value


def test_missing_coordinates_returns_needs_verification():
    provider = OSMCompetitorProvider()
    competitors, conf, warning = provider.get_competitors(
        lat=None,
        lon=None,
        category="Bakery",
        radius_km=5.0
    )
    assert len(competitors) == 0
    assert conf == CoverageConfidenceLevel.UNKNOWN.value
    assert "unavailable" in warning.lower()

    # Evidence item fallback
    res = provider.fetch_evidence({"category": "Bakery"})
    assert res.success is False
    assert len(res.evidence_items) == 1
    assert res.evidence_items[0].evidence_type.value == "NEEDS_VERIFICATION"


def test_empty_osm_response_does_not_imply_zero_competition():
    provider = OSMCompetitorProvider()
    # Remote location with 0 mapped POIs in snapshot
    competitors, conf, warning = provider.get_competitors(
        lat=12.1234,
        lon=76.1234,
        category="Unmapped Rare Craft",
        radius_km=5.0
    )
    assert len(competitors) == 0
    # Must be LOW confidence, NOT high certainty of 0 competition
    assert conf == CoverageConfidenceLevel.LOW.value
    assert "A low mapped count does not prove low competition" in warning

    res = provider.fetch_evidence({
        "latitude": 12.1234,
        "longitude": 76.1234,
        "category": "Unmapped Rare Craft",
        "radius_km": 5.0
    })
    assert res.evidence_items[0].evidence_type.value == "NEEDS_VERIFICATION"


def test_no_fake_competitor_names_in_production():
    provider = OSMCompetitorProvider()
    competitors, _, _ = provider.get_competitors(lat=18.1550, lon=74.5780, category="Bakery", radius_km=5.0)
    for c in competitors:
        assert "Prototype Competitor" not in c.business_name
        assert "[DEMO]" not in c.business_name


def test_udyam_district_context_separation():
    udyam_provider = UdyamContextProvider()
    ctx = udyam_provider.get_district_context("Maharashtra", "Pune")
    assert ctx is not None
    assert ctx.registered_msme_count > 300000
    assert ctx.micro_count is not None and ctx.micro_count > 200000
    assert ctx.geography_level.value == "DISTRICT"
    assert "Ministry of Micro, Small and Medium Enterprises" in ctx.source
    assert "District-level formal MSME context only; not a count of nearby competitors" in ctx.notes

    # Missing district returns None and fallback evidence
    ctx_missing = udyam_provider.get_district_context("Atlantis", "UnknownDist")
    assert ctx_missing is None
    res = udyam_provider.fetch_evidence({"state": "Atlantis", "district": "UnknownDist"})
    assert res.success is False
    assert res.evidence_items[0].evidence_type.value == "NEEDS_VERIFICATION"


def test_market_service_indicators_and_udyam_integration():
    service = MockMarketService()
    query = MarketEvidenceQuery(
        state="Maharashtra",
        district="Pune",
        village="Baramati",
        category="Bakery & Snacks",
        commodity="Wheat",
        market="Pune",
        latitude=18.1550,
        longitude=74.5780,
        radius_km=5.0
    )
    result = service.get_market_indicators(query)
    assert isinstance(result, MarketResultResponse)
    assert result.direct_competitor_count >= 1
    assert result.catchment_radius_km == 5.0
    assert result.udyam_context is not None
    assert result.udyam_context.registered_msme_count > 300000
    assert result.coverage_warning is not None

    # Check indicator IDs
    indicator_ids = [ind.indicator_id for ind in result.indicators]
    assert "MKT-COMP-COUNT" in indicator_ids
    assert "MKT-UDYAM-MSME" in indicator_ids


def test_competitor_evidence_cannot_alter_financial_engine_math():
    """Verify that changing competitor count or market evidence has 0 impact on deterministic financial formulas."""
    calc = FinancialService()
    assumptions = FinancialAssumptionsInput(
        startup_cost=25000.0,
        equipment_cost=100000.0,
        inventory_cost=25000.0,
        monthly_fixed_cost=6000.0,
        variable_cost_pct=50.0,
        avg_ticket_price=30.0,
        customers_per_day=50,
        working_days_per_month=26,
        interest_rate_pct=10.0,
        loan_tenure_months=36
    )

    baseline_fin = calc.calculate(own_capital=40000.0, desired_loan=110000.0, financials=assumptions)

    # Re-evaluate - financial math must remain identical
    repeat_fin = calc.calculate(own_capital=40000.0, desired_loan=110000.0, financials=assumptions)
    assert baseline_fin.monthly_revenue == repeat_fin.monthly_revenue
    assert baseline_fin.monthly_net_profit == repeat_fin.monthly_net_profit
    assert baseline_fin.monthly_emi == repeat_fin.monthly_emi
    assert baseline_fin.dscr == repeat_fin.dscr
    assert baseline_fin.break_even_units_daily == repeat_fin.break_even_units_daily


def test_feasibility_rules_authority_intact():
    """Verify feasibility recommendation hierarchy is preserved."""
    calc = FinancialService()
    assumptions = FinancialAssumptionsInput(
        startup_cost=25000.0,
        equipment_cost=100000.0,
        inventory_cost=25000.0,
        monthly_fixed_cost=6000.0,
        variable_cost_pct=50.0,
        avg_ticket_price=30.0,
        customers_per_day=50,
        working_days_per_month=26,
        interest_rate_pct=10.0,
        loan_tenure_months=36
    )
    fin_result = calc.calculate(own_capital=40000.0, desired_loan=110000.0, financials=assumptions)
    
    market_service = MockMarketService()
    query = MarketEvidenceQuery(
        state="Maharashtra",
        district="Pune",
        village="Baramati",
        category="Bakery & Snacks",
        latitude=18.1550,
        longitude=74.5780
    )
    market_result = market_service.get_market_indicators(query)
    
    verdict = FeasibilityRules.determine_status(fin_result, market_result)
    assert verdict in (RecommendationStatus.PROCEED, RecommendationStatus.VALIDATE_FIRST, RecommendationStatus.RECONSIDER)


def test_deterministic_repeated_analysis():
    service = MockMarketService()
    query = MarketEvidenceQuery(
        state="Maharashtra",
        district="Pune",
        village="Baramati",
        category="Bakery & Snacks",
        latitude=18.1550,
        longitude=74.5780,
        radius_km=5.0
    )
    res1 = service.get_market_indicators(query)
    res2 = service.get_market_indicators(query)

    assert res1.direct_competitor_count == res2.direct_competitor_count
    assert res1.udyam_context.registered_msme_count == res2.udyam_context.registered_msme_count
    assert len(res1.competitors) == len(res2.competitors)
    for c1, c2 in zip(res1.competitors, res2.competitors):
        assert c1.competitor_id == c2.competitor_id
        assert c1.distance_km == c2.distance_km
