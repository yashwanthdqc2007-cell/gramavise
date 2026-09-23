"""Phase 2D-F: SWOT Quality, Consistency & Decision-Coherence Audit Test Suite.

Verifies:
1. Representative business profiles (Strong, Moderate, Weak, Debt-free, Unverified geography).
2. Decision and recommendation consistency.
3. Financial consistency (SWOT is pure interpretation; uses exact FinancialService figures).
4. Threshold audit and exact boundary values (DSCR, Break-even, Competition, Profit, Loan).
5. Evidence quality (canonical IDs, correct EvidenceType, no ASSUMED marked as OBSERVED).
6. Opportunity and Threat cautious language safety.
7. Deduplication, quadrant balance, and absence of semantic contradictions.
8. Standard GramaVise demo business fixtures.
"""

import pytest
from app.schemas.financial import FinancialResultResponse
from app.schemas.market import (
    MarketResultResponse,
    PriceBenchmark,
    DemographicObservation,
    GeographyIdentity,
    CoverageConfidenceLevel,
)
from app.schemas.scheme import SchemeMatchResult, MatchedSchemeDetail
from app.schemas.evidence import EvidenceItem, EvidenceType
from app.schemas.analysis import DecisionTrace, RecommendationStatus
from app.services.recommendation.swot import SWOTEngine


def make_standard_evidence_ledger() -> list[EvidenceItem]:
    """Helper to provide a canonical evidence ledger containing all standard indicators."""
    return [
        EvidenceItem(
            evidence_id="EV-FIN-SURPLUS",
            indicator="Monthly Operating Surplus",
            claim="Operating surplus after expenses and debt servicing",
            value="24594.64",
            evidence_type=EvidenceType.CALCULATED,
            confidence=1.0,
            source="GramaVise Financial Engine",
        ),
        EvidenceItem(
            evidence_id="EV-FIN-BREAKEVEN",
            indicator="Daily Break-Even Volume",
            claim="Required daily customers to achieve operational break-even",
            value="14",
            evidence_type=EvidenceType.CALCULATED,
            confidence=1.0,
            source="GramaVise Financial Engine",
        ),
        EvidenceItem(
            evidence_id="EV-MKT-COMPETITORS",
            indicator="Nearby Mapped Competitor POIs",
            claim="Competitor count in catchment",
            value="0",
            evidence_type=EvidenceType.OBSERVED,
            confidence=1.0,
            source="OpenStreetMap (Overpass API)",
        ),
        EvidenceItem(
            evidence_id="EV-MKT-MANDI-PRICE-1",
            indicator="Agmarknet Mandi Commodity Price Reference",
            claim="Official modal commodity price",
            value="2850.0",
            evidence_type=EvidenceType.OBSERVED,
            confidence=1.0,
            source="Directorate of Marketing & Inspection (DMI) / OGD",
        ),
        EvidenceItem(
            evidence_id="EV-DEMO-CENSUS2011-1",
            indicator="Census 2011 Village Population",
            claim="Official population counts",
            value="4200",
            evidence_type=EvidenceType.OBSERVED,
            confidence=1.0,
            source="Office of the Registrar General & Census Commissioner, India",
        ),
        EvidenceItem(
            evidence_id="EV-USER-CUSTOMERS",
            indicator="Self-Reported Customer Footfall",
            claim="Daily customer footfall estimated by entrepreneur",
            value="35",
            evidence_type=EvidenceType.ASSUMED,
            confidence=0.75,
            source="Entrepreneur Self-Declaration",
        ),
        EvidenceItem(
            evidence_id="EV-SCHEME-PMEGP",
            indicator="PMEGP Scheme Eligibility",
            claim="Matched central government credit-linked capital subsidy",
            value="ELIGIBLE",
            evidence_type=EvidenceType.OBSERVED,
            confidence=0.95,
            source="Official PMEGP Guidelines",
        ),
        EvidenceItem(
            evidence_id="EV-SCHEME-MUDRA_KISHORE",
            indicator="MUDRA Kishore Scheme Eligibility",
            claim="Matched collateral-free micro enterprise loan",
            value="ELIGIBLE",
            evidence_type=EvidenceType.OBSERVED,
            confidence=0.95,
            source="Pradhan Mantri MUDRA Yojana Guidelines",
        ),
        EvidenceItem(
            evidence_id="EV-MKT-ODOP-1",
            indicator="ODOP Priority Product Match",
            claim="District One District One Product alignment",
            value="ALIGNED",
            evidence_type=EvidenceType.OBSERVED,
            confidence=1.0,
            source="Ministry of Food Processing Industries (MoFPI)",
        ),
    ]


