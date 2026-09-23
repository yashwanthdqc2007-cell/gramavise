import pytest
import math
from app.schemas.financial import FinancialResultResponse
from app.schemas.market import (
    MarketResultResponse,
    GeographyIdentity,
    DemographicObservation,
    PriceBenchmark,
    CoverageConfidenceLevel,
    SWOTAnalysis,
    SWOTItem,
)
from app.schemas.scheme import SchemeMatchResult, MatchedSchemeDetail
from app.schemas.evidence import EvidenceItem, EvidenceType
from app.services.recommendation.swot import SWOTEngine
from app.services.recommendation.feasibility import evaluate_feasibility_status, RecommendationStatus


@pytest.fixture
def base_evidence_ledger():
    return [
        EvidenceItem(
            evidence_id="EV-FIN-SURPLUS",
            indicator="Monthly Operating Surplus",
            claim="Monthly Operating Surplus after all costs & debt servicing",
            value="₹25,000.00",
            evidence_type=EvidenceType.CALCULATED,
            confidence=1.0,
            source="GramaVise Financial Engine",
            verification_status="CALCULATED",
        ),
        EvidenceItem(
            evidence_id="EV-FIN-BREAKEVEN",
            indicator="Daily Break-Even Footfall",
            claim="Required daily break-even sales volume",
            value="15 orders/day",
            evidence_type=EvidenceType.CALCULATED,
            confidence=1.0,
            source="GramaVise Financial Engine",
            verification_status="CALCULATED",
        ),
        EvidenceItem(
            evidence_id="EV-MKT-COMPETITORS",
            indicator="Catchment Mapped Competitors",
            claim="Direct mapped commercial competitors within catchment",
            value="1 direct mapped units",
            evidence_type=EvidenceType.OBSERVED,
            confidence=1.0,
            source="OpenStreetMap (Overpass API)",
            verification_status="VERIFIED_SOURCE",
        ),
        EvidenceItem(
            evidence_id="EV-USER-CUSTOMERS",
            indicator="Expected Daily Footfall",
            claim="Self-declared expected daily customer footfall",
            value="30 customers",
            evidence_type=EvidenceType.ASSUMED,
            confidence=0.75,
            source="Entrepreneur Self-Declaration",
            verification_status="Unverified self-declaration",
        ),
        EvidenceItem(
            evidence_id="EV-DEMO-CENSUS2011-1",
            indicator="Census Demographics",
            claim="Official Census 2011 Population",
            value="4,500 residents",
            evidence_type=EvidenceType.OBSERVED,
            confidence=1.0,
            source="Census 2011",
            verification_status="VERIFIED_SOURCE",
        ),
    ]


@pytest.fixture
def base_financial_result():
    return FinancialResultResponse(
        total_capex=300000.0,
        required_loan_amount=150000.0,
        monthly_revenue=150000.0,
        monthly_variable_cost=67500.0,
        monthly_gross_profit=82500.0,
        monthly_fixed_cost=30000.0,
        monthly_emi=4875.0,
        monthly_net_profit=47625.0,
        net_profit_margin_pct=31.75,
        break_even_revenue_monthly=63409.0,
        break_even_units_daily=13,
        dscr=16.92,
        is_financially_viable=True,
    )


@pytest.fixture
def base_market_result():
    return MarketResultResponse(
        location_summary="Baramati, Pune, Maharashtra",
        competitor_count=1,
        direct_competitor_count=1,
        adjacent_competitor_count=0,
        catchment_radius_km=5.0,
        coverage_confidence=CoverageConfidenceLevel.HIGH.value,
        demand_indicator="HIGH",
        geography=GeographyIdentity(
            state_name="Maharashtra",
            district_name="Pune",
            village_name="Baramati",
            is_geocoded=True,
        ),
        demographics=DemographicObservation(
            population=4500,
            households=900,
            reference_year=2011,
        ),
        price_benchmark=PriceBenchmark(
            category="Wheat",
            median_price=2450.0,
            unit="quintal",
            market_name="Baramati APMC",
            evidence_type=EvidenceType.OBSERVED,
            confidence=1.0,
        ),
    )


