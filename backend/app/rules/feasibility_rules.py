from typing import Tuple, List
from app.schemas.analysis import RecommendationStatus, RuleEvaluation, DecisionTrace
from app.schemas.financial import FinancialResultResponse
from app.schemas.market import MarketResultResponse


class FeasibilityRules:
    """Deterministic business feasibility verdict rules & decision trace engine.
    
    Guiding Principle:
    Evidence -> Calculate -> Explain -> Decide
    
    FeasibilityRules is the SINGLE authoritative source of truth for business verdicts.
    AI services, market signals, and explanations cannot override or mutate this authority.
    """

    @classmethod
    def evaluate_with_trace(
        cls,
        financials: FinancialResultResponse,
        market: MarketResultResponse
    ) -> Tuple[RecommendationStatus, DecisionTrace]:
        """Evaluate deterministic feasibility rules and produce a structured, transparent decision trace."""
        evaluations: List[RuleEvaluation] = []
        positives: List[str] = []
        cautions: List[str] = []

        # Rule 1: Operating Profitability (Net Profit > 0)
        net_profit = financials.monthly_net_profit
        if net_profit <= 0:
            evaluations.append(RuleEvaluation(
                rule_id="NET_PROFIT_POSITIVE",
                rule_name="Monthly Operating Profitability",
                condition="monthly_net_profit > 0",
                result="FAIL",
                severity="CRITICAL",
                explanation=f"Monthly net profit is negative (₹{net_profit:,.2f}). Operating at a deficit.",
                source="FeasibilityRules"
            ))
            cautions.append("Business generates a monthly operational deficit.")
        else:
            evaluations.append(RuleEvaluation(
                rule_id="NET_PROFIT_POSITIVE",
                rule_name="Monthly Operating Profitability",
                condition="monthly_net_profit > 0",
                result="PASS",
                severity="INFO",
                explanation=f"Monthly net profit is positive at ₹{net_profit:,.2f} after all variable costs, fixed overheads, and debt servicing.",
                source="FeasibilityRules"
            ))
            positives.append(f"Positive monthly operational surplus of ₹{net_profit:,.2f}.")

        # Rule 2: Solvency & Minimum Debt Coverage (DSCR >= 1.0)
        emi = financials.monthly_emi
        dscr = financials.dscr
        if emi > 0 and dscr < 1.0:
            evaluations.append(RuleEvaluation(
                rule_id="SOLVENCY_DSCR",
                rule_name="Solvency & Baseline Debt Coverage",
                condition="monthly_emi <= 0 or dscr >= 1.0",
                result="FAIL",
                severity="CRITICAL",
                explanation=f"DSCR of {dscr:.2f} is below insolvency threshold (1.00). Operating cash flow cannot service monthly loan EMI of ₹{emi:,.2f}.",
                source="FeasibilityRules"
            ))
            cautions.append(f"Insufficient cash flow to service monthly loan EMI (DSCR: {dscr:.2f} < 1.00).")
        elif emi > 0:
            evaluations.append(RuleEvaluation(
                rule_id="SOLVENCY_DSCR",
                rule_name="Solvency & Baseline Debt Coverage",
                condition="monthly_emi <= 0 or dscr >= 1.0",
                result="PASS",
                severity="INFO",
                explanation=f"DSCR of {dscr:.2f} meets baseline solvency threshold (>= 1.00) to cover monthly EMI of ₹{emi:,.2f}.",
                source="FeasibilityRules"
            ))
            positives.append(f"Operating cash flow covers debt obligations (DSCR: {dscr:.2f}).")
        else:
            evaluations.append(RuleEvaluation(
                rule_id="SOLVENCY_DSCR",
                rule_name="Solvency & Baseline Debt Coverage",
                condition="monthly_emi <= 0 or dscr >= 1.0",
                result="PASS",
                severity="INFO",
                explanation="Enterprise is debt-free with no monthly loan repayment obligations.",
                source="FeasibilityRules"
            ))
            positives.append("Debt-free enterprise with zero loan repayment burden.")

        # Rule 3: Strong Repayment Buffer (DSCR >= 1.50)
        strong_dscr_pass = (emi <= 0 or dscr >= 1.50)
        if emi > 0 and dscr >= 1.50:
            evaluations.append(RuleEvaluation(
                rule_id="STRONG_REPAYMENT_CAPACITY",
                rule_name="Strong Debt Service Safety Buffer",
                condition="monthly_emi <= 0 or dscr >= 1.50",
                result="PASS",
                severity="INFO",
                explanation=f"DSCR of {dscr:.2f} meets or exceeds strong safety buffer threshold (>= 1.50).",
                source="FeasibilityRules"
            ))
            positives.append(f"Strong debt servicing safety buffer (DSCR: {dscr:.2f} >= 1.50).")
        elif emi > 0 and 1.0 <= dscr < 1.50:
            evaluations.append(RuleEvaluation(
                rule_id="STRONG_REPAYMENT_CAPACITY",
                rule_name="Strong Debt Service Safety Buffer",
                condition="monthly_emi <= 0 or dscr >= 1.50",
                result="WARNING",
                severity="WARNING",
                explanation=f"DSCR of {dscr:.2f} is adequate (>= 1.00) but below the strong resilience benchmark of 1.50.",
                source="FeasibilityRules"
            ))
            cautions.append(f"DSCR of {dscr:.2f} is below strong safety benchmark (1.50), leaving lower resilience to demand drops.")
        elif emi <= 0:
            evaluations.append(RuleEvaluation(
                rule_id="STRONG_REPAYMENT_CAPACITY",
                rule_name="Strong Debt Service Safety Buffer",
                condition="monthly_emi <= 0 or dscr >= 1.50",
                result="PASS",
                severity="INFO",
                explanation="No debt servicing obligation.",
                source="FeasibilityRules"
            ))

        # Rule 4: Financial Viability Engine Check
        if financials.is_financially_viable:
            evaluations.append(RuleEvaluation(
                rule_id="FINANCIAL_VIABILITY",
                rule_name="Audited Financial Engine Viability",
                condition="is_financially_viable == True",
                result="PASS",
                severity="INFO",
                explanation="Deterministic financial engine confirms overall financial viability.",
                source="FeasibilityRules"
            ))
        else:
            evaluations.append(RuleEvaluation(
                rule_id="FINANCIAL_VIABILITY",
                rule_name="Audited Financial Engine Viability",
                condition="is_financially_viable == True",
                result="FAIL",
                severity="CRITICAL",
                explanation="Financial engine calculates negative profitability or insolvency.",
                source="FeasibilityRules"
            ))

        # Rule 5: Catchment Competitor Density (competitor_count <= 3)
        comp_count = market.competitor_count
        radius = market.catchment_radius_km
        if comp_count <= 3:
            evaluations.append(RuleEvaluation(
                rule_id="LOW_COMPETITION_CATCHMENT",
                rule_name="Catchment Competitor Density",
                condition="competitor_count <= 3",
                result="PASS",
                severity="INFO",
                explanation=f"{comp_count} direct mapped competitor(s) in {radius:g} km catchment (<= 3 units).",
                source="FeasibilityRules"
            ))
            positives.append(f"Manageable direct competitor density ({comp_count} units mapped within {radius:g} km).")
        else:
            evaluations.append(RuleEvaluation(
                rule_id="LOW_COMPETITION_CATCHMENT",
                rule_name="Catchment Competitor Density",
                condition="competitor_count <= 3",
                result="WARNING",
                severity="WARNING",
                explanation=f"{comp_count} direct mapped competitors in {radius:g} km catchment exceeds comfortable density threshold (3 units).",
                source="FeasibilityRules"
            ))
            cautions.append(f"High local competitor density ({comp_count} mapped units within {radius:g} km).")

        # Rule 6: OpenStreetMap Coverage Quality
        cov_conf = getattr(market, "coverage_confidence", "LOW")
        if cov_conf == "LOW":
            evaluations.append(RuleEvaluation(
                rule_id="MARKET_COVERAGE_QUALITY",
                rule_name="Geographic Data Coverage Confidence",
                condition="coverage_confidence != 'LOW'",
                result="WARNING",
                severity="WARNING",
                explanation="OpenStreetMap coverage is limited in rural catchment. A low mapped count does not prove absence of competition.",
                source="FeasibilityRules"
            ))
            cautions.append("Rural OpenStreetMap coverage is limited; on-ground physical competitor verification required.")
        else:
            evaluations.append(RuleEvaluation(
                rule_id="MARKET_COVERAGE_QUALITY",
                rule_name="Geographic Data Coverage Confidence",
                condition="coverage_confidence != 'LOW'",
                result="PASS",
                severity="INFO",
                explanation=f"Catchment competitor coverage confidence is {cov_conf}.",
                source="FeasibilityRules"
            ))

        # Determine Verdict
        has_critical_failure = any(e.result == "FAIL" for e in evaluations)
        if has_critical_failure or net_profit <= 0 or (emi > 0 and dscr < 1.0):
            status = RecommendationStatus.RECONSIDER
            summary = (
                "Business exhibits a financial deficit or insufficient operating cash flow to service debt obligations. "
                "Cost restructuring, pricing adjustments, or equity re-allocation are strongly advised before capital commitment."
            )
        elif strong_dscr_pass and financials.is_financially_viable and comp_count <= 3:
            status = RecommendationStatus.PROCEED
            summary = (
                "Business satisfies all financial viability criteria, demonstrates strong debt service coverage, "
                "and operates within a manageable local competitive catchment."
            )
        else:
            status = RecommendationStatus.VALIDATE_FIRST
            summary = (
                "Business is financially solvent but exhibits boundary conditions (moderate debt buffer or unverified rural market coverage). "
                "On-ground validation of footfall and competitor pricing is recommended before formal loan application."
            )

        trace = DecisionTrace(
            recommendation_status=status,
            summary=summary,
            rule_evaluations=evaluations,
            key_positive_factors=positives,
            key_caution_factors=cautions,
            authority="FeasibilityRules"
        )

        return status, trace

    @classmethod
    def determine_status(
        cls,
        financials: FinancialResultResponse,
        market: MarketResultResponse
    ) -> RecommendationStatus:
        """Evaluate hard decision rules for enterprise viability.
        
        Preserves 100% exact backward compatibility with previous steps.
        """
        status, _ = cls.evaluate_with_trace(financials=financials, market=market)
        return status