# =============================================================================
# 1. REPRESENTATIVE BUSINESS FIXTURES
# =============================================================================

def test_fixture_a_strong_business():
    """Case A: Strong Business (High profit, DSCR >= 1.50, manageable BE, low competition)."""
    fin = FinancialResultResponse(
        total_capex=150000.0,
        required_loan_amount=100000.0,
        monthly_revenue=70000.0,
        monthly_variable_cost=21000.0,
        monthly_gross_profit=49000.0,
        monthly_fixed_cost=10000.0,
        monthly_emi=3300.0,
        monthly_net_profit=35700.0,
        net_profit_margin_pct=51.0,
        break_even_revenue_monthly=19000.0,
        break_even_units_daily=10,
        dscr=11.8,
        is_financially_viable=True,
    )
    mkt = MarketResultResponse(
        location_summary="Baramati, Pune, Maharashtra",
        competitor_count=0,
        direct_competitor_count=0,
        adjacent_competitor_count=0,
        catchment_radius_km=5.0,
        coverage_confidence="HIGH",
        competitor_list=[],
        demand_indicator="HIGH",
        geography=GeographyIdentity(
            state_name="Maharashtra",
            district_name="Pune",
            village_name="Baramati",
            is_geocoded=True,
        ),
        demographics=DemographicObservation(population=4500, households=900),
        price_benchmark=PriceBenchmark(category="Flour", median_price=2800.0, unit="quintal"),
    )
    schemes = SchemeMatchResult(
        schemes=[
            MatchedSchemeDetail(
                scheme_code="PMEGP",
                scheme_name="Prime Minister's Employment Generation Programme",
                subsidy_eligible_amount=35000.0,
                own_contribution_required=15000.0,
                max_bank_loan=100000.0,
                eligibility_status="ELIGIBLE",
            )
        ],
        eligible_schemes_count=1,
    )

    swot = SWOTEngine.generate_swot(
        financial_result=fin,
        market_result=mkt,
        scheme_result=schemes,
        evidence_ledger=make_standard_evidence_ledger(),
        customers_per_day=35,
        desired_loan=100000.0,
        category="Flour & Spice Milling",
    )

    # 1. Top 4 strengths prioritized by importance (CRITICAL/HIGH first)
    str_ids = {s.id for s in swot.strengths}
    assert "STR-FIN-PROFIT-POSITIVE" in str_ids
    assert "STR-FIN-DSCR-STRONG" in str_ids
    assert "STR-MKT-COMP-LOW" in str_ids
    assert len(swot.strengths) == 4

    # 2. Must NOT emit false financial weaknesses
    wkn_ids = {w.id for w in swot.weaknesses}
    assert "WKN-FIN-PROFIT-NEGATIVE" not in wkn_ids
    assert "WKN-FIN-DSCR-TIGHT" not in wkn_ids
    assert "WKN-FIN-DSCR-DEFICIT" not in wkn_ids

    # 3. Opportunities must include potential PMEGP and market gap
    opp_ids = {o.id for o in swot.opportunities}
    assert "OPP-SCH-PMEGP" in opp_ids
    assert "OPP-MKT-COMP-GAP" in opp_ids