def test_01_strong_dscr_emits_strength(base_financial_result, base_market_result, base_evidence_ledger):
    """Test STR-FIN-DSCR-STRONG triggers when DSCR >= 1.50 and net profit is positive."""
    base_financial_result.dscr = 2.45
    base_financial_result.monthly_emi = 5000.0
    base_financial_result.monthly_net_profit = 35000.0

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
    )

    strong_dscr_items = [s for s in swot.strengths if s.id == "STR-FIN-DSCR-STRONG"]
    assert len(strong_dscr_items) == 1
    item = strong_dscr_items[0]
    assert item.category == "FINANCIAL"
    assert item.importance == "CRITICAL"
    assert "2.45x" in item.explanation
    assert "1.50x" in item.explanation
    assert "commercial banking" not in item.explanation.lower()
    assert item.evidence_ids == ["EV-FIN-SURPLUS"]


def test_02_moderate_dscr_informational_rule(base_financial_result, base_market_result, base_evidence_ledger):
    """Test that DSCR between 1.25 and 1.50 does not produce a false strength or false weakness."""
    base_financial_result.dscr = 1.35
    base_financial_result.monthly_emi = 5000.0
    base_financial_result.monthly_net_profit = 15000.0

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
    )

    # 1.35x is viable and moderate; must not be labeled as STR-FIN-DSCR-STRONG or WKN-FIN-DSCR-TIGHT
    assert not any(s.id == "STR-FIN-DSCR-STRONG" for s in swot.strengths)
    assert not any(w.id == "WKN-FIN-DSCR-TIGHT" for w in swot.weaknesses)
    assert not any(w.id == "WKN-FIN-DSCR-DEFICIT" for w in swot.weaknesses)


def test_03_tight_dscr_emits_weakness(base_financial_result, base_market_result, base_evidence_ledger):
    """Test WKN-FIN-DSCR-TIGHT triggers when 1.00 <= DSCR < 1.25."""
    base_financial_result.dscr = 1.15
    base_financial_result.monthly_emi = 5000.0
    base_financial_result.monthly_net_profit = 3000.0

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
    )

    tight_items = [w for w in swot.weaknesses if w.id == "WKN-FIN-DSCR-TIGHT"]
    assert len(tight_items) == 1
    assert "1.15x" in tight_items[0].explanation
    assert "1.25x" in tight_items[0].explanation
    assert tight_items[0].importance == "HIGH"


def test_04_dscr_deficit_emits_critical_weakness(base_financial_result, base_market_result, base_evidence_ledger):
    """Test WKN-FIN-DSCR-DEFICIT triggers when DSCR < 1.00."""
    base_financial_result.dscr = 0.85
    base_financial_result.monthly_emi = 10000.0
    base_financial_result.monthly_gross_profit = 35000.0
    base_financial_result.monthly_fixed_cost = 30000.0
    base_financial_result.monthly_net_profit = -5000.0

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
    )

    deficit_items = [w for w in swot.weaknesses if w.id == "WKN-FIN-DSCR-DEFICIT"]
    assert len(deficit_items) == 1
    assert deficit_items[0].importance == "CRITICAL"
    assert "0.85x" in deficit_items[0].explanation
    assert "10,000.00" in deficit_items[0].explanation


def test_05_debt_free_emits_debt_free_strength(base_financial_result, base_market_result, base_evidence_ledger):
    """Test STR-FIN-DEBT-FREE triggers when business has zero loan/EMI."""
    base_financial_result.monthly_emi = 0.0
    base_financial_result.required_loan_amount = 0.0
    base_financial_result.dscr = 0.0

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
        desired_loan=0.0,
    )

    debt_free_items = [s for s in swot.strengths if s.id == "STR-FIN-DEBT-FREE"]
    assert len(debt_free_items) == 1
    assert "100% promoter equity" in debt_free_items[0].explanation
    assert not any(s.id == "STR-FIN-DSCR-STRONG" for s in swot.strengths)


