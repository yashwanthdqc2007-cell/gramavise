from typing import List, Dict, Any, Optional
from app.schemas.analysis import (
    RecommendationStatus,
    DecisionTrace,
    RiskFactor
)
from app.schemas.financial import FinancialResultResponse
from app.schemas.market import MarketResultResponse
from app.schemas.scheme import SchemeMatchResult, MatchedSchemeDetail
from app.schemas.evidence import EvidenceItem, EvidenceType
from app.schemas.business import BusinessProfileBase
from app.schemas.action_plan import (
    ActionPriority,
    ActionCategory,
    ActionStatus,
    ActionSource,
    ActionItem,
    ActionPlan,
    DocumentStatus,
    DocumentItem,
    DocumentReadiness,
    ReadinessStatus,
    BankReadinessCategory,
    BankReadiness
)


class ActionPlanGenerator:
    """Deterministic generator for Pre-Loan Action Plans, Document Readiness, and Bank Readiness.
    
    Adheres to: Evidence → Calculate → Explain → Decide → Act.
    Strictly consumes existing analysis outputs without recalculating metrics or changing recommendation authority.
    """

    @classmethod
    def generate_action_plan(
        cls,
        recommendation_status: RecommendationStatus,
        financial_result: FinancialResultResponse,
        market_result: MarketResultResponse,
        scheme_result: SchemeMatchResult,
        evidence_ledger: List[EvidenceItem],
        decision_trace: Optional[DecisionTrace] = None,
        risks: Optional[List[RiskFactor]] = None,
        customers_per_day: Optional[int] = None
    ) -> ActionPlan:
        """Generate a deterministic, prioritized action plan tailored to the analysis results."""
        actions: List[ActionItem] = []
        seen_action_ids = set()

        def add_action(item: ActionItem):
            if item.action_id not in seen_action_ids:
                actions.append(item)
                seen_action_ids.add(item.action_id)

        # 1. Recommendation-Specific Core Roadmap
        if recommendation_status == RecommendationStatus.PROCEED:
            # Action 1: Capital Structure Confirmation
            if financial_result.required_loan_amount > 0:
                add_action(ActionItem(
                    action_id="ACT-CAP-001",
                    title="Confirm Final Financing Structure",
                    description=(
                        f"Review capex requirements: Total Project Outlay ₹{financial_result.total_capex:,.2f}, "
                        f"Promoter Contribution ₹{financial_result.total_capex - financial_result.required_loan_amount:,.2f}, "
                        f"Required Bank Borrowing ₹{financial_result.required_loan_amount:,.2f}."
                    ),
                    priority=ActionPriority.HIGH,
                    category=ActionCategory.FINANCIAL,
                    status=ActionStatus.RECOMMENDED,
                    action_source=ActionSource.FINANCIAL_RESULT,
                    reason="Modelled business case is financially feasible; finalize equity contribution and borrowing request.",
                    related_evidence_ids=["EV-FIN-SURPLUS"],
                    related_rule_ids=["FINANCIAL_VIABILITY"],
                    estimated_effort="1 day",
                    verification_required=False,
                    completion_effect="Prepares exact capital numbers for lender application discussion."
                ))

            # Action 2: Scheme Verification if schemes matched
            has_scheme_conditions = any(s.conditions_to_verify for s in scheme_result.schemes if s.eligibility_status in ("ELIGIBLE", "PARTIALLY_ELIGIBLE"))
            if has_scheme_conditions:
                add_action(ActionItem(
                    action_id="ACT-SCH-001",
                    title="Verify Matched Scheme Prerequisites",
                    description="Collate required statutory certificates and documentation for matched government schemes before bank submission.",
                    priority=ActionPriority.HIGH,
                    category=ActionCategory.SCHEME,
                    status=ActionStatus.TODO,
                    action_source=ActionSource.SCHEME_RESULT,
                    reason="Government credit schemes require pre-sanction document verification.",
                    related_evidence_ids=[e.evidence_id for e in evidence_ledger if e.evidence_id and e.evidence_id.startswith("EV-SCHEME-")],
                    related_rule_ids=[],
                    estimated_effort="2-3 days",
                    verification_required=True,
                    completion_effect="Ensures scheme subsidy and interest subvention eligibility during bank appraisal."
                ))

            # Action 3: Debt Repayment Buffer Check
            add_action(ActionItem(
                action_id="ACT-FIN-002",
                title="Review Repayment Cushion Under Stress",
                description=(
                    f"Baseline DSCR is {financial_result.dscr:.2f}x with monthly EMI of ₹{financial_result.monthly_emi:,.2f}. "
                    "Ensure adequate working cash buffer to maintain repayments during low-demand seasonal periods."
                ),
                priority=ActionPriority.MEDIUM,
                category=ActionCategory.FINANCIAL,
                status=ActionStatus.RECOMMENDED,
                action_source=ActionSource.DECISION_TRACE,
                reason="Adequate debt service coverage must be sustained throughout operational cycles.",
                related_evidence_ids=["EV-FIN-SURPLUS"],
                related_rule_ids=["STRONG_REPAYMENT_CAPACITY"],
                estimated_effort="Half day",
                verification_required=False,
                completion_effect="Builds operational cash buffer for uninterrupted loan servicing."
            ))

        elif recommendation_status == RecommendationStatus.VALIDATE_FIRST:
            # Action 1: Assumed Customer Volume Validation
            has_assumed_cust = any(e.evidence_id == "EV-USER-CUSTOMERS" and e.evidence_type == EvidenceType.ASSUMED for e in evidence_ledger)
            if has_assumed_cust:
                cust_val = customers_per_day if customers_per_day is not None else 50
                add_action(ActionItem(
                    action_id="ACT-ASM-001",
                    title="Validate Expected Customer Volume",
                    description=(
                        f"The revenue model relies on an assumed {cust_val} customers/day. "
                        "Conduct a 3-day manual footfall observation at the target site to verify daily traffic and peak buying hours."
                    ),
                    priority=ActionPriority.CRITICAL,
                    category=ActionCategory.VALIDATION,
                    status=ActionStatus.TODO,
                    action_source=ActionSource.EVIDENCE_LEDGER,
                    reason="Customer footfall is a self-declared assumption directly driving projected revenue and viability.",
                    related_evidence_ids=["EV-USER-CUSTOMERS"],
                    related_rule_ids=["FINANCIAL_VIABILITY"],
                    estimated_effort="2-3 days",
                    verification_required=True,
                    completion_effect="Provides verified daily volume baseline to update revenue and net profit calculations."
                ))

            # Action 2: Competitor Ground Survey
            has_unverified_mkt = any(
                e.evidence_id == "EV-MKT-COMPETITORS" and e.evidence_type == EvidenceType.NEEDS_VERIFICATION
                for e in evidence_ledger
            ) or market_result.direct_competitor_count == 0
            if has_unverified_mkt:
                add_action(ActionItem(
                    action_id="ACT-MKT-001",
                    title="Conduct Local Competitor Walk",
                    description=(
                        "Visit the primary village bazaar/road cluster within 5 km to locate and count active informal "
                        "or unmapped competitors offering similar goods or services."
                    ),
                    priority=ActionPriority.HIGH,
                    category=ActionCategory.MARKET,
                    status=ActionStatus.TODO,
                    action_source=ActionSource.MARKET_RESULT,
                    reason="Geospatial mapping returned zero or incomplete commercial POIs; on-ground survey is required to verify actual competitive density.",
                    related_evidence_ids=["EV-MKT-COMPETITORS"],
                    related_rule_ids=["MARKET_COVERAGE_QUALITY", "LOW_COMPETITION_CATCHMENT"],
                    estimated_effort="1 day",
                    verification_required=True,
                    completion_effect="Clarifies local market saturation and potential pricing pressure."
                ))

            # Action 3: Price Validation vs Wholesale Benchmarks
            has_mandi_price = any("Mandi" in (e.indicator or "") or "Agmarknet" in (e.source or "") for e in evidence_ledger)
            if has_mandi_price:
                add_action(ActionItem(
                    action_id="ACT-PRC-001",
                    title="Confirm Local Retail vs Wholesale Price",
                    description=(
                        "Distinguish official mandi wholesale benchmark prices from your target customer-facing retail price. "
                        "Survey 3 local shops or suppliers to confirm realistic local selling and procurement rates."
                    ),
                    priority=ActionPriority.HIGH,
                    category=ActionCategory.VALIDATION,
                    status=ActionStatus.TODO,
                    action_source=ActionSource.EVIDENCE_LEDGER,
                    reason="Wholesale mandi prices serve as market reference points and must not be confused with retail customer pricing.",
                    related_evidence_ids=[e.evidence_id for e in evidence_ledger if e.evidence_id and "PRICE" in e.evidence_id],
                    related_rule_ids=[],
                    estimated_effort="1 day",
                    verification_required=True,
                    completion_effect="Ensures gross margin assumptions reflect actual local retail reality."
                ))

            # Action 4: Debt Coverage Cushion Improvement
            if financial_result.dscr < 1.50 and financial_result.dscr >= 1.00:
                add_action(ActionItem(
                    action_id="ACT-FIN-003",
                    title="Improve Debt Service Safety Buffer",
                    description=(
                        f"Current DSCR is {financial_result.dscr:.2f}x (below the strong 1.50x benchmark). "
                        "Explore slightly higher equity contribution, lower overheads, or optimized ticket price to build a stronger safety margin."
                    ),
                    priority=ActionPriority.MEDIUM,
                    category=ActionCategory.FINANCIAL,
                    status=ActionStatus.RECOMMENDED,
                    action_source=ActionSource.DECISION_TRACE,
                    reason="Repayment capacity is mathematically solvent but provides limited buffer against revenue fluctuations.",
                    related_evidence_ids=["EV-FIN-SURPLUS"],
                    related_rule_ids=["STRONG_REPAYMENT_CAPACITY"],
                    estimated_effort="1 day",
                    verification_required=False,
                    completion_effect="Increases debt service coverage ratio to strengthen lender presentation."
                ))

            # Action 5: Re-run Feasibility Analysis
            add_action(ActionItem(
                action_id="ACT-RECALC-001",
                title="Update Business Assumptions and Re-run Analysis",
                description="After completing field observations and price checks, update the onboarding form to generate updated feasibility results.",
                priority=ActionPriority.MEDIUM,
                category=ActionCategory.BUSINESS_OPERATIONS,
                status=ActionStatus.TODO,
                action_source=ActionSource.DECISION_TRACE,
                reason="Field verification provides accurate inputs to recalculate unit economics and viability.",
                related_evidence_ids=[],
                related_rule_ids=[],
                estimated_effort="Immediate",
                verification_required=False,
                completion_effect="Replaces assumed values with verified ground evidence in GramaVise."
            ))

        elif recommendation_status == RecommendationStatus.RECONSIDER:
            # Action 1: Business Unit Economics Restructuring (CRITICAL)
            if financial_result.monthly_net_profit <= 0:
                add_action(ActionItem(
                    action_id="ACT-FIN-REWORK-001",
                    title="Restructure Business Unit Economics Before Borrowing",
                    description=(
                        f"Projected monthly net surplus is ₹{financial_result.monthly_net_profit:,.2f} (negative or zero). "
                        "Do not apply for credit in this state. Rework costs: reduce initial equipment capex, lower monthly recurring rent/wages, or adjust unit pricing."
                    ),
                    priority=ActionPriority.CRITICAL,
                    category=ActionCategory.FINANCIAL,
                    status=ActionStatus.TODO,
                    action_source=ActionSource.DECISION_TRACE,
                    reason="Business cannot service debt or sustain operations without positive operating cashflow.",
                    related_evidence_ids=["EV-FIN-SURPLUS"],
                    related_rule_ids=["NET_PROFIT_POSITIVE", "FINANCIAL_VIABILITY"],
                    estimated_effort="3-5 days",
                    verification_required=False,
                    completion_effect="Restores unit economics to positive operating surplus before any financing discussion."
                ))

            # Action 2: Break-Even Demand Pressure Re-assessment
            if financial_result.break_even_units_daily > 0:
                add_action(ActionItem(
                    action_id="ACT-MKT-REASSESS-001",
                    title="Reassess Required Daily Break-Even Sales Volume",
                    description=(
                        f"The business requires {financial_result.break_even_units_daily} sales/day just to cover fixed costs and EMI. "
                        "Evaluate if local village catchment demand can realistically support this daily volume."
                    ),
                    priority=ActionPriority.HIGH,
                    category=ActionCategory.MARKET,
                    status=ActionStatus.TODO,
                    action_source=ActionSource.FINANCIAL_RESULT,
                    reason="High break-even requirement increases risk of operational deficit during slower months.",
                    related_evidence_ids=["EV-FIN-BREAKEVEN"],
                    related_rule_ids=["FINANCIAL_VIABILITY"],
                    estimated_effort="2 days",
                    verification_required=True,
                    completion_effect="Helps right-size enterprise capacity to match actual local village demand."
                ))

            # Action 3: Test Smaller Financing / Phased Scenario
            add_action(ActionItem(
                action_id="ACT-CAP-REVISE-001",
                title="Test Smaller Financing or Revised Repayment Scenario",
                description=(
                    "Test a smaller financing requirement or revised repayment scenario before borrowing. "
                    "Explore starting with essential secondhand/modular equipment or higher own savings to reduce monthly debt obligations."
                ),
                priority=ActionPriority.HIGH,
                category=ActionCategory.FINANCIAL,
                status=ActionStatus.RECOMMENDED,
                action_source=ActionSource.FINANCIAL_RESULT,
                reason="Lower borrowing reduces monthly EMI burden and lowers the daily break-even threshold.",
                related_evidence_ids=["EV-FIN-SURPLUS"],
                related_rule_ids=["SOLVENCY_DSCR"],
                estimated_effort="1-2 days",
                verification_required=False,
                completion_effect="Allows testing if a leaner capital structure achieves financial viability."
            ))

        # 2. Scheme-Specific Document Actions (from matched schemes)
        for scheme in scheme_result.schemes:
            if scheme.eligibility_status in ("ELIGIBLE", "PARTIALLY_ELIGIBLE") and scheme.conditions_to_verify:
                for idx, cond in enumerate(scheme.conditions_to_verify):
                    act_id = f"ACT-DOC-{scheme.scheme_code}-{idx+1}"
                    add_action(ActionItem(
                        action_id=act_id,
                        title=f"Verify {scheme.scheme_code} Document: {cond.split('required')[0].strip() if 'required' in cond else cond[:40]}",
                        description=f"Statutory condition for {scheme.scheme_name}: {cond}. Obtain from relevant district department or Lead Bank.",
                        priority=ActionPriority.MEDIUM,
                        category=ActionCategory.DOCUMENTATION,
                        status=ActionStatus.TODO,
                        action_source=ActionSource.SCHEME_RESULT,
                        reason=f"Required for statutory subsidy / loan processing under {scheme.scheme_code}.",
                        related_evidence_ids=[e.evidence_id for e in evidence_ledger if e.evidence_id and scheme.scheme_code in e.evidence_id],
                        related_rule_ids=[],
                        estimated_effort="3-5 days",
                        verification_required=True,
                        completion_effect=f"Satisfies documentary eligibility prerequisite for {scheme.scheme_name}."
                    ))

        # Sort actions: CRITICAL -> HIGH -> MEDIUM -> LOW
        priority_order = {
            ActionPriority.CRITICAL: 0,
            ActionPriority.HIGH: 1,
            ActionPriority.MEDIUM: 2,
            ActionPriority.LOW: 3
        }
        actions.sort(key=lambda a: priority_order.get(a.priority, 99))

        crit_count = sum(1 for a in actions if a.priority == ActionPriority.CRITICAL)

        return ActionPlan(
            recommendation_status=recommendation_status,
            actions=actions,
            total_actions=len(actions),
            critical_actions_count=crit_count
        )

    @classmethod
    def generate_document_readiness(
        cls,
        scheme_result: SchemeMatchResult,
        evidence_ledger: Optional[List[EvidenceItem]] = None
    ) -> DocumentReadiness:
        """Generate document readiness items strictly supported by matched schemes and verified requirements.
        
        Does NOT invent universal checklists. If no scheme conditions exist, only returns verified scheme requirements.
        """
        documents: List[DocumentItem] = []
        seen_doc_ids = set()

        for scheme in scheme_result.schemes:
            if scheme.eligibility_status in ("ELIGIBLE", "PARTIALLY_ELIGIBLE"):
                for idx, cond in enumerate(scheme.conditions_to_verify):
                    doc_id = f"DOC-{scheme.scheme_code}-{idx+1}"
                    if doc_id not in seen_doc_ids:
                        documents.append(DocumentItem(
                            document_id=doc_id,
                            name=f"{scheme.scheme_code} Prerequisite: {cond}",
                            purpose=f"Documentary verification required for {scheme.scheme_name} sanction and subsidy disbursement.",
                            status=DocumentStatus.VERIFY,
                            required_for=scheme.scheme_name,
                            source=scheme.source_title or "Official Scheme Guidelines",
                            verification_status="NEEDS_VERIFICATION"
                        ))
                        seen_doc_ids.add(doc_id)

        req_count = sum(1 for d in documents if d.status == DocumentStatus.REQUIRED)
        ver_count = sum(1 for d in documents if d.status == DocumentStatus.VERIFY)
        done_count = sum(1 for d in documents if d.verification_status == "VERIFIED")

        return DocumentReadiness(
            documents=documents,
            required_count=req_count,
            verified_count=done_count,
            pending_count=ver_count
        )

    @classmethod
    def generate_bank_readiness(
        cls,
        recommendation_status: RecommendationStatus,
        financial_result: FinancialResultResponse,
        market_result: MarketResultResponse,
        scheme_result: SchemeMatchResult,
        evidence_ledger: List[EvidenceItem],
        action_plan: ActionPlan,
        document_readiness: DocumentReadiness
    ) -> BankReadiness:
        """Evaluate business case readiness across 5 deterministic dimensions.
        
        Strictly measures readiness for lender discussion. NOT a credit score or approval probability.
        """
        categories: List[BankReadinessCategory] = []

        # 1. FINANCIAL_CASE
        if financial_result.monthly_net_profit > 0 and financial_result.dscr >= 1.50 and financial_result.is_financially_viable:
            fin_status = ReadinessStatus.READY
            fin_reason = f"Viable unit economics: Positive monthly net profit (₹{financial_result.monthly_net_profit:,.2f}) and strong debt coverage (DSCR {financial_result.dscr:.2f}x >= 1.50x)."
        elif financial_result.monthly_net_profit > 0 and financial_result.dscr >= 1.00:
            fin_status = ReadinessStatus.PARTIALLY_READY
            fin_reason = f"Mathematically solvent (DSCR {financial_result.dscr:.2f}x >= 1.00x), but debt coverage is below the strong 1.50x buffer threshold."
        else:
            fin_status = ReadinessStatus.NOT_READY
            fin_reason = f"Unviable financial structure: Monthly net profit is ₹{financial_result.monthly_net_profit:,.2f} or DSCR is below 1.00x."
        
        categories.append(BankReadinessCategory(
            category="FINANCIAL_CASE",
            title="Financial Viability & Debt Coverage",
            status=fin_status,
            reason=fin_reason,
            supporting_evidence_ids=["EV-FIN-SURPLUS", "EV-FIN-BREAKEVEN"]
        ))

        # 2. MARKET_EVIDENCE
        if market_result.direct_competitor_count > 0 and market_result.coverage_confidence in ("HIGH", "MEDIUM"):
            mkt_status = ReadinessStatus.READY
            mkt_reason = f"Mapped market evidence available ({market_result.direct_competitor_count} direct competitors) with {market_result.coverage_confidence} coverage confidence."
        elif market_result.direct_competitor_count == 0 or market_result.coverage_confidence == "LOW":
            mkt_status = ReadinessStatus.PARTIALLY_READY
            mkt_reason = "OpenStreetMap returned 0 direct units or low coverage confidence; on-ground competitor walk recommended."
        else:
            mkt_status = ReadinessStatus.UNKNOWN
            mkt_reason = "Local market indicators could not be fully established."

        categories.append(BankReadinessCategory(
            category="MARKET_EVIDENCE",
            title="Local Catchment & Competitor Evidence",
            status=mkt_status,
            reason=mkt_reason,
            supporting_evidence_ids=["EV-MKT-COMPETITORS"]
        ))

        # 3. SCHEME_FIT
        eligible_schemes = [s for s in scheme_result.schemes if s.eligibility_status == "ELIGIBLE" and not s.conditions_to_verify]
        partial_schemes = [s for s in scheme_result.schemes if s.eligibility_status in ("ELIGIBLE", "PARTIALLY_ELIGIBLE")]
        if eligible_schemes:
            sch_status = ReadinessStatus.READY
            sch_reason = f"Direct match with {len(eligible_schemes)} government credit schemes with verified statutory criteria."
        elif partial_schemes:
            sch_status = ReadinessStatus.PARTIALLY_READY
            sch_reason = f"Matched {len(partial_schemes)} potential schemes with conditional documentary verification required."
        else:
            sch_status = ReadinessStatus.NOT_READY
            sch_reason = "No matching central credit schemes identified under current parameters."

        categories.append(BankReadinessCategory(
            category="SCHEME_FIT",
            title="Government Credit Scheme Alignment",
            status=sch_status,
            reason=sch_reason,
            supporting_evidence_ids=[e.evidence_id for e in evidence_ledger if e.evidence_id and e.evidence_id.startswith("EV-SCHEME-")]
        ))

        # 4. DOCUMENT_READINESS
        if document_readiness.pending_count == 0 and len(document_readiness.documents) > 0:
            doc_status = ReadinessStatus.READY
            doc_reason = "All scheme-supported documentary prerequisites are verified."
        elif document_readiness.pending_count > 0:
            doc_status = ReadinessStatus.PARTIALLY_READY
            doc_reason = f"{document_readiness.pending_count} scheme-supported documentary conditions require verification."
        else:
            doc_status = ReadinessStatus.UNKNOWN
            doc_reason = "No scheme-specific document requirements evaluated."

        categories.append(BankReadinessCategory(
            category="DOCUMENT_READINESS",
            title="Statutory Document Readiness",
            status=doc_status,
            reason=doc_reason,
            supporting_evidence_ids=[e.evidence_id for e in evidence_ledger if e.evidence_id and e.evidence_id.startswith("EV-COND-")]
        ))

        # 5. ASSUMPTION_QUALITY
        has_assumed = any(e.evidence_type == EvidenceType.ASSUMED for e in evidence_ledger)
        if has_assumed:
            asm_status = ReadinessStatus.PARTIALLY_READY
            asm_reason = "Key operating inputs (e.g. daily customer footfall) are applicant-stated assumptions requiring field confirmation."
        else:
            asm_status = ReadinessStatus.READY
            asm_reason = "Operational inputs are supported by verified or observed ground data."

        categories.append(BankReadinessCategory(
            category="ASSUMPTION_QUALITY",
            title="Operating Assumption Quality",
            status=asm_status,
            reason=asm_reason,
            supporting_evidence_ids=["EV-USER-CUSTOMERS"]
        ))

        # Determine Overall Readiness Status
        if recommendation_status == RecommendationStatus.PROCEED and fin_status == ReadinessStatus.READY:
            overall_status = ReadinessStatus.READY
            summary = "Business case and unit economics are well-structured for initial lender exploration. Address remaining documentation items."
        elif recommendation_status == RecommendationStatus.RECONSIDER or fin_status == ReadinessStatus.NOT_READY:
            overall_status = ReadinessStatus.NOT_READY
            summary = "Business model requires structural cost or demand adjustments before approaching lenders."
        else:
            overall_status = ReadinessStatus.PARTIALLY_READY
            summary = "Financial logic is solvent, but key market, volume, or scheme assumptions require on-ground validation."

        # Top 3 Action Titles
        top_actions = [a.title for a in action_plan.actions[:3]]

        return BankReadiness(
            overall_status=overall_status,
            summary=summary,
            categories=categories,
            top_actions=top_actions
        )
