from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field


class SchemeBase(BaseModel):
    scheme_id: str = Field(..., description="Unique scheme identifier (e.g. PMEGP, PMMY, PMFME)")
    scheme_name: str
    ministry: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    source_last_verified: Optional[str] = None
    applicable_states: List[str] = Field(default_factory=lambda: ["ALL_INDIA"])
    eligible_business_types: List[str] = Field(default_factory=list)
    eligible_enterprise_types: List[str] = Field(default_factory=lambda: ["MICRO"])
    new_or_existing: str = Field("BOTH", description="NEW, EXISTING, BOTH")
    minimum_age: int = 18
    maximum_project_cost: Optional[Union[float, Dict[str, float]]] = None
    maximum_loan_amount: Optional[float] = None
    subsidy_rate: Optional[Union[float, Dict[str, float]]] = None
    subsidy_max_amount: Optional[float] = None
    beneficiary_contribution: Optional[Union[float, Dict[str, float]]] = None
    collateral_required: bool = False
    categories_supported: List[str] = Field(default_factory=lambda: ["ALL"])
    geography_conditions: Optional[str] = None
    special_conditions: List[str] = Field(default_factory=list)
    exclusions: List[str] = Field(default_factory=list)
    matching_reasons: List[str] = Field(default_factory=list)
    verification_required: List[str] = Field(default_factory=list)
    evidence_type: str = "OBSERVED"


class SchemeResponse(SchemeBase):
    id: Optional[str] = None


class MatchedSchemeDetail(BaseModel):
    scheme_code: str
    scheme_name: str
    subsidy_eligible_amount: float
    own_contribution_required: float
    max_bank_loan: float
    eligibility_status: str = Field(..., description="ELIGIBLE, PARTIALLY_ELIGIBLE, NOT_ELIGIBLE")
    reasons: List[str] = Field(default_factory=list)
    portal_url: Optional[str] = None
    conditions_to_verify: List[str] = Field(default_factory=list)
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    evidence_type: str = "OBSERVED"
    scheme_version: Optional[str] = Field(default="2024.1", description="Authoritative version of the scheme evaluated")
    scheme_version_id: Optional[str] = None


class SchemeMatchResult(BaseModel):
    eligible_schemes_count: int
    schemes: List[MatchedSchemeDetail] = Field(default_factory=list)
    total_potential_subsidy: float = 0.0


# --- Catalog & Versioning Schemas ---

class SchemeVersionResponse(BaseModel):
    id: str
    scheme_code: str
    version: str
    status: str
    description: Optional[str] = None
    official_source_name: Optional[str] = None
    official_portal_url: Optional[str] = None
    source_publication_date: Optional[str] = None
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    retrieved_at: Optional[datetime] = None
    max_loan_amount: float = 0.0
    subsidy_percentage_general: float = 0.0
    subsidy_percentage_special: float = 0.0
    beneficiary_contribution_general_pct: float = 0.0
    beneficiary_contribution_special_pct: float = 0.0
    interest_subvention_pct: float = 0.0
    eligibility_criteria: Dict[str, Any] = Field(default_factory=dict)
    required_documents: List[str] = Field(default_factory=list)
    verification_notes: List[str] = Field(default_factory=list)
    metadata_payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class SchemeCatalogItem(BaseModel):
    id: str
    scheme_code: str
    scheme_name: str
    ministry: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None
    active_version: Optional[SchemeVersionResponse] = None
    total_versions: int = 1
    created_at: datetime