def test_06_high_break_even_emits_weakness(base_financial_result, base_market_result, base_evidence_ledger):
    """Test WKN-FIN-BREAKEVEN-HIGH triggers when break-even >= 70% of assumed customers."""
    base_financial_result.break_even_units_daily = 25
    customers_per_day = 30  # 25 / 30 = 83.3% >= 70%

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
        customers_per_day=customers_per_day,
    )

    be_items = [w for w in swot.weaknesses if w.id == "WKN-FIN-BREAKEVEN-HIGH"]
    assert len(be_items) == 1
    assert "25" in be_items[0].explanation
    assert "83%" in be_items[0].explanation
    assert be_items[0].evidence_ids == ["EV-FIN-BREAKEVEN"]


def test_07_verified_low_competition_emits_strength(base_financial_result, base_market_result, base_evidence_ledger):
    """Test STR-MKT-COMP-LOW triggers when direct competitors <= 1 and location is verified."""
    base_market_result.direct_competitor_count = 1
    base_market_result.coverage_confidence = "HIGH"
    base_market_result.geography.is_geocoded = True

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
    )

    comp_items = [s for s in swot.strengths if s.id == "STR-MKT-COMP-LOW"]
    assert len(comp_items) == 1
    assert "1 units" in comp_items[0].explanation
    assert "5 km" in comp_items[0].explanation


def test_08_unverified_zero_competition_does_not_emit_low_comp_strength(
    base_financial_result, base_market_result, base_evidence_ledger
):
    """Test that zero mapped competitors with unverified coordinates or LOW coverage does NOT emit strength."""
    base_market_result.direct_competitor_count = 0
    base_market_result.coverage_confidence = "LOW"
    base_market_result.geography.is_geocoded = False

    # EV-MKT-COMPETITORS is marked NEEDS_VERIFICATION
    for e in base_evidence_ledger:
        if e.evidence_id == "EV-MKT-COMPETITORS":
            e.evidence_type = EvidenceType.NEEDS_VERIFICATION
            e.confidence = 0.5

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
    )

    # Must NOT claim low competition strength
    assert not any(s.id == "STR-MKT-COMP-LOW" for s in swot.strengths)
    # Must emit unverified digital data coverage threat
    assert any(t.id == "THR-GEO-COVERAGE-LOW" for t in swot.threats)


def test_09_high_competition_emits_threat(base_financial_result, base_market_result, base_evidence_ledger):
    """Test THR-MKT-COMP-HIGH triggers when direct competitors >= 3 and location is verified."""
    base_market_result.direct_competitor_count = 4
    base_market_result.geography.is_geocoded = True

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
    )

    threat_items = [t for t in swot.threats if t.id == "THR-MKT-COMP-HIGH"]
    assert len(threat_items) == 1
    assert "4 established direct competitors" in threat_items[0].explanation
    assert "potential price competition" in threat_items[0].explanation


def test_10_low_coverage_or_unverified_geo_emits_threat(
    base_financial_result, base_market_result, base_evidence_ledger
):
    """Test THR-GEO-COVERAGE-LOW triggers when coverage is LOW or location is unverified."""
    base_market_result.coverage_confidence = "LOW"
    base_market_result.geography.is_geocoded = False

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
    )

    threat_items = [t for t in swot.threats if t.id == "THR-GEO-COVERAGE-LOW"]
    assert len(threat_items) == 1
    assert "unverified in digital registries" in threat_items[0].explanation
    assert threat_items[0].confidence == 0.0


def test_11_missing_mandi_price_emits_needs_verification_weakness(
    base_financial_result, base_market_result, base_evidence_ledger
):
    """Test WKN-EVD-MANDI-MISSING triggers when Mandi price is absent or marked NEEDS_VERIFICATION."""
    base_market_result.price_benchmark = None
    base_evidence_ledger.append(
        EvidenceItem(
            evidence_id="EV-MKT-MANDI-PRICE-1",
            indicator="Price Benchmark",
            claim="Mandi price unverified",
            value="Unverified",
            evidence_type=EvidenceType.NEEDS_VERIFICATION,
            confidence=0.0,
            source="Agmarknet",
            verification_status="NEEDS_VERIFICATION",
        )
    )

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
    )

    mandi_wkn = [w for w in swot.weaknesses if w.id == "WKN-EVD-MANDI-MISSING"]
    assert len(mandi_wkn) == 1
    assert "could not be cross-referenced against a verified local APMC mandi feed" in mandi_wkn[0].explanation
    assert "raw material prices are low" not in mandi_wkn[0].explanation.lower()
    assert mandi_wkn[0].confidence == 0.0