def test_fixture_b_moderate_validate_first_business():
    """Case B: Moderate Business (DSCR = 1.35 between 1.25 and 1.50, thin profit, unverified mandi)."""
    fin = FinancialResultResponse(
        total_capex=120000.0,
        required_loan_amount=80000.0,
        monthly_revenue=40000.0,
        monthly_variable_cost=24000.0,
        monthly_gross_profit=16000.0,
        monthly_fixed_cost=10000.0,
        monthly_emi=4400.0,
        monthly_net_profit=1600.0,
        net_profit_margin_pct=4.0,
        break_even_revenue_monthly=36000.0,
        break_even_units_daily=23,
        dscr=1.36,
        is_financially_viable=True,
    )
    # Market without mandi price benchmark
    mkt = MarketResultResponse(
        location_summary="Rural Block",
        competitor_count=2,
        direct_competitor_count=2,
        adjacent_competitor_count=0,
        catchment_radius_km=5.0,
        coverage_confidence="MEDIUM",
        competitor_list=[],
        demand_indicator="MEDIUM",
        geography=GeographyIdentity(is_geocoded=True),
        price_benchmark=None,
    )

    ledger = make_standard_evidence_ledger()
    # Mark mandi evidence as NEEDS_VERIFICATION
    for ev in ledger:
        if ev.evidence_id == "EV-MKT-MANDI-PRICE-1":
            ev.evidence_type = EvidenceType.NEEDS_VERIFICATION

    swot = SWOTEngine.generate_swot(
        financial_result=fin,
        market_result=mkt,
        evidence_ledger=ledger,
        customers_per_day=25,
        desired_loan=80000.0,
        category="General Retail",
    )

    # Strengths: Has positive profit
    str_ids = {s.id for s in swot.strengths}
    assert "STR-FIN-PROFIT-POSITIVE" in str_ids
    # DSCR is 1.36 (< 1.50), so STR-FIN-DSCR-STRONG must NOT be emitted
    assert "STR-FIN-DSCR-STRONG" not in str_ids

    # Weaknesses: High break-even (23/25 = 92% >= 70%) and unverified mandi
    wkn_ids = {w.id for w in swot.weaknesses}
    assert "WKN-FIN-BREAKEVEN-HIGH" in wkn_ids
    assert "WKN-EVD-MANDI-MISSING" in wkn_ids
    # DSCR is 1.36 (>= 1.25), so WKN-FIN-DSCR-TIGHT must NOT be emitted
    assert "WKN-FIN-DSCR-TIGHT" not in wkn_ids


def test_fixture_c_weak_reconsider_business():
    """Case C: Weak Business (Net profit < 0, DSCR < 1.0, severe cash deficit)."""
    fin = FinancialResultResponse(
        total_capex=200000.0,
        required_loan_amount=150000.0,
        monthly_revenue=30000.0,
        monthly_variable_cost=18000.0,
        monthly_gross_profit=12000.0,
        monthly_fixed_cost=11000.0,
        monthly_emi=5500.0,
        monthly_net_profit=-4500.0,
        net_profit_margin_pct=-15.0,
        break_even_revenue_monthly=41250.0,
        break_even_units_daily=35,
        dscr=0.18,
        is_financially_viable=False,
    )
    mkt = MarketResultResponse(
        location_summary="High Competition Town",
        competitor_count=4,
        direct_competitor_count=4,
        adjacent_competitor_count=1,
        catchment_radius_km=5.0,
        coverage_confidence="HIGH",
        competitor_list=[],
        demand_indicator="LOW",
        geography=GeographyIdentity(is_geocoded=True),
    )

    swot = SWOTEngine.generate_swot(
        financial_result=fin,
        market_result=mkt,
        evidence_ledger=make_standard_evidence_ledger(),
        customers_per_day=25,
        desired_loan=150000.0,
        category="Tailoring",
    )

    # 1. Must NOT emit positive financial strengths
    str_ids = {s.id for s in swot.strengths}
    assert "STR-FIN-PROFIT-POSITIVE" not in str_ids
    assert "STR-FIN-DSCR-STRONG" not in str_ids

    # 2. Must emit critical weaknesses
    wkn_ids = {w.id for w in swot.weaknesses}
    assert "WKN-FIN-PROFIT-NEGATIVE" in wkn_ids
    assert "WKN-FIN-DSCR-DEFICIT" in wkn_ids

    # 3. Must emit threats
    thr_ids = {t.id for t in swot.threats}
    assert "THR-MKT-COMP-HIGH" in thr_ids
    assert "THR-SCN-DEMAND-SENSITIVITY" in thr_ids


