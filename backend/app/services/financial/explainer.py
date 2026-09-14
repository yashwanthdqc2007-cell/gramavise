"""
Financial Explainer Service (Step 5C).

Provides declarative, render-ready metadata explaining how financial metrics were computed.

MANDATORY ARCHITECTURAL CONSTRAINTS:
1. FinancialService is the exclusive financial calculator.
2. FinancialExplainer NEVER duplicates or recalculates financial formulas.
3. It takes pre-computed FinancialResultResponse and inputs to format human-readable trace steps and substituted expressions.
4. Input parameters remain ASSUMED; derived metrics remain CALCULATED.
"""

from typing import Dict, List, Optional
from app.schemas.evidence import EvidenceType, EvidenceItem
from app.schemas.financial import (
    FinancialAssumptionsInput,
    FinancialResultResponse,
    NumberInputParameter,
    NumberExplanation,
)


class FinancialExplainer:
    """Assembles declarative explanation metadata from pre-computed financial results."""

    @staticmethod
    def generate_explanations(
        own_capital: float,
        desired_loan: Optional[float],
        financials: FinancialAssumptionsInput,
        result: FinancialResultResponse,
        evidence_ledger: Optional[List[EvidenceItem]] = None,
        is_scenario: bool = False,
    ) -> Dict[str, NumberExplanation]:
        """Generate comprehensive declarative explanation objects for all primary financial metrics."""
        explanations: Dict[str, NumberExplanation] = {}
        provenance_prefix = "Scenario Override: " if is_scenario else ""
        provenance_type = EvidenceType.ASSUMED

        is_debt_free = result.monthly_emi == 0.0 or result.dscr == 0.0 or result.required_loan_amount == 0.0

        # Helper to find related evidence IDs from ledger
        evidence_ids = [e.evidence_id for e in (evidence_ledger or []) if e.evidence_id]

        # -------------------------------------------------------------
        # 1. Total Capex (total_capex)
        # -------------------------------------------------------------
        explanations["total_capex"] = NumberExplanation(
            metric_id="total_capex",
            metric_name="Total Startup Outlay",
            plain_meaning="Total initial investment required to launch the business before opening day.",
            displayed_value=f"₹{result.total_capex:,.2f}",
            numeric_value=result.total_capex,
            unit="INR",
            provenance=EvidenceType.CALCULATED,
            formula_label="Setup & Civil Outlay + Machinery & Tools + Initial Inventory",
            formula_expression="startup_cost + equipment_cost + inventory_cost",
            substituted_expression=f"₹{financials.startup_cost:,.2f} + ₹{financials.equipment_cost:,.2f} + ₹{financials.inventory_cost:,.2f} = ₹{result.total_capex:,.2f}",
            inputs=[
                NumberInputParameter(
                    name="startup_cost",
                    label="Setup & Civil Prep",
                    raw_value=financials.startup_cost,
                    formatted_value=f"₹{financials.startup_cost:,.2f}",
                    provenance=provenance_type,
                    source_description=f"{provenance_prefix}User onboarding capital input",
                ),
                NumberInputParameter(
                    name="equipment_cost",
                    label="Machinery & Equipment",
                    raw_value=financials.equipment_cost,
                    formatted_value=f"₹{financials.equipment_cost:,.2f}",
                    provenance=provenance_type,
                    source_description=f"{provenance_prefix}User onboarding capital input",
                ),
                NumberInputParameter(
                    name="inventory_cost",
                    label="Initial Stock & Raw Materials",
                    raw_value=financials.inventory_cost,
                    formatted_value=f"₹{financials.inventory_cost:,.2f}",
                    provenance=provenance_type,
                    source_description=f"{provenance_prefix}User onboarding capital input",
                ),
            ],
            calculation_steps=[
                f"1. Setup / Civil Works: ₹{financials.startup_cost:,.2f}",
                f"2. Equipment & Machinery: ₹{financials.equipment_cost:,.2f}",
                f"3. Initial Inventory Stock: ₹{financials.inventory_cost:,.2f}",
                f"4. Total Startup Capital: ₹{result.total_capex:,.2f}",
            ],
            related_evidence_ids=[eid for eid in evidence_ids if "CAP" in eid or "FIN" in eid],
            limitations=[
                "Covers upfront setup only; ongoing operating expenses after opening are tracked separately.",
                "Assumes quotations and equipment pricing are firm.",
            ],
            is_debt_free=False,
        )

        # -------------------------------------------------------------
        # 2. Required Loan Amount (required_loan_amount)
        # -------------------------------------------------------------
        if desired_loan is not None and desired_loan > 0.0:
            loan_formula_label = "Requested Bank Loan (Explicit User Input)"
            loan_formula_expr = "desired_loan"
            loan_sub_expr = f"₹{result.required_loan_amount:,.2f} (Direct user request)"
            loan_provenance = EvidenceType.ASSUMED
            loan_steps = [
                f"1. Total Capital Outlay Required: ₹{result.total_capex:,.2f}",
                f"2. Available Own Equity: ₹{own_capital:,.2f}",
                f"3. Requested Bank Borrowing: ₹{result.required_loan_amount:,.2f}",
            ]
        else:
            loan_formula_label = "Total Startup Outlay − Available Own Equity"
            loan_formula_expr = "max(0.0, total_capex - own_capital)"
            loan_sub_expr = f"max(0.0, ₹{result.total_capex:,.2f} − ₹{own_capital:,.2f}) = ₹{result.required_loan_amount:,.2f}"
            loan_provenance = EvidenceType.CALCULATED
            loan_steps = [
                f"1. Total Capital Outlay: ₹{result.total_capex:,.2f}",
                f"2. Less Own Equity Contribution: ₹{own_capital:,.2f}",
                f"3. Net Bank Financing Required: ₹{result.required_loan_amount:,.2f}",
            ]

        explanations["required_loan_amount"] = NumberExplanation(
            metric_id="required_loan_amount",
            metric_name="Required Bank Loan",
            plain_meaning="The net financing required from a bank or government scheme after contributing your own savings.",
            displayed_value=f"₹{result.required_loan_amount:,.2f}",
            numeric_value=result.required_loan_amount,
            unit="INR",
            provenance=loan_provenance,
            formula_label=loan_formula_label,
            formula_expression=loan_formula_expr,
            substituted_expression=loan_sub_expr,
            inputs=[
                NumberInputParameter(
                    name="total_capex",
                    label="Total Capital Outlay",
                    raw_value=result.total_capex,
                    formatted_value=f"₹{result.total_capex:,.2f}",
                    provenance=EvidenceType.CALCULATED,
                    source_description="Deterministic Capex Sum (FinancialService)",
                ),
                NumberInputParameter(
                    name="own_capital",
                    label="Available Own Savings",
                    raw_value=own_capital,
                    formatted_value=f"₹{own_capital:,.2f}",
                    provenance=provenance_type,
                    source_description=f"{provenance_prefix}User onboarding profile equity",
                ),
            ],
            calculation_steps=loan_steps,
            related_evidence_ids=[eid for eid in evidence_ids if "SCHEME" in eid or "FIN" in eid],
            limitations=[
                "Actual loan sanction depends on bank appraisal, margin money norms, and credit policies.",
                "Schemes like PMEGP and MUDRA require mandatory promoter contribution (typically 5% to 10%).",
            ],
            is_debt_free=result.required_loan_amount == 0.0,
        )

        # -------------------------------------------------------------
        # 3. Monthly Revenue (monthly_revenue)
        # -------------------------------------------------------------
        daily_turnover_fmt = f"₹{(financials.customers_per_day * financials.avg_ticket_price):,.2f}"
        explanations["monthly_revenue"] = NumberExplanation(
            metric_id="monthly_revenue",
            metric_name="Monthly Gross Revenue",
            plain_meaning="Total estimated cash coming into the enterprise each month from customer sales.",
            displayed_value=f"₹{result.monthly_revenue:,.2f}",
            numeric_value=result.monthly_revenue,
            unit="INR/month",
            provenance=EvidenceType.CALCULATED,
            formula_label="Daily Customer Footfall × Average Billing Size × Working Days",
            formula_expression="(customers_per_day × avg_ticket_price) × working_days_per_month",
            substituted_expression=f"({financials.customers_per_day} × ₹{financials.avg_ticket_price:,.2f}) × {financials.working_days_per_month} days = ₹{result.monthly_revenue:,.2f}",
            inputs=[
                NumberInputParameter(
                    name="customers_per_day",
                    label="Expected Customers / Day",
                    raw_value=financials.customers_per_day,
                    formatted_value=f"{financials.customers_per_day} customers/day",
                    provenance=provenance_type,
                    source_description=f"{provenance_prefix}User estimated daily footfall",
                ),
                NumberInputParameter(
                    name="avg_ticket_price",
                    label="Average Sale / Order",
                    raw_value=financials.avg_ticket_price,
                    formatted_value=f"₹{financials.avg_ticket_price:,.2f}",
                    provenance=provenance_type,
                    source_description=f"{provenance_prefix}User estimated price per sale",
                ),
                NumberInputParameter(
                    name="working_days_per_month",
                    label="Operating Days / Month",
                    raw_value=financials.working_days_per_month,
                    formatted_value=f"{financials.working_days_per_month} days",
                    provenance=provenance_type,
                    source_description=f"{provenance_prefix}User operating schedule",
                ),
            ],
            calculation_steps=[
                f"1. Daily Sales Volume = {financials.customers_per_day} customers × ₹{financials.avg_ticket_price:,.2f} = {daily_turnover_fmt} / day",
                f"2. Monthly Turnover = {daily_turnover_fmt} × {financials.working_days_per_month} operating days = ₹{result.monthly_revenue:,.2f}",
            ],
            related_evidence_ids=[eid for eid in evidence_ids if "PRC" in eid or "MKT" in eid],
            limitations=[
                "Assumes continuous daily demand; bad weather, holidays, or local market closures may reduce actual monthly working days.",
                "Market prices should be cross-checked against local Mandi references.",
            ],
            is_debt_free=False,
        )

        # -------------------------------------------------------------
        # 4. Monthly Variable Cost (monthly_variable_cost)
        # -------------------------------------------------------------
        explanations["monthly_variable_cost"] = NumberExplanation(
            metric_id="monthly_variable_cost",
            metric_name="Monthly Variable Cost (COGS)",
            plain_meaning="Direct expenses for raw materials, inventory restock, and consumables that increase with every sale.",
            displayed_value=f"₹{result.monthly_variable_cost:,.2f}",
            numeric_value=result.monthly_variable_cost,
            unit="INR/month",
            provenance=EvidenceType.CALCULATED,
            formula_label="Monthly Revenue × Variable Cost Ratio",
            formula_expression="monthly_revenue × (variable_cost_pct / 100.0)",
            substituted_expression=f"₹{result.monthly_revenue:,.2f} × ({financials.variable_cost_pct}% / 100) = ₹{result.monthly_variable_cost:,.2f}",
            inputs=[
                NumberInputParameter(
                    name="monthly_revenue",
                    label="Monthly Gross Revenue",
                    raw_value=result.monthly_revenue,
                    formatted_value=f"₹{result.monthly_revenue:,.2f}",
                    provenance=EvidenceType.CALCULATED,
                    source_description="Deterministic Revenue (FinancialService)",
                ),
                NumberInputParameter(
                    name="variable_cost_pct",
                    label="Direct Cost Percentage",
                    raw_value=financials.variable_cost_pct,
                    formatted_value=f"{financials.variable_cost_pct}%",
                    provenance=provenance_type,
                    source_description=f"{provenance_prefix}User estimated COGS ratio",
                ),
            ],
            calculation_steps=[
                f"1. Monthly Turnover: ₹{result.monthly_revenue:,.2f}",
                f"2. Cost of Goods Sold: {financials.variable_cost_pct}% of sales",
                f"3. Monthly Variable Costs: ₹{result.monthly_variable_cost:,.2f}",
            ],
            related_evidence_ids=[eid for eid in evidence_ids if "FIN" in eid],
            limitations=[
                "Does not account for bulk wholesale discounts or seasonal input price spikes.",
                "Assumes material waste is contained within the stated cost percentage.",
            ],
            is_debt_free=False,
        )

        # -------------------------------------------------------------
        # 5. Monthly Gross Profit (monthly_gross_profit)
        # -------------------------------------------------------------
        explanations["monthly_gross_profit"] = NumberExplanation(
            metric_id="monthly_gross_profit",
            metric_name="Monthly Gross Profit",
            plain_meaning="Trading margin remaining after paying for raw materials and goods, before shop rent and loan repayments.",
            displayed_value=f"₹{result.monthly_gross_profit:,.2f}",
            numeric_value=result.monthly_gross_profit,
            unit="INR/month",
            provenance=EvidenceType.CALCULATED,
            formula_label="Monthly Revenue − Monthly Variable Costs",
            formula_expression="monthly_revenue - monthly_variable_cost",
            substituted_expression=f"₹{result.monthly_revenue:,.2f} − ₹{result.monthly_variable_cost:,.2f} = ₹{result.monthly_gross_profit:,.2f}",
            inputs=[
                NumberInputParameter(
                    name="monthly_revenue",
                    label="Monthly Gross Revenue",
                    raw_value=result.monthly_revenue,
                    formatted_value=f"₹{result.monthly_revenue:,.2f}",
                    provenance=EvidenceType.CALCULATED,
                    source_description="Deterministic Revenue (FinancialService)",
                ),
                NumberInputParameter(
                    name="monthly_variable_cost",
                    label="Monthly Variable Cost",
                    raw_value=result.monthly_variable_cost,
                    formatted_value=f"₹{result.monthly_variable_cost:,.2f}",
                    provenance=EvidenceType.CALCULATED,
                    source_description="Deterministic Variable Costs (FinancialService)",
                ),
            ],
            calculation_steps=[
                f"1. Total Inflow (Revenue): ₹{result.monthly_revenue:,.2f}",
                f"2. Direct Production Costs: ₹{result.monthly_variable_cost:,.2f}",
                f"3. Gross Trading Margin: ₹{result.monthly_gross_profit:,.2f}",
            ],
            related_evidence_ids=[eid for eid in evidence_ids if "FIN" in eid],
            limitations=[
                "Fixed costs (rent, wages) and EMI must still be paid out of this amount.",
            ],
            is_debt_free=False,
        )

        # -------------------------------------------------------------
        # 6. Monthly Fixed Cost (monthly_fixed_cost)
        # -------------------------------------------------------------
        explanations["monthly_fixed_cost"] = NumberExplanation(
            metric_id="monthly_fixed_cost",
            metric_name="Monthly Fixed Overheads",
            plain_meaning="Recurring monthly overhead expenses (rent, electricity base bills, salaries, license fees) that must be paid regardless of sales volume.",
            displayed_value=f"₹{result.monthly_fixed_cost:,.2f}",
            numeric_value=result.monthly_fixed_cost,
            unit="INR/month",
            provenance=provenance_type,
            formula_label="Recurring Monthly Operating Overheads",
            formula_expression="monthly_fixed_cost",
            substituted_expression=f"₹{result.monthly_fixed_cost:,.2f} (Self-reported recurring overheads)",
            inputs=[
                NumberInputParameter(
                    name="monthly_fixed_cost",
                    label="Monthly Overheads",
                    raw_value=financials.monthly_fixed_cost,
                    formatted_value=f"₹{financials.monthly_fixed_cost:,.2f}",
                    provenance=provenance_type,
                    source_description=f"{provenance_prefix}User onboarding operational input",
                ),
            ],
            calculation_steps=[
                f"1. Fixed overheads (Rent, Power, Wages, Maintenance): ₹{result.monthly_fixed_cost:,.2f} / month",
            ],
            related_evidence_ids=[eid for eid in evidence_ids if "FIN" in eid],
            limitations=[
                "Fixed expenses must be met even during zero-sales periods.",
                "Assumes rent and utility tariffs remain constant over the business cycle.",
            ],
            is_debt_free=False,
        )

        # -------------------------------------------------------------
        # 7. Monthly Loan EMI (monthly_emi)
        # -------------------------------------------------------------
        if is_debt_free or result.monthly_emi == 0.0:
            emi_label = "Debt-Free (Zero Bank Borrowing)"
            emi_expr = "0.0"
            emi_sub = "Principal = ₹0.00 → Monthly EMI = ₹0.00"
            emi_steps = ["1. Enterprise operates without bank debt.", "2. Monthly EMI obligation is ₹0.00."]
        else:
            emi_label = "Reducing Balance Loan Amortization"
            emi_expr = "P × r × (1+r)^n / ((1+r)^n - 1)"
            emi_sub = f"P = ₹{result.required_loan_amount:,.2f}, r = {financials.interest_rate_pct}% / 12, n = {financials.loan_tenure_months}m → EMI = ₹{result.monthly_emi:,.2f}"
            emi_steps = [
                f"1. Loan Principal: ₹{result.required_loan_amount:,.2f}",
                f"2. Annual Interest Rate: {financials.interest_rate_pct}% ({financials.interest_rate_pct/12:.3f}% per month)",
                f"3. Repayment Tenure: {financials.loan_tenure_months} months",
                f"4. Monthly Installment (EMI): ₹{result.monthly_emi:,.2f}",
            ]

        explanations["monthly_emi"] = NumberExplanation(
            metric_id="monthly_emi",
            metric_name="Monthly Loan EMI",
            plain_meaning="Fixed monthly repayment installment owed to the bank covering both principal and interest.",
            displayed_value=f"₹{result.monthly_emi:,.2f}" if not is_debt_free else "₹0.00 (Debt-Free)",
            numeric_value=result.monthly_emi,
            unit="INR/month",
            provenance=EvidenceType.CALCULATED,
            formula_label=emi_label,
            formula_expression=emi_expr,
            substituted_expression=emi_sub,
            inputs=[
                NumberInputParameter(
                    name="required_loan_amount",
                    label="Loan Principal",
                    raw_value=result.required_loan_amount,
                    formatted_value=f"₹{result.required_loan_amount:,.2f}",
                    provenance=EvidenceType.CALCULATED,
                    source_description="Deterministic Funding Requirement",
                ),
                NumberInputParameter(
                    name="interest_rate_pct",
                    label="Interest Rate",
                    raw_value=financials.interest_rate_pct,
                    formatted_value=f"{financials.interest_rate_pct}% p.a.",
                    provenance=provenance_type,
                    source_description=f"{provenance_prefix}Bank MSME lending benchmark",
                ),
                NumberInputParameter(
                    name="loan_tenure_months",
                    label="Tenure",
                    raw_value=financials.loan_tenure_months,
                    formatted_value=f"{financials.loan_tenure_months} months",
                    provenance=provenance_type,
                    source_description=f"{provenance_prefix}Loan repayment duration",
                ),
            ],
            calculation_steps=emi_steps,
            related_evidence_ids=[eid for eid in evidence_ids if "SCHEME" in eid or "FIN" in eid],
            limitations=[
                "Calculated using standard reducing balance method.",
                "Does not account for bank processing fees, GST on interest, or potential interest rate resets.",
            ],
            is_debt_free=is_debt_free,
        )

        # -------------------------------------------------------------
        # 8. Monthly Net Profit (monthly_net_profit)
        # -------------------------------------------------------------
        explanations["monthly_net_profit"] = NumberExplanation(
            metric_id="monthly_net_profit",
            metric_name="Monthly Net Profit",
            plain_meaning="Net disposable surplus remaining for the business owner after paying for all stock, fixed overheads, and monthly bank loan EMI.",
            displayed_value=f"₹{result.monthly_net_profit:,.2f}",
            numeric_value=result.monthly_net_profit,
            unit="INR/month",
            provenance=EvidenceType.CALCULATED,
            formula_label="Gross Profit − Fixed Costs − Monthly EMI",
            formula_expression="monthly_gross_profit - monthly_fixed_cost - monthly_emi",
            substituted_expression=f"₹{result.monthly_gross_profit:,.2f} − ₹{result.monthly_fixed_cost:,.2f} − ₹{result.monthly_emi:,.2f} = ₹{result.monthly_net_profit:,.2f}",
            inputs=[
                NumberInputParameter(
                    name="monthly_gross_profit",
                    label="Monthly Gross Profit",
                    raw_value=result.monthly_gross_profit,
                    formatted_value=f"₹{result.monthly_gross_profit:,.2f}",
                    provenance=EvidenceType.CALCULATED,
                    source_description="Trading Margin (FinancialService)",
                ),
                NumberInputParameter(
                    name="monthly_fixed_cost",
                    label="Fixed Overheads",
                    raw_value=result.monthly_fixed_cost,
                    formatted_value=f"₹{result.monthly_fixed_cost:,.2f}",
                    provenance=provenance_type,
                    source_description="Monthly Operating Overhead",
                ),
                NumberInputParameter(
                    name="monthly_emi",
                    label="Loan Repayment",
                    raw_value=result.monthly_emi,
                    formatted_value=f"₹{result.monthly_emi:,.2f}",
                    provenance=EvidenceType.CALCULATED,
                    source_description="Monthly Loan Obligation",
                ),
            ],
            calculation_steps=[
                f"1. Gross Trading Margin: ₹{result.monthly_gross_profit:,.2f}",
                f"2. Less Fixed Overheads: ₹{result.monthly_fixed_cost:,.2f}",
                f"3. Less Bank Loan EMI: ₹{result.monthly_emi:,.2f}",
                f"4. Net Disposable Profit: ₹{result.monthly_net_profit:,.2f}",
            ],
            related_evidence_ids=[eid for eid in evidence_ids if "FIN" in eid],
            limitations=[
                "Income taxes, owner's personal drawings, and emergency repairs are not deducted.",
                "A negative value indicates an operating deficit requiring capital restructuring.",
            ],
            is_debt_free=is_debt_free,
        )

        # -------------------------------------------------------------
        # 9. Monthly Break-Even Revenue (break_even_revenue_monthly)
        # -------------------------------------------------------------
        cmr_pct = round(100.0 - financials.variable_cost_pct, 2)
        explanations["break_even_revenue_monthly"] = NumberExplanation(
            metric_id="break_even_revenue_monthly",
            metric_name="Monthly Break-Even Revenue",
            plain_meaning="The minimum gross sales required each month so that trading margin exactly covers shop overheads and loan payments without loss.",
            displayed_value=f"₹{result.break_even_revenue_monthly:,.2f}",
            numeric_value=result.break_even_revenue_monthly,
            unit="INR/month",
            provenance=EvidenceType.CALCULATED,
            formula_label="Total Fixed Burden ÷ Contribution Margin Ratio",
            formula_expression="(monthly_fixed_cost + monthly_emi) / (1.0 - (variable_cost_pct / 100.0))",
            substituted_expression=f"(₹{result.monthly_fixed_cost:,.2f} + ₹{result.monthly_emi:,.2f}) ÷ ({cmr_pct}% / 100) = ₹{result.break_even_revenue_monthly:,.2f}",
            inputs=[
                NumberInputParameter(
                    name="monthly_fixed_cost",
                    label="Fixed Overheads",
                    raw_value=result.monthly_fixed_cost,
                    formatted_value=f"₹{result.monthly_fixed_cost:,.2f}",
                    provenance=provenance_type,
                    source_description="Monthly Overheads",
                ),
                NumberInputParameter(
                    name="monthly_emi",
                    label="Monthly EMI",
                    raw_value=result.monthly_emi,
                    formatted_value=f"₹{result.monthly_emi:,.2f}",
                    provenance=EvidenceType.CALCULATED,
                    source_description="Loan Repayment",
                ),
                NumberInputParameter(
                    name="variable_cost_pct",
                    label="Variable Cost %",
                    raw_value=financials.variable_cost_pct,
                    formatted_value=f"{financials.variable_cost_pct}%",
                    provenance=provenance_type,
                    source_description="COGS Percentage",
                ),
            ],
            calculation_steps=[
                f"1. Total Monthly Fixed Burden = Fixed Overhead (₹{result.monthly_fixed_cost:,.2f}) + EMI (₹{result.monthly_emi:,.2f}) = ₹{(result.monthly_fixed_cost + result.monthly_emi):,.2f}",
                f"2. Contribution Margin = 100% − {financials.variable_cost_pct}% = {cmr_pct}%",
                f"3. Break-Even Revenue = ₹{(result.monthly_fixed_cost + result.monthly_emi):,.2f} ÷ {cmr_pct/100:.2f} = ₹{result.break_even_revenue_monthly:,.2f}",
            ],
            related_evidence_ids=[eid for eid in evidence_ids if "BE" in eid or "FIN" in eid],
            limitations=[
                "Sales below this level create an immediate cash deficit.",
                "Assumes variable cost ratio remains steady as sales change.",
            ],
            is_debt_free=is_debt_free,
        )

        # -------------------------------------------------------------
        # 10. Daily Break-Even Customers (break_even_units_daily)
        # -------------------------------------------------------------
        daily_be_turnover = result.break_even_revenue_monthly / financials.working_days_per_month if financials.working_days_per_month > 0 else 0.0
        explanations["break_even_units_daily"] = NumberExplanation(
            metric_id="break_even_units_daily",
            metric_name="Daily Break-Even Customers",
            plain_meaning="Minimum paying customer footfall required each working day to cover all fixed costs and debt obligations.",
            displayed_value=f"{result.break_even_units_daily} customers/day",
            numeric_value=float(result.break_even_units_daily),
            unit="customers/day",
            provenance=EvidenceType.CALCULATED,
            formula_label="Daily Required Turnover ÷ Average Sale Per Customer",
            formula_expression="ceil(break_even_revenue_monthly / (avg_ticket_price * working_days_per_month))",
            substituted_expression=f"ceil(₹{result.break_even_revenue_monthly:,.2f} ÷ (₹{financials.avg_ticket_price:,.2f} × {financials.working_days_per_month} days)) = {result.break_even_units_daily} customers/day",
            inputs=[
                NumberInputParameter(
                    name="break_even_revenue_monthly",
                    label="Monthly Break-Even Revenue",
                    raw_value=result.break_even_revenue_monthly,
                    formatted_value=f"₹{result.break_even_revenue_monthly:,.2f}",
                    provenance=EvidenceType.CALCULATED,
                    source_description="Break-Even Threshold (FinancialService)",
                ),
                NumberInputParameter(
                    name="avg_ticket_price",
                    label="Average Sale / Customer",
                    raw_value=financials.avg_ticket_price,
                    formatted_value=f"₹{financials.avg_ticket_price:,.2f}",
                    provenance=provenance_type,
                    source_description=f"{provenance_prefix}Estimated ticket size",
                ),
                NumberInputParameter(
                    name="working_days_per_month",
                    label="Working Days / Month",
                    raw_value=financials.working_days_per_month,
                    formatted_value=f"{financials.working_days_per_month} days",
                    provenance=provenance_type,
                    source_description=f"{provenance_prefix}Operating days schedule",
                ),
            ],
            calculation_steps=[
                f"1. Daily Sales Target = ₹{result.break_even_revenue_monthly:,.2f} ÷ {financials.working_days_per_month} days = ₹{daily_be_turnover:,.2f} / day",
                f"2. Daily Customers Needed = ₹{daily_be_turnover:,.2f} ÷ ₹{financials.avg_ticket_price:,.2f} = {result.break_even_units_daily} customers / day",
            ],
            related_evidence_ids=[eid for eid in evidence_ids if "BE" in eid or "MKT" in eid],
            limitations=[
                "Assumes all customers spend the exact average ticket size.",
                "If customer footfall is less than this target, the business will lose money.",
            ],
            is_debt_free=is_debt_free,
        )

        # -------------------------------------------------------------
        # 11. Debt Service Coverage Ratio (DSCR) (dscr)
        # -------------------------------------------------------------
        net_op_inc = round(result.monthly_gross_profit - result.monthly_fixed_cost, 2)
        if is_debt_free:
            dscr_label = "Debt-Free Enterprise"
            dscr_expr = "N/A (Debt-Free)"
            dscr_sub = "Monthly EMI = ₹0.00 → Debt service obligation is zero."
            dscr_steps = [
                f"1. Net Operating Income: ₹{net_op_inc:,.2f}",
                "2. Monthly EMI: ₹0.00",
                "3. Enterprise is debt-free with zero repayment obligation (N/A).",
            ]
        else:
            dscr_label = "Net Operating Income ÷ Monthly Loan EMI"
            dscr_expr = "(monthly_gross_profit - monthly_fixed_cost) / monthly_emi"
            dscr_sub = f"₹{net_op_inc:,.2f} ÷ ₹{result.monthly_emi:,.2f} = {result.dscr:.2f}x"
            dscr_steps = [
                f"1. Gross Trading Margin: ₹{result.monthly_gross_profit:,.2f}",
                f"2. Less Fixed Overheads: ₹{result.monthly_fixed_cost:,.2f}",
                f"3. Net Operating Cash Available for Debt: ₹{net_op_inc:,.2f}",
                f"4. Monthly Loan EMI: ₹{result.monthly_emi:,.2f}",
                f"5. Repayment Cushion (DSCR): ₹{net_op_inc:,.2f} ÷ ₹{result.monthly_emi:,.2f} = {result.dscr:.2f}x",
            ]

        explanations["dscr"] = NumberExplanation(
            metric_id="dscr",
            metric_name="Debt Service Coverage Ratio (DSCR)",
            plain_meaning="The financial safety cushion showing how many times over your monthly operating cash covers your loan EMI payment.",
            displayed_value=f"{result.dscr:.2f}x" if not is_debt_free else "N/A (Debt-Free)",
            numeric_value=result.dscr,
            unit="ratio",
            provenance=EvidenceType.CALCULATED,
            formula_label=dscr_label,
            formula_expression=dscr_expr,
            substituted_expression=dscr_sub,
            inputs=[
                NumberInputParameter(
                    name="net_operating_income",
                    label="Operating Cash Available",
                    raw_value=net_op_inc,
                    formatted_value=f"₹{net_op_inc:,.2f}",
                    provenance=EvidenceType.CALCULATED,
                    source_description="Operating Cash before EMI (FinancialService)",
                ),
                NumberInputParameter(
                    name="monthly_emi",
                    label="Monthly EMI",
                    raw_value=result.monthly_emi,
                    formatted_value=f"₹{result.monthly_emi:,.2f}",
                    provenance=EvidenceType.CALCULATED,
                    source_description="Monthly Loan Installment",
                ),
            ],
            calculation_steps=dscr_steps,
            related_evidence_ids=[eid for eid in evidence_ids if "DSCR" in eid or "FIN" in eid],
            limitations=[
                "Commercial banks and MSME schemes typically require a minimum DSCR of 1.25x to 1.50x.",
                "A DSCR below 1.00x indicates operating cash cannot cover the required loan installment.",
            ],
            is_debt_free=is_debt_free,
        )

        # -------------------------------------------------------------
        # 12. Variable Cost Percentage (variable_cost_pct)
        # -------------------------------------------------------------
        explanations["variable_cost_pct"] = NumberExplanation(
            metric_id="variable_cost_pct",
            metric_name="Variable Cost Ratio (%)",
            plain_meaning="The portion of every ₹100 earned in sales that goes directly to buying raw stock, inventory, and packaging.",
            displayed_value=f"{financials.variable_cost_pct}%",
            numeric_value=financials.variable_cost_pct,
            unit="%",
            provenance=provenance_type,
            formula_label="Direct Cost of Goods Sold Percentage",
            formula_expression="variable_cost_pct",
            substituted_expression=f"{financials.variable_cost_pct}% of sales revenue",
            inputs=[
                NumberInputParameter(
                    name="variable_cost_pct",
                    label="Variable Cost Ratio",
                    raw_value=financials.variable_cost_pct,
                    formatted_value=f"{financials.variable_cost_pct}%",
                    provenance=provenance_type,
                    source_description=f"{provenance_prefix}User onboarding operational input",
                ),
            ],
            calculation_steps=[
                f"1. Variable Cost Proportion: {financials.variable_cost_pct}% of gross revenue.",
                f"2. For every ₹100 of customer billing, ₹{financials.variable_cost_pct:.2f} is spent on direct material costs.",
            ],
            related_evidence_ids=[eid for eid in evidence_ids if "FIN" in eid],
            limitations=[
                "Does not account for sudden supplier price increases or transportation freight spikes.",
            ],
            is_debt_free=False,
        )

        return explanations
