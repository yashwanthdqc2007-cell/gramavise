import pytest
from app.schemas.market import (
    MarketEvidenceQuery,
    MarketConfidenceLevel,
    MarketRiskSignal,
    CompetitorDetail
)
from app.schemas.evidence import EvidenceType
from app.schemas.financial import FinancialAssumptionsInput
from app.services.financial.calculator import FinancialService
from app.services.geo.market import MockMarketService
from app.services.evidence.collector import EvidenceCollector
from app.rules.feasibility_rules import FeasibilityRules


@pytest.fixture
def mock_market_service():
    return MockMarketService()


@pytest.fixture
def evidence_collector():
    return EvidenceCollector()


@pytest.fixture
def financial_service():
    return FinancialService()


@pytest.fixture
def base_query():
    return MarketEvidenceQuery(
        state="Maharashtra",
        district="Pune",
        village="Baramati",
        category="Flour & Spice Milling (Atta Chakki)",
        commodity=None,
        market=None,
        latitude=18.15,
        longitude=74.58,
        radius_km=5.0
    )


# Test 1: Real OSM competitor provider returns OBSERVED
def test_osm_market_provider_returns_observed(mock_market_service, base_query):
    res = mock_market_service.get_market_indicators(base_query)
    assert res.catchment is not None
    assert res.catchment.evidence_type == EvidenceType.MODELLED
    for comp in res.competitors:
        assert comp.evidence_type == EvidenceType.OBSERVED
        assert comp.source == "OpenStreetMap"
        assert comp.source_type == "OPEN_GEODATA"


# Test 2: Real OSM competitor names from verified snapshot
def test_osm_competitor_names_are_real_pois(mock_market_service, base_query):
    res = mock_market_service.get_market_indicators(base_query)
    assert len(res.competitors) > 0
    for comp in res.competitors:
        assert "Prototype Competitor" not in comp.business_name
        assert "[DEMO]" not in comp.business_name
        assert comp.distance_km <= 5.0


# Test 3: Authoritative OpenStreetMap source URLs
def test_authoritative_osm_source_urls(mock_market_service, base_query):
    res = mock_market_service.get_market_indicators(base_query)
    for comp in res.competitors:
        assert comp.source_url is not None
        assert "https://www.openstreetmap.org/" in comp.source_url


# Test 4: User customers/day is tagged as ASSUMED in evidence
def test_user_customers_is_assumed(evidence_collector):
    items = evidence_collector.collect({
        "monthly_net_profit": 20000.0,
        "break_even_units_daily": 12,
        "competitor_count": 2,
        "customers_per_day": 35
    })
    footfall_items = [i for i in items if i.indicator == "Expected Daily Footfall"]
    assert len(footfall_items) == 1
    assert footfall_items[0].evidence_type == EvidenceType.ASSUMED
    assert "35 customers" in footfall_items[0].value


# Test 5: Derived revenue and break-even are CALCULATED
def test_derived_financials_are_calculated(evidence_collector):
    items = evidence_collector.collect({
        "monthly_net_profit": 18500.0,
        "break_even_units_daily": 9,
        "competitor_count": 1,
        "customers_per_day": 20
    })
    calc_items = [i for i in items if i.evidence_type == EvidenceType.CALCULATED]
    assert len(calc_items) >= 2
    indicators = [i.indicator for i in calc_items]
    assert "Monthly Operating Surplus" in indicators
    assert "Daily Break-Even Footfall" in indicators


# Test 6: Missing market/price data becomes NEEDS_VERIFICATION
def test_missing_price_data_becomes_needs_verification(mock_market_service, base_query):
    res = mock_market_service.get_market_indicators(base_query)
    assert res.price_benchmark is not None
    assert res.price_benchmark.evidence_type == EvidenceType.NEEDS_VERIFICATION
    assert res.price_benchmark.verification_status == "NEEDS_VERIFICATION"


# Test 7: Catchment model preserves provenance
def test_catchment_model_preserves_provenance(mock_market_service, base_query):
    res = mock_market_service.get_market_indicators(base_query)
    catchment = res.catchment
    assert catchment.radius_km == 5.0
    assert catchment.estimated_population == 4500
    assert catchment.evidence_type == EvidenceType.MODELLED
    assert catchment.verification_status == "NEEDS_VERIFICATION"


# Test 8: Confidence categories are deterministic
def test_confidence_categories_deterministic(mock_market_service, base_query):
    res = mock_market_service.get_market_indicators(base_query)
    assert res.confidence_level == MarketConfidenceLevel.MEDIUM


# Test 9: Market risk signals are deterministic
def test_market_risk_signals_deterministic(mock_market_service, base_query):
    res = mock_market_service.get_market_indicators(base_query)
    assert MarketRiskSignal.MODERATE_COMPETITION in res.market_signals
    assert MarketRiskSignal.PRICE_UNCERTAIN in res.market_signals


# Test 10: Market signals cannot override financial recommendation
def test_market_signals_cannot_override_financial_engine(financial_service, mock_market_service, base_query):
    # Unviable financial scenario (deficit profit / DSCR < 1.0)
    unviable_assumptions = FinancialAssumptionsInput(
        startup_cost=50000.0,
        equipment_cost=200000.0,
        inventory_cost=50000.0,
        monthly_fixed_cost=25000.0,  # High overhead
        customers_per_day=5,        # Low volume
        avg_ticket_price=20.0,
        variable_cost_pct=50.0,
        working_days_per_month=26,
        interest_rate_pct=12.0,
        loan_tenure_months=36
    )
    fin_result = financial_service.calculate(own_capital=50000.0, desired_loan=250000.0, financials=unviable_assumptions)
    market_result = mock_market_service.get_market_indicators(base_query)

    # Feasibility verdict MUST fail strictly based on financial deficit despite low/moderate competition
    verdict = FeasibilityRules.determine_status(fin_result, market_result)
    assert verdict.value == "RECONSIDER"
    assert fin_result.is_financially_viable is False


# Test 11: Repeatability of market outputs
def test_market_output_repeatability(mock_market_service, base_query):
    res1 = mock_market_service.get_market_indicators(base_query)
    res2 = mock_market_service.get_market_indicators(base_query)
    assert res1.competitor_count == res2.competitor_count
    assert res1.location_summary == res2.location_summary
    assert len(res1.competitors) == len(res2.competitors)


# Test 12: Pipeline schema compatibility
def test_analyze_pipeline_schema_compatibility(mock_market_service, base_query):
    res = mock_market_service.get_market_indicators(base_query)
    dict_res = res.model_dump()
    assert "competitor_count" in dict_res
    assert "competitors" in dict_res
    assert "indicators" in dict_res
    assert "catchment" in dict_res
    assert "geography" in dict_res
    assert "demographics" in dict_res
    assert "udyam_context" in dict_res
    assert "coverage_warning" in dict_res
