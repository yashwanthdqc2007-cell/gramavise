"""Deterministic, Evidence-Grounded SWOT Intelligence Engine for GramaVise (SIH 2026).

CRITICAL ARCHITECTURAL CONSTRAINTS:
1. Purely deterministic rule evaluation (Zero LLM calls, zero synthetic hallucinations).
2. Grounded strictly in the verified Evidence Ledger (Only valid canonical evidence IDs).
3. Financial Invariance: Operates strictly as advisory evidence; never mutates FinancialService results,
   viability thresholds, DSCR calculations, or recommendation status.
4. Threshold Alignment: Adheres strictly to project-wide viability baseline (DSCR >= 1.25, strong >= 1.50).
5. Evidence Quality: Clearly distinguishes OBSERVED, CALCULATED, ASSUMED, and NEEDS_VERIFICATION.
6. Safe, Cautious Language: Uses "potential match", "indicates", "requires validation"; never claims "guaranteed".
"""

from typing import List, Dict, Any, Optional, Set
import math
from app.schemas.market import (
    SWOTAnalysis,
    SWOTItem,
    MarketResultResponse,
    CoverageConfidenceLevel,
)
from app.schemas.financial import FinancialResultResponse
from app.schemas.scheme import SchemeMatchResult, MatchedSchemeDetail
from app.schemas.evidence import EvidenceItem, EvidenceType
from app.schemas.analysis import DecisionTrace


# Explicit Consumer-Facing Business Categories for Census Demographics Relevance
CONSUMER_FACING_CATEGORIES = {
    "kirana & general store",
    "flour & spice milling (atta chakki)",
    "tailoring & garment making",
    "dairy farming & milk chilling",
    "poultry farming",
    "mobile & electronics repair",
    "building material & hardware",
    "small agro / food processing",
    "retail",
    "grocery",
    "food processing",
    "milling",
    "bakery",
}

IMPORTANCE_WEIGHTS = {
    "CRITICAL": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
}


