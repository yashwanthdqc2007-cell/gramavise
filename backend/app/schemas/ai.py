from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AIExplanationRequest(BaseModel):
    business_name: str
    category: str
    location: str
    recommendation_status: str
    financial_summary: Dict[str, Any]
    matched_schemes: List[Dict[str, Any]] = Field(default_factory=list)
    risk_factors: List[Dict[str, Any]] = Field(default_factory=list)
    preferred_language: str = Field("en", description="Target language (en, hi, mr, bn, te, ta)")


class AIExplanationResponse(BaseModel):
    language: str
    summary: str
    strengths: List[str] = Field(default_factory=list)
    cautions_and_risks: List[str] = Field(default_factory=list)
    actionable_next_steps: List[str] = Field(default_factory=list)
    disclaimer: str = "This advice is generated based on mathematical modeling and local indicators. Please consult a local bank officer before final commitments."
