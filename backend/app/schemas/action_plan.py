from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class RecommendationStatus(str, Enum):
    PROCEED = "PROCEED"
    VALIDATE_FIRST = "VALIDATE_FIRST"
    RECONSIDER = "RECONSIDER"


class ActionPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ActionCategory(str, Enum):
    FINANCIAL = "FINANCIAL"
    MARKET = "MARKET"
    SCHEME = "SCHEME"
    DOCUMENTATION = "DOCUMENTATION"
    BUSINESS_OPERATIONS = "BUSINESS_OPERATIONS"
    VALIDATION = "VALIDATION"


class ActionStatus(str, Enum):
    TODO = "TODO"
    RECOMMENDED = "RECOMMENDED"
    COMPLETED = "COMPLETED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ActionSource(str, Enum):
    DECISION_TRACE = "DECISION_TRACE"
    EVIDENCE_LEDGER = "EVIDENCE_LEDGER"
    VERIFICATION_CHECKLIST = "VERIFICATION_CHECKLIST"
    FINANCIAL_RESULT = "FINANCIAL_RESULT"
    SCHEME_RESULT = "SCHEME_RESULT"
    MARKET_RESULT = "MARKET_RESULT"


class ActionItem(BaseModel):
    """Deterministic, actionable task for the entrepreneur prior to borrowing."""
    action_id: str
    title: str
    description: str
    priority: ActionPriority
    category: ActionCategory
    status: ActionStatus = ActionStatus.TODO
    action_source: ActionSource
    reason: str
    related_evidence_ids: List[str] = Field(default_factory=list)
    related_rule_ids: List[str] = Field(default_factory=list)
    estimated_effort: Optional[str] = None
    verification_required: bool = False
    completion_effect: Optional[str] = None


class ActionPlan(BaseModel):
    """Complete pre-loan action plan derived deterministically from the analysis."""
    recommendation_status: RecommendationStatus
    actions: List[ActionItem] = Field(default_factory=list)
    total_actions: int = 0
    critical_actions_count: int = 0


class DocumentStatus(str, Enum):
    REQUIRED = "REQUIRED"
    VERIFY = "VERIFY"
    NOT_REQUIRED = "NOT_REQUIRED"
    UNKNOWN = "UNKNOWN"


class DocumentItem(BaseModel):
    """Scheme-supported statutory or banking documentary verification item."""
    document_id: str
    name: str
    purpose: str
    status: DocumentStatus
    required_for: str
    source: Optional[str] = None
    verification_status: str = "NEEDS_VERIFICATION"


class DocumentReadiness(BaseModel):
    """Status of scheme-supported documentation readiness."""
    documents: List[DocumentItem] = Field(default_factory=list)
    required_count: int = 0
    verified_count: int = 0
    pending_count: int = 0


class ReadinessStatus(str, Enum):
    READY = "READY"
    PARTIALLY_READY = "PARTIALLY_READY"
    NOT_READY = "NOT_READY"
    UNKNOWN = "UNKNOWN"


class BankReadinessCategory(BaseModel):
    """Readiness assessment for a specific dimension of the business case."""
    category: str = Field(..., description="FINANCIAL_CASE, MARKET_EVIDENCE, SCHEME_FIT, DOCUMENT_READINESS, ASSUMPTION_QUALITY")
    title: str
    status: ReadinessStatus
    reason: str
    supporting_evidence_ids: List[str] = Field(default_factory=list)


class BankReadiness(BaseModel):
    """Deterministic assessment of business case readiness for lender discussions.
    This is NOT a credit score or loan approval probability."""
    overall_status: ReadinessStatus
    summary: str
    categories: List[BankReadinessCategory] = Field(default_factory=list)
    top_actions: List[str] = Field(default_factory=list)
    disclaimer: str = (
        "This readiness assessment evaluates information completeness and mathematical feasibility "
        "for lender discussions. It is NOT a credit score, loan approval guarantee, or probability of success."
    )
