import pytest
from app.schemas.financial import (
    FinancialAssumptionsInput,
    FinancialResultResponse,
    FinancialCalculationRequest
)
from app.schemas.market import MarketResultResponse, CoverageConfidenceLevel
from app.schemas.analysis import RecommendationStatus, DecisionTrace
from app.schemas.scenario import (
    ComparisonDirection,
    MetricComparison,
    RuleComparison,
    RecommendationChange,
    ScenarioEvaluationRequest,
    ScenarioEvaluationResponse
)
from app.services.financial.calculator import FinancialService
from app.services.financial.sensitivity import run_sensitivity_analysis
from app.rules.feasibility_rules import FeasibilityRules
from app.services.recommendation.scenario_comparator import ScenarioComparator


@pytest.fixture
def financial_service():
    return FinancialService()


@pytest.fixture
def scenario_comparator(financial_service):
    return ScenarioComparator(financial_service=financial_service)


@pytest.fixture
def valid_baseline_assumptions():
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


# 1. Test Baseline vs Scenario Creation & Calculation
def test_scenario_calculation_and_comparison(scenario_comparator, valid_baseline_assumptions):
    # Scenario: Increase daily customers from 50 to 70 and increase own capital from 40k to 60k
    scenario_assumptions = valid_baseline_assumptions.model_copy(update={"customers_per_day": 70})
    
    req = ScenarioEvaluationRequest(
        scenario_id="SCEN-001",
        name="Higher Demand & Equity",
        description="Testing higher footfall and own equity buffer",
        baseline_own_capital=40000.0,
        baseline_desired_loan=110000.0,
        baseline_financials=valid_baseline_assumptions,
        scenario_own_capital=60000.0,
        scenario_desired_loan=90000.0,
        scenario_financials=scenario_assumptions
    )
    
    res = scenario_comparator.evaluate_scenario(req)
    
    assert res.scenario_id == "SCEN-001"
    assert res.name == "Higher Demand & Equity"
    assert res.scenario_result.monthly_revenue > res.baseline_result.monthly_revenue
    assert res.scenario_result.monthly_net_profit > res.baseline_result.monthly_net_profit
    assert res.scenario_result.dscr > res.baseline_result.dscr
    assert res.scenario_result.monthly_emi < res.baseline_result.monthly_emi
    assert len(res.metric_comparisons) >= 6


# 2. Test Baseline Immutability Invariant
def test_baseline_immutability(scenario_comparator, financial_service, valid_baseline_assumptions):
    base_fin_before = financial_service.calculate(own_capital=40000.0, desired_loan=110000.0, financials=valid_baseline_assumptions)
    
    scenario_assumptions = valid_baseline_assumptions.model_copy(update={"customers_per_day": 20, "avg_ticket_price": 15.0})
    req = ScenarioEvaluationRequest(
        scenario_id="SCEN-IMMUTABLE",
        name="Stressed Scenario",
        baseline_own_capital=40000.0,
        baseline_desired_loan=110000.0,
        baseline_financials=valid_baseline_assumptions,
        scenario_own_capital=20000.0,
        scenario_desired_loan=130000.0,
        scenario_financials=scenario_assumptions
    )
    res = scenario_comparator.evaluate_scenario(req)
    
    # Baseline result in response must equal pre-calculation baseline
    assert res.baseline_result.monthly_net_profit == base_fin_before.monthly_net_profit
    assert res.baseline_result.monthly_emi == base_fin_before.monthly_emi
    assert res.baseline_result.dscr == base_fin_before.dscr
    assert res.baseline_result.break_even_units_daily == base_fin_before.break_even_units_daily