def test_12_verified_mandi_benchmark_emits_opportunity(
    base_financial_result, base_market_result, base_evidence_ledger
):
    """Test OPP-MKT-MANDI-REF triggers when verified mandi price benchmark exists."""
    base_evidence_ledger.append(
        EvidenceItem(
            evidence_id="EV-MKT-MANDI-PRICE-1",
            indicator="Official Mandi Price",
            claim="Wheat modal rate",
            value="₹2,450.00/quintal",
            evidence_type=EvidenceType.OBSERVED,
            confidence=1.0,
            source="Agmarknet",
            verification_status="VERIFIED_SOURCE",
        )
    )

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
    )

    opp_items = [o for o in swot.opportunities if o.id == "OPP-MKT-MANDI-REF"]
    assert len(opp_items) == 1
    assert "2,450.00/quintal" in opp_items[0].explanation
    assert "Baramati APMC" in opp_items[0].explanation
    assert opp_items[0].confidence == 1.0


def test_13_assumed_customer_footfall_emits_assumption_weakness(
    base_financial_result, base_market_result, base_evidence_ledger
):
    """Test WKN-EVD-ASSUMPTION-UNVERIFIED triggers for entrepreneur self-declared footfall."""
    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
        customers_per_day=30,
    )

    user_wkn = [w for w in swot.weaknesses if w.id == "WKN-EVD-ASSUMPTION-UNVERIFIED"]
    assert len(user_wkn) == 1
    assert "self-reported expected daily footfall (30 customers/day)" in user_wkn[0].explanation
    assert user_wkn[0].evidence_type == EvidenceType.ASSUMED
    assert user_wkn[0].confidence == 0.75


def test_14_pmegp_potential_match_emits_opportunity(
    base_financial_result, base_market_result, base_evidence_ledger
):
    """Test OPP-SCH-PMEGP triggers with cautious wording when PMEGP is matched."""
    base_evidence_ledger.append(
        EvidenceItem(
            evidence_id="EV-SCHEME-PMEGP",
            indicator="Government Scheme: PMEGP",
            claim="Statutory eligibility matching for PMEGP",
            value="PARTIALLY_ELIGIBLE",
            evidence_type=EvidenceType.OBSERVED,
            confidence=0.95,
            source="KVIC Portal",
            verification_status="PARTIALLY_ELIGIBLE",
        )
    )
    scheme_res = SchemeMatchResult(
        schemes=[
            MatchedSchemeDetail(
                scheme_code="PMEGP",
                scheme_name="Prime Minister's Employment Generation Programme",
                eligibility_status="PARTIALLY_ELIGIBLE",
                subsidy_eligible_amount=75000.0,
                own_contribution_required=22500.0,
                max_bank_loan=150000.0,
                source_title="KVIC Portal Guidelines",
            )
        ],
        eligible_schemes_count=1,
    )

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        scheme_result=scheme_res,
        evidence_ledger=base_evidence_ledger,
    )

    pmegp_opp = [o for o in swot.opportunities if o.id == "OPP-SCH-PMEGP"]
    assert len(pmegp_opp) == 1
    assert "potential match with Prime Minister's Employment Generation Programme" in pmegp_opp[0].explanation
    assert "₹75,000.00" in pmegp_opp[0].explanation
    assert "guaranteed subsidy" not in pmegp_opp[0].explanation.lower()
    assert "bank will sanction" not in pmegp_opp[0].explanation.lower()
    assert pmegp_opp[0].confidence == 0.95


