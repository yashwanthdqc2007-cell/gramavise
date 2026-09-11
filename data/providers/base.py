from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class DataProvider(ABC):
    """Abstract base provider for hyper-local market, demographic, and benchmark data."""

    @abstractmethod
    def fetch_data(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch raw or structured records matching the query parameters."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Health check for external API or local source connectivity."""
        pass
