from typing import List
from app.schemas.financial import (
    FinancialCalculationRequest,
    FinancialResultResponse,
    SensitivityResponse,
    SensitivityScenario
)
from app.services.financial.calculator import FinancialService


def run_sensitivity_analysis(calc_request: FinancialCalculationRequest) -> SensitivityResponse:
    """Stress-test financial projections against demand, price, and cost shocks.
    
    Standard scenarios evaluated (as per FINANCIAL_ENGINE.md):
    1. Demand Dip: -20% daily footfall / customer volume
    2. Price Shock: -10% average selling price / ticket price
    3. Cost Escalation: +15% variable / raw material costs
    4. Combined Worst Case: -15% volume, +10% variable cost
    """
    service = FinancialService()
    baseline: FinancialResultResponse = service.calculate(
        own_capital=calc_request.own_capital,
        desired_loan=calc_request.desired_loan,
        financials=calc_request.financials
    )

    scenarios: List[SensitivityScenario] = []

    def evaluate_scenario_status(res: FinancialResultResponse) -> str:
        if res.monthly_net_profit > 0:
            if res.monthly_emi <= 0 or res.dscr >= 1.25:
                return "VIABLE"
            elif res.dscr >= 1.0:
                return "STRESSED"
        return "INSOLVENT"

    # Scenario 1: -20% Demand Shock
    stress_f1 = calc_request.financials.model_copy(update={
        "customers_per_day": max(1, int(round(calc_request.financials.customers_per_day * 0.8)))
    })
    res_s1 = service.calculate(calc_request.own_capital, calc_request.desired_loan, stress_f1)
    scenarios.append(SensitivityScenario(
        scenario_name="Demand Dip (-20% daily footfall)",
        monthly_revenue=res_s1.monthly_revenue,
        monthly_net_profit=res_s1.monthly_net_profit,
        break_even_revenue=res_s1.break_even_revenue_monthly,
        dscr=res_s1.dscr,
        status=evaluate_scenario_status(res_s1)
    ))

    # Scenario 2: -10% Price Shock
    stress_f2 = calc_request.financials.model_copy(update={
        "avg_ticket_price": round(calc_request.financials.avg_ticket_price * 0.9, 2)
    })
    res_s2 = service.calculate(calc_request.own_capital, calc_request.desired_loan, stress_f2)
    scenarios.append(SensitivityScenario(
        scenario_name="Price Compression (-10% realization)",
        monthly_revenue=res_s2.monthly_revenue,
        monthly_net_profit=res_s2.monthly_net_profit,
        break_even_revenue=res_s2.break_even_revenue_monthly,
        dscr=res_s2.dscr,
        status=evaluate_scenario_status(res_s2)
    ))

    # Scenario 3: +15% Variable Cost Escalation
    stress_f3 = calc_request.financials.model_copy(update={
        "variable_cost_pct": min(95.0, round(calc_request.financials.variable_cost_pct * 1.15, 2))
    })
    res_s3 = service.calculate(calc_request.own_capital, calc_request.desired_loan, stress_f3)
    scenarios.append(SensitivityScenario(
        scenario_name="Cost Escalation (+15% variable costs)",
        monthly_revenue=res_s3.monthly_revenue,
        monthly_net_profit=res_s3.monthly_net_profit,
        break_even_revenue=res_s3.break_even_revenue_monthly,
        dscr=res_s3.dscr,
        status=evaluate_scenario_status(res_s3)
    ))

    # Scenario 4: Combined Worst Case (-15% volume, +10% variable cost)
    stress_f4 = calc_request.financials.model_copy(update={
        "customers_per_day": max(1, int(round(calc_request.financials.customers_per_day * 0.85))),
        "variable_cost_pct": min(95.0, round(calc_request.financials.variable_cost_pct * 1.10, 2))
    })
    res_s4 = service.calculate(calc_request.own_capital, calc_request.desired_loan, stress_f4)
    scenarios.append(SensitivityScenario(
        scenario_name="Combined Worst Case (-15% volume, +10% cost)",
        monthly_revenue=res_s4.monthly_revenue,
        monthly_net_profit=res_s4.monthly_net_profit,
        break_even_revenue=res_s4.break_even_revenue_monthly,
        dscr=res_s4.dscr,
        status=evaluate_scenario_status(res_s4)
    ))

    # Overall resilience rating
    insolvent_count = sum(1 for s in scenarios if s.status == "INSOLVENT")
    stressed_count = sum(1 for s in scenarios if s.status == "STRESSED")
    if insolvent_count == 0 and stressed_count <= 1:
        resilience = "HIGH"
    elif insolvent_count <= 1:
        resilience = "MODERATE"
    else:
        resilience = "LOW"

    return SensitivityResponse(
        baseline=baseline,
        scenarios=scenarios,
        resilience_rating=resilience
    )
