from typing import Dict, Any, Tuple, List, Optional
from app.schemas.business import BusinessProfileBase


class SchemeRules:
    """Deterministic eligibility and matching rules for statutory government credit & subsidy schemes.
    
    Authoritative References:
    - PMEGP: KVIC / Ministry of MSME (https://www.pmegp.msme.gov.in/)
    - PMMY / MUDRA: Dept. of Financial Services, Ministry of Finance (https://financialservices.gov.in/pradhan-mantri-mudra-yojana-pmmy)
    - PMFME: Ministry of Food Processing Industries (https://pmfme.mofpi.gov.in/)
    """

    FOOD_PROCESSING_KEYWORDS = [
        "flour", "atta", "chakki", "milling", "spice", "dairy", "milk", "chilling",
        "poultry", "agro", "food", "processing", "bakery", "oil", "pickles", "juice",
        "grain", "pulses", "dal", "papad", "snack", "sweet", "beverage", "preservation"
    ]

    MANUFACTURING_KEYWORDS = [
        "flour", "milling", "spice", "dairy", "poultry", "agro", "processing",
        "tailoring", "garment", "apparel", "manufacturing", "fabrication", "welding",
        "pottery", "carpentry", "oil", "bakery", "handicraft", "soap", "candle"
    ]

    @classmethod
    def is_food_processing_business(cls, category: str, description: Optional[str] = None) -> bool:
        """Determine if enterprise belongs to food/agro-produce processing domain."""
        text = f"{category or ''} {description or ''}".lower()
        return any(kw in text for kw in cls.FOOD_PROCESSING_KEYWORDS)

    @classmethod
    def is_manufacturing_business(cls, category: str, description: Optional[str] = None) -> bool:
        """Determine if enterprise is manufacturing vs services/trading."""
        text = f"{category or ''} {description or ''}".lower()
        return any(kw in text for kw in cls.MANUFACTURING_KEYWORDS)

    @classmethod
    def evaluate_pmegp(
        cls,
        profile: BusinessProfileBase,
        capex: float,
        loan_amount: float
    ) -> Tuple[bool, str, float, float, List[str], List[str]]:
        """Evaluate applicant against PMEGP operational guidelines.
        
        Returns:
            (matched, eligibility_status, subsidy_amount, own_contribution, reasons, conditions_to_verify)
        """
        reasons: List[str] = []
        conditions_to_verify: List[str] = []

        is_mfg = cls.is_manufacturing_business(profile.category, profile.description)
        max_project_cost = 5000000.0 if is_mfg else 2000000.0

        # PMEGP Rule 1: First loan assistance is strictly for new enterprises (Greenfield)
        if not profile.is_new_business:
            return (
                False,
                "NOT_ELIGIBLE",
                0.0,
                0.0,
                ["PMEGP primary assistance is strictly restricted to establishing new enterprise units (Greenfield)."],
                ["Existing units require proven prior PMEGP loan repayment under 2nd loan scheme."]
            )

        # PMEGP Rule 2: Project cost ceiling (₹50L Mfg / ₹20L Service)
        if capex > max_project_cost:
            return (
                False,
                "NOT_ELIGIBLE",
                0.0,
                0.0,
                [f"Total project outlay (₹{capex:,.0f}) exceeds PMEGP ceiling of ₹{max_project_cost:,.0f} for {'Manufacturing' if is_mfg else 'Services'}."],
                []
            )

        # Baseline rural calculation:
        # General Rural = 25% subsidy, 10% own contribution
        # Special Category Rural = 35% subsidy, 5% own contribution
        # Because applicant social category is not verified in profile, calculate conservative baseline (25%)
        # and document the 35% possibility under conditions_to_verify.
        subsidy_rate = 25.0
        own_contrib_pct = 10.0

        subsidy_amount = round(capex * (subsidy_rate / 100.0), 2)
        own_contribution = round(capex * (own_contrib_pct / 100.0), 2)

        reasons.append(f"Greenfield new enterprise setup within ₹{max_project_cost/100000:.0f} Lakh {'Manufacturing' if is_mfg else 'Service'} cost ceiling.")
        reasons.append(f"Rural enterprise eligible for {subsidy_rate:.0f}% baseline margin money subsidy (₹{subsidy_amount:,.0f}).")

        conditions_to_verify.append("Applicant social category: Special category (SC/ST/OBC/Women/Minority/Ex-Servicemen) qualifies for enhanced 35% subsidy & 5% own margin.")
        if (is_mfg and capex > 1000000.0) or (not is_mfg and capex > 500000.0):
            conditions_to_verify.append("Educational qualification: Minimum 8th standard pass certificate required for projects above ₹10L (Mfg) / ₹5L (Service).")
        conditions_to_verify.append("Rural area certificate from Gram Panchayat / BDO.")

        return (
            True,
            "PARTIALLY_ELIGIBLE",
            subsidy_amount,
            own_contribution,
            reasons,
            conditions_to_verify
        )

    @classmethod
    def evaluate_mudra(
        cls,
        loan_amount: float,
        has_prior_tarun_repayment: bool = False
    ) -> Tuple[bool, str, str, str, float, float, List[str], List[str]]:
        """Evaluate loan amount against PMMY MUDRA tiers:
        - Shishu: Up to ₹50,000 (0% margin, no collateral)
        - Kishore: ₹50,001 to ₹5,00,000 (up to 15% margin, no collateral)
        - Tarun: ₹5,00,001 to ₹10,00,000 (up to 15% margin, no collateral)
        - Tarun Plus: ₹10,00,001 to ₹20,00,000 (requires verified prior Tarun repayment)
        
        Returns:
            (matched, tier_code, tier_name, eligibility_status, subsidy_amount, own_contribution, reasons, conditions_to_verify)
        """
        if loan_amount <= 0:
            return (False, "NONE", "None", "NOT_ELIGIBLE", 0.0, 0.0, ["No bank loan requested."], [])

        if loan_amount <= 50000.0:
            tier_code = "MUDRA_SHISHU"
            tier_name = "Pradhan Mantri MUDRA Yojana (Shishu)"
            margin = 0.0
            reasons = ["Loan amount up to ₹50,000 eligible under MUDRA Shishu with zero collateral and nil margin requirement."]
            conditions_to_verify = ["Valid KYC and basic trade verification by lending bank."]
            return (True, tier_code, tier_name, "ELIGIBLE", 0.0, margin, reasons, conditions_to_verify)

        elif loan_amount <= 500000.0:
            tier_code = "MUDRA_KISHORE"
            tier_name = "Pradhan Mantri MUDRA Yojana (Kishore)"
            margin = round(loan_amount * 0.15, 2)
            reasons = ["Loan amount between ₹50,001 and ₹5,00,000 eligible under MUDRA Kishore without third-party collateral."]
            conditions_to_verify = ["Machinery quotation / asset invoice and standard bank credit appraisal."]
            return (True, tier_code, tier_name, "ELIGIBLE", 0.0, margin, reasons, conditions_to_verify)

        elif loan_amount <= 1000000.0:
            tier_code = "MUDRA_TARUN"
            tier_name = "Pradhan Mantri MUDRA Yojana (Tarun)"
            margin = round(loan_amount * 0.15, 2)
            reasons = ["Loan amount between ₹5,00,001 and ₹10,00,000 eligible under MUDRA Tarun."]
            conditions_to_verify = ["Business performance track record, quotation, and CIBIL score check."]
            return (True, tier_code, tier_name, "ELIGIBLE", 0.0, margin, reasons, conditions_to_verify)

        elif loan_amount <= 2000000.0:
            tier_code = "MUDRA_TARUN_PLUS"
            tier_name = "Pradhan Mantri MUDRA Yojana (Tarun Plus)"
            margin = round(loan_amount * 0.15, 2)
            reasons = ["Loan amount between ₹10,00,001 and ₹20,00,000 matches MUDRA Tarun Plus tier."]
            conditions_to_verify = [
                "Mandatory prerequisite: Requires verified prior successful repayment of a loan under the Tarun category.",
                "Standard bank credit review and satisfactory repayment track record."
            ]
            status = "ELIGIBLE" if has_prior_tarun_repayment else "PARTIALLY_ELIGIBLE"
            return (True, tier_code, tier_name, status, 0.0, margin, reasons, conditions_to_verify)

        else:
            return (
                False,
                "EXCEEDS_MUDRA_LIMIT",
                "PMMY (Exceeds Limit)",
                "NOT_ELIGIBLE",
                0.0,
                0.0,
                [f"Requested loan amount (₹{loan_amount:,.0f}) exceeds statutory MUDRA upper limit of ₹20,00,000."],
                ["Explore CGTMSE-backed MSME term loans for requirements exceeding ₹20 Lakh."]
            )

    @classmethod
    def evaluate_pmfme(
        cls,
        profile: BusinessProfileBase,
        capex: float,
        loan_amount: float,
        odop_product: Optional[str] = None,
        is_odop_aligned: bool = False
    ) -> Tuple[bool, str, float, float, List[str], List[str]]:
        """Evaluate applicant against PM Formalisation of Micro Food Processing Enterprises (PMFME).
        
        Official MoFPI ODOP Rule (https://mofpi.gov.in/pmfme/one-district-one-product):
        - New individual/group units are supported only for ODOP products.
        - Existing individual micro-units producing other products may also be supported for upgradation.
        - ODOP alignment is an eligibility and prioritization signal, not proof of subsidy guarantee.
        
        Returns:
            (matched, eligibility_status, subsidy_amount, own_contribution, reasons, conditions_to_verify)
        """
        is_food = cls.is_food_processing_business(profile.category, profile.description)
        if not is_food:
            return (
                False,
                "NOT_ELIGIBLE",
                0.0,
                0.0,
                ["PMFME is strictly restricted to food processing, grain milling, dairy, and agro-value-addition enterprises."],
                []
            )

        # 35% subsidy of project cost, capped at maximum ₹10,00,000 (₹10 Lakh)
        subsidy_raw = capex * 0.35
        subsidy_amount = round(min(1000000.0, subsidy_raw), 2)
        own_contribution = round(capex * 0.10, 2)

        base_reasons = [
            "Enterprise activity is in the micro food processing / agro-processing domain.",
            f"Credit-linked capital subsidy at 35% (calculated: ₹{subsidy_amount:,.0f}, capped at ₹10 Lakh statutory ceiling)."
        ]

        base_conditions = [
            "FSSAI food safety compliance / basic registration post-sanction.",
            "Minimum 10% entrepreneur equity contribution."
        ]

        # Case 1: Unmapped / Ambiguous ODOP dataset
        if odop_product is None:
            return (
                True,
                "PARTIALLY_ELIGIBLE",
                subsidy_amount,
                own_contribution,
                base_reasons + ["District ODOP mapping is unmapped or pending verification."],
                base_conditions + [
                    "District ODOP alignment could not be verified from official snapshot; field verification required."
                ]
            )

        # Case 2: Business is ODOP-aligned
        if is_odop_aligned:
            unit_type_desc = "New" if profile.is_new_business else "Existing"
            return (
                True,
                "PARTIALLY_ELIGIBLE",
                subsidy_amount,
                own_contribution,
                base_reasons + [
                    f"District ODOP alignment observed: {unit_type_desc} enterprise aligns with notified ODOP produce ('{odop_product}')."
                ],
                base_conditions + [
                    "Detailed Project Report (DPR) submission and commercial bank credit appraisal."
                ]
            )

        # Case 3: Business is NOT ODOP-aligned
        if not profile.is_new_business:
            # Case B: NON-ODOP EXISTING food-processing unit -> Supported for upgradation
            return (
                True,
                "PARTIALLY_ELIGIBLE",
                subsidy_amount,
                own_contribution,
                base_reasons + [
                    f"Existing individual micro-units producing other products may also be supported under PMFME for upgradation (District notified ODOP is '{odop_product}')."
                ],
                base_conditions + [
                    "Proof of existing micro-enterprise operations and technology/machinery upgradation requirement."
                ]
            )
        else:
            # Case C: NON-ODOP NEW food-processing unit -> Not supported under PMFME
            return (
                False,
                "NOT_ELIGIBLE",
                0.0,
                0.0,
                [
                    f"Under MoFPI PMFME guidelines, new units are supported only for notified ODOP products. Proposed new enterprise does not align with district notified ODOP produce ('{odop_product}')."
                ],
                []
            )

    # Legacy Compatibility Methods
    @staticmethod
    def check_pmegp_eligibility(project_cost: float, is_rural: bool = True) -> Tuple[bool, float, float]:
        """PMEGP legacy helper: returns (eligible, subsidy_pct, own_contrib_pct)."""
        if project_cost > 5000000.0:
            return (False, 0.0, 0.0)
        subsidy_pct = 35.0 if is_rural else 25.0
        own_contrib_pct = 5.0 if is_rural else 10.0
        return (True, subsidy_pct, own_contrib_pct)

    @staticmethod
    def check_mudra_eligibility(loan_amount: float) -> Tuple[bool, str]:
        """Mudra legacy helper."""
        if loan_amount <= 50000:
            return (True, "MUDRA_SHISHU")
        elif loan_amount <= 500000:
            return (True, "MUDRA_KISHORE")
        elif loan_amount <= 1000000:
            return (True, "MUDRA_TARUN")
        elif loan_amount <= 2000000:
            return (True, "MUDRA_TARUN_PLUS")
        else:
            return (False, "EXCEEDS_MUDRA_LIMIT")

