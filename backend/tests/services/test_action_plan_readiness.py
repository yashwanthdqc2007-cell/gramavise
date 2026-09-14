import pytest
from app.schemas.financial import FinancialAssumptionsInput, FinancialResultResponse
from app.schemas.market import (
    MarketResultResponse,
    MarketEvidenceQuery,
    CoverageConfidenceLevel
)
from app.schemas.analysis import (
    RecommendationStatus,
    RuleEvaluation,
    DecisionTrace,
    VerificationCheckItem,
    AnalysisRequest,
    AnalysisResultResponse
)
from app.schemas.scheme import SchemeMatchResult, MatchedSchemeDetail
from app.schemas.business import BusinessProfileBase, LocationSchema
from app.schemas.evidence import EvidenceType, EvidenceItem
from app.schemas.action_plan import (
    ActionPriority,
    ActionCategory,
    ActionStatus,
    ActionSource,
    ActionItem,
    ActionPlan,
    DocumentStatus,
    DocumentItem,
    DocumentReadiness,
    ReadinessStatus,
    BankReadinessCategory,
    BankReadiness
)
from app.services.financial.calculator import FinancialService
from app.services.geo.market import MockMarketService
from app.services.schemes.matcher import SchemeService
from app.services.evidence.collector import EvidenceCollector
from app.rules.feasibility_rules import FeasibilityRules
from app.services.recommendation.action_plan import ActionPlanGenerator


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


# 1. Test PROCEED Action Plan
def test_action_plan_proceed(financial_service, market_service, valid_assumptions):
    fin = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_assumptions)
    query = MarketEvidenceQuery(state="Maharashtra", district="Pune", village="Baramati", category="Bakery & Snacks", latitude=18.155, longitude=74.578)
    market = market_service.get_market_indicators(query)
    scheme_res = SchemeMatchResult(eligible_schemes_count=1, schemes=[
        MatchedSchemeDetail(
            scheme_code="PMEGP",
            scheme_name="Prime Minister's Employment Generation Programme",
            subsidy_eligible_amount=35000.0,
            own_contribution_required=15000.0,
            max_bank_loan=100000.0,
            eligibility_status="ELIGIBLE",
            conditions_to_verify=["EDP training certificate required prior to subsidy disbursement."]
        )
    ])
    evidence_ledger = [
        EvidenceItem(evidence_id="EV-FIN-SURPLUS", indicator="Surplus", value="15000", evidence_type=EvidenceType.CALCULATED, confidence=1.0),
        EvidenceItem(evidence_id="EV-SCHEME-PMEGP", indicator="PMEGP", value="ELIGIBLE", evidence_type=EvidenceType.OBSERVED, confidence=0.95)
    ]
    
    action_plan = ActionPlanGenerator.generate_action_plan(
        recommendation_status=RecommendationStatus.PROCEED,
        financial_result=fin,
        market_result=market,
        scheme_result=scheme_res,
        evidence_ledger=evidence_ledger,
        customers_per_day=50
    )
    
    assert action_plan.recommendation_status == RecommendationStatus.PROCEED
    assert action_plan.total_actions >= 2
    action_ids = [a.action_id for a in action_plan.actions]
    assert "ACT-CAP-001" in action_ids
    assert "ACT-SCH-001" in action_ids
    
    # Confirm capital structure action mentions calculated amounts
    cap_act = next(a for a in action_plan.actions if a.action_id == "ACT-CAP-001")
    assert f"{fin.total_capex:,.2f}" in cap_act.description
    assert cap_act.action_source == ActionSource.FINANCIAL_RESULT


# 2. Test VALIDATE_FIRST Action Plan
def test_action_plan_validate_first(financial_service, valid_assumptions):
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
        location_summary="Remote Village",
        competitor_count=0,
        direct_competitor_count=0,
        coverage_confidence="LOW",
        demand_indicator="MEDIUM"
    )
    scheme_res = SchemeMatchResult(eligible_schemes_count=0, schemes=[])
    evidence_ledger = [
        EvidenceItem(evidence_id="EV-USER-CUSTOMERS", indicator="Customers", value="45", evidence_type=EvidenceType.ASSUMED, confidence=0.75),
        EvidenceItem(evidence_id="EV-MKT-COMPETITORS", indicator="Competitors", value="0", evidence_type=EvidenceType.NEEDS_VERIFICATION, confidence=0.5),
        EvidenceItem(evidence_id="EV-PRICE-BENCH-1", indicator="Mandi Price Benchmark", value="₹2,500/qtl", evidence_type=EvidenceType.OBSERVED, source="Agmarknet", confidence=0.9)
    ]
    
    action_plan = ActionPlanGenerator.generate_action_plan(
        recommendation_status=RecommendationStatus.VALIDATE_FIRST,
        financial_result=fin,
        market_result=market,
        scheme_result=scheme_res,
        evidence_ledger=evidence_ledger,
        customers_per_day=45
    )
    
    assert action_plan.recommendation_status == RecommendationStatus.VALIDATE_FIRST
    action_ids = [a.action_id for a in action_plan.actions]
    assert "ACT-ASM-001" in action_ids  # Customer volume validation
    assert "ACT-MKT-001" in action_ids  # Competitor walk
    assert "ACT-PRC-001" in action_ids  # Retail vs wholesale price confirmation
    assert "ACT-RECALC-001" in action_ids  # Re-run analysis


