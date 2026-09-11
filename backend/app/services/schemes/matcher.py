from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.schemas.business import BusinessProfileBase
from app.schemas.financial import FinancialResultResponse
from app.schemas.scheme import SchemeMatchResult, MatchedSchemeDetail, SchemeResponse


class SchemeServiceInterface(ABC):
    """Abstract interface defining required scheme matching operations."""

    @abstractmethod
    def get_schemes(self, category: str = None) -> List[Dict[str, Any]]:
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
    """Concrete scheme matching engine implementation."""

    def get_schemes(self, category: str = None) -> List[Dict[str, Any]]:
        """TODO [Schemes Lead]: Query database repository for active schemes."""
        return [
            {
                "scheme_code": "PMEGP",
                "scheme_name": "Prime Minister Employment Generation Programme",
                "ministry_or_dept": "Ministry of MSME",
                "max_loan_amount": 5000000.0,
                "subsidy_percentage_general": 25.0,
                "subsidy_percentage_special": 35.0,
                "interest_subvention_pct": 0.0,
                "official_portal_url": "https://www.kviconline.gov.in/pmegpeportal"
            },
            {
                "scheme_code": "MUDRA_KISHORE",
                "scheme_name": "Pradhan Mantri MUDRA Yojana (Kishore)",
                "ministry_or_dept": "Ministry of Finance",
                "max_loan_amount": 500000.0,
                "subsidy_percentage_general": 0.0,
                "subsidy_percentage_special": 0.0,
                "interest_subvention_pct": 2.0,
                "official_portal_url": "https://www.mudra.org.in"
            },
            {
                "scheme_code": "PMFME",
                "scheme_name": "PM Formalisation of Micro Food Processing Enterprises",
                "ministry_or_dept": "Ministry of Food Processing Industries",
                "max_loan_amount": 1000000.0,
                "subsidy_percentage_general": 35.0,
                "subsidy_percentage_special": 35.0,
                "interest_subvention_pct": 3.0,
                "official_portal_url": "https://pmfme.mofpi.gov.in"
            }
        ]

    def match_schemes(self, profile: BusinessProfileBase, financials: FinancialResultResponse) -> SchemeMatchResult:
        """Deterministic scheme matching stub."""
        matched: List[MatchedSchemeDetail] = []
        loan_needed = financials.required_loan_amount

        # PMEGP Evaluation Stub
        if loan_needed <= 5000000.0:
            subsidy_rate = 35.0  # Rural special category baseline
            subsidy = round(financials.total_capex * (subsidy_rate / 100.0), 2)
            own_contribution = round(financials.total_capex * 0.05, 2)
            matched.append(MatchedSchemeDetail(
                scheme_code="PMEGP",
                scheme_name="Prime Minister Employment Generation Programme",
                subsidy_eligible_amount=subsidy,
                own_contribution_required=own_contribution,
                max_bank_loan=loan_needed,
                eligibility_status="ELIGIBLE",
                reasons=["Eligible under Rural / Micro enterprise sector.", "Project cost within ₹50 Lakh limit."],
                portal_url="https://www.kviconline.gov.in/pmegpeportal"
            ))

        # Mudra Evaluation Stub
        if loan_needed <= 500000.0:
            matched.append(MatchedSchemeDetail(
                scheme_code="MUDRA_KISHORE",
                scheme_name="Pradhan Mantri MUDRA Yojana (Kishore)",
                subsidy_eligible_amount=0.0,
                own_contribution_required=round(loan_needed * 0.15, 2),
                max_bank_loan=loan_needed,
                eligibility_status="ELIGIBLE",
                reasons=["Collateral-free loan eligible up to ₹5,00,000."],
                portal_url="https://www.mudra.org.in"
            ))

        total_subsidy = sum(m.subsidy_eligible_amount for m in matched)

        return SchemeMatchResult(
            eligible_schemes_count=len(matched),
            schemes=matched,
            total_potential_subsidy=total_subsidy
        )

    def validate_scheme(self, scheme_code: str, profile_data: Dict[str, Any]) -> bool:
        """TODO [Schemes Lead]: Implement detailed rule validations."""
        return True
