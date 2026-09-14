import pytest
from app.providers.odop import OdopDataProvider
from app.schemas.evidence import EvidenceType, EvidenceItem
from app.schemas.business import BusinessProfileBase, LocationSchema
from app.schemas.financial import FinancialAssumptionsInput
from app.services.financial.calculator import FinancialService
from app.services.schemes.matcher import SchemeService
from app.rules.scheme_rules import SchemeRules
from app.services.evidence.collector import EvidenceCollector


@pytest.fixture
def odop_provider():
    return OdopDataProvider()


@pytest.fixture
def financial_service():
    return FinancialService()


@pytest.fixture
def scheme_service():
    return SchemeService()


@pytest.fixture
def evidence_collector():
    return EvidenceCollector()


# Test 1: Known state + district returns correct normalized ODOP record
def test_known_state_district_odop_record(odop_provider):
    rec = odop_provider.get_odop_record(state="Madhya Pradesh", district="Ujjain")
    assert rec is not None
    assert "Onion" in rec["odop_product"]
    assert rec["category"] == "FRUITS_VEGETABLES"


# Test 2: ODOP record has official source metadata
def test_odop_official_source_metadata(odop_provider):
    res = odop_provider.fetch_evidence({"state": "Madhya Pradesh", "district": "Ujjain"})
    assert res.success is True
    assert len(res.evidence_items) == 1
    item = res.evidence_items[0]
    assert item.source == "MoFPI PMFME ODOP Master Registry"
    assert item.source_url == "https://pmfme.mofpi.gov.in/"
    assert "Ministry of Food Processing Industries" in item.source_title


# Test 3: ODOP evidence is OBSERVED
def test_odop_evidence_type_is_observed(odop_provider):
    res = odop_provider.fetch_evidence({"state": "Maharashtra", "district": "Pune"})
    assert res.evidence_items[0].evidence_type == EvidenceType.OBSERVED
    assert res.evidence_items[0].verification_status == "OFFICIALLY_NOTIFIED"


# Test 4: ODOP evidence confidence is HIGH (1.0)
def test_odop_evidence_confidence_is_high(odop_provider):
    res = odop_provider.fetch_evidence({"state": "Uttar Pradesh", "district": "Varanasi"})
    assert res.evidence_items[0].confidence == 1.0


# Test 5 (Case A): ODOP-aligned NEW food-processing unit -> Supported under ODOP
def test_aligned_new_business_odop_pmfme(scheme_service, financial_service):
    profile = BusinessProfileBase(
        business_name="Ujjain Garlic & Onion Processing Unit",
        category="Small Agro / Food Processing",
        description="Dehydrated onion flakes and garlic paste manufacturing",
        location=LocationSchema(
            state="Madhya Pradesh",
            district="Ujjain",  # ODOP is Onion & Garlic Processing
            village="Nagda"
        ),
        experience_years=3,
        own_capital=40000.0,
        desired_loan=160000.0,
        is_new_business=True
    )
    assumptions = FinancialAssumptionsInput(
        startup_cost=20000.0,
        equipment_cost=140000.0,
        inventory_cost=40000.0,
        monthly_fixed_cost=6000.0,
        customers_per_day=25,
        avg_ticket_price=80.0,
        working_days_per_month=26,
        variable_cost_pct=30.0,
        interest_rate_pct=10.0,
        loan_tenure_months=36
    )
    financials = financial_service.calculate(
        own_capital=profile.own_capital,
        desired_loan=profile.desired_loan,
        financials=assumptions
    )
    result = scheme_service.match_schemes(profile, financials)

    pmfme_matches = [s for s in result.schemes if s.scheme_code == "PMFME"]
    assert len(pmfme_matches) == 1
    pmfme = pmfme_matches[0]
    assert pmfme.eligibility_status == "PARTIALLY_ELIGIBLE"
    # Reasons should clearly articulate ODOP alignment for new unit
    assert any("District ODOP alignment observed" in r for r in pmfme.reasons)
    assert any("New enterprise aligns with notified ODOP produce" in r for r in pmfme.reasons)


