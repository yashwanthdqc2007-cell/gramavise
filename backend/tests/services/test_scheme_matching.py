import pytest
from app.schemas.business import BusinessProfileBase, LocationSchema
from app.schemas.financial import FinancialAssumptionsInput
from app.services.financial.calculator import FinancialService
from app.services.schemes.matcher import SchemeService
from app.rules.scheme_rules import SchemeRules
from app.services.evidence.collector import EvidenceCollector


@pytest.fixture
def base_location():
    return LocationSchema(
        state="Maharashtra",
        district="Pune",
        village="Baramati",
        latitude=18.15,
        longitude=74.58
    )


@pytest.fixture
def financial_service():
    return FinancialService()


@pytest.fixture
def scheme_service():
    return SchemeService()


@pytest.fixture
def evidence_collector():
    return EvidenceCollector()


# Test 1: PMEGP new business within supported project range
def test_pmegp_new_business_within_range(base_location, financial_service, scheme_service):
    profile = BusinessProfileBase(
        business_name="New Agri Tailoring Unit",
        category="Tailoring & Garments",
        location=base_location,
        experience_years=2,
        own_capital=50000.0,
        desired_loan=250000.0,
        is_new_business=True
    )
    assumptions = FinancialAssumptionsInput(
        startup_cost=50000.0,
        equipment_cost=200000.0,
        inventory_cost=50000.0,
        monthly_fixed_cost=10000.0,
        customers_per_day=15,
        avg_ticket_price=100.0,
        working_days_per_month=25,
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

    pmegp_matches = [s for s in result.schemes if s.scheme_code == "PMEGP"]
    assert len(pmegp_matches) == 1
    pmegp = pmegp_matches[0]
    assert pmegp.subsidy_eligible_amount > 0
    assert pmegp.source_url == "https://www.pmegp.msme.gov.in/"
    assert pmegp.evidence_type == "OBSERVED"
    assert len(pmegp.reasons) > 0


# Test 2: PMEGP existing business restriction
def test_pmegp_existing_business_disqualified(base_location, financial_service, scheme_service):
    profile = BusinessProfileBase(
        business_name="Existing Kirana",
        category="Kirana & General Store",
        location=base_location,
        experience_years=5,
        own_capital=50000.0,
        desired_loan=200000.0,
        is_new_business=False  # Existing unit
    )
    assumptions = FinancialAssumptionsInput(
        startup_cost=20000.0,
        equipment_cost=100000.0,
        inventory_cost=130000.0,
        monthly_fixed_cost=8000.0,
        customers_per_day=25,
        avg_ticket_price=80.0,
        working_days_per_month=26,
        variable_cost_pct=40.0,
        interest_rate_pct=11.0,
        loan_tenure_months=36
    )
    financials = financial_service.calculate(
        own_capital=profile.own_capital,
        desired_loan=profile.desired_loan,
        financials=assumptions
    )
    result = scheme_service.match_schemes(profile, financials)

    pmegp_matches = [s for s in result.schemes if s.scheme_code == "PMEGP"]
    assert len(pmegp_matches) == 0  # Not matched for existing unit


# Test 3: MUDRA Shishu (loans <= ₹50,000)
def test_mudra_shishu(base_location, financial_service, scheme_service):
    profile = BusinessProfileBase(
        business_name="Small Mobile Repair",
        category="Electronics Repair",
        location=base_location,
        experience_years=1,
        own_capital=10000.0,
        desired_loan=40000.0,
        is_new_business=True
    )
    assumptions = FinancialAssumptionsInput(
        startup_cost=10000.0,
        equipment_cost=30000.0,
        inventory_cost=10000.0,
        monthly_fixed_cost=4000.0,
        customers_per_day=10,
        avg_ticket_price=50.0,
        working_days_per_month=26,
        variable_cost_pct=20.0,
        interest_rate_pct=9.5,
        loan_tenure_months=24
    )
    financials = financial_service.calculate(
        own_capital=profile.own_capital,
        desired_loan=profile.desired_loan,
        financials=assumptions
    )
    result = scheme_service.match_schemes(profile, financials)

    mudra_matches = [s for s in result.schemes if "MUDRA" in s.scheme_code]
    assert len(mudra_matches) == 1
    assert mudra_matches[0].scheme_code == "MUDRA_SHISHU"
    assert mudra_matches[0].eligibility_status == "ELIGIBLE"
    assert mudra_matches[0].own_contribution_required == 0.0


# Test 4: MUDRA Kishore (loans ₹50,001 to ₹5,00,000)
def test_mudra_kishore(base_location, financial_service, scheme_service):
    profile = BusinessProfileBase(
        business_name="Hardware Store",
        category="Building Material & Hardware",
        location=base_location,
        experience_years=3,
        own_capital=60000.0,
        desired_loan=240000.0,
        is_new_business=True
    )
    assumptions = FinancialAssumptionsInput(
        startup_cost=30000.0,
        equipment_cost=120000.0,
        inventory_cost=150000.0,
        monthly_fixed_cost=12000.0,
        customers_per_day=20,
        avg_ticket_price=200.0,
        working_days_per_month=26,
        variable_cost_pct=45.0,
        interest_rate_pct=10.5,
        loan_tenure_months=36
    )
    financials = financial_service.calculate(
        own_capital=profile.own_capital,
        desired_loan=profile.desired_loan,
        financials=assumptions
    )
    result = scheme_service.match_schemes(profile, financials)

    mudra_matches = [s for s in result.schemes if "MUDRA" in s.scheme_code]
    assert len(mudra_matches) == 1
    assert mudra_matches[0].scheme_code == "MUDRA_KISHORE"
    assert mudra_matches[0].eligibility_status == "ELIGIBLE"


# Test 5: MUDRA Tarun (loans ₹5,00,001 to ₹10,00,000)
def test_mudra_tarun(base_location, financial_service, scheme_service):
    profile = BusinessProfileBase(
        business_name="Commercial Garment Unit",
        category="Tailoring & Garments",
        location=base_location,
        experience_years=4,
        own_capital=150000.0,
        desired_loan=600000.0,
        is_new_business=True
    )
    assumptions = FinancialAssumptionsInput(
        startup_cost=50000.0,
        equipment_cost=450000.0,
        inventory_cost=250000.0,
        monthly_fixed_cost=20000.0,
        customers_per_day=30,
        avg_ticket_price=300.0,
        working_days_per_month=26,
        variable_cost_pct=35.0,
        interest_rate_pct=11.0,
        loan_tenure_months=48
    )
    financials = financial_service.calculate(
        own_capital=profile.own_capital,
        desired_loan=profile.desired_loan,
        financials=assumptions
    )
    result = scheme_service.match_schemes(profile, financials)

    mudra_matches = [s for s in result.schemes if "MUDRA" in s.scheme_code]
    assert len(mudra_matches) == 1
    assert mudra_matches[0].scheme_code == "MUDRA_TARUN"
    assert mudra_matches[0].eligibility_status == "ELIGIBLE"


# Test 6: MUDRA Tarun Plus without previous Tarun repayment -> must NOT claim eligibility
def test_mudra_tarun_plus_unverified():
    matched, tier_code, tier_name, status, subsidy, margin, reasons, verify = SchemeRules.evaluate_mudra(
        loan_amount=1500000.0,
        has_prior_tarun_repayment=False
    )
    assert matched is True
    assert tier_code == "MUDRA_TARUN_PLUS"
    assert status == "PARTIALLY_ELIGIBLE"
    assert any("prior successful repayment" in v for v in verify)


# Test 7: PMFME food-processing profile (existing micro-unit upgradation)
def test_pmfme_food_processing_eligible(base_location, financial_service, scheme_service):
    profile = BusinessProfileBase(
        business_name="Desi Atta Chakki & Spice Milling",
        category="Flour & Spice Milling (Atta Chakki)",
        description="Milling of wheat and organic spices",
        location=base_location,
        experience_years=3,
        own_capital=40000.0,
        desired_loan=160000.0,
        is_new_business=False  # Existing micro-unit eligible for upgradation
    )
    assumptions = FinancialAssumptionsInput(
        startup_cost=20000.0,
        equipment_cost=140000.0,
        inventory_cost=40000.0,
        monthly_fixed_cost=6000.0,
        customers_per_day=30,
        avg_ticket_price=60.0,
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
    assert pmfme.subsidy_eligible_amount == 70000.0  # 35% of 200,000 capex
    assert pmfme.source_url == "https://pmfme.mofpi.gov.in/"
    assert pmfme.eligibility_status == "PARTIALLY_ELIGIBLE"
    assert len(pmfme.conditions_to_verify) > 0


# Test 8: PMFME non-food business disqualified
def test_pmfme_non_food_disqualified(base_location, financial_service, scheme_service):
    profile = BusinessProfileBase(
        business_name="Auto Repair Garage",
        category="Automobile Servicing",
        description="Two-wheeler service center",
        location=base_location,
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
        customers_per_day=10,
        avg_ticket_price=300.0,
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
    assert len(pmfme_matches) == 0


# Test 9: Missing eligibility information -> verification required in evidence
def test_unverified_conditions_in_evidence(evidence_collector):
    from app.schemas.scheme import MatchedSchemeDetail
    scheme = MatchedSchemeDetail(
        scheme_code="PMEGP",
        scheme_name="PMEGP",
        subsidy_eligible_amount=50000.0,
        own_contribution_required=10000.0,
        max_bank_loan=100000.0,
        eligibility_status="PARTIALLY_ELIGIBLE",
        reasons=["Meets Greenfield criteria."],
        conditions_to_verify=["Applicant social category certificate required."],
        source_url="https://www.pmegp.msme.gov.in/",
        source_title="KVIC Portal",
        evidence_type="OBSERVED"
    )
    items = evidence_collector.collect({
        "monthly_net_profit": 15000.0,
        "break_even_units_daily": 10,
        "competitor_count": 2,
        "customers_per_day": 25,
        "schemes": [scheme]
    })
    unverified = [i for i in items if i.evidence_type.value == "NEEDS_VERIFICATION"]
    assert len(unverified) >= 1
    assert any("Applicant social category certificate" in i.value for i in unverified)


# Test 10: Scheme data contains authoritative source URLs
def test_scheme_authoritative_urls(scheme_service):
    schemes = scheme_service.get_schemes()
    assert len(schemes) >= 3
    for s in schemes:
        assert "source_url" in s and s["source_url"].startswith("https://")
        assert "source_title" in s
        assert s.get("evidence_type") == "OBSERVED"


# Test 11: Scheme matching is deterministic
def test_scheme_matching_deterministic(base_location, financial_service, scheme_service):
    profile = BusinessProfileBase(
        business_name="Atta Chakki",
        category="Flour & Spice Milling (Atta Chakki)",
        location=base_location,
        experience_years=2,
        own_capital=30000.0,
        desired_loan=120000.0,
        is_new_business=True
    )
    assumptions = FinancialAssumptionsInput(
        startup_cost=15000.0,
        equipment_cost=100000.0,
        inventory_cost=35000.0,
        monthly_fixed_cost=6000.0,
        customers_per_day=20,
        avg_ticket_price=80.0,
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

    res1 = scheme_service.match_schemes(profile, financials)
    res2 = scheme_service.match_schemes(profile, financials)

    assert res1.model_dump() == res2.model_dump()
