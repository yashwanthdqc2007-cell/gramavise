from fastapi import APIRouter
from app.schemas.ai import AIExplanationRequest, AIExplanationResponse
from app.services.ai.explanation import AIService

router = APIRouter()
ai_service = AIService()


@router.post("/ai/explain", response_model=AIExplanationResponse, summary="Generate Vernacular Advisory Explanation")
async def explain_with_ai(request: AIExplanationRequest):
    """Translate structured financial and market indicators into a plain-language vernacular advisory.
    
    TODO [AI Lead]: Integrate multilingual prompts and audio/voice TTS synthesis endpoints.
    """
    return ai_service.explain_analysis(request)
