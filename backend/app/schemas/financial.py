from typing import List, Optional
from pydantic import BaseModel, Field


class FinancialAssumptionsInput(BaseModel):
    """Input parameters for unit economics and financial modeling."""
    startup_cost: float = Field(..., ge=0.0, description="One-time registration, civil works, shed prep (INR)")
    equipment_cost: float = Field(..., ge=0.0, description="Machinery, tools, fixtures (INR)")
    inventory_cost: float = Field(..., ge=0.0, description="Initial stock and raw materials (INR)")
    monthly_fixed_cost: float = Field(..., ge=0.0, description="Rent, utility base fees, wages (INR)")
    customers_per_day: int = Field(..., ge=0, description="Expected daily customer footfall/orders")
    avg_ticket_price: float = Field(..., ge=0.0, description="Average order value / price per unit (INR)")
    working_days_per_month: int = Field(26, ge=1, le=31, description="Operating days per month")
    variable_cost_pct: float = Field(..., ge=0.0, le=100.0, description="COGS / variable cost as % of revenue")
    interest_rate_pct: float = Field(10.5, ge=0.0, le=40.0, description="Annual loan interest rate %")
    loan_tenure_months: int = Field(36, ge=1, le=120, description="Loan repayment tenure in months")


class FinancialCalculationRequest(BaseModel):
    own_capital: float = Field(0.0, ge=0.0, description="Available own equity (INR)")
    desired_loan: Optional[float] = Field(None, ge=0.0, description="Requested bank loan (INR)")
    financials: FinancialAssumptionsInput


class FinancialResultResponse(BaseModel):
    total_capex: float = Field(..., description="Total initial capital outlay (INR)")
    required_loan_amount: float = Field(..., description="Estimated loan requirement after equity contribution (INR)")
    monthly_revenue: float = Field(..., description="Estimated gross monthly revenue (INR)")
    monthly_variable_cost: float = Field(..., description="Estimated monthly variable cost (INR)")
    monthly_gross_profit: float = Field(..., description="Gross profit before fixed costs and EMI (INR)")
    monthly_fixed_cost: float = Field(..., description="Monthly recurring fixed costs (INR)")
    monthly_emi: float = Field(..., description="Estimated monthly loan repayment (INR)")
    monthly_net_profit: float = Field(..., description="Net disposable profit after all costs and EMI (INR)")
    net_profit_margin_pct: float = Field(..., description="Net profit as percentage of monthly revenue")
    break_even_revenue_monthly: float = Field(..., description="Minimum monthly revenue to avoid loss (INR)")
    break_even_units_daily: int = Field(..., description="Daily customer count / units needed to break even")
    dscr: float = Field(..., description="Debt Service Coverage Ratio")
    is_financially_viable: bool = Field(..., description="Deterministic boolean check of profitability & DSCR >= 1.25")


class SensitivityScenario(BaseModel):
    scenario_name: str = Field(..., description="Scenario title (e.g. -20% Demand)")
    monthly_revenue: float
    monthly_net_profit: float
    break_even_revenue: float
    dscr: float
    status: str = Field(..., description="VIABLE, STRESSED, INSOLVENT")


class SensitivityRequest(BaseModel):
    calculation: FinancialCalculationRequest


class SensitivityResponse(BaseModel):
    baseline: FinancialResultResponse
    scenarios: List[SensitivityScenario]
    resilience_rating: str = Field(..., description="HIGH, MODERATE, LOW")
