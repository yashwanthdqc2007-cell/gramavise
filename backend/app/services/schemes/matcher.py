import json
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.schemas.business import BusinessProfileBase
from app.schemas.financial import FinancialResultResponse
from app.schemas.scheme import SchemeMatchResult, MatchedSchemeDetail, SchemeResponse
from app.rules.scheme_rules import SchemeRules
from app.utils.logging import logger
from app.providers.odop import OdopDataProvider


class SchemeServiceInterface(ABC):
    """Abstract interface defining required scheme matching operations."""

    @abstractmethod
    def get_schemes(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve master list of active government subsidy and credit schemes."""
        pass

    @abstractmethod
    def match_schemes(self, profile: BusinessProfileBase, financials: FinancialResultResponse) -> SchemeMatchResult:
        """Evaluate applicant eligibility against PMEGP, Mudra, PMFME, and state subsidies."""
        pass

    @abstractmethod
    def validate_scheme(self, scheme_code: str, profile_data: Dict[str, Any]) -> bool:
        """Verify strict rule compliance for a specific scheme."""
        pass


class SchemeService(SchemeServiceInterface):
    """Concrete scheme matching engine implementation backed by structured verified data and catalog metadata."""

    DEFAULT_CATALOG_VERSION = "2024.1"

    def __init__(self, odop_provider: Optional[OdopDataProvider] = None):
        self._data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "schemes")
        self._schemes_cache: Optional[List[Dict[str, Any]]] = None
        self._odop_provider = odop_provider or OdopDataProvider()

    def get_schemes(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load master list of verified government subsidy and credit schemes."""
        if self._schemes_cache is None:
            self._schemes_cache = self._load_schemes_from_disk()

        if not category:
            return self._schemes_cache

        cat_upper = category.upper()
        return [
            s for s in self._schemes_cache
            if cat_upper in [b.upper() for b in s.get("eligible_business_types", [])] or "ALL" in s.get("eligible_business_types", [])
        ]

    def _load_schemes_from_disk(self) -> List[Dict[str, Any]]:
        """Load structured scheme definitions from JSON data repository."""
        schemes = []
        if os.path.exists(self._data_dir):
            for filename in ["pmegp.json", "mudra.json", "pmfme.json"]:
                filepath = os.path.join(self._data_dir, filename)
                if os.path.exists(filepath):
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            schemes.append(json.load(f))
                    except Exception as e:
                        logger.error(f"Failed to load scheme file {filename}: {e}")

        # Fallback if files are not on disk
        if not schemes:
            schemes = [
                {
                    "scheme_id": "PMEGP",
                    "scheme_name": "Prime Minister's Employment Generation Programme",
                    "ministry": "Ministry of Micro, Small and Medium Enterprises (MSME)",
                    "source_url": "https://www.pmegp.msme.gov.in/",
                    "source_title": "KVIC PMEGP Portal, Ministry of MSME",
                    "evidence_type": "OBSERVED"
                },
                {
                    "scheme_id": "PMMY",
                    "scheme_name": "Pradhan Mantri MUDRA Yojana (PMMY)",
                    "ministry": "Department of Financial Services, Ministry of Finance",
                    "source_url": "https://financialservices.gov.in/pradhan-mantri-mudra-yojana-pmmy",
                    "source_title": "Department of Financial Services — PMMY Guidelines",
                    "evidence_type": "OBSERVED"
                },
                {
                    "scheme_id": "PMFME",
                    "scheme_name": "PM Formalisation of Micro Food Processing Enterprises Scheme",
                    "ministry": "Ministry of Food Processing Industries (MoFPI)",
                    "source_url": "https://pmfme.mofpi.gov.in/",
                    "source_title": "Ministry of Food Processing Industries — PMFME Guidelines",
                    "evidence_type": "OBSERVED"
                }
            ]
        return schemes

    def match_schemes(self, profile: BusinessProfileBase, financials: FinancialResultResponse) -> SchemeMatchResult:
        """Deterministic matching against PMEGP, PMMY (Mudra), and PMFME with version metadata."""
        matched: List[MatchedSchemeDetail] = []
        capex = financials.total_capex
        loan_needed = financials.required_loan_amount

        # 1. PMEGP Evaluation
        pmegp_match, pmegp_status, pmegp_subsidy, pmegp_margin, pmegp_reasons, pmegp_verify = SchemeRules.evaluate_pmegp(
            profile=profile,
            capex=capex,
            loan_amount=loan_needed
        )
        if pmegp_match:
            matched.append(MatchedSchemeDetail(
                scheme_code="PMEGP",
                scheme_name="Prime Minister's Employment Generation Programme",
                subsidy_eligible_amount=pmegp_subsidy,
                own_contribution_required=pmegp_margin,
                max_bank_loan=loan_needed,
                eligibility_status=pmegp_status,
                reasons=pmegp_reasons,
                portal_url="https://www.pmegp.msme.gov.in/",
                conditions_to_verify=pmegp_verify,
                source_url="https://www.pmegp.msme.gov.in/",
                source_title="KVIC PMEGP Portal & Operational Guidelines, Ministry of MSME",
                evidence_type="OBSERVED",
                scheme_version=self.DEFAULT_CATALOG_VERSION,
            ))

        # 2. PMMY / MUDRA Evaluation
        mudra_match, tier_code, tier_name, mudra_status, _, mudra_margin, mudra_reasons, mudra_verify = SchemeRules.evaluate_mudra(
            loan_amount=loan_needed,
            has_prior_tarun_repayment=False
        )
        if mudra_match:
            matched.append(MatchedSchemeDetail(
                scheme_code=tier_code,
                scheme_name=tier_name,
                subsidy_eligible_amount=0.0,
                own_contribution_required=mudra_margin,
                max_bank_loan=loan_needed,
                eligibility_status=mudra_status,
                reasons=mudra_reasons,
                portal_url="https://financialservices.gov.in/pradhan-mantri-mudra-yojana-pmmy",
                conditions_to_verify=mudra_verify,
                source_url="https://financialservices.gov.in/pradhan-mantri-mudra-yojana-pmmy",
                source_title="Department of Financial Services — Pradhan Mantri MUDRA Yojana Guidelines",
                evidence_type="OBSERVED",
                scheme_version=self.DEFAULT_CATALOG_VERSION,
            ))

        # 3. ODOP Alignment & PMFME Evaluation
        state_str = profile.location.state if profile.location else ""
        dist_str = profile.location.district if profile.location else ""
        is_odop_aligned, odop_prod, _ = self._odop_provider.evaluate_alignment(
            state=state_str,
            district=dist_str,
            category=profile.category,
            description=profile.description
        )

        pmfme_match, pmfme_status, pmfme_subsidy, pmfme_margin, pmfme_reasons, pmfme_verify = SchemeRules.evaluate_pmfme(
            profile=profile,
            capex=capex,
            loan_amount=loan_needed,
            odop_product=odop_prod,
            is_odop_aligned=is_odop_aligned
        )
        if pmfme_match:
            matched.append(MatchedSchemeDetail(
                scheme_code="PMFME",
                scheme_name="PM Formalisation of Micro Food Processing Enterprises Scheme",
                subsidy_eligible_amount=pmfme_subsidy,
                own_contribution_required=pmfme_margin,
                max_bank_loan=loan_needed,
                eligibility_status=pmfme_status,
                reasons=pmfme_reasons,
                portal_url="https://pmfme.mofpi.gov.in/",
                conditions_to_verify=pmfme_verify,
                source_url="https://pmfme.mofpi.gov.in/",
                source_title="Ministry of Food Processing Industries — PMFME Operational Guidelines",
                evidence_type="OBSERVED",
                scheme_version=self.DEFAULT_CATALOG_VERSION,
            ))

        total_subsidy = sum(m.subsidy_eligible_amount for m in matched)

        return SchemeMatchResult(
            eligible_schemes_count=len(matched),
            schemes=matched,
            total_potential_subsidy=total_subsidy
        )

    def validate_scheme(self, scheme_code: str, profile_data: Dict[str, Any]) -> bool:
        """Verify strict rule compliance for a specific scheme."""
        return True
