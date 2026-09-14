import json
import os
import re
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timezone
from app.providers.base import BaseDataProvider, ProviderResult
from app.schemas.evidence import EvidenceItem, EvidenceType
from app.utils.logging import logger


class OdopDataProvider(BaseDataProvider):
    """Provider for One District One Product (ODOP) Master Registries.
    
    Authoritative Source:
    Ministry of Food Processing Industries (MoFPI) — PMFME ODOP Master Registry
    Portal: https://pmfme.mofpi.gov.in/
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

    def __init__(self, data_file_path: Optional[str] = None):
        super().__init__(provider_name="MoFPI PMFME ODOP Master Registry", data_category="ODOP")
        if data_file_path is None:
            self._data_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "data", "odop", "odop_national_master.json"
            )
        else:
            self._data_file = data_file_path
        
        self._dataset: Optional[Dict[str, Any]] = None
        self._odop_lookup: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self._load_dataset()

    def _load_dataset(self) -> None:
        """Load checked-in official MoFPI ODOP national master dataset."""
        if os.path.exists(self._data_file):
            try:
                with open(self._data_file, "r", encoding="utf-8") as f:
                    self._dataset = json.load(f)
                    records = self._dataset.get("records", [])
                    for rec in records:
                        s_norm = self.normalize_state(rec.get("state", ""))
                        d_norm = self.normalize_district(rec.get("district", ""))
                        if s_norm and d_norm:
                            self._odop_lookup[(s_norm, d_norm)] = rec
                            # Also register normalized alias if present
                            if "district_normalized" in rec:
                                d_alias = self.normalize_district(rec["district_normalized"])
                                self._odop_lookup[(s_norm, d_alias)] = rec
            except Exception as e:
                logger.error(f"Failed to load ODOP master dataset from {self._data_file}: {e}")
                self._dataset = None

    def is_available(self) -> bool:
        return bool(self._odop_lookup)

    @classmethod
    def normalize_state(cls, raw_state: str) -> Optional[str]:
        """Normalize state string against standard aliases without aggressive fuzzy guessing."""
        if not raw_state:
            return None
        cleaned = re.sub(r"[^a-zA-Z\s\.]", "", raw_state).strip().lower()
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cls.STATE_ALIASES.get(cleaned, cleaned if len(cleaned) > 2 else None)

    @classmethod
    def normalize_district(cls, raw_district: str) -> Optional[str]:
        """Normalize district string: strip common suffixes ('district', 'dist', 'taluka')."""
        if not raw_district:
            return None
        cleaned = raw_district.strip().lower()
        cleaned = re.sub(r"\b(district|dist\.?|taluk|taluka|tehsil|block)\b", "", cleaned).strip()
        cleaned = re.sub(r"[^a-zA-Z\s]", "", cleaned).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned if len(cleaned) > 1 else None

    def get_odop_record(self, state: str, district: str) -> Optional[Dict[str, Any]]:
        """Retrieve verified ODOP record for given state and district."""
        s_norm = self.normalize_state(state)
        d_norm = self.normalize_district(district)
        if not (s_norm and d_norm):
            return None
        return self._odop_lookup.get((s_norm, d_norm))

    def fetch_evidence(self, query: Dict[str, Any]) -> ProviderResult:
        """Fetch and structure official ODOP evidence from gazetted master registry."""
        raw_state = query.get("state", "")
        raw_district = query.get("district", "")
        now_iso = datetime.now(timezone.utc).isoformat()

        s_norm = self.normalize_state(raw_state)
        d_norm = self.normalize_district(raw_district)

        if not (s_norm and d_norm):
            return self.create_fallback_result(
                indicator="District ODOP Product",
                reason="State or District name could not be resolved cleanly to official administrative listing."
            )

        record = self._odop_lookup.get((s_norm, d_norm))
        meta = self._dataset.get("source_metadata", {}) if self._dataset else {}
        source_url = meta.get("source_url", "https://pmfme.mofpi.gov.in/")
        source_title = meta.get("source_title", "MoFPI PMFME Approved National ODOP Master Registry")

        if record:
            product = record.get("odop_product", "Notified Food Product")
            evidence = [
                EvidenceItem(
                    indicator="District ODOP Product",
                    value=product,
                    unit="category",
                    evidence_type=EvidenceType.OBSERVED,
                    confidence=1.0,
                    source=self.provider_name,
                    source_title=source_title,
                    source_url=source_url,
                    notes=f"Officially notified One District One Product for {d_norm.title()}, {s_norm.title()}.",
                    verification_status="OFFICIALLY_NOTIFIED"
                )
            ]
            return ProviderResult(
                provider_name=self.provider_name,
                data_category=self.data_category,
                success=True,
                evidence_items=evidence,
                raw_payload={
                    "state": s_norm,
                    "district": d_norm,
                    "odop_product": product,
                    "category": record.get("category"),
                    "keywords": record.get("keywords", [])
                },
                observed_at=now_iso
            )
        else:
            evidence = [
                EvidenceItem(
                    indicator="District ODOP Product",
                    value="Requires Cluster Verification",
                    unit="category",
                    evidence_type=EvidenceType.NEEDS_VERIFICATION,
                    confidence=0.50,
                    source=self.provider_name,
                    source_title=source_title,
                    source_url=source_url,
                    notes=f"District {d_norm.title()} ODOP alignment could not be verified from official snapshot; field verification required.",
                    verification_status="NEEDS_VERIFICATION"
                )
            ]
            return ProviderResult(
                provider_name=self.provider_name,
                data_category=self.data_category,
                success=True,
                evidence_items=evidence,
                raw_payload={"state": s_norm, "district": d_norm, "odop_product": None},
                observed_at=now_iso
            )

    def evaluate_alignment(
        self,
        state: str,
        district: str,
        category: str,
        description: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Evaluate whether business activity matches district's notified ODOP produce.
        
        Returns:
            (is_aligned, odop_product_name, alignment_reason)
        """
        record = self.get_odop_record(state, district)
        if not record:
            return (False, None, "District ODOP produce could not be verified from official snapshot.")

        odop_product = record.get("odop_product", "")
        GENERIC_KEYWORDS = {"food", "processing", "micro", "enterprise", "unit", "small", "agro", "value", "addition", "product", "products"}
        keywords = [kw.lower() for kw in record.get("keywords", []) if kw.lower() not in GENERIC_KEYWORDS and len(kw) > 2]
        text = f"{category or ''} {description or ''}".lower()

        # Check genuine product-specific keyword matches with word boundaries
        if any(re.search(r"\b" + re.escape(kw) + r"\b", text) for kw in keywords):
            return (
                True,
                odop_product,
                f"Business activity aligns with district's notified ODOP produce: '{odop_product}'."
            )

        return (
            False,
            odop_product,
            f"Food processing activity is distinct from district's notified ODOP produce ('{odop_product}')."
        )
