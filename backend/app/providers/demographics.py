import json
import os
import re
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from app.providers.base import BaseDataProvider, ProviderResult
from app.schemas.evidence import EvidenceItem, EvidenceType
from app.schemas.market import GeographyLevel
from app.utils.logging import logger


class DemographicDataProvider(BaseDataProvider):
    """Provider boundary for Village & District Demographics from Census of India 2011.
    
    Authoritative Source:
    Office of the Registrar General & Census Commissioner, India
    Dataset: Basic Population Figures of India/State/District/Sub-District/Village - 2011 (Primary Census Abstract)
    URL: https://censusindia.gov.in/census.website/data/population-finder
    Catalog: https://censusindia.gov.in/nada/index.php/catalog/42555
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
            provider_name="Office of the Registrar General & Census Commissioner, India",
            data_category="DEMOGRAPHICS"
        )
        self.is_mock = is_mock
        if data_file_path is None:
            self._data_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "data", "demographics", "census_2011_master.json"
            )
        else:
            self._data_file = data_file_path

        self._dataset: Optional[Dict[str, Any]] = None
        self._census_lookup: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
        self._load_dataset()

    def _load_dataset(self) -> None:
        """Load checked-in verified snapshot/sample of official Census 2011 PCA data."""
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
                            self._census_lookup[(s_norm, d_norm, v_norm)] = rec
            except Exception as e:
                logger.error(f"Failed to load Census 2011 master dataset from {self._data_file}: {e}")
                self._dataset = None

    def is_available(self) -> bool:
        return bool(self._census_lookup)

    @classmethod
    def normalize_state(cls, raw_state: str) -> Optional[str]:
        if not raw_state:
            return None
        cleaned = re.sub(r"[^a-zA-Z\s\.]", "", raw_state).strip().lower()
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cls.STATE_ALIASES.get(cleaned, cleaned if len(cleaned) > 2 else None)

    @classmethod
    def normalize_name(cls, raw_name: str) -> Optional[str]:
        if not raw_name:
            return None
        cleaned = raw_name.strip().lower()
        cleaned = re.sub(r"\b(district|dist\.?|taluk|taluka|tehsil|block|village|gram panchayat|gp)\b", "", cleaned).strip()
        cleaned = re.sub(r"[^a-zA-Z\s]", "", cleaned).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned if len(cleaned) > 1 else None

    def get_census_record(self, state: str, district: str, village: str) -> Optional[Dict[str, Any]]:
        s_norm = self.normalize_state(state)
        d_norm = self.normalize_name(district)
        v_norm = self.normalize_name(village)
        if not (s_norm and d_norm and v_norm):
            return None
        return self._census_lookup.get((s_norm, d_norm, v_norm))

    def fetch_evidence(self, query: Dict[str, Any]) -> ProviderResult:
        """Fetch official Census 2011 population and household observations."""
        raw_state = query.get("state", "")
        raw_district = query.get("district", "")
        raw_village = query.get("village", "")
        now_iso = datetime.now(timezone.utc).isoformat()

        s_norm = self.normalize_state(raw_state)
        d_norm = self.normalize_name(raw_district)
        v_norm = self.normalize_name(raw_village)

        if not (d_norm and v_norm):
            return self.create_fallback_result(
                indicator="Census 2011 Demographics",
                reason="District and village are required for Census 2011 demographic lookup."
            )

        meta = self._dataset.get("source_metadata", {}) if self._dataset else {}
        source_url = meta.get("source_url", "https://censusindia.gov.in/census.website/data/population-finder")
        source_title = meta.get("source_title", "Basic Population Figures of India/State/District/Sub-District/Village - 2011")
        source_last_verified = meta.get("source_last_verified", "2024-09")

        record = None
        if s_norm and (s_norm, d_norm, v_norm) in self._census_lookup:
            record = self._census_lookup[(s_norm, d_norm, v_norm)]
        elif not s_norm and d_norm and v_norm:
            # Match unique district + village
            matches = [rec for (s, d, v), rec in self._census_lookup.items() if d == d_norm and v == v_norm]
            if len(matches) == 1:
                record = matches[0]

        if record:
            pop = record.get("population", 0)
            hh = record.get("households", 0)
            ref_year = record.get("reference_year", 2011)
            v_name = record.get("village_name", raw_village)

            ev_type = EvidenceType.MODELLED if self.is_mock else EvidenceType.OBSERVED
            conf = 0.80 if self.is_mock else 1.0

            evidence = [
                EvidenceItem(
                    indicator="Census 2011 Population",
                    value=f"{pop:,} residents",
                    unit="persons",
                    evidence_type=ev_type,
                    confidence=conf,
                    source=self.provider_name,
                    source_title=source_title,
                    source_url=source_url,
                    source_last_verified=source_last_verified,
                    notes=f"Observed in Census 2011 for {v_name} (Reference Year: {ref_year}). Historical official observation; not a current population estimate.",
                    verification_status="VERIFIED_SOURCE"
                ),
                EvidenceItem(
                    indicator="Census 2011 Households",
                    value=f"{hh:,} households",
                    unit="households",
                    evidence_type=ev_type,
                    confidence=conf,
                    source=self.provider_name,
                    source_title=source_title,
                    source_url=source_url,
                    source_last_verified=source_last_verified,
                    notes=f"Observed in Census 2011 for {v_name} (Reference Year: {ref_year}). Historical official observation.",
                    verification_status="VERIFIED_SOURCE"
                )
            ]
            return ProviderResult(
                provider_name=self.provider_name,
                data_category=self.data_category,
                success=True,
                evidence_items=evidence,
                raw_payload={
                    "geography_level": GeographyLevel.VILLAGE.value,
                    "state_name": record.get("state_name"),
                    "district_name": record.get("district_name"),
                    "sub_district_name": record.get("sub_district_name"),
                    "village_name": v_name,
                    "population": pop,
                    "households": hh,
                    "reference_year": ref_year,
                    "data_status": "HISTORICAL_OFFICIAL",
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
        elif self.is_mock:
            # Fallback prototype demographic estimate if explicitly running in mock mode
            pop_item = EvidenceItem(
                indicator="Catchment Population Estimate",
                value="4,500 residents",
                unit="persons",
                evidence_type=EvidenceType.MODELLED,
                confidence=0.50,
                source="GramaVise Prototype Catchment Model",
                source_title="Prototype Radius Estimation [DEMO]",
                source_url=None,
                notes="[DEMO / PROTOTYPE DATA] Modelled catchment population within 5km radius.",
                verification_status="NEEDS_VERIFICATION"
            )
            return ProviderResult(
                provider_name=self.provider_name,
                data_category=self.data_category,
                success=True,
                evidence_items=[pop_item],
                raw_payload={"village": raw_village, "district": raw_district, "geography_level": GeographyLevel.CATCHMENT.value},
                observed_at=now_iso
            )
        else:
            evidence = [
                EvidenceItem(
                    indicator="Census 2011 Demographics",
                    value=f"Village '{raw_village}' requires field verification",
                    unit="persons",
                    evidence_type=EvidenceType.NEEDS_VERIFICATION,
                    confidence=0.50,
                    source=self.provider_name,
                    source_title=source_title,
                    source_url=source_url,
                    source_last_verified=source_last_verified,
                    notes=f"Village '{raw_village}' is outside the checked-in verified snapshot of Census 2011 PCA records; demographic field verification required.",
                    verification_status="NEEDS_VERIFICATION"
                )
            ]
            return ProviderResult(
                provider_name=self.provider_name,
                data_category=self.data_category,
                success=True,
                evidence_items=evidence,
                raw_payload={
                    "geography_level": GeographyLevel.VILLAGE.value,
                    "state_name": raw_state,
                    "district_name": raw_district,
                    "village_name": raw_village,
                    "population": None,
                    "households": None,
                    "reference_year": 2011,
                    "data_status": "NEEDS_VERIFICATION"
                },
                observed_at=now_iso
            )
