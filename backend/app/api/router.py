from fastapi import APIRouter
from app.api.routes import health, financial, market, schemes, ai, analysis

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(analysis.router, tags=["Analysis Pipeline"])
api_router.include_router(financial.router, tags=["Financial Engine"])
api_router.include_router(market.router, tags=["Market & Geo"])
api_router.include_router(schemes.router, tags=["Government Schemes"])
api_router.include_router(ai.router, tags=["AI Advisory"])
