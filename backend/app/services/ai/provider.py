from abc import ABC, abstractmethod
from typing import Dict, Any, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class AIProviderInterface(ABC):
    """Abstract interface defining the contract for AI/LLM integrations."""

    @abstractmethod
    def generate(self, prompt: str, system_instruction: str = None) -> str:
        """Generate unstructured text completion."""
        pass

    @abstractmethod
    def generate_structured(self, prompt: str, response_schema: Type[T], system_instruction: str = None) -> T:
        """Generate typed, schema-validated structured output."""
        pass


class MockAIProvider(AIProviderInterface):
    """Zero-dependency, offline mock AI provider for deterministic development and testing."""

    def generate(self, prompt: str, system_instruction: str = None) -> str:
        return "This is a deterministic mock advisory narrative generated for development purposes."

    def generate_structured(self, prompt: str, response_schema: Type[T], system_instruction: str = None) -> T:
        # Returns a mock instance conforming to the requested Pydantic schema
        from app.schemas.ai import AIExplanationResponse

        if response_schema == AIExplanationResponse:
            return AIExplanationResponse(
                language="en",
                summary="The proposed micro-enterprise demonstrates healthy operational unit economics and adequate debt servicing capacity.",
                strengths=[
                    "Low break-even threshold compared to projected daily customer footfall.",
                    "Eligible for credit-linked capital subsidy under PMEGP.",
                    "Sufficient DSCR cushion exceeding banking safety benchmarks (>= 1.5)."
                ],
                cautions_and_risks=[
                    "Seasonal fluctuation in raw material procurement prices.",
                    "Dependence on consistent daily customer traffic."
                ],
                actionable_next_steps=[
                    "Prepare project report and apply on the official PMEGP online portal.",
                    "Secure formal quotes for machinery and equipment.",
                    "Verify power tariff and utility connection feasibility at site."
                ],
                disclaimer="This advisory is generated based on mathematical modeling and local indicators. Please consult a local bank officer before final commitments."
            )
        
        # Fallback empty construction
        return response_schema.model_construct()


class LLMProvider(AIProviderInterface):
    """Concrete production LLM provider connecting to external AI APIs (OpenAI / Gemini / Anthropic)."""

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name

    def generate(self, prompt: str, system_instruction: str = None) -> str:
        """TODO [AI Lead]: Integrate Google GenAI SDK / OpenAI client."""
        # Fallback to mock behavior if no API key configured
        if not self.api_key:
            return MockAIProvider().generate(prompt, system_instruction)
        return "Live LLM response stub"

    def generate_structured(self, prompt: str, response_schema: Type[T], system_instruction: str = None) -> T:
        """TODO [AI Lead]: Implement structured JSON schema enforcement with live LLM."""
        if not self.api_key:
            return MockAIProvider().generate_structured(prompt, response_schema, system_instruction)
        return response_schema.model_construct()
