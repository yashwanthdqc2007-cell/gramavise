from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.schemas.market import MarketResultResponse, CompetitorInfo, MarketEvidenceQuery


class MarketServiceInterface(ABC):
    """Abstract interface defining required geospatial market intelligence operations."""

    @abstractmethod
    def get_location(self, state: str, district: str, village: str) -> Dict[str, float]:
        """Geocode village/block name into lat/lon coordinates."""
        pass

    @abstractmethod
    def get_local_businesses(self, lat: float, lon: float, category: str, radius_km: float) -> List[CompetitorInfo]:
        """Fetch nearby competitor POIs from OpenStreetMap or cache."""
        pass

    @abstractmethod
    def get_market_indicators(self, query: MarketEvidenceQuery) -> MarketResultResponse:
        """Aggregate catchment population, competitor density, and demand rating."""
        pass


class MockMarketService(MarketServiceInterface):
    """Development / Offline fallback for MarketService."""

    def get_location(self, state: str, district: str, village: str) -> Dict[str, float]:
        # Canned coordinates for development
        return {"latitude": 25.3176, "longitude": 82.9739}

    def get_local_businesses(self, lat: float, lon: float, category: str, radius_km: float) -> List[CompetitorInfo]:
        return [
            CompetitorInfo(name=f"Local {category} Unit 1", distance_km=1.2, category=category),
            CompetitorInfo(name=f"Gramin {category} Kendra", distance_km=2.8, category=category),
        ]

    def get_market_indicators(self, query: MarketEvidenceQuery) -> MarketResultResponse:
        competitors = self.get_local_businesses(query.latitude or 25.3, query.longitude or 82.9, query.category, query.radius_km)
        return MarketResultResponse(
            location_summary=f"{query.village}, {query.district}, {query.state}",
            competitor_count=len(competitors),
            competitor_list=competitors,
            demand_indicator="HIGH" if len(competitors) < 3 else "MEDIUM",
            catchment_population_estimate=4500,
            notes="Market shows underserved micro-catchment with moderate commercial density."
        )
