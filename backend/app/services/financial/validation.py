from typing import List, Tuple, Optional
from app.schemas.financial import FinancialAssumptionsInput


def validate_financial_assumptions(financials: FinancialAssumptionsInput) -> Tuple[bool, List[str]]:
    """Sanity-check input financial assumptions for boundary violations."""
    errors: List[str] = []

    if financials.startup_cost < 0:
        errors.append("Startup cost cannot be negative.")

    if financials.equipment_cost < 0:
        errors.append("Equipment cost cannot be negative.")

    if financials.inventory_cost < 0:
        errors.append("Inventory cost cannot be negative.")

    if financials.monthly_fixed_cost < 0:
        errors.append("Monthly fixed cost cannot be negative.")

    if financials.customers_per_day <= 0:
        errors.append("Expected daily customer volume must be greater than 0.")

    if financials.avg_ticket_price <= 0:
        errors.append("Average unit/ticket price must be greater than 0.")

    if financials.working_days_per_month < 1 or financials.working_days_per_month > 31:
        errors.append("Working days per month must be between 1 and 31.")

    if financials.variable_cost_pct < 0.0:
        errors.append("Variable cost percentage cannot be negative.")
    elif financials.variable_cost_pct >= 100.0:
        errors.append("Variable cost percentage cannot be 100% or greater (zero or negative gross margin).")

    if financials.interest_rate_pct < 0.0:
        errors.append("Interest rate percentage cannot be negative.")
    elif financials.interest_rate_pct > 100.0:
        errors.append("Interest rate percentage cannot exceed 100%.")

    if financials.loan_tenure_months <= 0:
        errors.append("Loan tenure must be at least 1 month.")

    return (len(errors) == 0, errors)


def validate_capital_inputs(own_capital: Optional[float], desired_loan: Optional[float]) -> Tuple[bool, List[str]]:
    """Validate own capital and desired loan amount bounds."""
    errors: List[str] = []
    if own_capital is not None and own_capital < 0:
        errors.append("Own capital cannot be negative.")
    if desired_loan is not None and desired_loan < 0:
        errors.append("Desired loan amount cannot be negative.")
    return (len(errors) == 0, errors)

