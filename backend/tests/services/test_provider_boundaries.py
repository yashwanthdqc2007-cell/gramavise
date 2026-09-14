import pytest
from app.providers.base import BaseDataProvider, ProviderResult
from app.providers.geo import GeoDataProvider
from app.providers.demographics import DemographicDataProvider
from app.providers.price import PriceDataProvider
from app.providers.odop import OdopDataProvider
from app.providers.market import MarketCompetitorProvider
from app.schemas.evidence import EvidenceType, EvidenceItem
from app.schemas.business import BusinessProfileBase, LocationSchema
from app.schemas.financial import FinancialAssumptionsInput
from app.services.financial.calculator import FinancialService
from app.services.recommendation.feasibility import evaluate_feasibility_status
from app.schemas.analysis import RecommendationStatus
from app.services.geo.market import MockMarketService


# Test 1: Provider returns normalized evidence in standard envelope
def test_provider_returns_normalized_evidence():
    geo_provider = GeoDataProvider(is_mock=True)
    res = geo_provider.fetch_evidence({"village": "Nagda", "district": "Ujjain", "state": "Madhya Pradesh"})
    assert isinstance(res, ProviderResult)
    assert res.success is True
    assert len(res.evidence_items) == 1
    assert isinstance(res.evidence_items[0], EvidenceItem)
    assert res.evidence_items[0].evidence_type == EvidenceType.MODELLED


# Test 2: Source metadata is preserved
def test_source_metadata_preserved():
    odop_provider = OdopDataProvider()
    res = odop_provider.fetch_evidence({"state": "Madhya Pradesh", "district": "Ujjain"})
    assert res.success is True
    assert len(res.evidence_items) == 1
    item = res.evidence_items[0]
    assert item.evidence_type == EvidenceType.OBSERVED
    assert item.source == "MoFPI PMFME ODOP Master Registry"
    assert item.source_url == "https://pmfme.mofpi.gov.in/"
    assert "Onion" in item.value


# Test 3: Geography level is preserved
def test_geography_level_preserved():
    demo_provider = DemographicDataProvider(is_mock=False)
    res = demo_provider.fetch_evidence({"village": "Nagda", "district": "Ujjain"})
    assert res.success is True
    assert res.raw_payload.get("geography_level") == "VILLAGE"
    assert res.evidence_items[0].evidence_type == EvidenceType.OBSERVED


# Test 4: Provider failure / timeout does not crash analysis and creates fallback
def test_provider_fallback_on_failure():
    class FailingProvider(BaseDataProvider):
        def is_available(self) -> bool:
            return False

        def fetch_evidence(self, query):
            # Simulate timeout or HTTP connection error
            return self.create_fallback_result("Commodity Mandi Price", "HTTP Connection Timeout (504 Gateway)")

    failing_provider = FailingProvider(provider_name="Test Mandi API", data_category="PRICING")
    res = failing_provider.fetch_evidence({"category": "Pulses"})
    
    assert res.success is False
    assert len(res.evidence_items) == 1
    assert res.evidence_items[0].evidence_type == EvidenceType.NEEDS_VERIFICATION
    assert res.evidence_items[0].verification_status == "NEEDS_VERIFICATION"
    assert "HTTP Connection Timeout" in res.errors[0]


# Test 5: Empty provider response becomes NEEDS_VERIFICATION
def test_empty_provider_query_handled():
    geo_provider = GeoDataProvider()
    res = geo_provider.fetch_evidence({})
    assert res.success is False
    assert res.evidence_items[0].evidence_type == EvidenceType.NEEDS_VERIFICATION


# Test 6: Stale evidence tracking
def test_stale_evidence_tracking():
    price_provider = PriceDataProvider(is_mock=False, freshness_hours=12)
    res = price_provider.fetch_evidence({"category": "Wheat", "district": "Pune"})
    assert res.observed_at is not None
    assert res.expires_at is not None
    assert res.is_stale is False


# Test 7: No provider can modify financial recommendation
def test_no_provider_modifies_financial_engine():
    fin_service = FinancialService()
    mock_market = MockMarketService()

    # Viable financial setup
    assumptions = FinancialAssumptionsInput(
        startup_cost=20000.0,
        equipment_cost=80000.0,
        inventory_cost=20000.0,
        monthly_fixed_cost=5000.0,
        customers_per_day=30,
        avg_ticket_price=100.0,
        working_days_per_month=26,
        variable_cost_pct=30.0,
        interest_rate_pct=10.0,
        loan_tenure_months=36
    )
    financials = fin_service.calculate(
        own_capital=30000.0,
        desired_loan=90000.0,
        financials=assumptions
    )

    market_res = mock_market.get_market_indicators(
        query=type("Query", (), {
            "state": "Maharashtra", "district": "Pune", "village": "Baramati",
            "category": "Flour Milling", "latitude": 18.15, "longitude": 74.58, "radius_km": 5.0
        })()
    )

    verdict = evaluate_feasibility_status(financials, market_res)
    # The financial engine recommendation status is strictly PROCEED based on math
    assert verdict == RecommendationStatus.PROCEED


# Test 8: Mock provider remains deterministic across repeated calls
def test_mock_provider_determinism():
    market_provider = MarketCompetitorProvider(is_mock=True)
    res1 = market_provider.fetch_evidence({"category": "Tailoring", "village": "Nagda"})
    res2 = market_provider.fetch_evidence({"category": "Tailoring", "village": "Nagda"})
    assert res1.raw_payload == res2.raw_payload
    assert res1.evidence_items[0].value == res2.evidence_items[0].value


# Test 9: Unmapped ODOP returns NEEDS_VERIFICATION cleanly
def test_unmapped_odop_needs_verification():
    odop_provider = OdopDataProvider()
    res = odop_provider.fetch_evidence({"state": "Unmapped State", "district": "Unknown District"})
    assert res.success is True
    assert res.evidence_items[0].evidence_type == EvidenceType.NEEDS_VERIFICATION
