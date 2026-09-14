from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.financial import FinancialAssumptionsInput, FinancialResultResponse
from app.schemas.analysis import RecommendationStatus, DecisionTrace, RiskFactor
from app.schemas.market import MarketResultResponse


class ComparisonDirection(str, Enum):
    IMPROVED = "IMPROVED"
    WORSENED = "WORSENED"
    UNCHANGED = "UNCHANGED"
    NEUTRAL = "NEUTRAL"


class MetricComparison(BaseModel):
    """Deterministic comparison between a baseline and scenario financial metric."""
    metric_key: str
    metric_name: str
    baseline_value: float
    scenario_value: float
    unit: str = "INR"
    absolute_change: float
    percentage_change: Optional[float] = None
    direction: ComparisonDirection
    explanation: str


class RuleComparison(BaseModel):
    """Comparison of rule evaluation outcomes between baseline and scenario."""
    rule_id: str
    rule_name: str
    baseline_result: str
    scenario_result: str
    changed: bool
    explanation: str


class RecommendationChange(BaseModel):
    """Summary of recommendation transition between baseline and scenario."""
    baseline_status: RecommendationStatus
    scenario_status: RecommendationStatus
    changed: bool
    summary: str
    reasons: List[str] = Field(default_factory=list)


class ScenarioEvaluationRequest(BaseModel):
    """Request payload to calculate a scenario and compare against baseline."""
    scenario_id: Optional[str] = None
    name: str = "Custom Scenario"
    description: Optional[str] = None
    
    # Baseline Parameters
    baseline_own_capital: float = Field(..., ge=0.0)
    baseline_desired_loan: Optional[float] = Field(None, ge=0.0)
    baseline_financials: FinancialAssumptionsInput
    
    # Scenario Parameters (User Overrides)
    scenario_own_capital: float = Field(..., ge=0.0)
    scenario_desired_loan: Optional[float] = Field(None, ge=0.0)
    scenario_financials: FinancialAssumptionsInput
    
    # Invariant Market Context (Kept identical between baseline and scenario)
    market_context: Optional[MarketResultResponse] = None


class ScenarioEvaluationResponse(BaseModel):
    """Complete deterministic scenario calculation and comparison result."""
    scenario_id: str
    name: str
    description: Optional[str] = None
    
    baseline_result: FinancialResultResponse
    scenario_result: FinancialResultResponse
    
    baseline_status: RecommendationStatus
    scenario_status: RecommendationStatus
    
    baseline_decision_trace: Optional[DecisionTrace] = None
    scenario_decision_trace: Optional[DecisionTrace] = None
    
    metric_comparisons: List[MetricComparison] = Field(default_factory=list)
    rule_comparisons: List[RuleComparison] = Field(default_factory=list)
    recommendation_change: RecommendationChange
    
    what_changed: List[str] = Field(default_factory=list)
    why_it_changed: List[str] = Field(default_factory=list)
    risk_factors: List[RiskFactor] = Field(default_factory=list)
    
    disclaimer: str = (
        "Scenario outputs are decision support simulations based on user-entered assumptions. "
        "They do not guarantee financial viability, subsidy eligibility, or loan approval."
    )


class CreateScenarioRequest(BaseModel):
    """Request payload to calculate and persist a saved scenario against a parent Analysis."""
    name: str = Field(default="Custom Scenario", max_length=150)
    description: Optional[str] = None
    
    # Scenario Parameters (User Overrides)
    scenario_own_capital: float = Field(..., ge=0.0)
    scenario_desired_loan: Optional[float] = Field(None, ge=0.0)
    scenario_financials: FinancialAssumptionsInput


class ScenarioRecordResponse(ScenarioEvaluationResponse):
    """Persisted scenario representation returned from persistence and retrieval endpoints."""
    analysis_id: str
    created_at: Optional[str] = None
    scenario_inputs: dict = Field(default_factory=dict)