# 3. Test RECONSIDER Action Plan (Neutral improvement options, no moratorium)
def test_action_plan_reconsider(financial_service):
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
    scheme_res = SchemeMatchResult(eligible_schemes_count=0, schemes=[])
    evidence_ledger = [
        EvidenceItem(evidence_id="EV-FIN-SURPLUS", indicator="Surplus", value="-15000", evidence_type=EvidenceType.CALCULATED, confidence=1.0),
        EvidenceItem(evidence_id="EV-FIN-BREAKEVEN", indicator="Break-Even", value="45 orders/day", evidence_type=EvidenceType.CALCULATED, confidence=1.0)
    ]
    
    action_plan = ActionPlanGenerator.generate_action_plan(
        recommendation_status=RecommendationStatus.RECONSIDER,
        financial_result=fin,
        market_result=market,
        scheme_result=scheme_res,
        evidence_ledger=evidence_ledger,
        customers_per_day=10
    )
    
    assert action_plan.recommendation_status == RecommendationStatus.RECONSIDER
    action_ids = [a.action_id for a in action_plan.actions]
    assert "ACT-FIN-REWORK-001" in action_ids
    assert "ACT-CAP-REVISE-001" in action_ids
    
    # Confirm no loan moratorium is mentioned anywhere
    full_text = " ".join([a.title + " " + a.description for a in action_plan.actions])
    assert "moratorium" not in full_text.lower()
    assert "smaller financing" in full_text.lower() or "revised repayment" in full_text.lower()


# 4. Test Negative Profit Action Trigger
def test_negative_profit_action(financial_service):
    deficit_assumptions = FinancialAssumptionsInput(
        startup_cost=50000.0, equipment_cost=200000.0, inventory_cost=50000.0,
        monthly_fixed_cost=25000.0, variable_cost_pct=60.0, avg_ticket_price=20.0,
        customers_per_day=10, working_days_per_month=26, interest_rate_pct=12.0, loan_tenure_months=36
    )
    fin = financial_service.calculate(own_capital=50000.0, desired_loan=250000.0, financials=deficit_assumptions)
    market = MarketResultResponse(location_summary="Test Village", competitor_count=0, demand_indicator="LOW")
    
    action_plan = ActionPlanGenerator.generate_action_plan(
        recommendation_status=RecommendationStatus.RECONSIDER,
        financial_result=fin,
        market_result=market,
        scheme_result=SchemeMatchResult(eligible_schemes_count=0, schemes=[]),
        evidence_ledger=[]
    )
    
    rework_act = next(a for a in action_plan.actions if a.action_id == "ACT-FIN-REWORK-001")
    assert rework_act.priority == ActionPriority.CRITICAL
    assert rework_act.category == ActionCategory.FINANCIAL
    assert rework_act.action_source == ActionSource.DECISION_TRACE


# 5. Test Weak DSCR Action Trigger
def test_weak_dscr_action(financial_service, valid_assumptions):
    tight_assumptions = FinancialAssumptionsInput(
        startup_cost=25000.0, equipment_cost=100000.0, inventory_cost=25000.0,
        monthly_fixed_cost=12000.0, variable_cost_pct=50.0, avg_ticket_price=30.0,
        customers_per_day=45, working_days_per_month=26, interest_rate_pct=11.0, loan_tenure_months=36
    )
    fin = financial_service.calculate(own_capital=30000.0, desired_loan=120000.0, financials=tight_assumptions)
    market = MarketResultResponse(location_summary="Test Village", competitor_count=1, demand_indicator="MEDIUM")
    
    action_plan = ActionPlanGenerator.generate_action_plan(
        recommendation_status=RecommendationStatus.VALIDATE_FIRST,
        financial_result=fin,
        market_result=market,
        scheme_result=SchemeMatchResult(eligible_schemes_count=0, schemes=[]),
        evidence_ledger=[]
    )
    
    dscr_act = next((a for a in action_plan.actions if a.action_id == "ACT-FIN-003"), None)
    assert dscr_act is not None
    assert "DSCR" in dscr_act.description
    assert dscr_act.related_rule_ids == ["STRONG_REPAYMENT_CAPACITY"]


