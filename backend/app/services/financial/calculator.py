import math
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.schemas.financial import FinancialAssumptionsInput, FinancialResultResponse


class FinancialServiceInterface(ABC):
    """Abstract interface defining required financial engine operations."""

    @abstractmethod
    def calculate(self, own_capital: float, desired_loan: Optional[float], financials: FinancialAssumptionsInput) -> FinancialResultResponse:
        """Calculate complete unit economics, Capex, and profitability."""
        pass

    @abstractmethod
    def calculate_break_even(self, fixed_costs: float, emi: float, avg_price: float, variable_cost_pct: float, working_days: int) -> Dict[str, Any]:
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
    """Calculate monthly estimated gross revenue deterministically.
    
    Formula:
        Daily Revenue = customers_per_day * avg_ticket_price
        Monthly Revenue = Daily Revenue * working_days
    """
    if customers_per_day <= 0 or avg_ticket_price <= 0.0 or working_days <= 0:
        return 0.0
    return round(float(customers_per_day * avg_ticket_price * working_days), 2)


def calculate_variable_cost(monthly_revenue: float, variable_cost_pct: float) -> float:
    """Calculate monthly variable operating cost from COGS percentage.
    
    Formula:
        Monthly Variable Cost = monthly_revenue * (variable_cost_pct / 100.0)
    """
    if monthly_revenue <= 0.0 or variable_cost_pct <= 0.0:
        return 0.0
    return round(float(monthly_revenue * (variable_cost_pct / 100.0)), 2)


def calculate_fixed_cost(monthly_fixed_cost: float) -> float:
    """Calculate total monthly recurring fixed overheads."""
    return round(max(0.0, float(monthly_fixed_cost)), 2)


def calculate_gross_profit(monthly_revenue: float, monthly_variable_cost: float) -> float:
    """Calculate monthly gross profit before fixed overheads and EMI.
    
    Formula:
        Monthly Gross Profit = monthly_revenue - monthly_variable_cost
    """
    return round(float(monthly_revenue - monthly_variable_cost), 2)


def calculate_loan_requirement(total_capex: float, own_capital: float) -> float:
    """Calculate net borrowing requirement after equity/own capital contribution.
    
    Formula:
        Loan Requirement = max(0.0, total_capex - own_capital)
    """
    return round(max(0.0, float(total_capex - max(0.0, own_capital))), 2)


def calculate_emi(principal: float, annual_rate_pct: float, tenure_months: int) -> float:
    """Calculate monthly loan installment using standard reducing-balance amortization formula.
    
    Formula:
        r = (annual_rate_pct / 100.0) / 12.0
        EMI = principal * r * (1 + r)^n / ((1 + r)^n - 1)
    
    Special Cases:
        - If principal <= 0 or tenure_months <= 0: EMI = 0.0
        - If annual_rate_pct == 0: EMI = principal / tenure_months
    """
    if principal <= 0.0 or tenure_months <= 0:
        return 0.0
    if annual_rate_pct <= 0.0:
        return round(float(principal / tenure_months), 2)
    
    r = (annual_rate_pct / 100.0) / 12.0
    rate_factor = (1.0 + r) ** tenure_months
    if rate_factor <= 1.0:
        return round(float(principal / tenure_months), 2)
    
    emi = principal * r * rate_factor / (rate_factor - 1.0)
    return round(float(emi), 2)


def calculate_net_profit(monthly_gross_profit: float, monthly_fixed_cost: float, monthly_emi: float) -> float:
    """Calculate net disposable monthly profit after all operating costs and debt obligations.
    
    Formula:
        Monthly Net Profit = monthly_gross_profit - monthly_fixed_cost - monthly_emi
    """
    return round(float(monthly_gross_profit - monthly_fixed_cost - monthly_emi), 2)


def calculate_break_even(
    monthly_fixed_cost: float,
    monthly_emi: float,
    avg_ticket_price: float,
    variable_cost_pct: float,
    working_days: int
) -> Dict[str, Any]:
    """Calculate monthly break-even revenue and daily units needed to cover fixed overheads and debt service.
    
    Formulas:
        Contribution Margin Ratio (CMR) = 1.0 - (variable_cost_pct / 100.0)
        Total Fixed Burden = monthly_fixed_cost + monthly_emi
        Break-Even Monthly Revenue = Total Fixed Burden / CMR
        Break-Even Daily Units = ceil(Break-Even Monthly Revenue / (avg_ticket_price * working_days))
    
    Safe handling:
        If CMR <= 0, avg_ticket_price <= 0, or working_days <= 0, returns 0.0 / 0.
    """
    cmr = 1.0 - (variable_cost_pct / 100.0)
    if cmr <= 0.0 or avg_ticket_price <= 0.0 or working_days <= 0:
        return {"break_even_revenue_monthly": 0.0, "break_even_units_daily": 0}
    
    total_fixed_burden = max(0.0, monthly_fixed_cost) + max(0.0, monthly_emi)
    if total_fixed_burden == 0.0:
        return {"break_even_revenue_monthly": 0.0, "break_even_units_daily": 0}
    
    break_even_revenue = total_fixed_burden / cmr
    daily_revenue_needed = break_even_revenue / working_days
    daily_units = math.ceil(daily_revenue_needed / avg_ticket_price)

    return {
        "break_even_revenue_monthly": round(float(break_even_revenue), 2),
        "break_even_units_daily": int(daily_units)
    }


