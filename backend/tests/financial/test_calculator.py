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


# ---------------- Revenue Tests ----------------

def test_calculate_revenue_normal():
    # 20 customers * 50 rs * 26 days = 26,000
    assert calculate_revenue(20, 50.0, 26) == 26000.0


def test_calculate_revenue_zero_customers():
    assert calculate_revenue(0, 50.0, 26) == 0.0


def test_calculate_revenue_zero_working_days():
    assert calculate_revenue(20, 50.0, 0) == 0.0


def test_calculate_revenue_fractional():
    # 15 customers * 33.50 rs * 25 days = 12562.5
    assert calculate_revenue(15, 33.50, 25) == 12562.5


# ---------------- Cost Tests ----------------

def test_calculate_variable_cost():
    # 26,000 * 30% = 7,800
    assert calculate_variable_cost(26000.0, 30.0) == 7800.0


def test_calculate_variable_cost_zero():
    assert calculate_variable_cost(0.0, 30.0) == 0.0
    assert calculate_variable_cost(26000.0, 0.0) == 0.0


def test_calculate_fixed_cost():
    assert calculate_fixed_cost(12500.0) == 12500.0
    assert calculate_fixed_cost(-500.0) == 0.0


# ---------------- Profit Tests ----------------

def test_calculate_gross_profit():
    assert calculate_gross_profit(50000.0, 20000.0) == 30000.0
    assert calculate_gross_profit(20000.0, 20000.0) == 0.0
    assert calculate_gross_profit(10000.0, 20000.0) == -10000.0


def test_calculate_net_profit():
    # Gross: 30000, Fixed: 10000, EMI: 5000 -> Net: 15000
    assert calculate_net_profit(30000.0, 10000.0, 5000.0) == 15000.0
    # Zero profit
    assert calculate_net_profit(15000.0, 10000.0, 5000.0) == 0.0
    # Negative profit (loss)
    assert calculate_net_profit(10000.0, 10000.0, 5000.0) == -5000.0


# ---------------- Loan & EMI Tests ----------------

def test_calculate_loan_requirement():
    # Capex 150,000, Own Capital 50,000 -> Loan 100,000
    assert calculate_loan_requirement(150000.0, 50000.0) == 100000.0
    # Own Capital exceeds Capex -> Loan 0
    assert calculate_loan_requirement(100000.0, 120000.0) == 0.0
    # Zero own capital
    assert calculate_loan_requirement(100000.0, 0.0) == 100000.0


def test_calculate_emi_normal():
    # 100,000 at 12% for 12 months ~ 8884.88
    emi = calculate_emi(100000.0, 12.0, 12)
    assert emi == 8884.88


def test_calculate_emi_zero_interest():
    # 60,000 at 0% for 12 months = 5000.0
    assert calculate_emi(60000.0, 0.0, 12) == 5000.0


def test_calculate_emi_invalid_inputs():
    assert calculate_emi(0.0, 10.0, 36) == 0.0
    assert calculate_emi(50000.0, 10.0, 0) == 0.0
    assert calculate_emi(-50000.0, 10.0, 36) == 0.0


# ---------------- Break-Even Tests ----------------

def test_calculate_break_even_normal():
    # Fixed: 10000, EMI: 2000, Price: 100, Var%: 40%, Days: 25
    # CMR = 0.60
    # BE Revenue = 12000 / 0.60 = 20000.0
    # Daily Revenue needed = 20000 / 25 = 800.0
    # Daily Units = ceil(800 / 100) = 8
    be = calculate_break_even(10000.0, 2000.0, 100.0, 40.0, 25)
    assert be["break_even_revenue_monthly"] == 20000.0
    assert be["break_even_units_daily"] == 8


def test_calculate_break_even_zero_margin():
    # Var% = 100% -> CMR = 0.0
    be = calculate_break_even(10000.0, 2000.0, 100.0, 100.0, 25)
    assert be["break_even_revenue_monthly"] == 0.0
    assert be["break_even_units_daily"] == 0


def test_calculate_break_even_zero_overhead():
    # No fixed costs, no EMI
    be = calculate_break_even(0.0, 0.0, 100.0, 40.0, 25)
    assert be["break_even_revenue_monthly"] == 0.0
    assert be["break_even_units_daily"] == 0


# ---------------- Repayment / DSCR Tests ----------------

def test_calculate_repayment_capacity_normal():
    # Net Operating Income: 30000, EMI: 15000 -> DSCR: 2.0
    assert calculate_repayment_capacity(30000.0, 15000.0) == 2.0


def test_calculate_repayment_capacity_debt_free():
    # EMI = 0 -> returns 0.0 (debt-free)
    assert calculate_repayment_capacity(30000.0, 0.0) == 0.0


def test_calculate_repayment_capacity_deficit():
    # Operating loss
    assert calculate_repayment_capacity(-5000.0, 5000.0) == 0.0


# ---------------- Service Integration Tests ----------------

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
    assert result.required_loan_amount == 60000.0
    assert result.monthly_revenue == 78000.0
    assert result.monthly_variable_cost == 31200.0
    assert result.monthly_gross_profit == 46800.0
    assert result.monthly_net_profit > 0
    assert result.dscr > 1.5
    assert result.is_financially_viable is True


def test_financial_service_debt_free_calculation():
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
    # 100% equity funded (own capital = 80,000, desired loan = 0)
    result = service.calculate(own_capital=80000.0, desired_loan=0.0, financials=assumptions)
    
    assert result.required_loan_amount == 0.0
    assert result.monthly_emi == 0.0
    assert result.dscr == 0.0
    assert result.is_financially_viable is True

