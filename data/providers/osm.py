from typing import Dict, Any, List
from data.providers.base import DataProvider


class OSMProvider(DataProvider):
    """OpenStreetMap Overpass / Nominatim API provider."""

    def __init__(self, overpass_url: str = "https://overpass-api.de/api/interpreter"):
        self.overpass_url = overpass_url

    def fetch_data(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """TODO [Data Lead]: Execute Overpass API query."""
        return {
            "source": "OpenStreetMap",
            "elements": []
        }

    def is_available(self) -> bool:
        return True


class GovernmentDataProvider(DataProvider):
    """myScheme & Data.gov.in integration provider."""

    def fetch_data(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """TODO [Schemes Lead]: Query myScheme API."""
        return {
            "source": "myScheme Portal",
            "schemes": []
        }

    def is_available(self) -> bool:
        return True


class MarketPriceProvider(DataProvider):
    """Agmarknet / Mandi price provider."""

    def fetch_data(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """TODO [Data Lead]: Fetch local Mandi commodity benchmark rates."""
        return {
            "source": "Agmarknet Mandi Rates",
            "commodity_rates": {}
        }

    def is_available(self) -> bool:
        return True


class CensusProvider(DataProvider):
    """Census & SECC demographic data provider."""

    def fetch_data(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """TODO [Data Lead]: Query village demographic aggregates."""
        return {
            "source": "Census 2011 Aggregates",
            "village_population": 3800,
            "households": 620
        }

    def is_available(self) -> bool:
        return True


class CachedDataProvider(DataProvider):
    """Offline cache provider backed by local JSON files."""

    def __init__(self, cache_dir: str = "data/processed/"):
        self.cache_dir = cache_dir

    def fetch_data(self, query: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "source": "Local Cache",
            "cached": True
        }

    def is_available(self) -> bool:
        return True


class DemoDataProvider(DataProvider):
    """Deterministic static canned dataset provider for zero-network testing."""

    def fetch_data(self, query: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "source": "Demo Data Provider",
            "status": "ready"
        }

    def is_available(self) -> bool:
        return True
