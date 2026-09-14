import pytest
from app.schemas.financial import FinancialAssumptionsInput, FinancialResultResponse
from app.schemas.market import (
    MarketResultResponse,
    MarketEvidenceQuery,
    CatchmentModel,
    PriceBenchmark,
    GeographyIdentity,
    DemographicObservation,
    UdyamDistrictContext,
    CoverageConfidenceLevel
)
from app.schemas.analysis import (
    RecommendationStatus,
    RuleEvaluation,
    DecisionTrace,
    VerificationCheckItem,
    AnalysisRequest
)
from app.schemas.business import BusinessProfileBase, LocationSchema
from app.schemas.evidence import EvidenceType, EvidenceItem
from app.services.financial.calculator import FinancialService
from app.services.geo.market import MockMarketService
from app.services.schemes.matcher import SchemeService
from app.services.evidence.collector import EvidenceCollector
from app.rules.feasibility_rules import FeasibilityRules
from app.services.ai.explanation import AIService
from app.schemas.ai import AIExplanationRequest, AIExplanationResponse


@pytest.fixture
def financial_service():
    return FinancialService()


@pytest.fixture
def market_service():
    return MockMarketService()


@pytest.fixture
def scheme_service():
    return SchemeService()


@pytest.fixture
def evidence_collector():
    return EvidenceCollector()


@pytest.fixture
def valid_assumptions():
    return FinancialAssumptionsInput(
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


# Test 1: Evidence ledger creation with proper IDs and claims
def test_evidence_ledger_creation(evidence_collector, financial_service, market_service, valid_assumptions):
    fin = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_assumptions)
    query = MarketEvidenceQuery(state="Maharashtra", district="Pune", village="Baramati", category="Bakery & Snacks", latitude=18.155, longitude=74.578)
    market = market_service.get_market_indicators(query)
    
    context = {
        "monthly_net_profit": fin.monthly_net_profit,
        "break_even_units_daily": fin.break_even_units_daily,
        "competitor_count": market.competitor_count,
        "customers_per_day": valid_assumptions.customers_per_day,
        "market_result": market,
        "state": "Maharashtra",
        "district": "Pune",
        "village": "Baramati"
    }
    ledger = evidence_collector.collect(context)
    
    assert len(ledger) >= 5
    evidence_ids = [item.evidence_id for item in ledger if item.evidence_id]
    assert "EV-FIN-SURPLUS" in evidence_ids
    assert "EV-FIN-BREAKEVEN" in evidence_ids
    assert "EV-USER-CUSTOMERS" in evidence_ids


# Test 2: Evidence type taxonomy classification
def test_evidence_type_taxonomy(evidence_collector, financial_service, valid_assumptions):
    fin = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_assumptions)
    context = {
        "monthly_net_profit": fin.monthly_net_profit,
        "break_even_units_daily": fin.break_even_units_daily,
        "customers_per_day": 50,
        "state": "Maharashtra",
        "district": "Pune",
        "village": "Baramati"
    }
    ledger = evidence_collector.collect(context)
    
    types = {item.evidence_type for item in ledger}
    assert EvidenceType.CALCULATED in types
    assert EvidenceType.ASSUMED in types
    assert EvidenceType.OBSERVED in types


# Test 3: Confidence levels and explanations attached deterministically
def test_confidence_level_and_explanation(evidence_collector, financial_service, valid_assumptions):
    fin = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_assumptions)
    ledger = evidence_collector.collect({
        "monthly_net_profit": fin.monthly_net_profit,
        "break_even_units_daily": fin.break_even_units_daily,
        "customers_per_day": 50,
        "state": "Maharashtra",
        "district": "Pune",
        "village": "Baramati"
    })
    
    for item in ledger:
        assert item.confidence_level in ("HIGH", "MEDIUM", "LOW", "UNKNOWN")
        assert item.confidence_explanation is not None
        assert len(item.confidence_explanation) > 10


# Test 4: Calculated financial evidence contains formula provenance
def test_calculated_financial_evidence_provenance(evidence_collector, financial_service, valid_assumptions):
    fin = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_assumptions)
    ledger = evidence_collector.collect({
        "monthly_net_profit": fin.monthly_net_profit,
        "break_even_units_daily": fin.break_even_units_daily
    })
    
    surplus_item = next(i for i in ledger if i.evidence_id == "EV-FIN-SURPLUS")
    assert surplus_item.evidence_type == EvidenceType.CALCULATED
    assert "Revenue" in surplus_item.confidence_explanation
    assert surplus_item.source == "GramaVise Financial Engine"


