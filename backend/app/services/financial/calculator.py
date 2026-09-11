from abc import ABC, abstractmethod
from typing import Dict, Any
from app.schemas.financial import FinancialAssumptionsInput, FinancialResultResponse


class FinancialServiceInterface(ABC):
    """Abstract interface defining required financial engine operations."""

    @abstractmethod
    def calculate(self, own_capital: float, desired_loan: float, financials: FinancialAssumptionsInput) -> FinancialResultResponse:
        """Calculate complete unit economics, Capex, and profitability."""
        pass

    @abstractmethod
    def calculate_break_even(self, fixed_costs: float, emi: float, avg_price: float, variable_cost_pct: float, working_days: int) -> Dict[str, float]:
        """Calculate monthly revenue and daily unit break-even thresholds."""
        pass

    @abstractmethod
    def calculate_emi(self, principal: float, annual_rate_pct: float, tenure_months: int) -> float:
        """Calculate monthly loan installment using standard amortization formula."""
        pass

    @abstractmethod
    def calculate_repayment(self, net_operating_income: float, monthly_emi: float) -> float:
        """Compute Debt Service Coverage Ratio (DSCR)."""
        pass


def calculate_revenue(customers_per_day: int, avg_ticket_price: float, working_days: int) -> float:
    """Calculate monthly estimated gross revenue.
    
    TODO [Financial Lead]: Implement formula: customers_per_day * avg_ticket_price * working_days
    """
    return float(customers_per_day * avg_ticket_price * working_days)


def calculate_variable_cost(monthly_revenue: float, variable_cost_pct: float) -> float:
    """Calculate monthly variable operating cost.
    
    TODO [Financial Lead]: Implement formula: monthly_revenue * (variable_cost_pct / 100.0)
    """
    return float(monthly_revenue * (variable_cost_pct / 100.0))


def calculate_fixed_cost(monthly_fixed_cost: float) -> float:
    """Calculate total monthly fixed overheads.
    
    TODO [Financial Lead]: Implement fixed cost aggregation (rent, electricity, minimum wages).
    """
    return float(monthly_fixed_cost)


def calculate_gross_profit(monthly_revenue: float, monthly_variable_cost: float) -> float:
    """Calculate monthly gross profit before overheads.
    
    TODO [Financial Lead]: Implement formula: monthly_revenue - monthly_variable_cost
    """
    return float(monthly_revenue - monthly_variable_cost)


def calculate_loan_requirement(total_capex: float, own_capital: float) -> float:
    """Calculate net borrowing need after own equity contribution.
    
    TODO [Financial Lead]: Implement formula: max(0.0, total_capex - own_capital)
    """
    return max(0.0, float(total_capex - own_capital))


def calculate_emi(principal: float, annual_rate_pct: float, tenure_months: int) -> float:
    """Calculate monthly loan installment using amortization formula.
    
    TODO [Financial Lead]: Implement formula: P * r * (1+r)^n / ((1+r)^n - 1)
    """
    if principal <= 0 or tenure_months <= 0:
        return 0.0
    r = (annual_rate_pct / 100.0) / 12.0
    if r == 0:
        return principal / tenure_months
    emi = principal * r * ((1 + r) ** tenure_months) / (((1 + r) ** tenure_months) - 1)
    return round(float(emi), 2)


def calculate_net_profit(monthly_gross_profit: float, monthly_fixed_cost: float, monthly_emi: float) -> float:
    """Calculate net disposable monthly surplus.
    
    TODO [Financial Lead]: Implement formula: gross_profit - fixed_cost - emi
    """
    return float(monthly_gross_profit - monthly_fixed_cost - monthly_emi)


