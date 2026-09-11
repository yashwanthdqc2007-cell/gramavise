from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel
from app.config import settings

router = APIRouter()


class HealthCheckResponse(BaseModel):
    status: str
    app_name: str
    version: str
    timestamp: datetime
    services: dict


@router.get("/health", response_model=HealthCheckResponse, summary="System Health & Readiness Check")
async def health_check():
    """Health check endpoint to verify backend service readiness.
    
    TODO [Backend Lead]: Add active PostgreSQL and Redis connection ping checks.
    """
    return HealthCheckResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow(),
        services={
            "database": "configured",
            "rule_engine": "ready",
            "ai_provider": settings.LLM_PROVIDER
        }
    )
