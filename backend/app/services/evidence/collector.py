from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.schemas.analysis import EvidenceItem, EvidenceType, VerificationCheckItem
from app.schemas.scheme import MatchedSchemeDetail
from app.schemas.market import MarketResultResponse, CompetitorRelationship
from app.providers.odop import OdopDataProvider
from app.providers.geo import GeoDataProvider
from app.providers.demographics import DemographicDataProvider
from app.providers.price import PriceDataProvider
from app.providers.competitor import OSMCompetitorProvider
from app.providers.udyam import UdyamContextProvider


class EvidenceServiceInterface(ABC):
    """Abstract interface defining evidence gathering and classification operations."""

    @abstractmethod
    def collect(self, context: Dict[str, Any]) -> List[EvidenceItem]:
        """Aggregate evidence items across all sub-engines."""
        pass

    @abstractmethod
    def validate(self, evidence: EvidenceItem) -> bool:
        """Validate provenance and integrity of evidence item."""
        pass

    @abstractmethod
    def calculate_confidence(self, evidence_list: List[EvidenceItem]) -> float:
        """Compute aggregate confidence score (0.0 to 1.0)."""
        pass

    @abstractmethod
    def generate_verification_checklist(self, evidence_list: List[EvidenceItem]) -> List[VerificationCheckItem]:
        """Generate actionable verification checklist from unresolved NEEDS_VERIFICATION evidence."""
        pass