def test_15_pmfme_potential_match_emits_opportunity(
    base_financial_result, base_market_result, base_evidence_ledger
):
    """Test OPP-SCH-PMFME triggers when PMFME is matched."""
    base_evidence_ledger.append(
        EvidenceItem(
            evidence_id="EV-SCHEME-PMFME",
            indicator="Government Scheme: PMFME",
            claim="Statutory matching for PMFME",
            value="ELIGIBLE",
            evidence_type=EvidenceType.OBSERVED,
            confidence=0.95,
            source="MoFPI Portal",
            verification_status="ELIGIBLE",
        )
    )
    scheme_res = SchemeMatchResult(
        schemes=[
            MatchedSchemeDetail(
                scheme_code="PMFME",
                scheme_name="PM Formalisation of Micro Food Processing Enterprises",
                eligibility_status="ELIGIBLE",
                subsidy_eligible_amount=105000.0,
                own_contribution_required=30000.0,
                max_bank_loan=200000.0,
                source_title="MoFPI Guidelines",
            )
        ],
        eligible_schemes_count=1,
    )

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        scheme_result=scheme_res,
        evidence_ledger=base_evidence_ledger,
    )

    pmfme_opp = [o for o in swot.opportunities if o.id == "OPP-SCH-PMFME"]
    assert len(pmfme_opp) == 1
    assert "PM Formalisation of Micro Food Processing Enterprises" in pmfme_opp[0].explanation
    assert "₹105,000.00" in pmfme_opp[0].explanation


def test_16_mudra_kishore_potential_match_emits_opportunity(
    base_financial_result, base_market_result, base_evidence_ledger
):
    """Test OPP-SCH-MUDRA_KISHORE triggers for MUDRA Kishore."""
    base_evidence_ledger.append(
        EvidenceItem(
            evidence_id="EV-SCHEME-MUDRA_KISHORE",
            indicator="Government Scheme: MUDRA",
            claim="Statutory matching for MUDRA",
            value="ELIGIBLE",
            evidence_type=EvidenceType.OBSERVED,
            confidence=0.95,
            source="MUDRA Portal",
            verification_status="ELIGIBLE",
        )
    )
    scheme_res = SchemeMatchResult(
        schemes=[
            MatchedSchemeDetail(
                scheme_code="MUDRA_KISHORE",
                scheme_name="Pradhan Mantri MUDRA Yojana (Kishore)",
                eligibility_status="ELIGIBLE",
                subsidy_eligible_amount=0.0,
                own_contribution_required=22500.0,
                max_bank_loan=150000.0,
                source_title="MUDRA Guidelines",
            )
        ],
        eligible_schemes_count=1,
    )

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        scheme_result=scheme_res,
        evidence_ledger=base_evidence_ledger,
    )

    mudra_opp = [o for o in swot.opportunities if o.id == "OPP-SCH-MUDRA_KISHORE"]
    assert len(mudra_opp) == 1
    assert "Pradhan Mantri MUDRA Yojana (Kishore)" in mudra_opp[0].explanation


def test_17_odop_match_emits_opportunity(base_financial_result, base_market_result, base_evidence_ledger):
    """Test OPP-MKT-ODOP triggers when ODOP evidence exists."""
    base_evidence_ledger.append(
        EvidenceItem(
            evidence_id="EV-MKT-ODOP-1",
            indicator="ODOP Alignment",
            claim="PMFME ODOP Master Registry",
            value="Sugarcane & Jaggery Processing",
            evidence_type=EvidenceType.OBSERVED,
            confidence=1.0,
            source="MoFPI ODOP Master",
            verification_status="VERIFIED_SOURCE",
        )
    )

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
        district="Pune",
    )

    odop_opp = [o for o in swot.opportunities if o.id == "OPP-MKT-ODOP"]
    assert len(odop_opp) == 1
    assert "One District One Product (ODOP) focus for Pune" in odop_opp[0].explanation
    assert "guarantees funding" not in odop_opp[0].explanation.lower()


def test_18_census_population_opportunity_when_conditions_satisfied(
    base_financial_result, base_market_result, base_evidence_ledger
):
    """Test OPP-DEM-CENSUS-POP triggers for consumer-facing business with verified geocoding."""
    base_market_result.geography.is_geocoded = True
    base_market_result.demographics.population = 4500
    base_market_result.demographics.households = 900

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
        category="Flour & Spice Milling (Atta Chakki)",
    )

    census_opp = [o for o in swot.opportunities if o.id == "OPP-DEM-CENSUS-POP"]
    assert len(census_opp) == 1
    assert "4,500 residents" in census_opp[0].explanation
    assert "900 households" in census_opp[0].explanation
    assert "guaranteed customer base" not in census_opp[0].explanation.lower()
    assert "walking distance" not in census_opp[0].explanation.lower()