# 6. Test Assumed Customer Volume Action
def test_assumed_customer_volume_action(financial_service, valid_assumptions):
    fin = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_assumptions)
    market = MarketResultResponse(location_summary="Village", competitor_count=1, demand_indicator="MEDIUM")
    evidence_ledger = [
        EvidenceItem(evidence_id="EV-USER-CUSTOMERS", indicator="Customers", value="50", evidence_type=EvidenceType.ASSUMED, confidence=0.75)
    ]
    
    action_plan = ActionPlanGenerator.generate_action_plan(
        recommendation_status=RecommendationStatus.VALIDATE_FIRST,
        financial_result=fin,
        market_result=market,
        scheme_result=SchemeMatchResult(eligible_schemes_count=0, schemes=[]),
        evidence_ledger=evidence_ledger,
        customers_per_day=50
    )
    
    cust_act = next(a for a in action_plan.actions if a.action_id == "ACT-ASM-001")
    assert cust_act.category == ActionCategory.VALIDATION
    assert cust_act.action_source == ActionSource.EVIDENCE_LEDGER
    assert cust_act.related_evidence_ids == ["EV-USER-CUSTOMERS"]


# 7. Test Market Verification Action on 0 Mapped Competitors
def test_market_verification_action(financial_service, valid_assumptions):
    fin = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_assumptions)
    market = MarketResultResponse(location_summary="Village", competitor_count=0, direct_competitor_count=0, demand_indicator="MEDIUM")
    evidence_ledger = [
        EvidenceItem(evidence_id="EV-MKT-COMPETITORS", indicator="Competitors", value="0", evidence_type=EvidenceType.NEEDS_VERIFICATION, confidence=0.5)
    ]
    
    action_plan = ActionPlanGenerator.generate_action_plan(
        recommendation_status=RecommendationStatus.VALIDATE_FIRST,
        financial_result=fin,
        market_result=market,
        scheme_result=SchemeMatchResult(eligible_schemes_count=0, schemes=[]),
        evidence_ledger=evidence_ledger
    )
    
    mkt_act = next(a for a in action_plan.actions if a.action_id == "ACT-MKT-001")
    assert mkt_act.category == ActionCategory.MARKET
    assert mkt_act.action_source == ActionSource.MARKET_RESULT
    assert "competitor walk" in mkt_act.title.lower()


# 8. Test Price Validation Action
def test_price_validation_action(financial_service, valid_assumptions):
    fin = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_assumptions)
    market = MarketResultResponse(location_summary="Village", competitor_count=1, demand_indicator="MEDIUM")
    evidence_ledger = [
        EvidenceItem(evidence_id="EV-PRICE-BENCH-1", indicator="Mandi Wholesale Benchmark", value="₹3,200/qtl", evidence_type=EvidenceType.OBSERVED, source="Agmarknet", confidence=0.95)
    ]
    
    action_plan = ActionPlanGenerator.generate_action_plan(
        recommendation_status=RecommendationStatus.VALIDATE_FIRST,
        financial_result=fin,
        market_result=market,
        scheme_result=SchemeMatchResult(eligible_schemes_count=0, schemes=[]),
        evidence_ledger=evidence_ledger
    )
    
    prc_act = next(a for a in action_plan.actions if a.action_id == "ACT-PRC-001")
    assert prc_act.category == ActionCategory.VALIDATION
    assert "retail vs wholesale" in prc_act.title.lower() or "selling price" in prc_act.title.lower()


