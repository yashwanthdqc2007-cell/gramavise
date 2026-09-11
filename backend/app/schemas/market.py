from typing import List, Optional
from pydantic import BaseModel, Field


class CompetitorInfo(BaseModel):
    name: str = Field(..., description="Business or amenity name")
    distance_km: float = Field(..., description="Distance from target village in km")
    category: str = Field(..., description="Amenity / business tag")


class MarketEvidenceQuery(BaseModel):
    state: str
    district: str
    village: str
    category: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: float = Field(5.0, description="Search radius in kilometers")


class MarketResultResponse(BaseModel):
    location_summary: str
    competitor_count: int
    competitor_list: List[CompetitorInfo] = Field(default_factory=list)
    demand_indicator: str = Field(..., description="HIGH, MEDIUM, LOW, UNKNOWN")
    catchment_population_estimate: Optional[int] = None
    notes: Optional[str] = None
