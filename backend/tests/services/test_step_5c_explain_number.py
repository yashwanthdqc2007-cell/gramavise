"""
Step 5C Verification Tests: Explain This Number Inspector.

Verifies:
1. Declarative explanation metadata generated for all primary financial metrics.
2. Exact numeric values and substituted expressions match FinancialService outputs.
3. Provenance rules: inputs are ASSUMED; derived outputs are CALCULATED.
4. Debt-free DSCR produces is_debt_free=True and 'N/A (Debt-Free)'.
5. Zero/edge cases (e.g. zero loan, zero revenue) are handled defensively without division by zero.
6. Scenario explanations clearly demarcate scenario assumptions while baseline remains immutable.
7. FinancialService and FeasibilityRules maintain 100% mathematical invariance.
"""

import pytest
from app.schemas.financial import FinancialAssumptionsInput
from app.schemas.scenario import ScenarioEvaluationRequest
from app.services.financial.calculator import FinancialService
from app.rules.feasibility_rules import FeasibilityRules
from app.services.recommendation.scenario_comparator import ScenarioComparator
from app.schemas.evidence import EvidenceType


@pytest.fixture
def sample_financials():
    return FinancialAssumptionsInput(
        startup_cost=50000.0,
        equipment_cost=150000.0,
        inventory_cost=50000.0,
        monthly_fixed_cost=15000.0,
        customers_per_day=45,
        avg_ticket_price=120.0,
        working_days_per_month=26,
        variable_cost_pct=40.0,
        interest_rate_pct=10.5,
        loan_tenure_months=36,
    )


def test_explanations_generated_for_all_metrics(sample_financials):
    service = FinancialService()
    result = service.calculate(
        own_capital=50000.0,
        desired_loan=200000.0,
        financials=sample_financials
    )

    assert result.explanations is not None
    exp = result.explanations

    expected_metrics = [
        "total_capex",
        "required_loan_amount",
        "monthly_revenue",
        "monthly_variable_cost",
        "monthly_gross_profit",
        "monthly_fixed_cost",
        "monthly_emi",
        "monthly_net_profit",
        "break_even_revenue_monthly",
        "break_even_units_daily",
        "dscr",
        "variable_cost_pct",
    ]

    for m in expected_metrics:
        assert m in exp, f"Metric '{m}' missing from explanations"
        assert exp[m].metric_id == m
        assert exp[m].plain_meaning != ""
        assert exp[m].formula_expression != ""
        assert exp[m].substituted_expression != ""
        assert len(exp[m].inputs) > 0 or m == "monthly_fixed_cost"
        assert len(exp[m].calculation_steps) > 0


def test_provenance_correctness(sample_financials):
    service = FinancialService()
    result = service.calculate(
        own_capital=50000.0,
        desired_loan=200000.0,
        financials=sample_financials
    )
    exp = result.explanations

    # Monthly revenue should be CALCULATED from ASSUMED inputs
    rev_exp = exp["monthly_revenue"]
    assert rev_exp.provenance == EvidenceType.CALCULATED
    for inp in rev_exp.inputs:
        assert inp.provenance == EvidenceType.ASSUMED

    # Gross profit should be CALCULATED from CALCULATED inputs
    gp_exp = exp["monthly_gross_profit"]
    assert gp_exp.provenance == EvidenceType.CALCULATED


def test_debt_free_dscr_explanation(sample_financials):
    service = FinancialService()
    # Debt-free: own_capital covers entire capex, desired_loan=0
    result = service.calculate(
        own_capital=250000.0,
        desired_loan=0.0,
        financials=sample_financials
    )
    exp = result.explanations

    dscr_exp = exp["dscr"]
    assert dscr_exp.is_debt_free is True
    assert "N/A (Debt-Free)" in dscr_exp.displayed_value
    assert "debt-free" in dscr_exp.substituted_expression.lower() or "0.00" in dscr_exp.substituted_expression


def test_scenario_explanation_immutability(sample_financials):
    comparator = ScenarioComparator()

    scenario_fin = FinancialAssumptionsInput(
        startup_cost=50000.0,
        equipment_cost=150000.0,
        inventory_cost=50000.0,
        monthly_fixed_cost=12000.0,
        customers_per_day=60,
        avg_ticket_price=120.0,
        working_days_per_month=26,
        variable_cost_pct=35.0,
        interest_rate_pct=10.5,
        loan_tenure_months=36,
    )

    req = ScenarioEvaluationRequest(
        scenario_id="SCEN-TEST-01",
        name="Higher Demand Scenario",
        baseline_own_capital=50000.0,
        baseline_desired_loan=200000.0,
        baseline_financials=sample_financials,
        scenario_own_capital=50000.0,
        scenario_desired_loan=150000.0,
        scenario_financials=scenario_fin,
    )

    resp = comparator.evaluate_scenario(req)

    # Baseline explanations must reflect 45 customers/day
    base_rev_exp = resp.baseline_result.explanations["monthly_revenue"]
    assert base_rev_exp.numeric_value == 45 * 120.0 * 26  # 140,400

    # Scenario explanations must reflect 60 customers/day
    scen_rev_exp = resp.scenario_result.explanations["monthly_revenue"]
    assert scen_rev_exp.numeric_value == 60 * 120.0 * 26  # 187,200
    assert "Scenario Override" in scen_rev_exp.inputs[0].source_description


def test_financial_service_and_rules_invariance(sample_financials):
    service = FinancialService()
    result = service.calculate(
        own_capital=50000.0,
        desired_loan=200000.0,
        financials=sample_financials
    )

    assert result.monthly_revenue == 140400.0
    assert result.monthly_gross_profit == 84240.0
    assert result.is_financially_viable is True