# 9. Test Scheme-Supported Document Readiness (No Universal Lists)
def test_no_unsupported_document_requirements():
    scheme_res = SchemeMatchResult(eligible_schemes_count=1, schemes=[
        MatchedSchemeDetail(
            scheme_code="PMEGP",
            scheme_name="Prime Minister's Employment Generation Programme",
            subsidy_eligible_amount=35000.0,
            own_contribution_required=15000.0,
            max_bank_loan=100000.0,
            eligibility_status="ELIGIBLE",
            conditions_to_verify=[
                "EDP training certificate required prior to subsidy disbursement.",
                "Special category caste certificate required for 35% margin subsidy."
            ]
        )
    ])
    
    doc_readiness = ActionPlanGenerator.generate_document_readiness(scheme_res)
    assert len(doc_readiness.documents) == 2
    assert all(d.status in (DocumentStatus.VERIFY, DocumentStatus.REQUIRED) for d in doc_readiness.documents)
    assert all(d.required_for == "Prime Minister's Employment Generation Programme" for d in doc_readiness.documents)
    
    # Empty schemes produce 0 document requirements (no universal checklist invented)
    empty_res = SchemeMatchResult(eligible_schemes_count=0, schemes=[])
    empty_docs = ActionPlanGenerator.generate_document_readiness(empty_res)
    assert len(empty_docs.documents) == 0


# 10. Test No Generic Actions Without Supporting Conditions
def test_no_generic_actions_without_supporting_conditions(financial_service, valid_assumptions):
    fin = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_assumptions)
    market = MarketResultResponse(location_summary="Village", competitor_count=2, direct_competitor_count=2, coverage_confidence="HIGH", demand_indicator="HIGH")
    # Empty schemes and clean evidence
    action_plan = ActionPlanGenerator.generate_action_plan(
        recommendation_status=RecommendationStatus.PROCEED,
        financial_result=fin,
        market_result=market,
        scheme_result=SchemeMatchResult(eligible_schemes_count=0, schemes=[]),
        evidence_ledger=[]
    )
    
    # Should not generate competitor walk or customer volume validation for clean PROCEED
    action_ids = [a.action_id for a in action_plan.actions]
    assert "ACT-MKT-001" not in action_ids
    assert "ACT-ASM-001" not in action_ids


# 11. Test Action Traceability and ActionSource
def test_action_traceability_and_source(financial_service, valid_assumptions):
    fin = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_assumptions)
    market = MarketResultResponse(location_summary="Village", competitor_count=0, direct_competitor_count=0, demand_indicator="MEDIUM")
    evidence_ledger = [
        EvidenceItem(evidence_id="EV-USER-CUSTOMERS", indicator="Customers", value="50", evidence_type=EvidenceType.ASSUMED, confidence=0.75),
        EvidenceItem(evidence_id="EV-MKT-COMPETITORS", indicator="Competitors", value="0", evidence_type=EvidenceType.NEEDS_VERIFICATION, confidence=0.5)
    ]
    
    action_plan = ActionPlanGenerator.generate_action_plan(
        recommendation_status=RecommendationStatus.VALIDATE_FIRST,
        financial_result=fin,
        market_result=market,
        scheme_result=SchemeMatchResult(eligible_schemes_count=0, schemes=[]),
        evidence_ledger=evidence_ledger
    )
    
    for action in action_plan.actions:
        assert isinstance(action.action_source, ActionSource)
        assert len(action.reason) > 10
        assert action.priority in (ActionPriority.CRITICAL, ActionPriority.HIGH, ActionPriority.MEDIUM, ActionPriority.LOW)


# 12. Test Deterministic Bank-Readiness Classification Across All 5 Categories
def test_bank_readiness_deterministic_classification(financial_service, valid_assumptions):
    fin = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_assumptions)
    market = MarketResultResponse(location_summary="Village", competitor_count=3, direct_competitor_count=3, coverage_confidence="HIGH", demand_indicator="HIGH")
    scheme_res = SchemeMatchResult(eligible_schemes_count=1, schemes=[
        MatchedSchemeDetail(
            scheme_code="PMMY",
            scheme_name="Pradhan Mantri Mudra Yojana",
            subsidy_eligible_amount=0.0,
            own_contribution_required=15000.0,
            max_bank_loan=100000.0,
            eligibility_status="ELIGIBLE",
            conditions_to_verify=[]
        )
    ])
    evidence_ledger = [
        EvidenceItem(evidence_id="EV-FIN-SURPLUS", indicator="Surplus", value="15000", evidence_type=EvidenceType.CALCULATED, confidence=1.0),
        EvidenceItem(evidence_id="EV-MKT-COMPETITORS", indicator="Competitors", value="3", evidence_type=EvidenceType.OBSERVED, confidence=1.0),
        EvidenceItem(evidence_id="EV-SCHEME-PMMY", indicator="Mudra", value="ELIGIBLE", evidence_type=EvidenceType.OBSERVED, confidence=0.95)
    ]
    
    action_plan = ActionPlanGenerator.generate_action_plan(
        recommendation_status=RecommendationStatus.PROCEED,
        financial_result=fin,
        market_result=market,
        scheme_result=scheme_res,
        evidence_ledger=evidence_ledger
    )
    doc_readiness = ActionPlanGenerator.generate_document_readiness(scheme_res)
    bank_readiness = ActionPlanGenerator.generate_bank_readiness(
        recommendation_status=RecommendationStatus.PROCEED,
        financial_result=fin,
        market_result=market,
        scheme_result=scheme_res,
        evidence_ledger=evidence_ledger,
        action_plan=action_plan,
        document_readiness=doc_readiness
    )
    
    cat_map = {c.category: c.status for c in bank_readiness.categories}
    assert cat_map["FINANCIAL_CASE"] == ReadinessStatus.READY
    assert cat_map["MARKET_EVIDENCE"] == ReadinessStatus.READY
    assert cat_map["SCHEME_FIT"] == ReadinessStatus.READY
    assert bank_readiness.overall_status == ReadinessStatus.READY
    assert len(bank_readiness.top_actions) <= 3