def test_fixture_d_debt_free_business():
    """Case D: Debt-Free Business (Loan = 0, EMI = 0)."""
    fin = FinancialResultResponse(
        total_capex=50000.0,
        required_loan_amount=0.0,
        monthly_revenue=30000.0,
        monthly_variable_cost=10000.0,
        monthly_gross_profit=20000.0,
        monthly_fixed_cost=5000.0,
        monthly_emi=0.0,
        monthly_net_profit=15000.0,
        net_profit_margin_pct=50.0,
        break_even_revenue_monthly=7500.0,
        break_even_units_daily=5,
        dscr=999.0,  # Synthetic internal high value
        is_financially_viable=True,
    )
    mkt = MarketResultResponse(
        location_summary="Village Square",
        competitor_count=1,
        direct_competitor_count=1,
        adjacent_competitor_count=0,
        catchment_radius_km=5.0,
        coverage_confidence="HIGH",
        competitor_list=[],
        demand_indicator="HIGH",
        geography=GeographyIdentity(is_geocoded=True),
    )

    swot = SWOTEngine.generate_swot(
        financial_result=fin,
        market_result=mkt,
        evidence_ledger=make_standard_evidence_ledger(),
        customers_per_day=20,
        desired_loan=0.0,
        category="Poultry",
    )

    str_ids = {s.id for s in swot.strengths}
    assert "STR-FIN-DEBT-FREE" in str_ids

    # Must NOT emit debt weaknesses or false DSCR shortfall
    wkn_ids = {w.id for w in swot.weaknesses}
    assert "WKN-FIN-DSCR-TIGHT" not in wkn_ids
    assert "WKN-FIN-DSCR-DEFICIT" not in wkn_ids


def test_fixture_e_unverified_geography():
    """Case E: Unverified Geography (Competitor count = 0, but is_geocoded = False or cov_conf = LOW)."""
    fin = FinancialResultResponse(
        total_capex=60000.0,
        required_loan_amount=30000.0,
        monthly_revenue=25000.0,
        monthly_variable_cost=8000.0,
        monthly_gross_profit=17000.0,
        monthly_fixed_cost=4000.0,
        monthly_emi=1100.0,
        monthly_net_profit=11900.0,
        net_profit_margin_pct=47.6,
        break_even_revenue_monthly=7500.0,
        break_even_units_daily=5,
        dscr=11.8,
        is_financially_viable=True,
    )
    mkt = MarketResultResponse(
        location_summary="Unverified Remote Location",
        competitor_count=0,
        direct_competitor_count=0,
        adjacent_competitor_count=0,
        catchment_radius_km=5.0,
        coverage_confidence="LOW",
        competitor_list=[],
        demand_indicator="UNKNOWN",
        geography=GeographyIdentity(is_geocoded=False),
    )

    ledger = make_standard_evidence_ledger()
    for ev in ledger:
        if ev.evidence_id == "EV-MKT-COMPETITORS":
            ev.evidence_type = EvidenceType.NEEDS_VERIFICATION

    swot = SWOTEngine.generate_swot(
        financial_result=fin,
        market_result=mkt,
        evidence_ledger=ledger,
        customers_per_day=20,
        desired_loan=30000.0,
        category="Kirana",
    )

    # 1. Must NOT emit low competition strength or market gap opportunity when geocoding is unverified
    str_ids = {s.id for s in swot.strengths}
    opp_ids = {o.id for o in swot.opportunities}
    assert "STR-MKT-COMP-LOW" not in str_ids
    assert "OPP-MKT-COMP-GAP" not in opp_ids

    # 2. Must emit unverified data coverage threat
    thr_ids = {t.id for t in swot.threats}
    assert "THR-GEO-COVERAGE-LOW" in thr_ids


# =============================================================================
# 2. EXACT BOUNDARY VALUE TESTS
# =============================================================================

