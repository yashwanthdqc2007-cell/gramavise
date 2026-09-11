from typing import List, Optional
from fastapi import APIRouter, Query
from app.schemas.scheme import SchemeMatchResult, SchemeBase
from app.services.schemes.matcher import SchemeService

router = APIRouter()
scheme_service = SchemeService()


@router.get("/schemes", response_model=List[dict], summary="List Government Credit and Subsidy Schemes")
async def list_schemes(category: Optional[str] = Query(None, description="Filter by business sector")):
    """Fetch active government schemes available for rural micro-enterprises.
    
    TODO [Schemes Lead]: Query SchemeRepository from PostgreSQL database.
    """
    return scheme_service.get_schemes(category=category)
