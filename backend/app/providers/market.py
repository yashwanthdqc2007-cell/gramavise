from typing import Dict, Any, Optional
from app.providers.base import BaseDataProvider, ProviderResult
from app.providers.competitor import OSMCompetitorProvider


class MarketCompetitorProvider(OSMCompetitorProvider):
    """Backward-compatible alias for OSMCompetitorProvider."""
    pass