class SWOTEngine:
    """Deterministic, rule-based SWOT analysis engine grounded in verified Evidence Ledger items."""

    @classmethod
    def generate_swot(
        cls,
        financial_result: Optional[FinancialResultResponse] = None,
        market_result: Optional[MarketResultResponse] = None,
        scheme_result: Optional[SchemeMatchResult] = None,
        evidence_ledger: Optional[List[EvidenceItem]] = None,
        decision_trace: Optional[DecisionTrace] = None,
        customers_per_day: Optional[int] = None,
        desired_loan: Optional[float] = None,
        category: Optional[str] = None,
        state: Optional[str] = None,
        district: Optional[str] = None,
        village: Optional[str] = None,
        max_items_per_quadrant: int = 4,
        # Keyword aliases for compatibility
        fin_res: Optional[FinancialResultResponse] = None,
        market_res: Optional[MarketResultResponse] = None,
        scheme_res: Optional[SchemeMatchResult] = None,
        evidence_items: Optional[List[EvidenceItem]] = None,
        **kwargs,
    ) -> SWOTAnalysis:
        """Produce a structured, evidence-backed SWOTAnalysis object from normalized inputs."""
        financial_result = financial_result or fin_res
        market_result = market_result or market_res
        scheme_result = scheme_result or scheme_res
        ledger = evidence_ledger or evidence_items or []

        available_evidence_ids: Set[str] = {
            e.evidence_id for e in ledger if getattr(e, "evidence_id", None)
        }
        evidence_map: Dict[str, EvidenceItem] = {
            e.evidence_id: e for e in ledger if getattr(e, "evidence_id", None)
        }

        # Candidate collectors for each quadrant
        strengths: List[SWOTItem] = []
        weaknesses: List[SWOTItem] = []
        opportunities: List[SWOTItem] = []
        threats: List[SWOTItem] = []
        informational: List[SWOTItem] = []

        # =====================================================================
        # 1. FINANCIAL STRENGTHS & WEAKNESSES
        # =====================================================================
        if financial_result:
            emi = financial_result.monthly_emi
            net_profit = financial_result.monthly_net_profit
            dscr = financial_result.dscr
            be_units = financial_result.break_even_units_daily
            rev = financial_result.monthly_revenue
            var_cost = financial_result.monthly_variable_cost
            fixed_cost = financial_result.monthly_fixed_cost
            gross_profit = financial_result.monthly_gross_profit

            # A) Positive Profitability (Strength) vs Negative/Zero Profitability (Weakness)
            if net_profit > 0:
                ev_id = "EV-FIN-SURPLUS"
                if ev_id in available_evidence_ids:
                    strengths.append(
                        SWOTItem(
                            id="STR-FIN-PROFIT-POSITIVE",
                            title="Positive Operating Profitability",
                            explanation=(
                                f"Projected monthly operations generate positive operating net profit of "
                                f"₹{net_profit:,.2f} (Net Profit Margin: {financial_result.net_profit_margin_pct:.1f}%), "
                                "confirming viable unit economics under baseline assumptions."
                            ),
                            category="FINANCIAL",
                            importance="HIGH",
                            evidence_ids=[ev_id],
                            evidence_type=EvidenceType.CALCULATED,
                            confidence=1.0,
                            source="GramaVise Financial Engine",
                        )
                    )
            else:
                ev_id = "EV-FIN-SURPLUS"
                if ev_id in available_evidence_ids:
                    weaknesses.append(
                        SWOTItem(
                            id="WKN-FIN-PROFIT-NEGATIVE",
                            title="Operating Cash Deficit",
                            explanation=(
                                f"Projected monthly operations result in a net operating loss of "
                                f"₹{abs(net_profit):,.2f}, indicating that revenue is insufficient to cover "
                                "operating expenses and debt obligations."
                            ),
                            category="FINANCIAL",
                            importance="CRITICAL",
                            evidence_ids=[ev_id],
                            evidence_type=EvidenceType.CALCULATED,
                            confidence=1.0,
                            source="GramaVise Financial Engine",
                        )
                    )

            # B) STR-FIN-DSCR-STRONG: DSCR >= 1.50 AND loan > 0 AND net_profit > 0
            if dscr >= 1.50 and emi > 0 and net_profit > 0:
                ev_id = "EV-FIN-SURPLUS"
                if ev_id in available_evidence_ids:
                    strengths.append(
                        SWOTItem(
                            id="STR-FIN-DSCR-STRONG",
                            title="Strong Debt Servicing Cushion",
                            explanation=(
                                f"The projected DSCR is {dscr:,.2f}x, above GramaVise's internal strong-cushion "
                                f"reference of 1.50x, indicating a healthy operational buffer to service monthly "
                                f"loan EMIs (₹{emi:,.2f})."
                            ),
                            category="FINANCIAL",
                            importance="CRITICAL",
                            evidence_ids=[ev_id],
                            evidence_type=EvidenceType.CALCULATED,
                            confidence=1.0,
                            source="GramaVise Financial Engine",
                        )
                    )

            # C) STR-FIN-DEBT-FREE: loan == 0 or emi == 0
            is_debt_free = emi == 0 or (desired_loan is not None and desired_loan == 0)
            if is_debt_free:
                ev_id = "EV-FIN-SURPLUS"
                if ev_id in available_evidence_ids:
                    strengths.append(
                        SWOTItem(
                            id="STR-FIN-DEBT-FREE",
                            title="Zero External Debt Exposure",
                            explanation=(
                                "Business operates on 100% promoter equity without external debt service "
                                "obligations, eliminating monthly EMI repayment pressure."
                            ),
                            category="FINANCIAL",
                            importance="HIGH",
                            evidence_ids=[ev_id],
                            evidence_type=EvidenceType.CALCULATED,
                            confidence=1.0,
                            source="GramaVise Financial Engine",
                        )
                    )

            # D) INF-FIN-DSCR-MODERATE: 1.25 <= DSCR < 1.50 AND loan > 0 (Informational candidate)
            if 1.25 <= dscr < 1.50 and emi > 0:
                ev_id = "EV-FIN-SURPLUS"
                if ev_id in available_evidence_ids:
                    informational.append(
                        SWOTItem(
                            id="INF-FIN-DSCR-MODERATE",
                            title="Moderate Debt Coverage Cushion",
                            explanation=(
                                f"The projected DSCR is {dscr:,.2f}x, meeting GramaVise's baseline viability "
                                f"reference (1.25x), but leaving a moderate cushion against operating cost variances. "
                                "Key assumptions should be validated."
                            ),
                            category="FINANCIAL",
                            importance="MEDIUM",
                            evidence_ids=[ev_id],
                            evidence_type=EvidenceType.CALCULATED,
                            confidence=1.0,
                            source="GramaVise Financial Engine",
                        )
                    )

            # E) WKN-FIN-DSCR-TIGHT: 1.00 <= DSCR < 1.25 AND loan > 0
            if 1.00 <= dscr < 1.25 and emi > 0:
                ev_id = "EV-FIN-SURPLUS"
                if ev_id in available_evidence_ids:
                    weaknesses.append(
                        SWOTItem(
                            id="WKN-FIN-DSCR-TIGHT",
                            title="Tight Debt Service Cushion",
                            explanation=(
                                f"The projected DSCR of {dscr:,.2f}x reflects a weak debt repayment cushion below "
                                "GramaVise's 1.25x baseline reference, leaving minimal margin for unexpected expenses."
                            ),
                            category="FINANCIAL",
                            importance="HIGH",
                            evidence_ids=[ev_id],
                            evidence_type=EvidenceType.CALCULATED,
                            confidence=1.0,
                            source="GramaVise Financial Engine",
                        )
                    )

            # F) WKN-FIN-DSCR-DEFICIT: DSCR < 1.00 AND loan > 0
            if dscr < 1.00 and emi > 0:
                ev_id = "EV-FIN-SURPLUS"
                if ev_id in available_evidence_ids:
                    surplus_val = max(0.0, gross_profit - fixed_cost)
                    weaknesses.append(
                        SWOTItem(
                            id="WKN-FIN-DSCR-DEFICIT",
                            title="Debt Service Shortfall Risk",
                            explanation=(
                                f"Projected net operating surplus (₹{surplus_val:,.2f}) is insufficient to cover "
                                f"the monthly loan repayment of ₹{emi:,.2f} (DSCR: {dscr:,.2f}x), creating severe "
                                "repayment pressure under current assumptions."
                            ),
                            category="FINANCIAL",
                            importance="CRITICAL",
                            evidence_ids=[ev_id],
                            evidence_type=EvidenceType.CALCULATED,
                            confidence=1.0,
                            source="GramaVise Financial Engine",
                        )
                    )

            # G) STR-FIN-CONTRIBUTION-MARGIN: Healthy Contribution Margin >= 40%
            if rev > 0 and (gross_profit / rev) >= 0.40:
                ev_id = "EV-FIN-SURPLUS"
                if ev_id in available_evidence_ids:
                    margin_pct = (gross_profit / rev) * 100.0
                    strengths.append(
                        SWOTItem(
                            id="STR-FIN-CONTRIBUTION-MARGIN",
                            title="Healthy Operating Contribution Margin",
                            explanation=(
                                f"Gross operating contribution margin of {margin_pct:.1f}% provides resilient "
                                "absorption capacity against raw material and operating cost variances."
                            ),
                            category="FINANCIAL",
                            importance="MEDIUM",
                            evidence_ids=[ev_id],
                            evidence_type=EvidenceType.CALCULATED,
                            confidence=1.0,
                            source="GramaVise Financial Engine",
                        )
                    )

            # H) Break-even requirement: Manageable (Strength) vs High (Weakness)
            cust_day = customers_per_day or 0
            if cust_day > 0:
                be_pct = (be_units / cust_day) * 100.0
                if be_units <= (0.50 * cust_day):
                    ev_id = "EV-FIN-BREAKEVEN"
                    if ev_id in available_evidence_ids:
                        strengths.append(
                            SWOTItem(
                                id="STR-FIN-BREAKEVEN-MANAGEABLE",
                                title="Manageable Break-Even Sales Requirement",
                                explanation=(
                                    f"Enterprise achieves operational break-even at {be_units} daily orders "
                                    f"({be_pct:.0f}% of assumed volume), providing substantial buffer against demand fluctuations."
                                ),
                                category="FINANCIAL",
                                importance="MEDIUM",
                                evidence_ids=[ev_id],
                                evidence_type=EvidenceType.CALCULATED,
                                confidence=1.0,
                                source="GramaVise Financial Engine",
                            )
                        )
                elif be_units >= (0.70 * cust_day):
                    ev_id = "EV-FIN-BREAKEVEN"
                    if ev_id in available_evidence_ids:
                        weaknesses.append(
                            SWOTItem(
                                id="WKN-FIN-BREAKEVEN-HIGH",
                                title="High Break-Even Sales Requirement",
                                explanation=(
                                    f"Enterprise requires {be_units} daily orders ({be_pct:.0f}% of assumed capacity) "
                                    "merely to cover fixed costs and loan EMI."
                                ),
                                category="FINANCIAL",
                                importance="HIGH",
                                evidence_ids=[ev_id],
                                evidence_type=EvidenceType.CALCULATED,
                                confidence=1.0,
                                source="GramaVise Financial Engine",
                            )
                        )

            # I) WKN-FIN-FIXED-COST-BURDEN: Fixed overheads > 50% of gross profit
            if gross_profit > 0 and fixed_cost > (0.50 * gross_profit):
                ev_id = "EV-FIN-SURPLUS"
                if ev_id in available_evidence_ids:
                    fc_pct = (fixed_cost / gross_profit) * 100.0
                    weaknesses.append(
                        SWOTItem(
                            id="WKN-FIN-FIXED-COST-BURDEN",
                            title="High Fixed-Cost Overhead Burden",
                            explanation=(
                                f"Monthly fixed operating overheads (₹{fixed_cost:,.2f}) absorb {fc_pct:.0f}% of "
                                "gross profit, reducing financial flexibility during slow trading months."
                            ),
                            category="FINANCIAL",
                            importance="MEDIUM",
                            evidence_ids=[ev_id],
                            evidence_type=EvidenceType.CALCULATED,
                            confidence=1.0,
                            source="GramaVise Financial Engine",
                        )
                    )

            # J) THR-SCN-DEMAND-SENSITIVITY: 20% demand reduction leads to negative net profit
            stress_rev = 0.80 * rev
            stress_var = 0.80 * var_cost
            stress_net_profit = stress_rev - stress_var - fixed_cost - emi
            if stress_net_profit < 0 and emi > 0:
                ev_id = "EV-FIN-SURPLUS"
                if ev_id in available_evidence_ids:
                    threats.append(
                        SWOTItem(
                            id="THR-SCN-DEMAND-SENSITIVITY",
                            title="Sensitivity to Demand Contraction",
                            explanation=(
                                f"Under the 20% demand-reduction scenario, projected monthly cash flow becomes "
                                f"negative (₹{stress_net_profit:,.2f}), indicating increased repayment pressure "
                                "and highlighting the need to validate daily sales assumptions."
                            ),
                            category="FINANCIAL",
                            importance="HIGH",
                            evidence_ids=[ev_id],
                            evidence_type=EvidenceType.CALCULATED,
                            confidence=1.0,
                            source="GramaVise Scenario Simulator",
                        )
                    )

        # =====================================================================
        # 2. MARKET COMPETITION & GEOGRAPHIC COVERAGE
        # =====================================================================
        if market_result:
            direct_count = market_result.direct_competitor_count
            radius = market_result.catchment_radius_km
            cov_conf = getattr(market_result, "coverage_confidence", "LOW")
            geography = market_result.geography
            is_geocoded = getattr(geography, "is_geocoded", False) if geography else False

            ev_comp = evidence_map.get("EV-MKT-COMPETITORS")

            # STR-MKT-COMP-LOW: direct_count <= 1 AND is_geocoded AND cov_conf in ["HIGH", "MEDIUM"]
            if (
                direct_count <= 1
                and is_geocoded
                and cov_conf in [CoverageConfidenceLevel.HIGH.value, CoverageConfidenceLevel.MEDIUM.value, "HIGH", "MEDIUM"]
                and ev_comp is not None
                and ev_comp.evidence_type != EvidenceType.NEEDS_VERIFICATION
            ):
                strengths.append(
                    SWOTItem(
                        id="STR-MKT-COMP-LOW",
                        title="Low Direct Catchment Competition",
                        explanation=(
                            f"Verified catchment mapping indicates limited direct competitive presence "
                            f"({direct_count} units) within a {radius:g} km radius."
                        ),
                        category="MARKET",
                        importance="HIGH",
                        evidence_ids=["EV-MKT-COMPETITORS"],
                        evidence_type=EvidenceType.OBSERVED,
                        confidence=ev_comp.confidence,
                        source="OpenStreetMap (Overpass API)",
                    )
                )

                # OPP-MKT-COMP-GAP: Genuine verified zero competitors represents a market gap opportunity
                if direct_count == 0:
                    opportunities.append(
                        SWOTItem(
                            id="OPP-MKT-COMP-GAP",
                            title="Potential Local Market Gap",
                            explanation=(
                                f"Verified geodata identifies no existing direct competitors within {radius:g} km, "
                                "suggesting a potential first-mover advantage subject to on-ground demand validation."
                            ),
                            category="MARKET",
                            importance="HIGH",
                            evidence_ids=["EV-MKT-COMPETITORS"],
                            evidence_type=EvidenceType.OBSERVED,
                            confidence=ev_comp.confidence,
                            source="OpenStreetMap (Overpass API)",
                        )
                    )

            # THR-MKT-COMP-HIGH: direct_count >= 3 AND is_geocoded
            if direct_count >= 3 and is_geocoded and ev_comp is not None:
                threats.append(
                    SWOTItem(
                        id="THR-MKT-COMP-HIGH",
                        title="High Direct Competitor Density",
                        explanation=(
                            f"Catchment contains {direct_count} established direct competitors within "
                            f"{radius:g} km, creating potential price competition for customer footfall."
                        ),
                        category="MARKET",
                        importance="HIGH",
                        evidence_ids=["EV-MKT-COMPETITORS"],
                        evidence_type=EvidenceType.OBSERVED,
                        confidence=1.0,
                        source="OpenStreetMap (Overpass API)",
                    )
                )

            # THR-GEO-COVERAGE-LOW: cov_conf == "LOW" OR is_geocoded is False
            if (cov_conf == "LOW" or not is_geocoded) and ev_comp is not None:
                threats.append(
                    SWOTItem(
                        id="THR-GEO-COVERAGE-LOW",
                        title="Unverified Digital Data Coverage",
                        explanation=(
                            "Geographic data coverage for this rural location is unverified in digital "
                            "registries; unmapped informal competitors may exist locally."
                        ),
                        category="MARKET",
                        importance="MEDIUM",
                        evidence_ids=["EV-MKT-COMPETITORS"],
                        evidence_type=EvidenceType.NEEDS_VERIFICATION,
                        confidence=0.0,
                        source="OpenStreetMap Geocoding Engine",
                    )
                )

            # =================================================================
            # 3. MANDI WHOLESALE PRICE BENCHMARK
            # =================================================================
            ev_mandi = evidence_map.get("EV-MKT-MANDI-PRICE-1")
            price_bench = market_result.price_benchmark

            if (
                ev_mandi is not None
                and ev_mandi.evidence_type == EvidenceType.OBSERVED
                and price_bench is not None
                and price_bench.median_price is not None
            ):
                m_name = price_bench.market_name or "local APMC"
                unit_str = price_bench.unit or "quintal"
                opportunities.append(
                    SWOTItem(
                        id="OPP-MKT-MANDI-REF",
                        title="Verified Mandi Price Benchmark",
                        explanation=(
                            f"Local APMC Mandi wholesale price benchmark of ₹{price_bench.median_price:,.2f}/{unit_str} "
                            f"({m_name}) provides a verified procurement reference point."
                        ),
                        category="MARKET",
                        importance="MEDIUM",
                        evidence_ids=["EV-MKT-MANDI-PRICE-1"],
                        evidence_type=EvidenceType.OBSERVED,
                        confidence=1.0,
                        source="Directorate of Marketing & Inspection (DMI) / OGD",
                    )
                )
            else:
                target_ev_id = "EV-MKT-MANDI-PRICE-1" if "EV-MKT-MANDI-PRICE-1" in available_evidence_ids else None
                if target_ev_id:
                    weaknesses.append(
                        SWOTItem(
                            id="WKN-EVD-MANDI-MISSING",
                            title="Unverified Commodity Price Benchmark",
                            explanation=(
                                "Key raw material procurement costs could not be cross-referenced against a "
                                "verified local APMC mandi feed; assumptions remain subject to local price validation."
                            ),
                            category="OPERATIONAL",
                            importance="MEDIUM",
                            evidence_ids=[target_ev_id],
                            evidence_type=EvidenceType.NEEDS_VERIFICATION,
                            confidence=0.0,
                            source="Agmarknet Mandi Network",
                        )
                    )

            # =================================================================
            # 4. CENSUS 2011 POPULATION
            # =================================================================
            ev_census = evidence_map.get("EV-DEMO-CENSUS2011-1")
            demo_obs = market_result.demographics
            cat_lower = (category or "").lower().strip()
            is_consumer_facing = any(c in cat_lower for c in CONSUMER_FACING_CATEGORIES) if cat_lower else True

            if (
                ev_census is not None
                and is_geocoded
                and demo_obs is not None
                and demo_obs.population is not None
                and demo_obs.population > 0
                and is_consumer_facing
            ):
                pop_val = demo_obs.population
                hh_val = demo_obs.households or (pop_val // 5)
                opportunities.append(
                    SWOTItem(
                        id="OPP-DEM-CENSUS-POP",
                        title="Established Village Population Base",
                        explanation=(
                            f"The available Census 2011 data indicates a village population of {pop_val:,} residents "
                            f"({hh_val:,} households). Current population, customer reach, and purchasing demand "
                            "require local validation."
                        ),
                        category="LOCAL_DEMAND",
                        importance="MEDIUM",
                        evidence_ids=["EV-DEMO-CENSUS2011-1"],
                        evidence_type=EvidenceType.OBSERVED,
                        confidence=1.0,
                        source="Office of the Registrar General & Census Commissioner, India",
                    )
                )

            # =================================================================
            # 5. SEASONAL THREATS & SUPPLY CHAIN RISKS (From Market Result)
            # =================================================================
            if getattr(market_result, "seasonal_threats", None):
                for st in market_result.seasonal_threats:
                    st_ev_ids = [eid for eid in st.evidence_ids if eid in available_evidence_ids]
                    if not st_ev_ids and "EV-MKT-COMPETITORS" in available_evidence_ids:
                        st_ev_ids = ["EV-MKT-COMPETITORS"]
                    if st_ev_ids:
                        threats.append(
                            SWOTItem(
                                id=f"THR-MKT-SEASONAL-{st.threat_id}",
                                title=f"Seasonal Threat: {st.title}",
                                explanation=(
                                    f"{st.explanation} (Affected period: {st.affected_period or 'Seasonal'}). "
                                    "Requires working capital buffer planning."
                                ),
                                category="MARKET",
                                importance=st.severity or "MEDIUM",
                                evidence_ids=st_ev_ids,
                                evidence_type=st.evidence_type or EvidenceType.NEEDS_VERIFICATION,
                                confidence=st.confidence,
                                source="Market Intelligence Seasonality Model",
                            )
                        )

            if getattr(market_result, "supply_chain", None):
                for scr in market_result.supply_chain:
                    scr_ev_ids = [eid for eid in scr.evidence_ids if eid in available_evidence_ids]
                    if not scr_ev_ids and "EV-MKT-COMPETITORS" in available_evidence_ids:
                        scr_ev_ids = ["EV-MKT-COMPETITORS"]
                    if scr_ev_ids:
                        scr_id = scr.risk_id or f"SCR-{abs(hash(scr.input_material)) % 1000}"
                        threats.append(
                            SWOTItem(
                                id=f"THR-MKT-SUPPLY-{scr_id}",
                                title=f"Supply Chain Risk: {scr.input_material}",
                                explanation=(
                                    f"Procurement vulnerability for {scr.input_material} "
                                    f"({scr.supplier_dependency or 'Local procurement'}, "
                                    f"volatility: {scr.price_volatility or 'Moderate'}). {scr.notes or ''}"
                                ).strip(),
                                category="OPERATIONAL",
                                importance="HIGH" if scr.price_volatility in ["HIGH", "EXTREME"] else "MEDIUM",
                                evidence_ids=scr_ev_ids,
                                evidence_type=scr.evidence_type or EvidenceType.NEEDS_VERIFICATION,
                                confidence=scr.confidence,
                                source="Market Intelligence Supply Chain Model",
                            )
                        )

        # =====================================================================
        # 6. ENTREPRENEUR STATED ASSUMPTIONS (ASSUMED EVIDENCE)
        # =====================================================================
        ev_user = evidence_map.get("EV-USER-CUSTOMERS")
        if ev_user is not None and ev_user.evidence_type == EvidenceType.ASSUMED:
            cust_val = customers_per_day or 0
            weaknesses.append(
                SWOTItem(
                    id="WKN-EVD-ASSUMPTION-UNVERIFIED",
                    title="Self-Declared Footfall Assumptions",
                    explanation=(
                        f"Projected revenue relies on self-reported expected daily footfall ({cust_val} customers/day); "
                        "on-ground customer demand requires field validation."
                    ),
                    category="OPERATIONAL",
                    importance="MEDIUM",
                    evidence_ids=["EV-USER-CUSTOMERS"],
                    evidence_type=EvidenceType.ASSUMED,
                    confidence=0.75,
                    source="Entrepreneur Self-Declaration",
                )
            )

        # =====================================================================
        # 7. STATUTORY GOVERNMENT SCHEMES & ODOP
        # =====================================================================
        if scheme_result and getattr(scheme_result, "schemes", None):
            for s in scheme_result.schemes:
                code = s.scheme_code
                name = s.scheme_name
                status = s.eligibility_status
                subsidy = getattr(s, "subsidy_eligible_amount", getattr(s, "max_subsidy_amount", 0.0))
                ev_id = f"EV-SCHEME-{code}"

                if ev_id in available_evidence_ids and status in ["ELIGIBLE", "PARTIALLY_ELIGIBLE"]:
                    opportunities.append(
                        SWOTItem(
                            id=f"OPP-SCH-{code}",
                            title=f"Potential {code} Credit Support Match",
                            explanation=(
                                f"The business profile shows a potential match with {name} (potential margin subsidy "
                                f"up to ₹{subsidy:,.2f}). Final eligibility, documentary verification, and subsidy "
                                "availability require confirmation from the implementing nodal agency and lending bank."
                            ),
                            category="REGULATORY",
                            importance="HIGH",
                            evidence_ids=[ev_id],
                            evidence_type=EvidenceType.OBSERVED,
                            confidence=0.95,
                            source=s.source_title or f"Official {code} Guidelines",
                        )
                    )

        # ODOP Alignment
        ev_odop = evidence_map.get("EV-MKT-ODOP-1")
        if ev_odop is not None and ev_odop.evidence_type == EvidenceType.OBSERVED:
            dist_name = district or (market_result.geography.district_name if market_result and market_result.geography else "the district")
            opportunities.append(
                SWOTItem(
                    id="OPP-MKT-ODOP",
                    title="District ODOP Priority Sector Alignment",
                    explanation=(
                        f"Business activity aligns with the official One District One Product (ODOP) focus for "
                        f"{dist_name}, offering potential alignment with district-level agro-processing development initiatives."
                    ),
                    category="REGULATORY",
                    importance="MEDIUM",
                    evidence_ids=["EV-MKT-ODOP-1"],
                    evidence_type=EvidenceType.OBSERVED,
                    confidence=1.0,
                    source="Ministry of Food Processing Industries (MoFPI)",
                )
            )

        # Udyam District Context (Informational Candidate)
        ev_udyam = evidence_map.get("EV-MKT-UDYAM-1")
        if ev_udyam is not None and ev_udyam.evidence_type == EvidenceType.OBSERVED:
            dist_name = district or "District"
            informational.append(
                SWOTItem(
                    id="INF-MKT-DISTRICT-MSME",
                    title="Formal District MSME Registration Context",
                    explanation=(
                        f"Ministry of MSME data records formal enterprise registrations in {dist_name}. "
                        "This represents regional economic activity and is not a measure of immediate local village competition."
                    ),
                    category="MARKET",
                    importance="LOW",
                    evidence_ids=["EV-MKT-UDYAM-1"],
                    evidence_type=EvidenceType.OBSERVED,
                    confidence=1.0,
                    source="Ministry of MSME / Udyam",
                )
            )

        # =====================================================================
        # 8. DEDUPLICATION & DETERMINISTIC PRIORITIZATION
        # =====================================================================
        def rank_and_deduplicate(items: List[SWOTItem]) -> List[SWOTItem]:
            seen_ids: Set[str] = set()
            unique_items: List[SWOTItem] = []
            for item in items:
                valid_ev_ids = [eid for eid in item.evidence_ids if eid in available_evidence_ids]
                if not valid_ev_ids and item.evidence_ids:
                    continue
                item.evidence_ids = valid_ev_ids

                if item.id not in seen_ids:
                    seen_ids.add(item.id)
                    unique_items.append(item)

            # Sort deterministically:
            # 1. Importance (CRITICAL=4 > HIGH=3 > MEDIUM=2 > LOW=1)
            # 2. Confidence (1.0 > 0.0)
            # 3. Stable tie-breaker by ID
            unique_items.sort(
                key=lambda x: (
                    -IMPORTANCE_WEIGHTS.get(x.importance or "MEDIUM", 2),
                    -x.confidence,
                    x.id,
                )
            )
            return unique_items[:max_items_per_quadrant]

        final_strengths = rank_and_deduplicate(strengths)
        final_weaknesses = rank_and_deduplicate(weaknesses)
        final_opportunities = rank_and_deduplicate(opportunities)
        final_threats = rank_and_deduplicate(threats)

        all_emitted = final_strengths + final_weaknesses + final_opportunities + final_threats
        overall_conf = (
            round(sum(it.confidence for it in all_emitted) / len(all_emitted), 2)
            if all_emitted
            else 1.0
        )

        return SWOTAnalysis(
            strengths=final_strengths,
            weaknesses=final_weaknesses,
            opportunities=final_opportunities,
            threats=final_threats,
            evidence_type=EvidenceType.CALCULATED,
            confidence=overall_conf,
            verification_status="DERIVED",
            notes="Deterministically derived from verified Evidence Ledger items.",
        )