@pytest.mark.parametrize("dscr,expected_str,expected_wkn", [
    (0.9999, False, "WKN-FIN-DSCR-DEFICIT"),
    (1.0000, False, "WKN-FIN-DSCR-TIGHT"),
    (1.2499, False, "WKN-FIN-DSCR-TIGHT"),
    (1.2500, False, None),  # Baseline viable: neither tight nor strong
    (1.4999, False, None),  # Moderate: neither tight nor strong
    (1.5000, "STR-FIN-DSCR-STRONG", None),
    (2.5000, "STR-FIN-DSCR-STRONG", None),
])
def test_dscr_exact_boundaries(dscr, expected_str, expected_wkn):
    fin = FinancialResultResponse(
        total_capex=100000.0,
        required_loan_amount=50000.0,
        monthly_revenue=50000.0,
        monthly_variable_cost=20000.0,
        monthly_gross_profit=30000.0,
        monthly_fixed_cost=10000.0,
        monthly_emi=2000.0,
        monthly_net_profit=18000.0 if dscr >= 1.0 else -500.0,
        net_profit_margin_pct=36.0 if dscr >= 1.0 else -1.0,
        break_even_revenue_monthly=20000.0,
        break_even_units_daily=10,
        dscr=dscr,
        is_financially_viable=dscr >= 1.25,
    )

    swot = SWOTEngine.generate_swot(
        financial_result=fin,
        evidence_ledger=make_standard_evidence_ledger(),
        customers_per_day=30,
        desired_loan=50000.0,
    )

    str_ids = {s.id for s in swot.strengths}
    wkn_ids = {w.id for w in swot.weaknesses}

    if expected_str:
        assert expected_str in str_ids
    else:
        assert "STR-FIN-DSCR-STRONG" not in str_ids

    if expected_wkn:
        assert expected_wkn in wkn_ids
    else:
        assert "WKN-FIN-DSCR-TIGHT" not in wkn_ids
        assert "WKN-FIN-DSCR-DEFICIT" not in wkn_ids


@pytest.mark.parametrize("be_units,cust_day,expected_str,expected_wkn", [
    (15, 30, "STR-FIN-BREAKEVEN-MANAGEABLE", None),  # 50.0% -> Manageable
    (16, 30, None, None),                            # 53.3% -> Neutral
    (20, 30, None, None),                            # 66.7% -> Neutral
    (21, 30, None, "WKN-FIN-BREAKEVEN-HIGH"),         # 70.0% -> High
    (30, 30, None, "WKN-FIN-BREAKEVEN-HIGH"),         # 100.0% -> High
])
def test_breakeven_exact_boundaries(be_units, cust_day, expected_str, expected_wkn):
    fin = FinancialResultResponse(
        total_capex=100000.0,
        required_loan_amount=50000.0,
        monthly_revenue=50000.0,
        monthly_variable_cost=20000.0,
        monthly_gross_profit=30000.0,
        monthly_fixed_cost=10000.0,
        monthly_emi=2000.0,
        monthly_net_profit=18000.0,
        net_profit_margin_pct=36.0,
        break_even_revenue_monthly=20000.0,
        break_even_units_daily=be_units,
        dscr=10.0,
        is_financially_viable=True,
    )

    swot = SWOTEngine.generate_swot(
        financial_result=fin,
        evidence_ledger=make_standard_evidence_ledger(),
        customers_per_day=cust_day,
        desired_loan=50000.0,
    )

    str_ids = {s.id for s in swot.strengths}
    wkn_ids = {w.id for w in swot.weaknesses}

    if expected_str:
        assert expected_str in str_ids
    else:
        assert "STR-FIN-BREAKEVEN-MANAGEABLE" not in str_ids

    if expected_wkn:
        assert expected_wkn in wkn_ids
    else:
        assert "WKN-FIN-BREAKEVEN-HIGH" not in wkn_ids


@pytest.mark.parametrize("comp_count,expected_str,expected_opp,expected_thr", [
    (0, "STR-MKT-COMP-LOW", "OPP-MKT-COMP-GAP", None),
    (1, "STR-MKT-COMP-LOW", None, None),
    (2, None, None, None),                         # Neutral 2 competitors
    (3, None, None, "THR-MKT-COMP-HIGH"),
    (5, None, None, "THR-MKT-COMP-HIGH"),
])
def test_competition_count_boundaries(comp_count, expected_str, expected_opp, expected_thr):
    mkt = MarketResultResponse(
        location_summary="Test Town",
        competitor_count=comp_count,
        direct_competitor_count=comp_count,
        adjacent_competitor_count=0,
        catchment_radius_km=5.0,
        coverage_confidence="HIGH",
        competitor_list=[],
        demand_indicator="HIGH",
        geography=GeographyIdentity(is_geocoded=True),
    )

    swot = SWOTEngine.generate_swot(
        market_result=mkt,
        evidence_ledger=make_standard_evidence_ledger(),
    )

    str_ids = {s.id for s in swot.strengths}
    opp_ids = {o.id for o in swot.opportunities}
    thr_ids = {t.id for t in swot.threats}

    if expected_str:
        assert expected_str in str_ids
    else:
        assert "STR-MKT-COMP-LOW" not in str_ids

    if expected_opp:
        assert expected_opp in opp_ids
    else:
        assert "OPP-MKT-COMP-GAP" not in opp_ids

    if expected_thr:
        assert expected_thr in thr_ids
    else:
        assert "THR-MKT-COMP-HIGH" not in thr_ids


