import pytest
from app.schemas.financial import FinancialAssumptionsInput
from app.services.financial.validation import (
    validate_financial_assumptions,
    validate_capital_inputs
)


def test_validation_valid_input():
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
    is_valid, errors = validate_financial_assumptions(assumptions)
    assert is_valid is True
    assert len(errors) == 0


def test_validation_negative_costs():
    assumptions = FinancialAssumptionsInput.model_construct(
        startup_cost=-1000.0,
        equipment_cost=-5000.0,
        inventory_cost=-2000.0,
        monthly_fixed_cost=-500.0,
        customers_per_day=30,
        avg_ticket_price=100.0,
        working_days_per_month=26,
        variable_cost_pct=40.0,
        interest_rate_pct=10.0,
        loan_tenure_months=36
    )
    is_valid, errors = validate_financial_assumptions(assumptions)
    assert is_valid is False
    assert any("Startup cost" in e for e in errors)
    assert any("Equipment cost" in e for e in errors)
    assert any("Inventory cost" in e for e in errors)
    assert any("Monthly fixed cost" in e for e in errors)


def test_validation_zero_customers_and_price():
    assumptions = FinancialAssumptionsInput.model_construct(
        startup_cost=10000.0,
        equipment_cost=50000.0,
        inventory_cost=20000.0,
        monthly_fixed_cost=5000.0,
        customers_per_day=0,
        avg_ticket_price=0.0,
        working_days_per_month=26,
        variable_cost_pct=40.0,
        interest_rate_pct=10.0,
        loan_tenure_months=36
    )
    is_valid, errors = validate_financial_assumptions(assumptions)
    assert is_valid is False
    assert any("customer volume" in e for e in errors)
    assert any("ticket price" in e for e in errors)


def test_validation_invalid_working_days():
    assumptions = FinancialAssumptionsInput.model_construct(
        startup_cost=10000.0,
        equipment_cost=50000.0,
        inventory_cost=20000.0,
        monthly_fixed_cost=5000.0,
        customers_per_day=20,
        avg_ticket_price=50.0,
        working_days_per_month=0,
        variable_cost_pct=40.0,
        interest_rate_pct=10.0,
        loan_tenure_months=36
    )
    is_valid, errors = validate_financial_assumptions(assumptions)
    assert is_valid is False
    assert any("Working days" in e for e in errors)


def test_validation_invalid_variable_cost_pct():
    assumptions = FinancialAssumptionsInput.model_construct(
        startup_cost=10000.0,
        equipment_cost=50000.0,
        inventory_cost=20000.0,
        monthly_fixed_cost=5000.0,
        customers_per_day=20,
        avg_ticket_price=50.0,
        working_days_per_month=26,
        variable_cost_pct=105.0,
        interest_rate_pct=10.0,
        loan_tenure_months=36
    )
    is_valid, errors = validate_financial_assumptions(assumptions)
    assert is_valid is False
    assert any("Variable cost percentage" in e for e in errors)


def test_validation_invalid_interest_and_tenure():
    assumptions = FinancialAssumptionsInput.model_construct(
        startup_cost=10000.0,
        equipment_cost=50000.0,
        inventory_cost=20000.0,
        monthly_fixed_cost=5000.0,
        customers_per_day=20,
        avg_ticket_price=50.0,
        working_days_per_month=26,
        variable_cost_pct=40.0,
        interest_rate_pct=-5.0,
        loan_tenure_months=0
    )
    is_valid, errors = validate_financial_assumptions(assumptions)
    assert is_valid is False
    assert any("Interest rate" in e for e in errors)
    assert any("Loan tenure" in e for e in errors)


def test_validation_capital_inputs():
    is_valid, errors = validate_capital_inputs(-1000.0, -5000.0)
    assert is_valid is False
    assert len(errors) == 2
    assert any("Own capital" in e for e in errors)
    assert any("Desired loan" in e for e in errors)

    is_valid, errors = validate_capital_inputs(50000.0, 100000.0)
    assert is_valid is True
    assert len(errors) == 0
