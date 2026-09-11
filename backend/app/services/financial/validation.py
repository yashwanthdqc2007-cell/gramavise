from typing import List, Tuple
from app.schemas.financial import FinancialAssumptionsInput


def validate_financial_assumptions(financials: FinancialAssumptionsInput) -> Tuple[bool, List[str]]:
    """Sanity-check input financial assumptions for boundary violations.
    
    TODO [Financial Lead]: Add sector-specific boundary checks (e.g. max realistic kirana ticket size).
    """
    errors: List[str] = []

    if financials.startup_cost < 0:
        errors.append("Startup cost cannot be negative.")

    if financials.equipment_cost < 0:
        errors.append("Equipment cost cannot be negative.")

    if financials.inventory_cost < 0:
        errors.append("Inventory cost cannot be negative.")

    if financials.customers_per_day <= 0:
        errors.append("Expected daily customer volume must be greater than 0.")

    if financials.avg_ticket_price <= 0:
        errors.append("Average unit/ticket price must be greater than 0.")

    if financials.variable_cost_pct >= 100.0:
        errors.append("Variable cost percentage cannot be 100% or greater (zero or negative gross margin).")

    if financials.loan_tenure_months <= 0:
        errors.append("Loan tenure must be at least 1 month.")

    return (len(errors) == 0, errors)