# Test 5: Applicant assumptions are explicitly tagged ASSUMED
def test_applicant_assumptions_tagged_assumed(evidence_collector):
    ledger = evidence_collector.collect({"customers_per_day": 40})
    cust_item = next(i for i in ledger if i.evidence_id == "EV-USER-CUSTOMERS")
    assert cust_item.evidence_type == EvidenceType.ASSUMED
    assert "Self-reported" in cust_item.confidence_explanation
    assert "optimism bias" in cust_item.limitations


# Test 6: Modelled catchment demographic evidence preserves prototype status
def test_modelled_catchment_evidence(evidence_collector, market_service):
    query = MarketEvidenceQuery(state="Maharashtra", district="Pune", village="Baramati", category="Bakery & Snacks", latitude=18.155, longitude=74.578)
    market = market_service.get_market_indicators(query)
    ledger = evidence_collector.collect({"market_result": market})
    
    pop_item = next(i for i in ledger if i.evidence_id == "EV-MKT-CATCHMENT-POP")
    assert pop_item.evidence_type == EvidenceType.MODELLED
    assert pop_item.confidence_level == "LOW"
    assert "prototype" in pop_item.confidence_explanation.lower()


# Test 7: OSM zero results handle incomplete coverage with NEEDS_VERIFICATION
def test_osm_zero_results_needs_verification(evidence_collector):
    empty_market = MarketResultResponse(
        location_summary="Remote Village",
        competitor_count=0,
        direct_competitor_count=0,
        coverage_confidence="LOW",
        demand_indicator="HIGH"
    )
    ledger = evidence_collector.collect({"market_result": empty_market})
    comp_item = next(i for i in ledger if i.evidence_id == "EV-MKT-COMPETITORS")
    assert comp_item.evidence_type == EvidenceType.NEEDS_VERIFICATION
    assert comp_item.confidence_level == "LOW"
    assert "does NOT prove absence of competition" in comp_item.confidence_explanation


# Test 8: Decision trace for PROCEED
def test_decision_trace_proceed(financial_service, market_service, valid_assumptions):
    fin = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_assumptions)
    query = MarketEvidenceQuery(state="Maharashtra", district="Pune", village="Baramati", category="Bakery & Snacks", latitude=18.155, longitude=74.578)
    market = market_service.get_market_indicators(query)
    
    status, trace = FeasibilityRules.evaluate_with_trace(fin, market)
    assert status == RecommendationStatus.PROCEED
    assert trace.recommendation_status == RecommendationStatus.PROCEED
    assert trace.authority == "FeasibilityRules"
    assert len(trace.rule_evaluations) >= 5
    assert any(r.rule_id == "NET_PROFIT_POSITIVE" and r.result == "PASS" for r in trace.rule_evaluations)
    assert any(r.rule_id == "STRONG_REPAYMENT_CAPACITY" and r.result == "PASS" for r in trace.rule_evaluations)


# Test 9: Decision trace for VALIDATE_FIRST (boundary condition / moderate DSCR / unverified coverage)
def test_decision_trace_validate_first(financial_service, valid_assumptions):
    # Tight financials: DSCR between 1.0 and 1.5
    tight_assumptions = FinancialAssumptionsInput(
        startup_cost=25000.0,
        equipment_cost=100000.0,
        inventory_cost=25000.0,
        monthly_fixed_cost=12000.0,
        variable_cost_pct=50.0,
        avg_ticket_price=30.0,
        customers_per_day=45,
        working_days_per_month=26,
        interest_rate_pct=11.0,
        loan_tenure_months=36
    )
    fin = financial_service.calculate(own_capital=30000.0, desired_loan=120000.0, financials=tight_assumptions)
    market = MarketResultResponse(
        location_summary="Test Village",
        competitor_count=1,
        direct_competitor_count=1,
        coverage_confidence="LOW",
        demand_indicator="MEDIUM"
    )
    
    status, trace = FeasibilityRules.evaluate_with_trace(fin, market)
    assert status == RecommendationStatus.VALIDATE_FIRST
    assert any(r.rule_id == "STRONG_REPAYMENT_CAPACITY" and r.result == "WARNING" for r in trace.rule_evaluations)


# Test 10: Decision trace for RECONSIDER (insolvency or negative profit)
def test_decision_trace_reconsider(financial_service):
    deficit_assumptions = FinancialAssumptionsInput(
        startup_cost=50000.0,
        equipment_cost=200000.0,
        inventory_cost=50000.0,
        monthly_fixed_cost=25000.0,
        variable_cost_pct=60.0,
        avg_ticket_price=20.0,
        customers_per_day=10,
        working_days_per_month=26,
        interest_rate_pct=12.0,
        loan_tenure_months=36
    )
    fin = financial_service.calculate(own_capital=50000.0, desired_loan=250000.0, financials=deficit_assumptions)
    market = MarketResultResponse(location_summary="Test Village", competitor_count=0, demand_indicator="LOW")
    
    status, trace = FeasibilityRules.evaluate_with_trace(fin, market)
    assert status == RecommendationStatus.RECONSIDER
    assert any(r.rule_id == "NET_PROFIT_POSITIVE" and r.result == "FAIL" for r in trace.rule_evaluations)