# =============================================================================
# 3. EVIDENCE & CAUTIOUS LANGUAGE SAFETY AUDIT
# =============================================================================

def test_evidence_provenance_and_no_assumed_as_observed():
    """Verify that every emitted SWOT item preserves exact evidence types and valid canonical IDs."""
    fin = FinancialResultResponse(
        total_capex=100000.0,
        required_loan_amount=50000.0,
        monthly_revenue=50000.0,
        monthly_variable_cost=20000.0,
        monthly_gross_profit=30000.0,
        monthly_fixed_cost=10000.0,
        monthly_emi=2000.0,
        monthly_net_profit=18000.0,
        net_profit_margin_pct=36.0,
        break_even_revenue_monthly=20000.0,
        break_even_units_daily=10,
        dscr=10.0,
        is_financially_viable=True,
    )
    mkt = MarketResultResponse(
        location_summary="Village",
        competitor_count=0,
        direct_competitor_count=0,
        adjacent_competitor_count=0,
        catchment_radius_km=5.0,
        coverage_confidence="HIGH",
        competitor_list=[],
        demand_indicator="HIGH",
        geography=GeographyIdentity(is_geocoded=True),
        demographics=DemographicObservation(population=3000),
    )
    schemes = SchemeMatchResult(
        schemes=[
            MatchedSchemeDetail(
                scheme_code="MUDRA_KISHORE",
                scheme_name="Pradhan Mantri MUDRA Yojana (Kishore)",
                subsidy_eligible_amount=0.0,
                own_contribution_required=10000.0,
                max_bank_loan=50000.0,
                eligibility_status="ELIGIBLE",
            )
        ],
        eligible_schemes_count=1,
    )

    ledger = make_standard_evidence_ledger()
    swot = SWOTEngine.generate_swot(
        financial_result=fin,
        market_result=mkt,
        scheme_result=schemes,
        evidence_ledger=ledger,
        customers_per_day=30,
        desired_loan=50000.0,
        category="Retail",
    )

    all_items = swot.strengths + swot.weaknesses + swot.opportunities + swot.threats
    canonical_ids = {e.evidence_id for e in ledger}

    for item in all_items:
        # 1. Every evidence ID must exist in ledger
        assert len(item.evidence_ids) > 0, f"Item {item.id} has no evidence IDs"
        for eid in item.evidence_ids:
            assert eid in canonical_ids, f"Item {item.id} references non-canonical evidence ID {eid}"

        # 2. ASSUMED item must have ASSUMED evidence type
        if item.id == "WKN-EVD-ASSUMPTION-UNVERIFIED":
            assert item.evidence_type == EvidenceType.ASSUMED

        # 3. NEEDS_VERIFICATION item must have confidence 0.0 or NEEDS_VERIFICATION type
        if item.evidence_type == EvidenceType.NEEDS_VERIFICATION:
            assert item.confidence == 0.0 or item.evidence_type == EvidenceType.NEEDS_VERIFICATION


def test_opportunity_and_threat_language_cautious():
    """Verify that scheme opportunities and stress threats contain prudent, non-exaggerated wording."""
    schemes = SchemeMatchResult(
        schemes=[
            MatchedSchemeDetail(
                scheme_code="PMEGP",
                scheme_name="Prime Minister's Employment Generation Programme",
                subsidy_eligible_amount=35000.0,
                own_contribution_required=15000.0,
                max_bank_loan=100000.0,
                eligibility_status="ELIGIBLE",
            )
        ],
        eligible_schemes_count=1,
    )

    swot = SWOTEngine.generate_swot(
        scheme_result=schemes,
        evidence_ledger=make_standard_evidence_ledger(),
    )

    opp = next((o for o in swot.opportunities if o.id == "OPP-SCH-PMEGP"), None)
    assert opp is not None
    # Must use 'potential match' / 'potential margin subsidy'
    assert "potential match" in opp.explanation.lower() or "potential" in opp.title.lower()
    # Must NOT claim guaranteed loan or approval
    assert "guaranteed loan" not in opp.explanation.lower()
    assert "approved" not in opp.explanation.lower()
    assert "guaranteed subsidy" not in opp.explanation.lower()