def test_19_modelled_catchment_population_cannot_generate_census_opportunity(
    base_financial_result, base_market_result, base_evidence_ledger
):
    """Test that absent Census evidence (or unverified location) blocks Census opportunity."""
    # Remove Census evidence
    base_evidence_ledger = [e for e in base_evidence_ledger if e.evidence_id != "EV-DEMO-CENSUS2011-1"]
    base_market_result.demographics = None

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
        category="Flour & Spice Milling (Atta Chakki)",
    )

    assert not any(o.id == "OPP-DEM-CENSUS-POP" for o in swot.opportunities)


def test_20_demand_stress_20pct_emits_threat_when_negative(
    base_financial_result, base_market_result, base_evidence_ledger
):
    """Test THR-SCN-DEMAND-SENSITIVITY triggers when 20% revenue drop results in negative cash flow."""
    # Setup tightly profitable baseline where 20% drop goes negative:
    # monthly_revenue = 50,000, var_cost = 25,000, fixed = 15,000, emi = 8,000
    # Baseline profit = 50k - 25k - 15k - 8k = +2,000
    # Stress -20%: rev = 40,000, var = 20,000, profit = 40k - 20k - 15k - 8k = -3,000
    base_financial_result.monthly_revenue = 50000.0
    base_financial_result.monthly_variable_cost = 25000.0
    base_financial_result.monthly_fixed_cost = 15000.0
    base_financial_result.monthly_emi = 8000.0
    base_financial_result.monthly_net_profit = 2000.0

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
    )

    stress_threats = [t for t in swot.threats if t.id == "THR-SCN-DEMAND-SENSITIVITY"]
    assert len(stress_threats) == 1
    assert "20% demand-reduction scenario" in stress_threats[0].explanation
    assert "-3,000.00" in stress_threats[0].explanation
    assert "default will occur" not in stress_threats[0].explanation.lower()
    assert "loan will default" not in stress_threats[0].explanation.lower()


def test_21_demand_stress_does_not_emit_threat_when_cashflow_remains_positive(
    base_financial_result, base_market_result, base_evidence_ledger
):
    """Test THR-SCN-DEMAND-SENSITIVITY does NOT trigger when cash flow stays comfortably positive under -20% stress."""
    # High margin business where -20% revenue leaves surplus of +25,000
    base_financial_result.monthly_revenue = 150000.0
    base_financial_result.monthly_variable_cost = 60000.0
    base_financial_result.monthly_fixed_cost = 20000.0
    base_financial_result.monthly_emi = 5000.0
    base_financial_result.monthly_net_profit = 65000.0
    # Stress: rev = 120,000, var = 48,000, net = 120k - 48k - 20k - 5k = +47,000 > 0

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
    )

    assert not any(t.id == "THR-SCN-DEMAND-SENSITIVITY" for t in swot.threats)


def test_22_udyam_context_informational_rule_not_competitor(
    base_financial_result, base_market_result, base_evidence_ledger
):
    """Test that district Udyam data is never placed into direct competitor threats."""
    base_evidence_ledger.append(
        EvidenceItem(
            evidence_id="EV-MKT-UDYAM-1",
            indicator="Udyam District Context",
            claim="District MSME count",
            value="312,450 registered MSMEs",
            evidence_type=EvidenceType.OBSERVED,
            confidence=1.0,
            source="Ministry of MSME",
            verification_status="VERIFIED_SOURCE",
        )
    )

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
    )

    # Udyam is macro context only; must NOT create a high competition threat
    assert not any("312,450" in t.explanation for t in swot.threats)


def test_23_missing_evidence_id_does_not_create_orphan_swot_item(
    base_financial_result, base_market_result
):
    """Test that if the evidence ledger is completely empty, no orphaned SWOT items with nonexistent IDs are created."""
    empty_ledger = []

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=empty_ledger,
    )

    for item in swot.strengths + swot.weaknesses + swot.opportunities + swot.threats:
        for eid in item.evidence_ids:
            assert eid in [e.evidence_id for e in empty_ledger], f"Orphaned evidence_id found: {eid}"