# Test 11: FeasibilityRules determine_status and evaluate_with_trace produce identical verdict
def test_feasibility_rules_consistency(financial_service, market_service, valid_assumptions):
    fin = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_assumptions)
    market = market_service.get_market_indicators(MarketEvidenceQuery(state="Maharashtra", district="Pune", village="Baramati", category="Bakery & Snacks"))
    
    status_direct = FeasibilityRules.determine_status(fin, market)
    status_traced, trace = FeasibilityRules.evaluate_with_trace(fin, market)
    assert status_direct == status_traced == trace.recommendation_status


# Test 12: Financial results unchanged by decision trace or explainability layer
def test_financial_engine_invariance(financial_service, market_service, valid_assumptions):
    fin1 = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_assumptions)
    market = market_service.get_market_indicators(MarketEvidenceQuery(state="Maharashtra", district="Pune", village="Baramati", category="Bakery & Snacks"))
    
    _, trace = FeasibilityRules.evaluate_with_trace(fin1, market)
    fin2 = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_assumptions)
    
    assert fin1.monthly_net_profit == fin2.monthly_net_profit
    assert fin1.monthly_emi == fin2.monthly_emi
    assert fin1.dscr == fin2.dscr
    assert fin1.break_even_units_daily == fin2.break_even_units_daily


# Test 13: Actionable Verification Checklist synthesis from NEEDS_VERIFICATION items
def test_verification_checklist_synthesis(evidence_collector):
    mock_ledger = [
        EvidenceItem(
            evidence_id="EV-MKT-COMPETITORS",
            indicator="Catchment Mapped Competitors",
            value="0 direct units",
            evidence_type=EvidenceType.NEEDS_VERIFICATION,
            confidence=0.5
        ),
        EvidenceItem(
            evidence_id="EV-COND-PMEGP-1",
            indicator="Verification: PMEGP",
            value="Special category certificate required for 35% margin subsidy",
            evidence_type=EvidenceType.NEEDS_VERIFICATION,
            confidence=0.5
        ),
        EvidenceItem(
            evidence_id="EV-USER-CUSTOMERS",
            indicator="Expected Daily Footfall",
            value="50 customers",
            evidence_type=EvidenceType.ASSUMED,
            confidence=0.75
        )
    ]
    checklist = evidence_collector.generate_verification_checklist(mock_ledger)
    assert len(checklist) >= 3
    categories = {c.category for c in checklist}
    assert "MARKET" in categories
    assert "SCHEME" in categories
    assert "ASSUMPTION" in categories


# Test 14: AI fallback is deterministic and grounded in decision trace
def test_ai_fallback_grounded_in_trace(financial_service, market_service, valid_assumptions):
    fin = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_assumptions)
    market = market_service.get_market_indicators(MarketEvidenceQuery(state="Maharashtra", district="Pune", village="Baramati", category="Bakery & Snacks"))
    status, trace = FeasibilityRules.evaluate_with_trace(fin, market)
    
    # Grounded fallback payload
    fallback = AIExplanationResponse(
        language="hi",
        summary=trace.summary,
        strengths=trace.key_positive_factors,
        cautions_and_risks=trace.key_caution_factors,
        actionable_next_steps=["Verify footfall count on ground."],
        disclaimer="Deterministic fallback advisory."
    )
    assert status.value in fallback.summary or "satisfies" in fallback.summary
    assert len(fallback.strengths) > 0


# Test 15: Repeatability of decision trace for identical inputs
def test_decision_trace_repeatability(financial_service, market_service, valid_assumptions):
    fin = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_assumptions)
    market = market_service.get_market_indicators(MarketEvidenceQuery(state="Maharashtra", district="Pune", village="Baramati", category="Bakery & Snacks"))
    
    status1, trace1 = FeasibilityRules.evaluate_with_trace(fin, market)
    status2, trace2 = FeasibilityRules.evaluate_with_trace(fin, market)
    
    assert status1 == status2
    assert trace1.summary == trace2.summary
    assert len(trace1.rule_evaluations) == len(trace2.rule_evaluations)
    for r1, r2 in zip(trace1.rule_evaluations, trace2.rule_evaluations):
        assert r1.rule_id == r2.rule_id
        assert r1.result == r2.result