class EvidenceCollector(EvidenceServiceInterface):
    """Aggregates and tags evidence items with rigorous provenance classifications for the Evidence Ledger:
    - CALCULATED: Deterministic mathematical outputs (Financial Engine)
    - OBSERVED: Ground-truth statutory rules & census/LGD/ODOP/Agmarknet/OSM/Udyam records with official sources
    - MODELLED: Statistical / prototype simulations ([DEMO / PROTOTYPE DATA])
    - ASSUMED: Entrepreneur self-declarations requiring field verification
    - NEEDS_VERIFICATION: Unconfirmed regulatory, price, or market preconditions / incomplete rural coverage
    """

    def __init__(
        self,
        odop_provider: Optional[OdopDataProvider] = None,
        geo_provider: Optional[GeoDataProvider] = None,
        demographics_provider: Optional[DemographicDataProvider] = None,
        price_provider: Optional[PriceDataProvider] = None,
        competitor_provider: Optional[OSMCompetitorProvider] = None,
        udyam_provider: Optional[UdyamContextProvider] = None
    ):
        self._odop_provider = odop_provider or OdopDataProvider()
        self._geo_provider = geo_provider or GeoDataProvider()
        self._demographics_provider = demographics_provider or DemographicDataProvider()
        self._price_provider = price_provider or PriceDataProvider()
        self._competitor_provider = competitor_provider or OSMCompetitorProvider()
        self._udyam_provider = udyam_provider or UdyamContextProvider()

    def collect(self, context: Dict[str, Any]) -> List[EvidenceItem]:
        """Compile comprehensive evidence records for the Evidence Ledger."""
        items: List[EvidenceItem] = []

        # 1. Financial Unit Economics Evidence (CALCULATED)
        net_profit = context.get("monthly_net_profit", 0)
        items.append(EvidenceItem(
            evidence_id="EV-FIN-SURPLUS",
            indicator="Monthly Operating Surplus",
            claim="Monthly Operating Surplus after all costs & debt servicing",
            value=f"₹{net_profit:,.2f}",
            unit="INR/month",
            evidence_type=EvidenceType.CALCULATED,
            confidence=1.0,
            confidence_level="HIGH",
            confidence_explanation="Deterministic formula computed from audited financial engine: Revenue - Variable Costs - Fixed Overheads - Debt EMI.",
            source="GramaVise Financial Engine",
            source_title="Deterministic Financial Calculator",
            methodology="Audited unit economics arithmetic",
            supports="Operating profitability and debt repayment capacity",
            limitations="Assumes accurate self-declared revenue and cost inputs",
            notes="Computed via audited formulas: Monthly Revenue - Variable Costs - Fixed Overheads - Debt EMI.",
            verification_status="CALCULATED"
        ))

        be_units = context.get("break_even_units_daily", 0)
        items.append(EvidenceItem(
            evidence_id="EV-FIN-BREAKEVEN",
            indicator="Daily Break-Even Footfall",
            claim="Required daily break-even sales volume",
            value=f"{be_units} orders/day",
            unit="units/day",
            evidence_type=EvidenceType.CALCULATED,
            confidence=1.0,
            confidence_level="HIGH",
            confidence_explanation="Deterministic contribution margin model: (Fixed Costs + Monthly EMI) / Unit Contribution Margin / Working Days.",
            source="GramaVise Financial Engine",
            source_title="Contribution Margin Model",
            methodology="Contribution margin arithmetic",
            supports="Minimum operational sales target required to avoid deficit",
            notes="Required minimum sales to cover monthly operational overheads and debt obligations.",
            verification_status="CALCULATED"
        ))

        # 2. Market Catchment & Competitor Evidence (OpenStreetMap - OBSERVED or NEEDS_VERIFICATION)
        market_res = context.get("market_result")
        direct_count = 0
        adjacent_count = 0
        radius_km = 5.0
        cov_conf = "LOW"
        if isinstance(market_res, MarketResultResponse):
            direct_count = market_res.direct_competitor_count
            adjacent_count = market_res.adjacent_competitor_count
            radius_km = market_res.catchment_radius_km
            cov_conf = getattr(market_res, "coverage_confidence", "LOW")
        elif isinstance(market_res, dict):
            direct_count = market_res.get("direct_competitor_count", market_res.get("competitor_count", 0))
            adjacent_count = market_res.get("adjacent_competitor_count", 0)
            radius_km = market_res.get("catchment_radius_km", 5.0)
            cov_conf = market_res.get("coverage_confidence", "LOW")

        if direct_count > 0:
            items.append(EvidenceItem(
                evidence_id="EV-MKT-COMPETITORS",
                indicator="Catchment Mapped Competitors",
                claim="Direct mapped commercial competitors within catchment",
                value=f"{direct_count} direct mapped units" + (f" ({adjacent_count} adjacent)" if adjacent_count > 0 else ""),
                unit="units",
                evidence_type=EvidenceType.OBSERVED,
                confidence=1.0,
                confidence_level="MEDIUM" if cov_conf == "MEDIUM" else "HIGH",
                confidence_explanation="Direct mapped commercial POIs from OpenStreetMap within 5 km straight-line radius.",
                source="OpenStreetMap (Overpass API)",
                source_url="https://www.openstreetmap.org/",
                source_title="OpenStreetMap Commercial POI Layer",
                methodology="Overpass API POI extraction + Haversine straight-line distance calculation",
                supports="Local commercial competitor density evaluation",
                limitations="Rural mapping coverage may be incomplete; unmapped informal vendors may exist",
                notes=(
                    f"Observed {direct_count} direct mapped commercial POIs within {radius_km:g} km catchment. "
                    "Straight-line distance; informal or unmapped rural units may also exist."
                ),
                verification_status="VERIFIED_SOURCE"
            ))
        else:
            items.append(EvidenceItem(
                evidence_id="EV-MKT-COMPETITORS",
                indicator="Catchment Mapped Competitors",
                claim="Direct mapped commercial competitors within catchment",
                value="0 direct mapped units",
                unit="units",
                evidence_type=EvidenceType.NEEDS_VERIFICATION,
                confidence=0.50,
                confidence_level="LOW",
                confidence_explanation="No direct commercial units mapped in OpenStreetMap within 5 km. Rural coverage is incomplete; 0 mapped units does NOT prove absence of competition.",
                source="OpenStreetMap (Overpass API)",
                source_url="https://www.openstreetmap.org/",
                source_title="OpenStreetMap Commercial POI Layer",
                methodology="Overpass API POI extraction + Haversine straight-line distance calculation",
                supports="Requires physical on-ground vendor survey before capital investment",
                limitations="Incomplete rural geodata mapping in OpenStreetMap",
                notes=(
                    f"No direct commercial units mapped in OpenStreetMap within {radius_km:g} km. "
                    "Rural mapping coverage is often incomplete; physical local survey required to verify absence of competition."
                ),
                verification_status="NEEDS_VERIFICATION"
            ))

        catchment_pop = market_res.catchment_population_estimate if isinstance(market_res, MarketResultResponse) else context.get("catchment_population_estimate", 4500)
        if catchment_pop:
            items.append(EvidenceItem(
                evidence_id="EV-MKT-CATCHMENT-POP",
                indicator="Estimated Catchment Population",
                claim="Modelled Catchment Population within 5 km",
                value=f"{catchment_pop:,} residents",
                unit="persons",
                evidence_type=EvidenceType.MODELLED,
                confidence=0.50,
                confidence_level="LOW",
                confidence_explanation="Geometric model estimate baseline for prototype demonstration. Not a direct census observation.",
                source="GramaVise Prototype Market Model",
                source_title="Catchment Demographic Model",
                methodology="Prototype geometric catchment radius estimation [DEMO]",
                supports="Baseline potential customer universe for demand scoping",
                limitations="Modelled prototype estimate; physical survey required",
                notes="[DEMO / PROTOTYPE DATA] Catchment population estimate from prototype model.",
                verification_status="NEEDS_VERIFICATION"
            ))

        # 3. Market Price Benchmark Evidence (Official Agmarknet / OGD Price Data Provider)
        cat_val = context.get("category", "") or context.get("business_type", "") or ""
        state_val = context.get("state")
        dist_val = context.get("district")
        village_val = context.get("village")
        if not (state_val and dist_val) and context.get("location"):
            loc = context["location"]
            state_val = getattr(loc, "state", None) or (loc.get("state") if isinstance(loc, dict) else None)
            dist_val = getattr(loc, "district", None) or (loc.get("district") if isinstance(loc, dict) else None)
            village_val = getattr(loc, "village", None) or (loc.get("village") if isinstance(loc, dict) else None)

        price_res = self._price_provider.fetch_evidence({
            "category": cat_val,
            "commodity": cat_val,
            "state": state_val or "",
            "district": dist_val or ""
        })
        for idx, price_item in enumerate(price_res.evidence_items):
            if not price_item.evidence_id:
                price_item.evidence_id = f"EV-MKT-MANDI-PRICE-{idx+1}"
            if not price_item.claim:
                price_item.claim = "Official Mandi Wholesale Price Benchmark"
            if not price_item.confidence_level:
                price_item.confidence_level = "HIGH" if price_item.evidence_type == EvidenceType.OBSERVED else "UNKNOWN"
            if not price_item.confidence_explanation:
                price_item.confidence_explanation = (
                    "Official agricultural mandi modal price from Directorate of Marketing & Inspection / data.gov.in."
                    if price_item.evidence_type == EvidenceType.OBSERVED
                    else "Commodity price feed outside checked-in Agmarknet snapshot."
                )
            if not price_item.limitations:
                price_item.limitations = "Observed mandi modal price from Agmarknet / OGD. Wholesale market observation only; not a retail selling price recommendation."
            items.append(price_item)

        # 4. Entrepreneur Stated Assumptions (ASSUMED)
        cust_day = context.get("customers_per_day", 0)
        items.append(EvidenceItem(
            evidence_id="EV-USER-CUSTOMERS",
            indicator="Expected Daily Footfall",
            claim="Self-declared expected daily customer footfall",
            value=f"{cust_day} customers",
            unit="customers/day",
            evidence_type=EvidenceType.ASSUMED,
            confidence=0.75,
            confidence_level="MEDIUM",
            confidence_explanation="Self-reported baseline customer volume from entrepreneur input requiring on-ground verification.",
            source="Entrepreneur Self-Declaration",
            source_title="User Input Assumptions",
            methodology="Entrepreneur assumption",
            supports="Daily revenue projection and operating margin basis",
            limitations="Unverified self-declaration; subject to entrepreneur optimism bias",
            notes="Self-reported baseline customer volume requiring on-ground verification.",
            verification_status="Unverified self-declaration"
        ))

        # 5. Scheme Evidence & Unverified Preconditions
        schemes = context.get("schemes", [])
        for s_idx, scheme in enumerate(schemes):
            if isinstance(scheme, MatchedSchemeDetail) or isinstance(scheme, dict):
                s_name = scheme.scheme_name if isinstance(scheme, MatchedSchemeDetail) else scheme.get("scheme_name", "")
                s_code = scheme.scheme_code if isinstance(scheme, MatchedSchemeDetail) else scheme.get("scheme_code", "")
                s_url = scheme.source_url if isinstance(scheme, MatchedSchemeDetail) else scheme.get("source_url")
                s_title = scheme.source_title if isinstance(scheme, MatchedSchemeDetail) else scheme.get("source_title")
                s_status = scheme.eligibility_status if isinstance(scheme, MatchedSchemeDetail) else scheme.get("eligibility_status")
                s_conditions = scheme.conditions_to_verify if isinstance(scheme, MatchedSchemeDetail) else scheme.get("conditions_to_verify", [])

                # Add observed scheme evidence
                items.append(EvidenceItem(
                    evidence_id=f"EV-SCHEME-{s_code}",
                    indicator=f"Government Scheme: {s_code}",
                    claim=f"Statutory eligibility matching for {s_name}",
                    value=s_status,
                    unit="status",
                    evidence_type=EvidenceType.OBSERVED,
                    confidence=0.95,
                    confidence_level="HIGH",
                    confidence_explanation=f"Deterministic matching evaluated under official {s_name} published guidelines.",
                    source=s_title or "Official Scheme Portal",
                    source_url=s_url,
                    source_title=s_title,
                    methodology="Statutory criteria mapping",
                    supports=f"Potential credit subsidy or bank loan eligibility under {s_code}",
                    limitations="Informational matching only; final sanction requires bank credit appraisal",
                    notes=f"Statutory matching evaluated under {s_name} official guidelines.",
                    verification_status=s_status
                ))

                # Add explicit unverified preconditions if status is PARTIALLY_ELIGIBLE
                if s_conditions:
                    for c_idx, cond in enumerate(s_conditions):
                        items.append(EvidenceItem(
                            evidence_id=f"EV-COND-{s_code}-{c_idx+1}",
                            indicator=f"Verification: {s_code}",
                            claim=f"Required verification condition for {s_code}",
                            value=cond,
                            unit="condition",
                            evidence_type=EvidenceType.NEEDS_VERIFICATION,
                            confidence=0.50,
                            confidence_level="LOW",
                            confidence_explanation=f"Statutory documentation required by {s_code} implementing agency before subsidy release.",
                            source="Official Scheme Authority Verification Required",
                            source_url=s_url,
                            source_title=s_title,
                            methodology="Documentary verification requirement",
                            supports=f"Conditional milestone required for {s_code} approval",
                            limitations="Applicant documentation must be submitted to nodal bank or DIC",
                            notes="Documentary evidence must be verified with lending bank or nodal agency.",
                            verification_status="NEEDS_VERIFICATION"
                        ))

        # 6. Official ODOP, LGD, Census 2011, and Udyam Evidence
        if state_val and dist_val:
            # ODOP
            odop_res = self._odop_provider.fetch_evidence({"state": state_val, "district": dist_val})
            for idx, odop_item in enumerate(odop_res.evidence_items):
                if not odop_item.evidence_id:
                    odop_item.evidence_id = f"EV-MKT-ODOP-{idx+1}"
                if not odop_item.claim:
                    odop_item.claim = "Official PMFME One District One Product (ODOP) Alignment"
                if not odop_item.confidence_level:
                    odop_item.confidence_level = "HIGH" if odop_item.evidence_type == EvidenceType.OBSERVED else "LOW"
                if not odop_item.confidence_explanation:
                    odop_item.confidence_explanation = "Official PMFME ODOP Master Registry published by MoFPI."
                items.append(odop_item)

            # LGD Geography Identity
            geo_res = self._geo_provider.fetch_evidence({
                "state": state_val,
                "district": dist_val,
                "village": village_val or ""
            })
            for idx, geo_item in enumerate(geo_res.evidence_items):
                if not geo_item.evidence_id:
                    geo_item.evidence_id = f"EV-GEO-LGD-{idx+1}"
                if not geo_item.claim:
                    geo_item.claim = "Administrative Entity Identity & Official LGD Codes"
                if not geo_item.confidence_level:
                    geo_item.confidence_level = "HIGH" if geo_item.evidence_type == EvidenceType.OBSERVED else "LOW"
                if not geo_item.confidence_explanation:
                    geo_item.confidence_explanation = "Official Local Government Directory code from Ministry of Panchayati Raj."
                items.append(geo_item)

            # Census 2011 Historical Demographics
            if village_val:
                demo_res = self._demographics_provider.fetch_evidence({
                    "state": state_val,
                    "district": dist_val,
                    "village": village_val
                })
                for idx, demo_item in enumerate(demo_res.evidence_items):
                    if not demo_item.evidence_id:
                        demo_item.evidence_id = f"EV-DEMO-CENSUS2011-{idx+1}"
                    if not demo_item.claim:
                        demo_item.claim = "Official Historical Population Count (Census 2011)"
                    if not demo_item.confidence_level:
                        demo_item.confidence_level = "HIGH" if demo_item.evidence_type == EvidenceType.OBSERVED else "LOW"
                    if not demo_item.confidence_explanation:
                        demo_item.confidence_explanation = "Historical official population from Census 2011. Not a current population estimate."
                    items.append(demo_item)

            # Udyam District MSME Context
            udyam_res = self._udyam_provider.fetch_evidence({"state": state_val, "district": dist_val})
            for idx, udyam_item in enumerate(udyam_res.evidence_items):
                if not udyam_item.evidence_id:
                    udyam_item.evidence_id = f"EV-MKT-UDYAM-{idx+1}"
                if not udyam_item.claim:
                    udyam_item.claim = "District Formal MSME Registration Density"
                if not udyam_item.confidence_level:
                    udyam_item.confidence_level = "HIGH" if udyam_item.evidence_type == EvidenceType.OBSERVED else "LOW"
                if not udyam_item.confidence_explanation:
                    udyam_item.confidence_explanation = "Official district-level formal MSME registration aggregates from Ministry of MSME."
                if not udyam_item.limitations:
                    udyam_item.limitations = "District-level formal MSME context only; not a count of nearby competitors."
                items.append(udyam_item)

        return items

    def validate(self, evidence: EvidenceItem) -> bool:
        return evidence.confidence >= 0.0 and bool(evidence.indicator)

    def calculate_confidence(self, evidence_list: List[EvidenceItem]) -> float:
        """Compute weighted mean confidence across all evidence items."""
        if not evidence_list:
            return 0.5
        total = sum(e.confidence for e in evidence_list)
        return round(total / len(evidence_list), 2)

    def generate_verification_checklist(self, evidence_list: List[EvidenceItem]) -> List[VerificationCheckItem]:
        """Convert unresolved NEEDS_VERIFICATION & critical ASSUMED items into an actionable checklist."""
        checklist: List[VerificationCheckItem] = []
        seen_keys = set()

        for item in evidence_list:
            # 1. Catchment Competitor Verification
            if item.evidence_id == "EV-MKT-COMPETITORS" and item.evidence_type == EvidenceType.NEEDS_VERIFICATION:
                if "competitor_check" not in seen_keys:
                    checklist.append(VerificationCheckItem(
                        item_id="CHK-MKT-001",
                        title="On-Ground Competitor Survey",
                        description="Visit the local market cluster within 5 km to count active informal or unmapped competitors.",
                        category="MARKET",
                        source_evidence_id=item.evidence_id,
                        action_type="ON_GROUND_SURVEY"
                    ))
                    seen_keys.add("competitor_check")

            # 2. Mandi / Wholesale Price Benchmark Verification
            if item.indicator.startswith("MKT-PRICE-BENCH") or "Agmarknet" in (item.source or "") or "Mandi" in item.indicator:
                if item.evidence_type == EvidenceType.NEEDS_VERIFICATION and "price_check" not in seen_keys:
                    checklist.append(VerificationCheckItem(
                        item_id="CHK-PRC-001",
                        title="Wholesale Supplier Price Inquiry",
                        description="Inquire at nearest wholesale APMC market or local mandi to confirm current raw material procurement prices.",
                        category="PRICING",
                        source_evidence_id=item.evidence_id,
                        action_type="SUPPLIER_CHECK"
                    ))
                    seen_keys.add("price_check")

            # 3. Scheme Conditional Document Requirements
            if item.indicator.startswith("Verification:") or (item.evidence_id and item.evidence_id.startswith("EV-COND-")):
                chk_id = f"CHK-SCH-{len(checklist)+1:03d}"
                checklist.append(VerificationCheckItem(
                    item_id=chk_id,
                    title=f"Scheme Document: {item.indicator.replace('Verification: ', '')}",
                    description=f"Obtain and verify: {item.value}",
                    category="SCHEME",
                    source_evidence_id=item.evidence_id,
                    action_type="DOCUMENT_VERIFICATION"
                ))

            # 4. Entrepreneur Footfall Validation
            if item.evidence_id == "EV-USER-CUSTOMERS" and "footfall_check" not in seen_keys:
                checklist.append(VerificationCheckItem(
                    item_id="CHK-ASM-001",
                    title="Customer Footfall Count",
                    description=f"Conduct a 3-day manual footfall count at the proposed location to validate the assumption of {item.value}.",
                    category="ASSUMPTION",
                    source_evidence_id=item.evidence_id,
                    action_type="ON_GROUND_SURVEY"
                ))
                seen_keys.add("footfall_check")

        return checklist
