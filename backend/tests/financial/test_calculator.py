from app.services.financial.calculator import (
    calculate_revenue,
    calculate_variable_cost,
    calculate_emi,
    calculate_break_even,
    FinancialService
)
from app.schemas.financial import FinancialAssumptionsInput


def test_calculate_revenue():
    # 20 customers * 50 rs * 26 days = 26,000
    assert calculate_revenue(20, 50.0, 26) == 26000.0


def test_calculate_variable_cost():
    # 26,000 * 30% = 7,800
    assert calculate_variable_cost(26000.0, 30.0) == 7800.0


def test_calculate_emi():
    # 100,000 at 12% for 12 months ~ 8884.88
    emi = calculate_emi(100000.0, 12.0, 12)
    assert 8800.0 < emi < 8950.0


def test_financial_service_calculation():
    service = FinancialService()
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
    result = service.calculate(own_capital=20000.0, desired_loan=60000.0, financials=assumptions)
    
    assert result.total_capex == 80000.0
    assert result.monthly_revenue == 78000.0
    assert result.monthly_gross_profit == 46800.0
    assert result.monthly_net_profit > 0
    assert result.is_financially_viable is True