# 13. Test Absence of Fake Loan Approval Probability or Credit Scores
def test_no_fake_loan_approval_probability(financial_service, valid_assumptions):
    fin = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_assumptions)
    market = MarketResultResponse(location_summary="Village", competitor_count=1, demand_indicator="MEDIUM")
    action_plan = ActionPlanGenerator.generate_action_plan(
        recommendation_status=RecommendationStatus.PROCEED,
        financial_result=fin,
        market_result=market,
        scheme_result=SchemeMatchResult(eligible_schemes_count=0, schemes=[]),
        evidence_ledger=[]
    )
    doc_readiness = ActionPlanGenerator.generate_document_readiness(SchemeMatchResult(eligible_schemes_count=0, schemes=[]))
    bank_readiness = ActionPlanGenerator.generate_bank_readiness(
        recommendation_status=RecommendationStatus.PROCEED,
        financial_result=fin,
        market_result=market,
        scheme_result=SchemeMatchResult(eligible_schemes_count=0, schemes=[]),
        evidence_ledger=[],
        action_plan=action_plan,
        document_readiness=doc_readiness
    )
    
    # Assert no numeric probability percentages or credit scores in schemas
    assert not hasattr(bank_readiness, "approval_probability")
    assert not hasattr(bank_readiness, "credit_score")
    assert not hasattr(bank_readiness, "success_chance")
    assert "NOT a credit score, loan approval guarantee" in bank_readiness.disclaimer


# 14. Test Action Completion Does Not Mutate Analysis or Financials
def test_action_completion_does_not_mutate_analysis(financial_service, valid_assumptions):
    fin1 = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_assumptions)
    market = MarketResultResponse(location_summary="Village", competitor_count=1, demand_indicator="MEDIUM")
    action_plan = ActionPlanGenerator.generate_action_plan(
        recommendation_status=RecommendationStatus.PROCEED,
        financial_result=fin1,
        market_result=market,
        scheme_result=SchemeMatchResult(eligible_schemes_count=0, schemes=[]),
        evidence_ledger=[]
    )
    
    # Mark first action completed
    assert len(action_plan.actions) > 0
    action_plan.actions[0].status = ActionStatus.COMPLETED
    
    # Financial engine remains completely isolated and invariant
    fin2 = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_assumptions)
    assert fin1.monthly_net_profit == fin2.monthly_net_profit
    assert fin1.dscr == fin2.dscr


# 15. Test Deterministic Repeatability of Action Plan and Readiness
def test_deterministic_action_plan_repeatability(financial_service, valid_assumptions):
    fin = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_assumptions)
    market = MarketResultResponse(location_summary="Village", competitor_count=1, demand_indicator="MEDIUM")
    scheme_res = SchemeMatchResult(eligible_schemes_count=0, schemes=[])
    
    ap1 = ActionPlanGenerator.generate_action_plan(RecommendationStatus.PROCEED, fin, market, scheme_res, [])
    ap2 = ActionPlanGenerator.generate_action_plan(RecommendationStatus.PROCEED, fin, market, scheme_res, [])
    
    assert len(ap1.actions) == len(ap2.actions)
    for a1, a2 in zip(ap1.actions, ap2.actions):
        assert a1.action_id == a2.action_id
        assert a1.priority == a2.priority
        assert a1.title == a2.title
        assert a1.action_source == a2.action_source
