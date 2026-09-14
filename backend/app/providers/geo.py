import json
import os
import re
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timezone
from app.providers.base import BaseDataProvider, ProviderResult
from app.schemas.evidence import EvidenceItem, EvidenceType
from app.schemas.market import GeographyLevel
from app.utils.logging import logger


class GeoDataProvider(BaseDataProvider):
    """Provider boundary for Geographic Hierarchy & Entity Identification (LGD).
    
    Authoritative Source:
    Ministry of Panchayati Raj, Government of India — Local Government Directory (LGD)
    Portal: https://lgdirectory.gov.in/
    Catalog: https://data.gov.in/catalog/local-government-directory-lgd
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
    }

    def __init__(self, data_file_path: Optional[str] = None, is_mock: bool = False, **kwargs):
        super().__init__(
            provider_name="Ministry of Panchayati Raj / Local Government Directory (LGD)",
            data_category="GEOGRAPHY"
        )
        self.is_mock = is_mock
        if data_file_path is None:
            self._data_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "data", "geo", "lgd_master.json"
            )
        else:
            self._data_file = data_file_path

        self._dataset: Optional[Dict[str, Any]] = None
        self._village_lookup: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
        self._district_lookup: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self._load_dataset()

    def _load_dataset(self) -> None:
        """Load checked-in verified snapshot/sample of official LGD master data."""
        if os.path.exists(self._data_file):
            try:
                with open(self._data_file, "r", encoding="utf-8") as f:
                    self._dataset = json.load(f)
                    records = self._dataset.get("records", [])
                    for rec in records:
                        s_norm = self.normalize_name(rec.get("state_name", ""))
                        d_norm = self.normalize_name(rec.get("district_name", ""))
                        v_norm = self.normalize_name(rec.get("village_name", ""))
                        if s_norm and d_norm and v_norm:
                            self._village_lookup[(s_norm, d_norm, v_norm)] = rec
                        if s_norm and d_norm and (s_norm, d_norm) not in self._district_lookup:
                            self._district_lookup[(s_norm, d_norm)] = {
                                "state_name": rec.get("state_name"),
                                "state_lgd_code": rec.get("state_lgd_code"),
                                "district_name": rec.get("district_name"),
                                "district_lgd_code": rec.get("district_lgd_code"),
                                "hierarchy_level": "DISTRICT"
                            }
            except Exception as e:
                logger.error(f"Failed to load LGD master dataset from {self._data_file}: {e}")
                self._dataset = None

    def is_available(self) -> bool:
        return bool(self._village_lookup or self._district_lookup)

    @classmethod
    def normalize_state(cls, raw_state: str) -> Optional[str]:
        if not raw_state:
            return None
        cleaned = re.sub(r"[^a-zA-Z\s\.]", "", raw_state).strip().lower()
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cls.STATE_ALIASES.get(cleaned, cleaned if len(cleaned) > 2 else None)

    @classmethod
    def normalize_name(cls, raw_name: str) -> Optional[str]:
        """Normalize district/sub-district/village names safely without aggressive fuzzy matching."""
        if not raw_name:
            return None
        cleaned = raw_name.strip().lower()
        cleaned = re.sub(r"\b(district|dist\.?|taluk|taluka|tehsil|block|village|gram panchayat|gp)\b", "", cleaned).strip()
        cleaned = re.sub(r"[^a-zA-Z\s]", "", cleaned).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned if len(cleaned) > 1 else None

    def get_lgd_record(self, state: str, district: str, village: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Lookup verified LGD record by hierarchy."""
        s_norm = self.normalize_state(state)
        d_norm = self.normalize_name(district)
        v_norm = self.normalize_name(village) if village else None

        if not (s_norm and d_norm):
            return None

        if v_norm and (s_norm, d_norm, v_norm) in self._village_lookup:
            return self._village_lookup[(s_norm, d_norm, v_norm)]

        return self._district_lookup.get((s_norm, d_norm))

    def fetch_evidence(self, query: Dict[str, Any]) -> ProviderResult:
        """Fetch normalized LGD administrative identity and official codes."""
        raw_state = query.get("state", "")
        raw_district = query.get("district", "")
        raw_village = query.get("village", "")
        now_iso = datetime.now(timezone.utc).isoformat()

        s_norm = self.normalize_state(raw_state)
        d_norm = self.normalize_name(raw_district)
        v_norm = self.normalize_name(raw_village) if raw_village else None

        if not (s_norm and d_norm):
            return self.create_fallback_result(
                indicator="Administrative Boundary (LGD)",
                reason="State or District name could not be resolved to an official administrative entity."
            )

        meta = self._dataset.get("source_metadata", {}) if self._dataset else {}
        source_url = meta.get("source_url", "https://lgdirectory.gov.in/")
        source_title = meta.get("source_title", "Local Government Directory (LGD) — Administrative Master Registry")
        source_last_verified = meta.get("source_last_verified", "2024-09")

        # 1. Exact Village Match
        if v_norm and (s_norm, d_norm, v_norm) in self._village_lookup:
            rec = self._village_lookup[(s_norm, d_norm, v_norm)]
            v_code = rec.get("village_lgd_code")
            d_code = rec.get("district_lgd_code")
            s_code = rec.get("state_lgd_code")
            sd_name = rec.get("sub_district_name", "")

            evidence = [
                EvidenceItem(
                    indicator="Administrative Boundary (LGD)",
                    value=f"{rec.get('village_name')}, {rec.get('district_name')}, {rec.get('state_name')}",
                    unit="hierarchy",
                    evidence_type=EvidenceType.MODELLED if self.is_mock else EvidenceType.OBSERVED,
                    confidence=0.80 if self.is_mock else 1.0,
                    source=self.provider_name,
                    source_title=source_title,
                    source_url=source_url,
                    source_last_verified=source_last_verified,
                    notes=f"Identified administrative entity in LGD. Village LGD Code: {v_code}, District LGD Code: {d_code}.",
                    verification_status="VERIFIED_SOURCE"
                )
            ]
            return ProviderResult(
                provider_name=self.provider_name,
                data_category=self.data_category,
                success=True,
                evidence_items=evidence,
                raw_payload={
                    "state_name": rec.get("state_name"),
                    "state_lgd_code": s_code,
                    "district_name": rec.get("district_name"),
                    "district_lgd_code": d_code,
                    "sub_district_name": sd_name,
                    "sub_district_lgd_code": rec.get("sub_district_lgd_code"),
                    "village_name": rec.get("village_name"),
                    "village_lgd_code": v_code,
                    "geography_level": GeographyLevel.VILLAGE.value,
                    "source": self.provider_name,
                    "source_url": source_url,
                    "source_title": source_title,
                    "source_last_verified": source_last_verified,
                    "evidence_type": "OBSERVED",
                    "confidence": "HIGH",
                    "verification_status": "VERIFIED_SOURCE"
                },
                observed_at=now_iso
            )

        # 2. District Verified, but Village Unresolved in Snapshot
        elif (s_norm, d_norm) in self._district_lookup:
            rec = self._district_lookup[(s_norm, d_norm)]
            d_code = rec.get("district_lgd_code")
            s_code = rec.get("state_lgd_code")

            evidence = [
                EvidenceItem(
                    indicator="Administrative Boundary (LGD)",
                    value=f"{rec.get('district_name')}, {rec.get('state_name')}",
                    unit="hierarchy",
                    evidence_type=EvidenceType.MODELLED if self.is_mock else EvidenceType.OBSERVED,
                    confidence=0.80 if self.is_mock else 1.0,
                    source=self.provider_name,
                    source_title=source_title,
                    source_url=source_url,
                    source_last_verified=source_last_verified,
                    notes=f"District administrative identity verified (District LGD Code: {d_code}). Village '{raw_village}' is outside the checked-in verified snapshot and requires field verification.",
                    verification_status="VERIFIED_SOURCE"
                )
            ]
            return ProviderResult(
                provider_name=self.provider_name,
                data_category=self.data_category,
                success=True,
                evidence_items=evidence,
                raw_payload={
                    "state_name": rec.get("state_name"),
                    "state_lgd_code": s_code,
                    "district_name": rec.get("district_name"),
                    "district_lgd_code": d_code,
                    "sub_district_name": None,
                    "sub_district_lgd_code": None,
                    "village_name": None,
                    "village_lgd_code": None,
                    "geography_level": GeographyLevel.DISTRICT.value,
                    "source": self.provider_name,
                    "source_url": source_url,
                    "source_title": source_title,
                    "source_last_verified": source_last_verified,
                    "evidence_type": "OBSERVED",
                    "confidence": "HIGH",
                    "verification_status": "VERIFIED_SOURCE"
                },
                observed_at=now_iso
            )

        # 3. Unresolved / Out-of-Snapshot
        else:
            evidence = [
                EvidenceItem(
                    indicator="Administrative Boundary (LGD)",
                    value=f"{raw_village}, {raw_district}, {raw_state}".strip(", "),
                    unit="hierarchy",
                    evidence_type=EvidenceType.NEEDS_VERIFICATION,
                    confidence=0.50,
                    source=self.provider_name,
                    source_title=source_title,
                    source_url=source_url,
                    source_last_verified=source_last_verified,
                    notes=f"Administrative entity could not be verified in the checked-in LGD snapshot; administrative directory verification required.",
                    verification_status="NEEDS_VERIFICATION"
                )
            ]
            return ProviderResult(
                provider_name=self.provider_name,
                data_category=self.data_category,
                success=True,
                evidence_items=evidence,
                raw_payload={
                    "state_name": raw_state,
                    "district_name": raw_district,
                    "village_name": raw_village,
                    "geography_level": GeographyLevel.VILLAGE.value,
                    "state_lgd_code": None,
                    "district_lgd_code": None,
                    "village_lgd_code": None
                },
                observed_at=now_iso
            )
