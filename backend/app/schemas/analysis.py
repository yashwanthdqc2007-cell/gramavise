from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from app.schemas.business import BusinessProfileBase
from app.schemas.financial import FinancialAssumptionsInput, FinancialResultResponse
from app.schemas.market import MarketResultResponse
from app.schemas.scheme import SchemeMatchResult
from app.schemas.ai import AIExplanationResponse
from app.schemas.evidence import EvidenceType, EvidenceItem, VerificationCheckItem
from app.schemas.action_plan import ActionPlan, DocumentReadiness, BankReadiness


class RecommendationStatus(str, Enum):
    PROCEED = "PROCEED"
    VALIDATE_FIRST = "VALIDATE_FIRST"
    RECONSIDER = "RECONSIDER"


class RuleResult(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    INFO = "INFO"


class RuleSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


class RuleEvaluation(BaseModel):
    """Deterministic rule condition evaluation record for transparency."""
    rule_id: str
    rule_name: str
    condition: str
    result: str = Field(..., description="PASS, FAIL, WARNING, INFO")
    severity: str = Field(..., description="CRITICAL, WARNING, INFO")
    explanation: str
    source: str = "FeasibilityRules"


class DecisionTrace(BaseModel):
    """Complete transparent trail of deterministic rules and evidence behind the recommendation verdict."""
    recommendation_status: RecommendationStatus
    summary: str
    rule_evaluations: List[RuleEvaluation] = Field(default_factory=list)
    key_positive_factors: List[str] = Field(default_factory=list)
    key_caution_factors: List[str] = Field(default_factory=list)
    authority: str = "FeasibilityRules"


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
    overall_verdict: Optional[RecommendationStatus] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    financial_result: FinancialResultResponse
    market_result: MarketResultResponse
    scheme_result: SchemeMatchResult
    risk_factors: List[RiskFactor] = Field(default_factory=list)
    evidence_list: List[EvidenceItem] = Field(default_factory=list)
    evidence_ledger: Optional[List[EvidenceItem]] = None
    decision_trace: Optional[DecisionTrace] = None
    verification_checklist: List[VerificationCheckItem] = Field(default_factory=list)
    action_plan: Optional[ActionPlan] = None
    document_readiness: Optional[DocumentReadiness] = None
    bank_readiness: Optional[BankReadiness] = None
    ai_explanation: Optional[AIExplanationResponse] = None