# Test 6 (Case B): NON-ODOP EXISTING food-processing unit -> Supported for upgradation
def test_non_aligned_existing_food_business_pmfme(scheme_service, financial_service):
    profile = BusinessProfileBase(
        business_name="Varanasi Traditional Dairy Sweets",
        category="Dairy Farming & Milk Chilling",
        description="Fresh paneer and milk sweets production",
        location=LocationSchema(
            state="Uttar Pradesh",
            district="Varanasi",  # ODOP is Chilli & Red Pepper
            village="Shivpur"
        ),
        experience_years=5,
        own_capital=50000.0,
        desired_loan=200000.0,
        is_new_business=False  # Existing unit
    )
    assumptions = FinancialAssumptionsInput(
        startup_cost=30000.0,
        equipment_cost=170000.0,
        inventory_cost=50000.0,
        monthly_fixed_cost=8000.0,
        customers_per_day=30,
        avg_ticket_price=100.0,
        working_days_per_month=26,
        variable_cost_pct=35.0,
        interest_rate_pct=10.5,
        loan_tenure_months=36
    )
    financials = financial_service.calculate(
        own_capital=profile.own_capital,
        desired_loan=profile.desired_loan,
        financials=assumptions
    )
    result = scheme_service.match_schemes(profile, financials)

    pmfme_matches = [s for s in result.schemes if s.scheme_code == "PMFME"]
    assert len(pmfme_matches) == 1
    pmfme = pmfme_matches[0]
    assert pmfme.eligibility_status == "PARTIALLY_ELIGIBLE"
    # Reasons should clearly articulate support for existing unit producing other products
    assert any("Existing individual micro-units producing other products may also be supported" in r for r in pmfme.reasons)


# Test 7 (Case C): NON-ODOP NEW food-processing unit -> Not supported under PMFME
def test_non_aligned_new_food_business_pmfme(scheme_service, financial_service):
    profile = BusinessProfileBase(
        business_name="Varanasi New Dairy Plant",
        category="Dairy Farming & Milk Chilling",
        description="Proposed new dairy processing facility",
        location=LocationSchema(
            state="Uttar Pradesh",
            district="Varanasi",  # ODOP is Chilli & Red Pepper
            village="Shivpur"
        ),
        experience_years=0,
        own_capital=50000.0,
        desired_loan=200000.0,
        is_new_business=True  # New unit
    )
    assumptions = FinancialAssumptionsInput(
        startup_cost=30000.0,
        equipment_cost=170000.0,
        inventory_cost=50000.0,
        monthly_fixed_cost=8000.0,
        customers_per_day=30,
        avg_ticket_price=100.0,
        working_days_per_month=26,
        variable_cost_pct=35.0,
        interest_rate_pct=10.5,
        loan_tenure_months=36
    )
    financials = financial_service.calculate(
        own_capital=profile.own_capital,
        desired_loan=profile.desired_loan,
        financials=assumptions
    )
    result = scheme_service.match_schemes(profile, financials)

    # New non-ODOP units are not supported under PMFME
    pmfme_matches = [s for s in result.schemes if s.scheme_code == "PMFME"]
    assert len(pmfme_matches) == 0


# Test 8: Missing / unmapped district produces NEEDS_VERIFICATION
def test_unmapped_district_needs_verification(odop_provider):
    res = odop_provider.fetch_evidence({"state": "Goa", "district": "Unknown District"})
    assert res.success is True
    assert res.evidence_items[0].evidence_type == EvidenceType.NEEDS_VERIFICATION
    assert res.evidence_items[0].verification_status == "NEEDS_VERIFICATION"


# Test 9: Ambiguous district normalization produces safe fallback
def test_ambiguous_normalization_fallback(odop_provider):
    res = odop_provider.fetch_evidence({"state": "123", "district": "!!!"})
    assert res.success is False
    assert res.evidence_items[0].evidence_type == EvidenceType.NEEDS_VERIFICATION


# Test 9: Provider failure does not crash analysis and preserves financial recommendation
def test_odop_provider_failure_resilience():
    # Pass empty or invalid queries to evidence collector
    collector = EvidenceCollector(odop_provider=None)
    items = collector.collect({
        "monthly_net_profit": 25000.0,
        "break_even_units_daily": 10,
        "competitor_count": 1,
        "customers_per_day": 30,
        "state": None,
        "district": None
    })
    # Should complete without error
    assert len(items) >= 4


# Test 10: API response remains compatible and includes ODOP in evidence
def test_odop_in_evidence_collector(evidence_collector):
    items = evidence_collector.collect({
        "monthly_net_profit": 20000.0,
        "break_even_units_daily": 8,
        "competitor_count": 2,
        "customers_per_day": 20,
        "state": "Madhya Pradesh",
        "district": "Ujjain"
    })
    odop_items = [i for i in items if i.indicator == "District ODOP Product"]
    assert len(odop_items) == 1
    assert odop_items[0].evidence_type == EvidenceType.OBSERVED
    assert "Onion & Garlic" in odop_items[0].value


# Test 11: Repeated lookup is deterministic
def test_odop_deterministic_lookup(odop_provider):
    res1 = odop_provider.fetch_evidence({"state": "Maharashtra", "district": "Pune"})
    res2 = odop_provider.fetch_evidence({"state": "Maharashtra", "district": "Pune"})
    assert res1.evidence_items[0].model_dump() == res2.evidence_items[0].model_dump()


# Test 12: No external network is required (fully offline)
def test_offline_odop_availability(odop_provider):
    assert odop_provider.is_available() is True
    rec = odop_provider.get_odop_record("Bihar", "Muzaffarpur")
    assert rec is not None
    assert "Litchi" in rec["odop_product"]
