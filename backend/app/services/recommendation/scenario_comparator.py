import uuid
from typing import List, Dict, Any, Optional
from app.schemas.financial import FinancialAssumptionsInput, FinancialResultResponse
from app.schemas.market import MarketResultResponse
from app.schemas.analysis import RecommendationStatus, DecisionTrace, RiskFactor
from app.schemas.scenario import (
    ComparisonDirection,
    MetricComparison,
    RuleComparison,
    RecommendationChange,
    ScenarioEvaluationRequest,
    ScenarioEvaluationResponse
)
from app.services.financial.calculator import FinancialService
from app.services.financial.validation import (
    validate_financial_assumptions,
    validate_capital_inputs
)
from app.rules.feasibility_rules import FeasibilityRules
from app.services.recommendation.risk import assess_business_risks


class ScenarioComparator:
    """Deterministic comparator between baseline and user-modified scenario assumptions.
    
    Invariants:
    1. Reuses existing FinancialService.calculate() and FeasibilityRules.evaluate_with_trace().
    2. Baseline parameters and results remain strictly immutable.
    3. Market context is preserved identically between baseline and scenario.
    4. Deltas and rule changes are calculated deterministically with zero-denominator safety.
    """

    def __init__(self, financial_service: Optional[FinancialService] = None):
        self._financial_service = financial_service or FinancialService()

    def evaluate_scenario(self, request: ScenarioEvaluationRequest) -> ScenarioEvaluationResponse:
        """Calculate and compare scenario against baseline."""
        # 1. Validate Baseline & Scenario Inputs
        is_valid_bf, errors_bf = validate_financial_assumptions(request.baseline_financials)
        is_valid_bc, errors_bc = validate_capital_inputs(request.baseline_own_capital, request.baseline_desired_loan)
        baseline_errors = errors_bf + errors_bc
        if baseline_errors:
            raise ValueError(f"Invalid baseline inputs: {', '.join(baseline_errors)}")

        is_valid_sf, errors_sf = validate_financial_assumptions(request.scenario_financials)
        is_valid_sc, errors_sc = validate_capital_inputs(request.scenario_own_capital, request.scenario_desired_loan)
        scenario_errors = errors_sf + errors_sc
        if scenario_errors:
            raise ValueError(f"Invalid scenario inputs: {', '.join(scenario_errors)}")

        # 2. Compute Deterministic Financial Results
        baseline_res = self._financial_service.calculate(
            own_capital=request.baseline_own_capital,
            desired_loan=request.baseline_desired_loan,
            financials=request.baseline_financials
        )
        scenario_res = self._financial_service.calculate(
            own_capital=request.scenario_own_capital,
            desired_loan=request.scenario_desired_loan,
            financials=request.scenario_financials
        )
        from app.services.financial.explainer import FinancialExplainer
        scenario_res.explanations = FinancialExplainer.generate_explanations(
            own_capital=request.scenario_own_capital,
            desired_loan=request.scenario_desired_loan,
            financials=request.scenario_financials,
            result=scenario_res,
            is_scenario=True
        )

        # 3. Market Context Invariance
        market_context = request.market_context or MarketResultResponse(
            location_summary="Scenario Analysis Location",
            competitor_count=1,
            direct_competitor_count=1,
            coverage_confidence="MEDIUM",
            demand_indicator="MEDIUM"
        )

        # 4. Authoritative Recommendation & Decision Trace Evaluation
        base_status, base_trace = FeasibilityRules.evaluate_with_trace(baseline_res, market_context)
        scen_status, scen_trace = FeasibilityRules.evaluate_with_trace(scenario_res, market_context)

        # 5. Risk Assessment
        scenario_risks = assess_business_risks(scenario_res, market_context)

        # 6. Deterministic Metric Comparisons
        metric_comparisons = self._compare_metrics(baseline_res, scenario_res)

        # 7. Rule Trace Comparisons
        rule_comparisons = self._compare_rules(base_trace, scen_trace)

        # 8. Recommendation Change Synthesis
        rec_change = self._synthesize_recommendation_change(base_status, scen_status, rule_comparisons)

        # 9. "What Changed?" and "Why Did It Change?" Bullet Points
        what_changed = self._generate_what_changed(metric_comparisons, request)
        why_it_changed = self._generate_why_it_changed(base_status, scen_status, rule_comparisons, metric_comparisons)

        scenario_id = request.scenario_id or f"SCEN-{uuid.uuid4().hex[:8]}"

        return ScenarioEvaluationResponse(
            scenario_id=scenario_id,
            name=request.name,
            description=request.description,
            baseline_result=baseline_res,
            scenario_result=scenario_res,
            baseline_status=base_status,
            scenario_status=scen_status,
            baseline_decision_trace=base_trace,
            scenario_decision_trace=scen_trace,
            metric_comparisons=metric_comparisons,
            rule_comparisons=rule_comparisons,
            recommendation_change=rec_change,
            what_changed=what_changed,
            why_it_changed=why_it_changed,
            risk_factors=scenario_risks
        )

    def _compare_metrics(
        self,
        base: FinancialResultResponse,
        scen: FinancialResultResponse
    ) -> List[MetricComparison]:
        """Compute absolute and percentage deltas with safe direction tagging."""
        comparisons: List[MetricComparison] = []

        # Helper to compute metric row safely
        def add_comp(
            key: str,
            name: str,
            b_val: float,
            s_val: float,
            unit: str,
            higher_is_better: bool,
            is_debt: bool = False
        ):
            diff = round(s_val - b_val, 2)
            pct = None
            if abs(b_val) > 0.0001:
                pct = round((diff / abs(b_val)) * 100.0, 1)

            if abs(diff) < 0.001:
                direction = ComparisonDirection.UNCHANGED
                explanation = f"{name} remains unchanged at {b_val:,.2f} {unit}."
            elif is_debt:
                # Lower debt is generally improved from a solvency risk perspective
                direction = ComparisonDirection.IMPROVED if diff < 0 else ComparisonDirection.WORSENED
                explanation = f"{name} {'decreased' if diff < 0 else 'increased'} by {abs(diff):,.2f} {unit}."
            elif higher_is_better:
                direction = ComparisonDirection.IMPROVED if diff > 0 else ComparisonDirection.WORSENED
                explanation = f"{name} {'increased' if diff > 0 else 'decreased'} by {abs(diff):,.2f} {unit}."
            else:
                # Lower is better (e.g. EMI, break-even volume)
                direction = ComparisonDirection.IMPROVED if diff < 0 else ComparisonDirection.WORSENED
                explanation = f"{name} {'decreased' if diff < 0 else 'increased'} by {abs(diff):,.2f} {unit}."

            comparisons.append(MetricComparison(
                metric_key=key,
                metric_name=name,
                baseline_value=round(b_val, 2),
                scenario_value=round(s_val, 2),
                unit=unit,
                absolute_change=diff,
                percentage_change=pct,
                direction=direction,
                explanation=explanation
            ))

        add_comp("monthly_net_profit", "Monthly Net Profit", base.monthly_net_profit, scen.monthly_net_profit, "INR", higher_is_better=True)
        add_comp("dscr", "Debt Service Coverage (DSCR)", base.dscr, scen.dscr, "x", higher_is_better=True)
        add_comp("monthly_emi", "Monthly Loan EMI", base.monthly_emi, scen.monthly_emi, "INR", higher_is_better=False)
        add_comp("break_even_units_daily", "Daily Break-Even Footfall", float(base.break_even_units_daily), float(scen.break_even_units_daily), "units/day", higher_is_better=False)
        add_comp("net_profit_margin_pct", "Net Profit Margin", base.net_profit_margin_pct, scen.net_profit_margin_pct, "%", higher_is_better=True)
        add_comp("required_loan_amount", "Required Financing Outlay", base.required_loan_amount, scen.required_loan_amount, "INR", higher_is_better=False, is_debt=True)
        add_comp("monthly_revenue", "Monthly Gross Revenue", base.monthly_revenue, scen.monthly_revenue, "INR", higher_is_better=True)
        add_comp("total_capex", "Total Initial Capex", base.total_capex, scen.total_capex, "INR", higher_is_better=False)

        return comparisons

    def _compare_rules(
        self,
        base_trace: Optional[DecisionTrace],
        scen_trace: Optional[DecisionTrace]
    ) -> List[RuleComparison]:
        """Align and compare individual rule evaluations."""
        if not base_trace or not scen_trace:
            return []

        base_rules = {r.rule_id: r for r in base_trace.rule_evaluations}
        scen_rules = {r.rule_id: r for r in scen_trace.rule_evaluations}
        
        all_ids = list(dict.fromkeys(list(base_rules.keys()) + list(scen_rules.keys())))
        rule_comparisons: List[RuleComparison] = []

        for rid in all_ids:
            b_rule = base_rules.get(rid)
            s_rule = scen_rules.get(rid)
            b_res = b_rule.result if b_rule else "UNKNOWN"
            s_res = s_rule.result if s_rule else "UNKNOWN"
            r_name = s_rule.rule_name if s_rule else (b_rule.rule_name if b_rule else rid)

            changed = (b_res != s_res)
            if changed:
                explanation = f"Rule '{r_name}' shifted from {b_res} to {s_res} under scenario assumptions."
            else:
                explanation = f"Rule '{r_name}' remained {s_res}."

            rule_comparisons.append(RuleComparison(
                rule_id=rid,
                rule_name=r_name,
                baseline_result=b_res,
                scenario_result=s_res,
                changed=changed,
                explanation=explanation
            ))

        return rule_comparisons

    def _synthesize_recommendation_change(
        self,
        base_status: RecommendationStatus,
        scen_status: RecommendationStatus,
        rule_comps: List[RuleComparison]
    ) -> RecommendationChange:
        """Summarize recommendation transition and link triggered rules."""
        changed = (base_status != scen_status)
        reasons: List[str] = []

        for rc in rule_comps:
            if rc.changed:
                reasons.append(f"{rc.rule_name}: {rc.baseline_result} → {rc.scenario_result}")

        if changed:
            summary = f"Feasibility recommendation changed from {base_status.value} to {scen_status.value}."
        else:
            summary = f"Feasibility recommendation remains {scen_status.value}."

        return RecommendationChange(
            baseline_status=base_status,
            scenario_status=scen_status,
            changed=changed,
            summary=summary,
            reasons=reasons
        )

    def _generate_what_changed(
        self,
        metric_comps: List[MetricComparison],
        req: ScenarioEvaluationRequest
    ) -> List[str]:
        """Generate human-readable summary of meaningful metric and assumption deltas."""
        bullets: List[str] = []

        # Check assumption overrides
        if req.scenario_own_capital != req.baseline_own_capital:
            diff = req.scenario_own_capital - req.baseline_own_capital
            bullets.append(f"Own equity capital {'increased' if diff > 0 else 'decreased'} by ₹{abs(diff):,.2f}.")
        
        if (req.scenario_desired_loan or 0) != (req.baseline_desired_loan or 0):
            diff = (req.scenario_desired_loan or 0) - (req.baseline_desired_loan or 0)
            bullets.append(f"Desired borrowing {'increased' if diff > 0 else 'decreased'} by ₹{abs(diff):,.2f}.")

        if req.scenario_financials.customers_per_day != req.baseline_financials.customers_per_day:
            diff = req.scenario_financials.customers_per_day - req.baseline_financials.customers_per_day
            bullets.append(f"Expected customer footfall {'increased' if diff > 0 else 'decreased'} by {abs(diff)} customers/day.")

        if req.scenario_financials.avg_ticket_price != req.baseline_financials.avg_ticket_price:
            diff = req.scenario_financials.avg_ticket_price - req.baseline_financials.avg_ticket_price
            bullets.append(f"Average ticket price {'increased' if diff > 0 else 'decreased'} by ₹{abs(diff):,.2f}.")

        # Check key output deltas
        for m in metric_comps:
            if m.metric_key in ("monthly_net_profit", "dscr", "monthly_emi", "break_even_units_daily") and abs(m.absolute_change) > 0.01:
                direction_sym = "✓" if m.direction == ComparisonDirection.IMPROVED else ("⚠" if m.direction == ComparisonDirection.WORSENED else "•")
                pct_str = f" ({m.percentage_change:+.1f}%)" if m.percentage_change is not None else ""
                bullets.append(f"{direction_sym} {m.metric_name}: {m.baseline_value:,.2f} {m.unit} → {m.scenario_value:,.2f} {m.unit}{pct_str}")

        return bullets

    def _generate_why_it_changed(
        self,
        base_status: RecommendationStatus,
        scen_status: RecommendationStatus,
        rule_comps: List[RuleComparison],
        metric_comps: List[MetricComparison]
    ) -> List[str]:
        """Explain the causal chain linking scenario inputs → financial outputs → rule evaluations → verdict."""
        reasons: List[str] = []

        if base_status != scen_status:
            reasons.append(
                f"The scenario's adjusted assumptions altered financial unit economics, causing feasibility rules to transition the verdict from {base_status.value} to {scen_status.value}."
            )
            for rc in rule_comps:
                if rc.changed:
                    reasons.append(f"Rule '{rc.rule_name}' shifted from {rc.baseline_result} to {rc.scenario_result}.")
        else:
            reasons.append(
                f"Although specific metrics shifted, all evaluated feasibility rules maintained consistent status, keeping the recommendation at {scen_status.value}."
            )

        # Highlight key drivers (DSCR, profit, break-even)
        dscr_comp = next((m for m in metric_comps if m.metric_key == "dscr"), None)
        if dscr_comp and abs(dscr_comp.absolute_change) > 0.05:
            reasons.append(
                f"Debt service coverage shifted from {dscr_comp.baseline_value:.2f}x to {dscr_comp.scenario_value:.2f}x."
            )

        surplus_comp = next((m for m in metric_comps if m.metric_key == "monthly_net_profit"), None)
        if surplus_comp and abs(surplus_comp.absolute_change) > 100:
            reasons.append(
                f"Monthly net surplus shifted by ₹{surplus_comp.absolute_change:+,.2f} (from ₹{surplus_comp.baseline_value:,.2f} to ₹{surplus_comp.scenario_value:,.2f})."
            )

        return reasons
