import pytest
from app.services.financial.calculator import (
    calculate_revenue,
    calculate_variable_cost,
    calculate_fixed_cost,
    calculate_gross_profit,
    calculate_loan_requirement,
    calculate_emi,
    calculate_net_profit,
    calculate_break_even,
    calculate_repayment_capacity,
    FinancialService
)
from app.schemas.financial import FinancialAssumptionsInput


def test_deterministic_reference_scenario():
    """Reference Test Case matching the specification:
    
    Inputs:
    - Customers/day: 120
    - Average order value (avg_ticket_price): ₹40
    - Working days/month: 26
    - Startup cost: ₹35,000
    - Equipment cost: ₹1,00,000
    - Inventory cost: ₹40,000
    - Total Capex: ₹1,75,000
    - Own capital: ₹1,00,000
    - Required Loan: ₹75,000
    - Monthly fixed cost: ₹15,000
    - Variable cost percentage: 40%
    - Annual interest rate: 10.5%
    - Loan tenure: 36 months
    """
    # 1. Revenue
    # Daily Revenue = 120 * 40 = 4,800
    # Monthly Revenue = 4,800 * 26 = 1,24,800
    monthly_rev = calculate_revenue(customers_per_day=120, avg_ticket_price=40.0, working_days=26)
    assert monthly_rev == 124800.0

    # 2. Variable Cost
    # 1,24,800 * 40% = 49,920
    monthly_var = calculate_variable_cost(monthly_revenue=monthly_rev, variable_cost_pct=40.0)
    assert monthly_var == 49920.0

    # 3. Gross Profit
    # 1,24,800 - 49,920 = 74,880
    monthly_gross = calculate_gross_profit(monthly_revenue=monthly_rev, monthly_variable_cost=monthly_var)
    assert monthly_gross == 74880.0

    # 4. Total Capex & Loan Requirement
    total_capex = 35000.0 + 100000.0 + 40000.0
    assert total_capex == 175000.0
    required_loan = calculate_loan_requirement(total_capex=total_capex, own_capital=100000.0)
    assert required_loan == 75000.0

    # 5. Fixed Cost
    monthly_fixed = calculate_fixed_cost(15000.0)
    assert monthly_fixed == 15000.0

    # 6. EMI
    # Principal: 75,000, Rate: 10.5% p.a., Tenure: 36 months
    # Monthly rate r = (10.5 / 100) / 12 = 0.00875
    # EMI = 75000 * 0.00875 * (1.00875)^36 / ((1.00875)^36 - 1) = 2437.68
    emi = calculate_emi(principal=required_loan, annual_rate_pct=10.5, tenure_months=36)
    assert emi == 2437.68

    # 7. Net Profit
    # Gross Profit (74,880) - Fixed Cost (15,000) - EMI (2,437.68) = 57,442.32
    monthly_net = calculate_net_profit(monthly_gross_profit=monthly_gross, monthly_fixed_cost=monthly_fixed, monthly_emi=emi)
    assert monthly_net == 57442.32

    # 8. Break-Even
    # CMR = 1 - 0.40 = 0.60
    # Fixed burden = 15,000 + 2,437.68 = 17,437.68
    # BE Revenue = 17,437.68 / 0.60 = 29,062.80
    # Daily Revenue needed = 29,062.80 / 26 = 1,117.80
    # Daily Units needed = ceil(1,117.80 / 40) = ceil(27.945) = 28
    be = calculate_break_even(
        monthly_fixed_cost=monthly_fixed,
        monthly_emi=emi,
        avg_ticket_price=40.0,
        variable_cost_pct=40.0,
        working_days=26
    )
    assert be["break_even_revenue_monthly"] == 29062.80
    assert be["break_even_units_daily"] == 28

    # 9. Repayment Capacity (DSCR)
    # Net Operating Income = Gross Profit (74,880) - Fixed Cost (15,000) = 59,880
    # DSCR = 59,880 / 2,437.68 = 24.56
    net_operating_income = monthly_gross - monthly_fixed
    dscr = calculate_repayment_capacity(monthly_net_operating_income=net_operating_income, monthly_emi=emi)
    assert dscr == 24.56

    # 10. End-to-end FinancialService verification
    service = FinancialService()
    assumptions = FinancialAssumptionsInput(
        startup_cost=35000.0,
        equipment_cost=100000.0,
        inventory_cost=40000.0,
        monthly_fixed_cost=15000.0,
        customers_per_day=120,
        avg_ticket_price=40.0,
        working_days_per_month=26,
        variable_cost_pct=40.0,
        interest_rate_pct=10.5,
        loan_tenure_months=36
    )
    result = service.calculate(own_capital=100000.0, desired_loan=None, financials=assumptions)

    assert result.total_capex == 175000.0
    assert result.required_loan_amount == 75000.0
    assert result.monthly_revenue == 124800.0
    assert result.monthly_variable_cost == 49920.0
    assert result.monthly_gross_profit == 74880.0
    assert result.monthly_fixed_cost == 15000.0
    assert result.monthly_emi == 2437.68
    assert result.monthly_net_profit == 57442.32
    assert result.net_profit_margin_pct == 46.03  # 57,442.32 / 1,24,800 * 100
    assert result.break_even_revenue_monthly == 29062.80
    assert result.break_even_units_daily == 28
    assert result.dscr == 24.56
    assert result.is_financially_viable is True