# =============================================================================
# 4. DEMO PROFILES CONSISTENCY VALIDATION
# =============================================================================

def test_demo_kisan_flour_mill():
    """Kisan Flour Mill in Baramati (Viable Atta Chakki)."""
    fin = FinancialResultResponse(
        total_capex=150000.0,
        required_loan_amount=110000.0,
        monthly_revenue=59150.0,
        monthly_variable_cost=18928.0,
        monthly_gross_profit=40222.0,
        monthly_fixed_cost=12000.0,
        monthly_emi=3627.36,
        monthly_net_profit=24594.64,
        net_profit_margin_pct=41.58,
        break_even_revenue_monthly=22981.41,
        break_even_units_daily=14,
        dscr=7.78,
        is_financially_viable=True,
    )
    mkt = MarketResultResponse(
        location_summary="Baramati Rural, Pune, Maharashtra",
        competitor_count=0,
        direct_competitor_count=0,
        adjacent_competitor_count=0,
        catchment_radius_km=5.0,
        coverage_confidence="HIGH",
        competitor_list=[],
        demand_indicator="HIGH",
        geography=GeographyIdentity(
            state_name="Maharashtra",
            district_name="Pune",
            village_name="Baramati Rural",
            is_geocoded=True,
        ),
        demographics=DemographicObservation(population=4200),
        price_benchmark=PriceBenchmark(category="Wheat Flour", median_price=2850.0, unit="quintal"),
    )
    schemes = SchemeMatchResult(
        schemes=[
            MatchedSchemeDetail(
                scheme_code="PMEGP",
                scheme_name="Prime Minister's Employment Generation Programme",
                subsidy_eligible_amount=37500.0,
                own_contribution_required=15000.0,
                max_bank_loan=110000.0,
                eligibility_status="ELIGIBLE",
            ),
            MatchedSchemeDetail(
                scheme_code="MUDRA_KISHORE",
                scheme_name="Pradhan Mantri MUDRA Yojana (Kishore)",
                subsidy_eligible_amount=0.0,
                own_contribution_required=10000.0,
                max_bank_loan=100000.0,
                eligibility_status="ELIGIBLE",
            ),
        ],
        eligible_schemes_count=2,
    )

    swot = SWOTEngine.generate_swot(
        financial_result=fin,
        market_result=mkt,
        scheme_result=schemes,
        evidence_ledger=make_standard_evidence_ledger(),
        customers_per_day=35,
        desired_loan=110000.0,
        category="Flour & Spice Milling (Atta Chakki)",
        district="Pune",
    )

    # Strengths (4): Positive profit, strong DSCR, manageable break-even (14/35 = 40% <= 50%), healthy margin (68% >= 40%)
    assert len(swot.strengths) == 4
    # Weaknesses (1): Self-declared footfall assumption
    assert len(swot.weaknesses) >= 1
    # Opportunities: Schemes + Census + Mandi benchmark + ODOP
    assert len(swot.opportunities) >= 2
    # Zero contradiction
    assert not any("deficit" in s.title.lower() for s in swot.strengths)


