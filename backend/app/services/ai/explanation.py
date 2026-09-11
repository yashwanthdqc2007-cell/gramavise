from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.schemas.ai import AIExplanationRequest, AIExplanationResponse
from app.schemas.analysis import RiskFactor
from app.services.ai.provider import AIProviderInterface, MockAIProvider, LLMProvider
from app.services.ai.prompts import SYSTEM_ADVISORY_PROMPT, BUSINESS_EXPLANATION_PROMPT
from app.config import settings


class AIServiceInterface(ABC):
    """Abstract interface defining AI advisory and explanation operations."""

    @abstractmethod
    def analyze_business(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize multi-modal context for advisory generation."""
        pass

    @abstractmethod
    def explain_analysis(self, request: AIExplanationRequest) -> AIExplanationResponse:
        """Translate deterministic metrics into vernacular advisory summaries."""
        pass

    @abstractmethod
    def generate_risks(self, business_data: Dict[str, Any]) -> List[RiskFactor]:
        """Identify domain and location-specific risk vectors."""
        pass

    @abstractmethod
    def generate_recommendations(self, analysis_summary: Dict[str, Any]) -> List[str]:
        """Generate tactical, actionable milestones."""
        pass


class AIService(AIServiceInterface):
    """Concrete implementation of AI explanation and narrative generation."""

    def __init__(self, provider: AIProviderInterface = None):
        if provider is not None:
            self.provider = provider
        elif settings.LLM_PROVIDER == "mock" or not settings.LLM_API_KEY:
            self.provider = MockAIProvider()
        else:
            self.provider = LLMProvider(api_key=settings.LLM_API_KEY, model_name=settings.LLM_MODEL)

    def analyze_business(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """TODO [AI Lead]: Orchestrate composite prompt context."""
        return {"status": "analyzed"}

    def explain_analysis(self, request: AIExplanationRequest) -> AIExplanationResponse:
        """Translate deterministic metrics into plain-language advisory narratives."""
        prompt = BUSINESS_EXPLANATION_PROMPT.format(
            business_name=request.business_name,
            category=request.category,
            location=request.location,
            recommendation_status=request.recommendation_status,
            total_capex=request.financial_summary.get("total_capex", 0),
            monthly_revenue=request.financial_summary.get("monthly_revenue", 0),
            monthly_net_profit=request.financial_summary.get("monthly_net_profit", 0),
            break_even_units_daily=request.financial_summary.get("break_even_units_daily", 0),
            customers_per_day=request.financial_summary.get("customers_per_day", 0),
            monthly_emi=request.financial_summary.get("monthly_emi", 0),
            dscr=request.financial_summary.get("dscr", 0),
            matched_schemes=str(request.matched_schemes),
            risk_factors=str(request.risk_factors),
            target_language=request.preferred_language
        )
        return self.provider.generate_structured(
            prompt=prompt,
            response_schema=AIExplanationResponse,
            system_instruction=SYSTEM_ADVISORY_PROMPT
        )

    def generate_risks(self, business_data: Dict[str, Any]) -> List[RiskFactor]:
        """TODO [AI Lead]: Generate contextual risk factors and mitigation advice."""
        return [
            RiskFactor(
                factor="Working Capital Buffer",
                severity="MEDIUM",
                mitigation="Maintain at least 45 days of raw material inventory reserve."
            ),
            RiskFactor(
                factor="Power & Utility Dependability",
                severity="LOW",
                mitigation="Verify village commercial feeder reliability or solar backup options."
            )
        ]

    def generate_recommendations(self, analysis_summary: Dict[str, Any]) -> List[str]:
        """TODO [AI Lead]: Synthesize next step checklist."""
        return [
            "Download business feasibility report.",
            "Apply for Udyam Registration (free online MSME portal).",
            "Present project profile to local Lead District Bank officer."
        ]