def test_24_all_emitted_swot_items_have_valid_evidence_ids(
    base_financial_result, base_market_result, base_evidence_ledger
):
    """Test that every emitted SWOT item strictly references an evidence ID in the ledger."""
    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
        customers_per_day=30,
        category="Flour & Spice Milling (Atta Chakki)",
    )

    ledger_ids = {e.evidence_id for e in base_evidence_ledger}
    all_items = swot.strengths + swot.weaknesses + swot.opportunities + swot.threats

    assert len(all_items) > 0
    for item in all_items:
        assert len(item.evidence_ids) > 0
        for eid in item.evidence_ids:
            assert eid in ledger_ids


def test_25_provider_failure_or_empty_inputs_does_not_crash_engine():
    """Test that None/empty arguments do not crash the engine and return a safe empty SWOTAnalysis."""
    swot = SWOTEngine.generate_swot(
        financial_result=None,
        market_result=None,
        scheme_result=None,
        evidence_ledger=None,
    )

    assert isinstance(swot, SWOTAnalysis)
    assert swot.strengths == []
    assert swot.weaknesses == []
    assert swot.opportunities == []
    assert swot.threats == []
    assert swot.confidence == 1.0


def test_26_no_nan_or_infinity_in_outputs(base_financial_result, base_market_result, base_evidence_ledger):
    """Test that float calculations in explanations never contain NaN or Infinity."""
    base_financial_result.dscr = 15.6789
    base_financial_result.monthly_net_profit = 227025.91
    base_financial_result.monthly_emi = 3224.09

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
        customers_per_day=25,
    )

    for item in swot.strengths + swot.weaknesses + swot.opportunities + swot.threats:
        assert "nan" not in item.explanation.lower()
        assert "inf" not in item.explanation.lower()
        assert not math.isnan(item.confidence)
        assert not math.isinf(item.confidence)


def test_27_deterministic_repeated_execution_produces_identical_output(
    base_financial_result, base_market_result, base_evidence_ledger
):
    """Test that calling generate_swot multiple times on identical inputs yields bit-for-bit identical outputs."""
    swot1 = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
        customers_per_day=30,
        category="Flour & Spice Milling (Atta Chakki)",
    )
    swot2 = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
        customers_per_day=30,
        category="Flour & Spice Milling (Atta Chakki)",
    )

    assert swot1.model_dump() == swot2.model_dump()


def test_28_swot_does_not_mutate_financial_results(
    base_financial_result, base_market_result, base_evidence_ledger
):
    """Test that running SWOT analysis strictly preserves all fields of the financial calculation result."""
    original_dump = base_financial_result.model_dump()

    _ = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
    )

    assert base_financial_result.model_dump() == original_dump


def test_29_swot_does_not_alter_feasibility_status_or_thresholds(
    base_financial_result, base_market_result, base_evidence_ledger
):
    """Test that feasibility recommendation status logic remains completely independent and invariant."""
    status_before = evaluate_feasibility_status(base_financial_result, base_market_result)
    assert status_before == RecommendationStatus.PROCEED

    _ = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
    )

    status_after = evaluate_feasibility_status(base_financial_result, base_market_result)
    assert status_after == status_before


def test_30_quadrant_capacity_and_importance_sorting(
    base_financial_result, base_market_result, base_evidence_ledger
):
    """Test that items within quadrants are deterministically sorted by importance (CRITICAL > HIGH > MEDIUM > LOW)."""
    # Create multiple weaknesses
    base_financial_result.dscr = 0.80  # WKN-FIN-DSCR-DEFICIT (CRITICAL)
    base_financial_result.monthly_emi = 5000.0
    base_financial_result.break_even_units_daily = 28
    customers_per_day = 30  # WKN-FIN-BREAKEVEN-HIGH (HIGH)
    # WKN-EVD-ASSUMPTION-UNVERIFIED (MEDIUM)

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
        customers_per_day=customers_per_day,
        max_items_per_quadrant=4,
    )

    assert len(swot.weaknesses) <= 4
    # The first item should be CRITICAL
    assert swot.weaknesses[0].importance == "CRITICAL"
    assert swot.weaknesses[0].id == "WKN-FIN-DSCR-DEFICIT"