def calculate_break_even(monthly_fixed_cost: float, monthly_emi: float, avg_ticket_price: float, variable_cost_pct: float, working_days: int) -> Dict[str, float]:
    """Calculate break-even monthly turnover and daily customer volume.
    
    TODO [Financial Lead]: Implement Contribution Margin Ratio (CMR) = 1 - (variable_cost_pct/100)
    """
    cmr = 1.0 - (variable_cost_pct / 100.0)
    if cmr <= 0 or avg_ticket_price <= 0 or working_days <= 0:
        return {"break_even_revenue_monthly": 0.0, "break_even_units_daily": 0.0}
    
    total_fixed_burden = monthly_fixed_cost + monthly_emi
    break_even_revenue = total_fixed_burden / cmr
    daily_revenue_needed = break_even_revenue / working_days
    daily_units = int(daily_revenue_needed / avg_ticket_price) + 1

    return {
        "break_even_revenue_monthly": round(break_even_revenue, 2),
        "break_even_units_daily": daily_units
    }


def calculate_repayment_capacity(monthly_net_operating_income: float, monthly_emi: float) -> float:
    """Compute Debt Service Coverage Ratio (DSCR).
    
    TODO [Financial Lead]: Implement DSCR = Net Operating Income / Monthly EMI
    """
    if monthly_emi <= 0:
        return 999.0  # Zero debt burden
    return round(monthly_net_operating_income / monthly_emi, 2)


class FinancialService(FinancialServiceInterface):
    """Concrete implementation of FinancialService with deterministic computations."""

    def calculate(self, own_capital: float, desired_loan: float, financials: FinancialAssumptionsInput) -> FinancialResultResponse:
        total_capex = financials.startup_cost + financials.equipment_cost + financials.inventory_cost
        required_loan = desired_loan if desired_loan > 0 else calculate_loan_requirement(total_capex, own_capital)
        
        monthly_rev = calculate_revenue(financials.customers_per_day, financials.avg_ticket_price, financials.working_days_per_month)
        monthly_var = calculate_variable_cost(monthly_rev, financials.variable_cost_pct)
        monthly_gross = calculate_gross_profit(monthly_rev, monthly_var)
        
        emi = calculate_emi(required_loan, financials.interest_rate_pct, financials.loan_tenure_months)
        monthly_net = calculate_net_profit(monthly_gross, financials.monthly_fixed_cost, emi)
        
        be_data = calculate_break_even(financials.monthly_fixed_cost, emi, financials.avg_ticket_price, financials.variable_cost_pct, financials.working_days_per_month)
        net_operating_income = monthly_gross - financials.monthly_fixed_cost
        dscr = calculate_repayment_capacity(net_operating_income, emi)
        
        margin_pct = round((monthly_net / monthly_rev * 100.0), 2) if monthly_rev > 0 else 0.0
        is_viable = (monthly_net > 0) and (dscr >= 1.25)

        return FinancialResultResponse(
            total_capex=total_capex,
            required_loan_amount=required_loan,
            monthly_revenue=monthly_rev,
            monthly_variable_cost=monthly_var,
            monthly_gross_profit=monthly_gross,
            monthly_fixed_cost=financials.monthly_fixed_cost,
            monthly_emi=emi,
            monthly_net_profit=monthly_net,
            net_profit_margin_pct=margin_pct,
            break_even_revenue_monthly=be_data["break_even_revenue_monthly"],
            break_even_units_daily=int(be_data["break_even_units_daily"]),
            dscr=dscr,
            is_financially_viable=is_viable
        )

    def calculate_break_even(self, fixed_costs: float, emi: float, avg_price: float, variable_cost_pct: float, working_days: int) -> Dict[str, float]:
        return calculate_break_even(fixed_costs, emi, avg_price, variable_cost_pct, working_days)

    def calculate_emi(self, principal: float, annual_rate_pct: float, tenure_months: int) -> float:
        return calculate_emi(principal, annual_rate_pct, tenure_months)

    def calculate_repayment(self, net_operating_income: float, monthly_emi: float) -> float:
        return calculate_repayment_capacity(net_operating_income, monthly_emi)
