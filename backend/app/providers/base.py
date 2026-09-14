from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from app.schemas.evidence import EvidenceItem, EvidenceType


class ProviderResult(BaseModel):
    """Normalized response envelope returned by all external or local data providers."""
    provider_name: str
    data_category: str
    success: bool
    evidence_items: List[EvidenceItem] = Field(default_factory=list)
    raw_payload: Optional[Dict[str, Any]] = None
    errors: List[str] = Field(default_factory=list)
    observed_at: Optional[str] = None
    expires_at: Optional[str] = None
    is_stale: bool = False
    freshness_hours: Optional[int] = None


class BaseDataProvider(ABC):
    """Abstract base class for all GramaVise data providers.
    
    Guiding Architectural Principles:
    1. Isolation: Provider failures (timeouts, rate limits) NEVER crash the advisory engine.
    2. Non-interference: Providers CANNOT modify financial math or feasibility verdicts.
    3. Provenance: Every returned data point must carry explicit evidence classification.
    4. Fallback: Unavailable data resolves gracefully to NEEDS_VERIFICATION.
    """

    def __init__(self, provider_name: str, data_category: str):
        self.provider_name = provider_name
        self.data_category = data_category

    @abstractmethod
    def fetch_evidence(self, query: Dict[str, Any]) -> ProviderResult:
        """Fetch and normalize evidence records matching the query parameters."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Health check for provider connectivity and credential status."""
        pass

    def create_fallback_result(self, indicator: str, reason: str, geography: str = "Catchment") -> ProviderResult:
        """Generate a safe, non-crashing fallback record marked NEEDS_VERIFICATION."""
        fallback_item = EvidenceItem(
            indicator=indicator,
            value="Data Unavailable",
            unit=None,
            evidence_type=EvidenceType.NEEDS_VERIFICATION,
            confidence=0.0,
            source=self.provider_name,
            source_url=None,
            source_title=f"{self.provider_name} ({self.data_category})",
            notes=f"Provider lookup failed or unconfigured: {reason}. Physical verification required.",
            verification_status="NEEDS_VERIFICATION"
        )
        return ProviderResult(
            provider_name=self.provider_name,
            data_category=self.data_category,
            success=False,
            evidence_items=[fallback_item],
            errors=[reason],
            observed_at=datetime.now(timezone.utc).isoformat(),
            is_stale=False
        )
