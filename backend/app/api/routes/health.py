from datetime import datetime, timezone
from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from app.config import settings
from app.database import check_database_health

router = APIRouter()


class HealthCheckResponse(BaseModel):
    status: str
    app_name: str
    version: str
    timestamp: datetime
    services: dict


class ReadinessResponse(BaseModel):
    status: str
    app_name: str
    version: str
    timestamp: datetime
    database: str
    environment: str


@router.get("/health", response_model=HealthCheckResponse, summary="Process Liveness Probe")
async def health_check():
    """Liveness probe to verify that the application process is running.
    
    Guaranteed fast: does not execute database queries so liveness is never coupled to DB uptime.
    """
    return HealthCheckResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        timestamp=datetime.now(timezone.utc),
        services={
            "process": "running",
            "rule_engine": "ready",
            "ai_provider": settings.LLM_PROVIDER
        }
    )


@router.get("/ready", response_model=ReadinessResponse, summary="Application Readiness Probe")
async def readiness_check(response: Response):
    """Readiness probe to verify that the application is ready to accept and serve traffic.
    
    Executes a fast database connectivity ping. If the database is unreachable,
    returns HTTP 503 Service Unavailable without exposing internal connection details.
    """
    db_ok = check_database_health()
    now = datetime.now(timezone.utc)

    if not db_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadinessResponse(
            status="unhealthy",
            app_name=settings.APP_NAME,
            version=settings.APP_VERSION,
            timestamp=now,
            database="unavailable",
            environment=settings.ENVIRONMENT,
        )

    return ReadinessResponse(
        status="ready",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        timestamp=now,
        database="connected",
        environment=settings.ENVIRONMENT,
    )
