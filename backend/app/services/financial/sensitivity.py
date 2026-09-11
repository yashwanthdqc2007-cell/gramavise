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
    
    TODO [Financial Lead]: Extend with multi-dimensional Monte Carlo or custom shock scenarios.
    """
    service = FinancialService()
    baseline: FinancialResultResponse = service.calculate(
        own_capital=calc_request.own_capital,
        desired_loan=calc_request.desired_loan or 0.0,
        financials=calc_request.financials
    )

    scenarios: List[SensitivityScenario] = []

    # Scenario 1: -20% Demand Shock
    stress_f1 = calc_request.financials.model_copy(update={
        "customers_per_day": max(1, int(calc_request.financials.customers_per_day * 0.8))
    })
    res_s1 = service.calculate(calc_request.own_capital, calc_request.desired_loan or 0.0, stress_f1)
    status_s1 = "VIABLE" if res_s1.dscr >= 1.25 else ("STRESSED" if res_s1.dscr >= 1.0 else "INSOLVENT")
    scenarios.append(SensitivityScenario(
        scenario_name="Demand Dip (-20% daily footfall)",
        monthly_revenue=res_s1.monthly_revenue,
        monthly_net_profit=res_s1.monthly_net_profit,
        break_even_revenue=res_s1.break_even_revenue_monthly,
        dscr=res_s1.dscr,
        status=status_s1
    ))

    # Scenario 2: -10% Price Shock
    stress_f2 = calc_request.financials.model_copy(update={
        "avg_ticket_price": calc_request.financials.avg_ticket_price * 0.9
    })
    res_s2 = service.calculate(calc_request.own_capital, calc_request.desired_loan or 0.0, stress_f2)
    status_s2 = "VIABLE" if res_s2.dscr >= 1.25 else ("STRESSED" if res_s2.dscr >= 1.0 else "INSOLVENT")
    scenarios.append(SensitivityScenario(
        scenario_name="Price Compression (-10% realization)",
        monthly_revenue=res_s2.monthly_revenue,
        monthly_net_profit=res_s2.monthly_net_profit,
        break_even_revenue=res_s2.break_even_revenue_monthly,
        dscr=res_s2.dscr,
        status=status_s2
    ))

    # Scenario 3: +15% Variable Cost Escalation
    stress_f3 = calc_request.financials.model_copy(update={
        "variable_cost_pct": min(95.0, calc_request.financials.variable_cost_pct * 1.15)
    })
    res_s3 = service.calculate(calc_request.own_capital, calc_request.desired_loan or 0.0, stress_f3)
    status_s3 = "VIABLE" if res_s3.dscr >= 1.25 else ("STRESSED" if res_s3.dscr >= 1.0 else "INSOLVENT")
    scenarios.append(SensitivityScenario(
        scenario_name="Cost Escalation (+15% variable/raw material costs)",
        monthly_revenue=res_s3.monthly_revenue,
        monthly_net_profit=res_s3.monthly_net_profit,
        break_even_revenue=res_s3.break_even_revenue_monthly,
        dscr=res_s3.dscr,
        status=status_s3
    ))

    # Overall rating
    insolvent_count = sum(1 for s in scenarios if s.status == "INSOLVENT")
    if insolvent_count == 0:
        resilience = "HIGH"
    elif insolvent_count == 1:
        resilience = "MODERATE"
    else:
        resilience = "LOW"

    return SensitivityResponse(
        baseline=baseline,
        scenarios=scenarios,
        resilience_rating=resilience
    )