# 3. Test Recommendation Transition: VALIDATE_FIRST -> PROCEED
def test_recommendation_transition_validate_first_to_proceed(scenario_comparator):
    # Baseline with tight DSCR (< 1.50)
    baseline_assumptions = FinancialAssumptionsInput(
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
    # Scenario increases ticket price to ₹35, boosting DSCR above 1.50
    scenario_assumptions = baseline_assumptions.model_copy(update={"avg_ticket_price": 38.0})
    
    market = MarketResultResponse(
        location_summary="Test Village",
        competitor_count=1,
        direct_competitor_count=1,
        coverage_confidence="HIGH",
        demand_indicator="MEDIUM"
    )
    
    req = ScenarioEvaluationRequest(
        scenario_id="SCEN-TRANSITION",
        name="Optimized Pricing",
        baseline_own_capital=30000.0,
        baseline_desired_loan=120000.0,
        baseline_financials=baseline_assumptions,
        scenario_own_capital=40000.0,
        scenario_desired_loan=110000.0,
        scenario_financials=scenario_assumptions,
        market_context=market
    )
    
    res = scenario_comparator.evaluate_scenario(req)
    
    assert res.baseline_status == RecommendationStatus.VALIDATE_FIRST
    assert res.scenario_status == RecommendationStatus.PROCEED
    assert res.recommendation_change.changed is True
    assert "VALIDATE_FIRST to PROCEED" in res.recommendation_change.summary


# 4. Test Recommendation Transition: RECONSIDER -> VALIDATE_FIRST / PROCEED
def test_recommendation_transition_reconsider_to_viable(scenario_comparator):
    # Deficit baseline
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
    # Scenario: Right-size capex, reduce fixed rent/wages, increase realistic price
    restructured_assumptions = FinancialAssumptionsInput(
        startup_cost=20000.0,
        equipment_cost=80000.0,
        inventory_cost=20000.0,
        monthly_fixed_cost=7000.0,
        variable_cost_pct=45.0,
        avg_ticket_price=35.0,
        customers_per_day=35,
        working_days_per_month=26,
        interest_rate_pct=10.0,
        loan_tenure_months=36
    )
    
    req = ScenarioEvaluationRequest(
        scenario_id="SCEN-RESTRUCTURE",
        name="Restructured Business Model",
        baseline_own_capital=50000.0,
        baseline_desired_loan=250000.0,
        baseline_financials=deficit_assumptions,
        scenario_own_capital=40000.0,
        scenario_desired_loan=80000.0,
        scenario_financials=restructured_assumptions
    )
    
    res = scenario_comparator.evaluate_scenario(req)
    
    assert res.baseline_status == RecommendationStatus.RECONSIDER
    assert res.scenario_status in (RecommendationStatus.PROCEED, RecommendationStatus.VALIDATE_FIRST)
    assert res.recommendation_change.changed is True


# 5. Test Zero-Baseline Percentage Change Safety
def test_zero_baseline_percentage_safety(scenario_comparator, valid_baseline_assumptions):
    # Debt-free baseline (desired_loan = 0, required_loan = 0, EMI = 0)
    req = ScenarioEvaluationRequest(
        scenario_id="SCEN-ZERO-BASE",
        name="From Debt-Free to Loan",
        baseline_own_capital=150000.0,
        baseline_desired_loan=0.0,
        baseline_financials=valid_baseline_assumptions,
        scenario_own_capital=50000.0,
        scenario_desired_loan=100000.0,
        scenario_financials=valid_baseline_assumptions
    )
    res = scenario_comparator.evaluate_scenario(req)
    
    emi_comp = next(m for m in res.metric_comparisons if m.metric_key == "monthly_emi")
    assert emi_comp.baseline_value == 0.0
    assert emi_comp.percentage_change is None  # Safe handling of 0 denominator


# 6. Test Metric Direction Tagging (IMPROVED vs WORSENED)
def test_metric_direction_tagging(scenario_comparator, valid_baseline_assumptions):
    # Scenario increases monthly fixed cost from 6k to 15k (worsening net profit)
    worse_assumptions = valid_baseline_assumptions.model_copy(update={"monthly_fixed_cost": 15000.0})
    req = ScenarioEvaluationRequest(
        scenario_id="SCEN-DIR-TEST",
        name="Higher Fixed Cost",
        baseline_own_capital=40000.0,
        baseline_desired_loan=110000.0,
        baseline_financials=valid_baseline_assumptions,
        scenario_own_capital=40000.0,
        scenario_desired_loan=110000.0,
        scenario_financials=worse_assumptions
    )
    res = scenario_comparator.evaluate_scenario(req)
    
    surplus_comp = next(m for m in res.metric_comparisons if m.metric_key == "monthly_net_profit")
    assert surplus_comp.direction == ComparisonDirection.WORSENED
    
    be_comp = next(m for m in res.metric_comparisons if m.metric_key == "break_even_units_daily")
    assert be_comp.direction == ComparisonDirection.WORSENED  # higher break-even volume is worse


# 7. Test Market Context Invariance
def test_market_context_invariance(scenario_comparator, valid_baseline_assumptions):
    custom_market = MarketResultResponse(
        location_summary="Specific Panchayat, Satara",
        competitor_count=4,
        direct_competitor_count=2,
        coverage_confidence="HIGH",
        demand_indicator="HIGH"
    )
    scenario_assumptions = valid_baseline_assumptions.model_copy(update={"customers_per_day": 65})
    req = ScenarioEvaluationRequest(
        scenario_id="SCEN-MKT-INVAR",
        name="Market Invariance Test",
        baseline_own_capital=40000.0,
        baseline_desired_loan=110000.0,
        baseline_financials=valid_baseline_assumptions,
        scenario_own_capital=40000.0,
        scenario_desired_loan=110000.0,
        scenario_financials=scenario_assumptions,
        market_context=custom_market
    )
    res = scenario_comparator.evaluate_scenario(req)
    
    # Both baseline and scenario decision traces must evaluate against the exact same market context
    base_comp_rule = next(r for r in res.baseline_decision_trace.rule_evaluations if r.rule_id == "LOW_COMPETITION_CATCHMENT")
    scen_comp_rule = next(r for r in res.scenario_decision_trace.rule_evaluations if r.rule_id == "LOW_COMPETITION_CATCHMENT")
    assert base_comp_rule.result == scen_comp_rule.result


# 8. Test Invalid Scenario Inputs Rejection
def test_invalid_scenario_inputs_rejection(scenario_comparator, valid_baseline_assumptions):
    with pytest.raises(ValueError):
        # Invalid variable cost >= 100%
        invalid_assumptions = valid_baseline_assumptions.model_copy(update={"variable_cost_pct": 105.0})
        req = ScenarioEvaluationRequest(
            scenario_id="SCEN-INVALID",
            name="Invalid Scenario",
            baseline_own_capital=40000.0,
            baseline_desired_loan=110000.0,
            baseline_financials=valid_baseline_assumptions,
            scenario_own_capital=40000.0,
            scenario_desired_loan=110000.0,
            scenario_financials=invalid_assumptions
        )
        scenario_comparator.evaluate_scenario(req)


# 9. Test Deterministic Repeatability
def test_deterministic_repeatability(scenario_comparator, valid_baseline_assumptions):
    scenario_assumptions = valid_baseline_assumptions.model_copy(update={"customers_per_day": 60})
    req = ScenarioEvaluationRequest(
        scenario_id="SCEN-REPEAT",
        name="Repeatability Test",
        baseline_own_capital=40000.0,
        baseline_desired_loan=110000.0,
        baseline_financials=valid_baseline_assumptions,
        scenario_own_capital=40000.0,
        scenario_desired_loan=110000.0,
        scenario_financials=scenario_assumptions
    )
    res1 = scenario_comparator.evaluate_scenario(req)
    res2 = scenario_comparator.evaluate_scenario(req)
    
    assert res1.scenario_result.monthly_net_profit == res2.scenario_result.monthly_net_profit
    assert res1.scenario_result.dscr == res2.scenario_result.dscr
    assert len(res1.what_changed) == len(res2.what_changed)
    assert len(res1.metric_comparisons) == len(res2.metric_comparisons)


# 10. Test Absence of Fake Loan Approval Probability or Optimization
def test_no_fake_approval_probability_or_optimization(scenario_comparator, valid_baseline_assumptions):
    req = ScenarioEvaluationRequest(
        scenario_id="SCEN-NO-FAKE",
        name="Safety Check",
        baseline_own_capital=40000.0,
        baseline_desired_loan=110000.0,
        baseline_financials=valid_baseline_assumptions,
        scenario_own_capital=50000.0,
        scenario_desired_loan=100000.0,
        scenario_financials=valid_baseline_assumptions
    )
    res = scenario_comparator.evaluate_scenario(req)
    
    assert not hasattr(res, "approval_probability")
    assert not hasattr(res, "optimal_loan_amount")
    assert not hasattr(res, "credit_score")
    assert "decision support simulations" in res.disclaimer


# 11. Test Sensitivity Analysis Remains Separate and Unchanged
def test_sensitivity_analysis_invariance(valid_baseline_assumptions):
    calc_req = FinancialCalculationRequest(
        own_capital=40000.0,
        desired_loan=110000.0,
        financials=valid_baseline_assumptions
    )
    sens_res = run_sensitivity_analysis(calc_req)
    assert len(sens_res.scenarios) == 4
    assert sens_res.resilience_rating in ("HIGH", "MODERATE", "LOW")

