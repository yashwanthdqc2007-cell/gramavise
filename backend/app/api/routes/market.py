from typing import Optional
from fastapi import APIRouter, Query
from app.schemas.market import MarketResultResponse, MarketEvidenceQuery
from app.services.geo.market import MockMarketService

router = APIRouter()
market_service = MockMarketService()


@router.get("/market/evidence", response_model=MarketResultResponse, summary="Query Local Market & Competitor Indicators")
async def get_market_evidence(
    state: str = Query(..., description="Target state"),
    district: str = Query(..., description="Target district"),
    village: str = Query(..., description="Target village / town"),
    category: str = Query(..., description="Business category (e.g. Kirana, Atta Chakki)"),
    latitude: Optional[float] = Query(None, description="GPS Latitude"),
    longitude: Optional[float] = Query(None, description="GPS Longitude"),
    radius_km: float = Query(5.0, description="Search radius in kilometers")
):
    """Retrieve hyper-local competitor density and demand indicators.
    
    TODO [Data Lead]: Replace MockMarketService with live OpenStreetMap/Overpass provider.
    """
    query = MarketEvidenceQuery(
        state=state,
        district=district,
        village=village,
        category=category,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km
    )
    return market_service.get_market_indicators(query)