def test_31_positive_profit_emits_strength(base_financial_result, base_market_result, base_evidence_ledger):
    """Test that positive net profit emits STR-FIN-PROFIT-POSITIVE strength."""
    base_financial_result.monthly_net_profit = 25000.0
    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
    )
    assert any(s.id == "STR-FIN-PROFIT-POSITIVE" for s in swot.strengths)


def test_32_negative_profit_emits_critical_weakness(base_financial_result, base_market_result, base_evidence_ledger):
    """Test that negative net profit emits WKN-FIN-PROFIT-NEGATIVE weakness."""
    base_financial_result.monthly_net_profit = -5000.0
    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
    )
    assert any(w.id == "WKN-FIN-PROFIT-NEGATIVE" for w in swot.weaknesses)
    neg_item = next(w for w in swot.weaknesses if w.id == "WKN-FIN-PROFIT-NEGATIVE")
    assert neg_item.importance == "CRITICAL"


def test_33_seasonal_threat_detection(base_financial_result, base_market_result, base_evidence_ledger):
    """Test that populated seasonal threats in MarketResultResponse emit corresponding SWOT threats."""
    from app.schemas.market import SeasonalThreatDetail
    base_market_result.seasonal_threats = [
        SeasonalThreatDetail(
            threat_id="THR-SEA-MONSOON-01",
            threat_type="MONSOON",
            title="Monsoon Access Disruption",
            explanation="Heavy monsoon precipitation in Jul-Aug may restrict supply arrivals and footfall.",
            affected_period="Jul-Aug",
            severity="MEDIUM",
            evidence_ids=["EV-MKT-COMPETITORS"],
            confidence=0.8,
        )
    ]
    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
    )
    assert any("THR-MKT-SEASONAL" in t.id for t in swot.threats)


def test_34_supply_chain_risk_detection(base_financial_result, base_market_result, base_evidence_ledger):
    """Test that populated supply chain risks in MarketResultResponse emit corresponding SWOT threats."""
    from app.schemas.market import SupplyChainRiskDetail
    base_market_result.supply_chain = [
        SupplyChainRiskDetail(
            risk_id="SCR-WHEAT-01",
            input_material="Raw Wheat Grain",
            supplier_dependency="LOCAL_MARKET",
            price_volatility="HIGH",
            evidence_ids=["EV-MKT-COMPETITORS"],
            confidence=0.85,
            notes="Subject to seasonal post-harvest price spikes.",
        )
    ]
    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
    )
    assert any("THR-MKT-SUPPLY" in t.id for t in swot.threats)


def test_35_verified_zero_competition_emits_market_gap_opportunity(base_financial_result, base_market_result, base_evidence_ledger):
    """Test that genuine verified zero competitors emits OPP-MKT-COMP-GAP opportunity."""
    base_market_result.direct_competitor_count = 0
    base_market_result.coverage_confidence = "HIGH"
    base_market_result.geography.is_geocoded = True

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
    )
    assert any(o.id == "OPP-MKT-COMP-GAP" for o in swot.opportunities)


def test_36_healthy_contribution_margin_and_manageable_breakeven(base_financial_result, base_market_result, base_evidence_ledger):
    """Test that high gross margin and low break-even units emit respective strength factors."""
    base_financial_result.monthly_revenue = 100000.0
    base_financial_result.monthly_gross_profit = 55000.0  # 55% margin
    base_financial_result.break_even_units_daily = 10
    customers_per_day = 25  # 10 <= 0.50 * 25

    swot = SWOTEngine.generate_swot(
        financial_result=base_financial_result,
        market_result=base_market_result,
        evidence_ledger=base_evidence_ledger,
        customers_per_day=customers_per_day,
        max_items_per_quadrant=6,
    )
    assert any(s.id == "STR-FIN-CONTRIBUTION-MARGIN" for s in swot.strengths)
    assert any(s.id == "STR-FIN-BREAKEVEN-MANAGEABLE" for s in swot.strengths)

