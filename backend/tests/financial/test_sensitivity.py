from app.schemas.financial import FinancialAssumptionsInput, FinancialCalculationRequest
from app.services.financial.sensitivity import run_sensitivity_analysis


def test_run_sensitivity_analysis():
    assumptions = FinancialAssumptionsInput(
        startup_cost=10000.0,
        equipment_cost=50000.0,
        inventory_cost=20000.0,
        monthly_fixed_cost=5000.0,
        customers_per_day=30,
        avg_ticket_price=100.0,
        working_days_per_month=26,
        variable_cost_pct=40.0,
        interest_rate_pct=10.0,
        loan_tenure_months=36
    )
    req = FinancialCalculationRequest(own_capital=20000.0, desired_loan=60000.0, financials=assumptions)
    res = run_sensitivity_analysis(req)

    assert len(res.scenarios) == 4
    assert res.resilience_rating in ["HIGH", "MODERATE", "LOW"]
    scenario_names = [s.scenario_name for s in res.scenarios]
    assert any("Demand Dip" in name for name in scenario_names)
    assert any("Price Compression" in name for name in scenario_names)
    assert any("Cost Escalation" in name for name in scenario_names)
    assert any("Combined Worst Case" in name for name in scenario_names)
    for s in res.scenarios:
        assert s.status in ["VIABLE", "STRESSED", "INSOLVENT"]

