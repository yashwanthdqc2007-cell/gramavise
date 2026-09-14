import json
import os
import re
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timezone
from app.providers.base import BaseDataProvider, ProviderResult
from app.schemas.evidence import EvidenceItem, EvidenceType
from app.schemas.market import UdyamDistrictContext, GeographyLevel
from app.utils.logging import logger


class UdyamContextProvider(BaseDataProvider):
    """Provider for District-Level Registered MSME Aggregates.
    
    Authoritative Source:
    Ministry of Micro, Small and Medium Enterprises (MoMSME) / data.gov.in
    Portal: https://udyamregistration.gov.in/
    
    IMPORTANT POLICY:
    - Provides district-level formal enterprise density context ONLY.
    - Must NOT be used as or converted into a count of nearby competitors.
    """

    STATE_ALIASES = {
        "mp": "madhya pradesh",
        "m.p.": "madhya pradesh",
        "madhya pradesh": "madhya pradesh",
        "mh": "maharashtra",
        "m.h.": "maharashtra",
        "maharashtra": "maharashtra",
        "up": "uttar pradesh",
        "u.p.": "uttar pradesh",
        "uttar pradesh": "uttar pradesh",
        "bihar": "bihar",
        "rajasthan": "rajasthan",
        "rj": "rajasthan",
        "gujarat": "gujarat",
        "telangana": "telangana",
        "ts": "telangana",
        "tg": "telangana",
        "tamil nadu": "tamil nadu",
        "tn": "tamil nadu",
        "karnataka": "karnataka",
        "ka": "karnataka",
        "punjab": "punjab",
        "pb": "punjab",
        "haryana": "haryana",
        "hr": "haryana",
        "andhra pradesh": "andhra pradesh",
        "ap": "andhra pradesh",
        "kerala": "kerala",
        "kl": "kerala",
        "west bengal": "west bengal",
        "wb": "west bengal",
        "odisha": "odisha",
        "orissa": "odisha",
        "jharkhand": "jharkhand",
        "chhattisgarh": "chhattisgarh",
        "assam": "assam"
    }

    def __init__(self, data_file_path: Optional[str] = None):
        super().__init__(
            provider_name="Ministry of Micro, Small and Medium Enterprises / data.gov.in",
            data_category="UDYAM_MSME"
        )
        if data_file_path is None:
            self._data_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "data", "udyam", "udyam_district_master.json"
            )
        else:
            self._data_file = data_file_path
        
        self._dataset: Optional[Dict[str, Any]] = None
        self._udyam_lookup: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self._load_dataset()

    def _load_dataset(self) -> None:
        """Load checked-in official Udyam district MSME aggregates."""
        if os.path.exists(self._data_file):
            try:
                with open(self._data_file, "r", encoding="utf-8") as f:
                    self._dataset = json.load(f)
                    records = self._dataset.get("records", [])
                    for rec in records:
                        s_norm = self.normalize_state(rec.get("state_name", ""))
                        d_norm = self.normalize_district(rec.get("district_name", ""))
                        if s_norm and d_norm:
                            self._udyam_lookup[(s_norm, d_norm)] = rec
            except Exception as e:
                logger.error(f"Failed to load Udyam master dataset from {self._data_file}: {e}")
                self._dataset = None

    def is_available(self) -> bool:
        return bool(self._udyam_lookup)

    @classmethod
    def normalize_state(cls, raw_state: str) -> Optional[str]:
        """Normalize state string against standard aliases."""
        if not raw_state:
            return None
        cleaned = re.sub(r"[^a-zA-Z\s\.]", "", raw_state).strip().lower()
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cls.STATE_ALIASES.get(cleaned, cleaned if len(cleaned) > 2 else None)

    @classmethod
    def normalize_district(cls, raw_district: str) -> Optional[str]:
        """Normalize district string."""
        if not raw_district:
            return None
        cleaned = re.sub(r"[^a-zA-Z\s]", "", raw_district).strip().lower()
        cleaned = re.sub(r"\b(district|dist|taluka|subdivision|division)\b", "", cleaned).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned if len(cleaned) >= 2 else None

    def get_district_context(self, state: str, district: str) -> Optional[UdyamDistrictContext]:
        """Lookup district-level Udyam aggregates."""
        s_norm = self.normalize_state(state)
        d_norm = self.normalize_district(district)
        if not (s_norm and d_norm):
            return None

        rec = self._udyam_lookup.get((s_norm, d_norm))
        if not rec:
            return None

        meta = (self._dataset or {}).get("source_metadata", {})
        return UdyamDistrictContext(
            state_name=rec.get("state_name", state),
            district_name=rec.get("district_name", district),
            lgd_district_code=rec.get("lgd_district_code"),
            registered_msme_count=rec.get("registered_msme_count", 0),
            micro_count=rec.get("micro_count"),
            small_count=rec.get("small_count"),
            medium_count=rec.get("medium_count"),
            manufacturing_count=rec.get("manufacturing_count"),
            services_count=rec.get("services_count"),
            geography_level=GeographyLevel.DISTRICT,
            evidence_type=EvidenceType.OBSERVED,
            confidence=1.0,
            source=meta.get("nodal_ministry", "Ministry of Micro, Small and Medium Enterprises / data.gov.in"),
            source_url=meta.get("source_url", "https://udyamregistration.gov.in/"),
            dataset_name=meta.get("source_title", "Udyam Registration District-wise MSME Aggregates"),
            observed_at=rec.get("observed_at") or meta.get("observed_at"),
            verification_status="VERIFIED_SOURCE",
            notes="District-level formal MSME context only; not a count of nearby competitors."
        )

    def fetch_evidence(self, query: Dict[str, Any]) -> ProviderResult:
        """Fetch district-level registered MSME context."""
        state = query.get("state", "")
        district = query.get("district", "")
        now_iso = datetime.now(timezone.utc).isoformat()

        context_obj = self.get_district_context(state, district)
        if not context_obj:
            return self.create_fallback_result(
                indicator="District Registered MSMEs",
                reason=f"District '{district}' in '{state}' not found in official Udyam snapshot",
                geography="District"
            )

        evidence = [
            EvidenceItem(
                indicator="District Registered MSMEs",
                value=f"{context_obj.registered_msme_count:,} registered enterprises",
                unit="enterprises",
                evidence_type=EvidenceType.OBSERVED,
                confidence=1.0,
                source=context_obj.source,
                source_url=context_obj.source_url,
                source_title=context_obj.dataset_name,
                notes=(
                    f"District formal MSME density: {context_obj.micro_count or 0:,} micro, "
                    f"{context_obj.small_count or 0:,} small, {context_obj.medium_count or 0:,} medium. "
                    "District-level formal context only; not a count of nearby competitors."
                ),
                verification_status="VERIFIED_SOURCE"
            )
        ]

        return ProviderResult(
            provider_name=self.provider_name,
            data_category=self.data_category,
            success=True,
            evidence_items=evidence,
            raw_payload={"udyam_context": context_obj.model_dump()},
            observed_at=context_obj.observed_at or now_iso
        )
