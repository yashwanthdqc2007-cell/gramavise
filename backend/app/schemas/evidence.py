from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    OBSERVED = "OBSERVED"
    CALCULATED = "CALCULATED"
    MODELLED = "MODELLED"
    ASSUMED = "ASSUMED"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class EvidenceItem(BaseModel):
    """Structured evidence record representing a data point in the GramaVise Evidence Ledger."""
    evidence_id: Optional[str] = None
    indicator: str
    claim: Optional[str] = None
    value: str
    unit: Optional[str] = None
    evidence_type: EvidenceType
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    confidence_level: Optional[str] = None
    confidence_explanation: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    observed_at: Optional[str] = None
    geography_level: Optional[str] = None
    verification_status: Optional[str] = None
    methodology: Optional[str] = None
    supports: Optional[str] = None
    limitations: Optional[str] = None
    notes: Optional[str] = None


class VerificationCheckItem(BaseModel):
    """Actionable verification task derived from unresolved NEEDS_VERIFICATION evidence."""
    item_id: str
    title: str
    description: str
    category: str = Field(..., description="MARKET, PRICING, SCHEME, DEMOGRAPHICS, ASSUMPTION")
    source_evidence_id: Optional[str] = None
    action_type: str = Field("ON_GROUND_SURVEY", description="ON_GROUND_SURVEY, DOCUMENT_VERIFICATION, BANK_CONSULTATION, SUPPLIER_CHECK")
    is_completed: bool = False
