from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SchemeBase(BaseModel):
    scheme_code: str = Field(..., description="Unique scheme identifier (e.g. PMEGP, MUDRA_SHISHU)")
    scheme_name: str
    ministry_or_dept: Optional[str] = None
    max_loan_amount: float
    subsidy_percentage_general: float
    subsidy_percentage_special: float
    interest_subvention_pct: float
    eligibility_criteria: Dict[str, Any] = Field(default_factory=dict)
    required_documents: List[str] = Field(default_factory=list)
    official_portal_url: Optional[str] = None


class SchemeResponse(SchemeBase):
    id: str


class MatchedSchemeDetail(BaseModel):
    scheme_code: str
    scheme_name: str
    subsidy_eligible_amount: float
    own_contribution_required: float
    max_bank_loan: float
    eligibility_status: str = Field(..., description="ELIGIBLE, PARTIALLY_ELIGIBLE, NOT_ELIGIBLE")
    reasons: List[str] = Field(default_factory=list)
    portal_url: Optional[str] = None


class SchemeMatchResult(BaseModel):
    eligible_schemes_count: int
    schemes: List[MatchedSchemeDetail] = Field(default_factory=list)
    total_potential_subsidy: float = 0.0
