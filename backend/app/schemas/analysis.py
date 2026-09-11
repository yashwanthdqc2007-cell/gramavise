from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from app.schemas.business import BusinessProfileBase
from app.schemas.financial import FinancialAssumptionsInput, FinancialResultResponse
from app.schemas.market import MarketResultResponse
from app.schemas.scheme import SchemeMatchResult
from app.schemas.ai import AIExplanationResponse


class RecommendationStatus(str, Enum):
    PROCEED = "PROCEED"
    VALIDATE_FIRST = "VALIDATE_FIRST"
    RECONSIDER = "RECONSIDER"


class EvidenceType(str, Enum):
    OBSERVED = "OBSERVED"
    CALCULATED = "CALCULATED"
    MODELLED = "MODELLED"
    ASSUMED = "ASSUMED"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"


class EvidenceItem(BaseModel):
    indicator: str
    value: str
    unit: Optional[str] = None
    evidence_type: EvidenceType
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    source: Optional[str] = None
    source_url: Optional[str] = None
    notes: Optional[str] = None


class RiskFactor(BaseModel):
    factor: str
    severity: str = Field(..., description="HIGH, MEDIUM, LOW")
    mitigation: str


class AnalysisRequest(BaseModel):
    profile: BusinessProfileBase
    financials: FinancialAssumptionsInput
    preferred_language: str = Field("en", description="Target language code: en, hi, mr, bn, te, ta")


class AnalysisResultResponse(BaseModel):
    analysis_id: str
    recommendation_status: RecommendationStatus
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    financial_result: FinancialResultResponse
    market_result: MarketResultResponse
    scheme_result: SchemeMatchResult
    risk_factors: List[RiskFactor] = Field(default_factory=list)
    evidence_list: List[EvidenceItem] = Field(default_factory=list)
    ai_explanation: Optional[AIExplanationResponse] = None