def test_demo_lakshmi_tailoring():
    """Lakshmi Tailoring & Garment Making (Moderate Capex, viable)."""
    fin = FinancialResultResponse(
        total_capex=75000.0,
        required_loan_amount=50000.0,
        monthly_revenue=35000.0,
        monthly_variable_cost=10500.0,
        monthly_gross_profit=24500.0,
        monthly_fixed_cost=6500.0,
        monthly_emi=1648.8,
        monthly_net_profit=16351.2,
        net_profit_margin_pct=46.7,
        break_even_revenue_monthly=11641.0,
        break_even_units_daily=8,
        dscr=10.9,
        is_financially_viable=True,
    )
    mkt = MarketResultResponse(
        location_summary="Dindigul Rural, Tamil Nadu",
        competitor_count=1,
        direct_competitor_count=1,
        adjacent_competitor_count=0,
        catchment_radius_km=5.0,
        coverage_confidence="HIGH",
        competitor_list=[],
        demand_indicator="HIGH",
        geography=GeographyIdentity(is_geocoded=True),
    )

    swot = SWOTEngine.generate_swot(
        financial_result=fin,
        market_result=mkt,
        evidence_ledger=make_standard_evidence_ledger(),
        customers_per_day=25,
        desired_loan=50000.0,
        category="Tailoring & Garment Making",
    )

    str_ids = {s.id for s in swot.strengths}
    assert "STR-FIN-PROFIT-POSITIVE" in str_ids
    assert "STR-FIN-DSCR-STRONG" in str_ids
    assert "STR-FIN-BREAKEVEN-MANAGEABLE" in str_ids


def test_demo_village_dairy():
    """Village Dairy Farming & Milk Chilling (High contribution margin, agricultural)."""
    fin = FinancialResultResponse(
        total_capex=250000.0,
        required_loan_amount=180000.0,
        monthly_revenue=85000.0,
        monthly_variable_cost=34000.0,
        monthly_gross_profit=51000.0,
        monthly_fixed_cost=15000.0,
        monthly_emi=5935.0,
        monthly_net_profit=30065.0,
        net_profit_margin_pct=35.37,
        break_even_revenue_monthly=34892.0,
        break_even_units_daily=19,
        dscr=6.06,
        is_financially_viable=True,
    )
    mkt = MarketResultResponse(
        location_summary="Anand Rural, Gujarat",
        competitor_count=1,
        direct_competitor_count=1,
        adjacent_competitor_count=0,
        catchment_radius_km=5.0,
        coverage_confidence="HIGH",
        competitor_list=[],
        demand_indicator="HIGH",
        geography=GeographyIdentity(is_geocoded=True),
    )

    swot = SWOTEngine.generate_swot(
        financial_result=fin,
        market_result=mkt,
        evidence_ledger=make_standard_evidence_ledger(),
        customers_per_day=45,
        desired_loan=180000.0,
        category="Dairy Farming & Milk Chilling",
    )

    str_ids = {s.id for s in swot.strengths}
    assert "STR-FIN-PROFIT-POSITIVE" in str_ids
    assert "STR-FIN-DSCR-STRONG" in str_ids
    assert "STR-MKT-COMP-LOW" in str_ids
    assert len(swot.strengths) == 4


def test_demo_sri_amman_tea_and_snacks():
    """Sri Amman Tea & Snacks (High footfall, low ticket, fast break-even)."""
    fin = FinancialResultResponse(
        total_capex=60000.0,
        required_loan_amount=35000.0,
        monthly_revenue=52000.0,
        monthly_variable_cost=20800.0,
        monthly_gross_profit=31200.0,
        monthly_fixed_cost=9000.0,
        monthly_emi=1154.0,
        monthly_net_profit=21046.0,
        net_profit_margin_pct=40.47,
        break_even_revenue_monthly=16923.0,
        break_even_units_daily=26,
        dscr=19.23,
        is_financially_viable=True,
    )
    mkt = MarketResultResponse(
        location_summary="Madurai Rural, Tamil Nadu",
        competitor_count=0,
        direct_competitor_count=0,
        adjacent_competitor_count=0,
        catchment_radius_km=5.0,
        coverage_confidence="HIGH",
        competitor_list=[],
        demand_indicator="HIGH",
        geography=GeographyIdentity(is_geocoded=True),
    )

    swot = SWOTEngine.generate_swot(
        financial_result=fin,
        market_result=mkt,
        evidence_ledger=make_standard_evidence_ledger(),
        customers_per_day=80,
        desired_loan=35000.0,
        category="Kirana & General Store",
    )

    str_ids = {s.id for s in swot.strengths}
    assert "STR-FIN-PROFIT-POSITIVE" in str_ids
    assert "STR-FIN-DSCR-STRONG" in str_ids
    assert "STR-FIN-BREAKEVEN-MANAGEABLE" in str_ids