def calculate_repayment_capacity(monthly_net_operating_income: float, monthly_emi: float) -> float:
    """Compute Debt Service Coverage Ratio (DSCR).
    
    Formula:
        DSCR = monthly_net_operating_income / monthly_emi
    
    Notes:
        - Numerator: Net Operating Income (Monthly Gross Profit - Monthly Fixed Costs),
          representing cash available for debt service BEFORE loan repayment.
        - If monthly_emi <= 0: Returns 0.0 (Debt-free; no debt servicing obligation).
        - If monthly_net_operating_income <= 0: Returns 0.0 (Operating deficit).
    """
    if monthly_emi <= 0.0:
        return 0.0
    if monthly_net_operating_income <= 0.0:
        return 0.0
    return round(float(monthly_net_operating_income / monthly_emi), 2)


class FinancialService(FinancialServiceInterface):
    """Concrete implementation of FinancialService with deterministic computations."""

    def calculate(
        self,
        own_capital: float,
        desired_loan: Optional[float],
        financials: FinancialAssumptionsInput
    ) -> FinancialResultResponse:
        total_capex = round(float(financials.startup_cost + financials.equipment_cost + financials.inventory_cost), 2)
        
        if desired_loan is not None and desired_loan > 0.0:
            required_loan = round(float(desired_loan), 2)
        else:
            required_loan = calculate_loan_requirement(total_capex, own_capital)
        
        monthly_rev = calculate_revenue(
            financials.customers_per_day,
            financials.avg_ticket_price,
            financials.working_days_per_month
        )
        monthly_var = calculate_variable_cost(monthly_rev, financials.variable_cost_pct)
        monthly_gross = calculate_gross_profit(monthly_rev, monthly_var)
        
        emi = calculate_emi(required_loan, financials.interest_rate_pct, financials.loan_tenure_months)
        monthly_net = calculate_net_profit(monthly_gross, financials.monthly_fixed_cost, emi)
        
        net_operating_income = monthly_gross - financials.monthly_fixed_cost
        dscr = calculate_repayment_capacity(net_operating_income, emi)
        
        be_data = calculate_break_even(
            financials.monthly_fixed_cost,
            emi,
            financials.avg_ticket_price,
            financials.variable_cost_pct,
            financials.working_days_per_month
        )
        
        margin_pct = round((monthly_net / monthly_rev * 100.0), 2) if monthly_rev > 0.0 else 0.0
        
        # Viability: profitable after all costs and healthy debt servicing (or debt-free)
        if emi > 0.0:
            is_viable = (monthly_net > 0.0) and (dscr >= 1.25)
        else:
            is_viable = monthly_net > 0.0

        from app.services.financial.explainer import FinancialExplainer

        res = FinancialResultResponse(
            total_capex=total_capex,
            required_loan_amount=required_loan,
            monthly_revenue=monthly_rev,
            monthly_variable_cost=monthly_var,
            monthly_gross_profit=monthly_gross,
            monthly_fixed_cost=round(float(financials.monthly_fixed_cost), 2),
            monthly_emi=emi,
            monthly_net_profit=monthly_net,
            net_profit_margin_pct=margin_pct,
            break_even_revenue_monthly=be_data["break_even_revenue_monthly"],
            break_even_units_daily=int(be_data["break_even_units_daily"]),
            dscr=dscr,
            is_financially_viable=is_viable
        )
        res.explanations = FinancialExplainer.generate_explanations(
            own_capital=own_capital,
            desired_loan=desired_loan,
            financials=financials,
            result=res
        )
        return res

    def calculate_break_even(
        self,
        fixed_costs: float,
        emi: float,
        avg_price: float,
        variable_cost_pct: float,
        working_days: int
    ) -> Dict[str, Any]:
        return calculate_break_even(fixed_costs, emi, avg_price, variable_cost_pct, working_days)

    def calculate_emi(self, principal: float, annual_rate_pct: float, tenure_months: int) -> float:
        return calculate_emi(principal, annual_rate_pct, tenure_months)

    def calculate_repayment(self, net_operating_income: float, monthly_emi: float) -> float:
        return calculate_repayment_capacity(net_operating_income, monthly_emi)
