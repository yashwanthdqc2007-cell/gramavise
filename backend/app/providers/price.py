import json
import os
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone, timedelta
from app.providers.base import BaseDataProvider, ProviderResult
from app.schemas.evidence import EvidenceItem, EvidenceType
from app.schemas.market import GeographyLevel
from app.utils.logging import logger


class PriceDataProvider(BaseDataProvider):
    """Provider boundary for Agricultural Mandi & Essential Commodity Prices.
    
    Authoritative Official Source:
    Government of India — Open Government Data (OGD) Platform
    Dataset: "Current Daily Price of Various Commodities from Various Markets (Mandi)"
    Source Department: Directorate of Marketing & Inspection (DMI), Department of Agriculture & Farmers Welfare
    Source URL: https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi
    Agmarknet Portal: https://agmarknet.gov.in/
    """

    COMMODITY_MAPPINGS = {
        "tomato": "Tomato",
        "tomatoes": "Tomato",
        "tamatar": "Tomato",
        "onion": "Onion",
        "onions": "Onion",
        "pyaz": "Onion",
        "kanda": "Onion",
        "garlic": "Garlic",
        "lahsun": "Garlic",
        "lasun": "Garlic",
        "wheat": "Wheat",
        "wheat grain": "Wheat",
        "gehun": "Wheat",
        "potato": "Potato",
        "potatoes": "Potato",
        "aloo": "Potato",
        "batata": "Potato",
        "soybean": "Soybean",
        "soya bean": "Soybean",
        "soyabean": "Soybean",
        "chilli": "Chilli Green",
        "green chilli": "Chilli Green",
        "chilli green": "Chilli Green",
        "mirchi": "Chilli Green",
        "kodo": "Millet (Kodo)",
        "kodo millet": "Millet (Kodo)",
        "millet (kodo)": "Millet (Kodo)",
        "millet": "Millet (Kodo)",
        "banana": "Banana",
        "kela": "Banana",
    }

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
        "karnataka": "karnataka",
        "ka": "karnataka",
        "punjab": "punjab",
        "haryana": "haryana",
        "andhra pradesh": "andhra pradesh",
        "tamil nadu": "tamil nadu",
    }

    def __init__(self, data_file_path: Optional[str] = None, is_mock: bool = False, freshness_hours: int = 24, **kwargs):
        super().__init__(
            provider_name="Directorate of Marketing & Inspection (DMI) / OGD",
            data_category="PRICING"
        )
        self.is_mock = is_mock
        self.freshness_hours = freshness_hours
        if data_file_path is None:
            self._data_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "data", "pricing", "mandi_prices_master.json"
            )
        else:
            self._data_file = data_file_path

        self._dataset: Optional[Dict[str, Any]] = None
        self._records: List[Dict[str, Any]] = []
        self._load_dataset()

    def _load_dataset(self) -> None:
        """Load checked-in verified snapshot of official Agmarknet / OGD daily mandi prices."""
        if os.path.exists(self._data_file):
            try:
                with open(self._data_file, "r", encoding="utf-8") as f:
                    self._dataset = json.load(f)
                    self._records = self._dataset.get("records", [])
            except Exception as e:
                logger.error(f"Failed to load Mandi Prices master dataset from {self._data_file}: {e}")
                self._dataset = None
                self._records = []

    def is_available(self) -> bool:
        return bool(self._records)

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
        cleaned = re.sub(r"\b(district|dist\.?|apmc|mandi|market|sub-market|yard)\b", "", cleaned).strip()
        cleaned = re.sub(r"[^a-zA-Z\s]", "", cleaned).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned if len(cleaned) > 1 else None

    @classmethod
    def resolve_commodity(cls, raw_input: str) -> Optional[str]:
        """Conservative commodity matching. No aggressive fuzzy matching."""
        if not raw_input:
            return None
        cleaned = raw_input.strip().lower()
        # Direct lookup
        if cleaned in cls.COMMODITY_MAPPINGS:
            return cls.COMMODITY_MAPPINGS[cleaned]

        # Clean non-alphanumeric except spaces
        cleaned_alpha = re.sub(r"[^a-zA-Z\s]", "", cleaned).strip()
        cleaned_alpha = re.sub(r"\s+", " ", cleaned_alpha)
        if cleaned_alpha in cls.COMMODITY_MAPPINGS:
            return cls.COMMODITY_MAPPINGS[cleaned_alpha]

        # Check token equality for exact commodity noun phrases (avoid partial substring collisions)
        for key, canonical in cls.COMMODITY_MAPPINGS.items():
            if cleaned_alpha == key:
                return canonical

        return None

    def query_mandi_prices(
        self,
        commodity: str,
        state: Optional[str] = None,
        district: Optional[str] = None,
        market: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Find matching mandi records following strict hierarchical matching:
        1. Exact market match in district & state
        2. District-level match
        3. State-level match
        """
        resolved_comm = self.resolve_commodity(commodity)
        if not resolved_comm:
            return []

        s_norm = self.normalize_state(state) if state else None
        d_norm = self.normalize_name(district) if district else None
        m_norm = self.normalize_name(market) if market else None

        # Filter by commodity
        comm_records = [
            r for r in self._records
            if r.get("commodity", "").strip().lower() == resolved_comm.lower()
        ]

        if not comm_records:
            return []

        # 1. Exact market match
        if m_norm and d_norm:
            exact_market = [
                r for r in comm_records
                if self.normalize_name(r.get("market_name", "")) == m_norm
                and (not d_norm or self.normalize_name(r.get("district_name", "")) == d_norm)
                and (not s_norm or self.normalize_state(r.get("state_name", "")) == s_norm)
            ]
            if exact_market:
                return exact_market

        # 2. District-level match
        if d_norm:
            district_matches = [
                r for r in comm_records
                if self.normalize_name(r.get("district_name", "")) == d_norm
                and (not s_norm or self.normalize_state(r.get("state_name", "")) == s_norm)
            ]
            if district_matches:
                return district_matches

        # 3. State-level match
        if s_norm:
            state_matches = [
                r for r in comm_records
                if self.normalize_state(r.get("state_name", "")) == s_norm
            ]
            if state_matches:
                return state_matches

        return []

    def fetch_evidence(self, query: Dict[str, Any]) -> ProviderResult:
        """Fetch official Agmarknet / OGD mandi price observations with strict provenance."""
        category = query.get("category", "") or query.get("commodity", "") or ""
        state = query.get("state", "")
        district = query.get("district", "")
        market = query.get("market", "")
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        expires_at = (now + timedelta(hours=self.freshness_hours)).isoformat() if self.freshness_hours else None

        meta = self._dataset.get("source_metadata", {}) if self._dataset else {}
        source_url = meta.get("source_url", "https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi")
        source_title = meta.get("source_title", "Current Daily Price of Various Commodities from Various Markets (Mandi)")
        source_department = meta.get("source_department", "Directorate of Marketing & Inspection (DMI)")
        source_last_verified = meta.get("source_last_verified", "2024-09")

        resolved_comm = self.resolve_commodity(category)
        if not resolved_comm:
            # Commodity not identified or outside agricultural snapshot
            evidence = [
                EvidenceItem(
                    indicator="Observed Mandi Price",
                    value=f"No verified mandi price feed for '{category}'",
                    unit="INR/quintal",
                    evidence_type=EvidenceType.NEEDS_VERIFICATION,
                    confidence=0.0,
                    source=self.provider_name,
                    source_title=source_title,
                    source_url=source_url,
                    source_last_verified=source_last_verified,
                    notes=f"Commodity/category '{category}' is not mapped or outside the checked-in Agmarknet mandi price snapshot. Local wholesale verification required.",
                    verification_status="NEEDS_VERIFICATION"
                )
            ]
            return ProviderResult(
                provider_name=self.provider_name,
                data_category=self.data_category,
                success=True,
                evidence_items=evidence,
                raw_payload={
                    "commodity": category,
                    "district": district,
                    "state": state,
                    "verification_status": "NEEDS_VERIFICATION",
                    "price_observations": []
                },
                observed_at=now_iso,
                expires_at=expires_at,
                freshness_hours=self.freshness_hours,
                is_stale=False
            )

        matching_records = self.query_mandi_prices(
            commodity=resolved_comm,
            state=state,
            district=district,
            market=market
        )

        if not matching_records:
            evidence = [
                EvidenceItem(
                    indicator=f"Observed Mandi Price: {resolved_comm}",
                    value=f"No reported mandi observations in {district or state or 'target area'}",
                    unit="INR/quintal",
                    evidence_type=EvidenceType.NEEDS_VERIFICATION,
                    confidence=0.0,
                    source=self.provider_name,
                    source_title=source_title,
                    source_url=source_url,
                    source_last_verified=source_last_verified,
                    notes=f"No official mandi price records found for {resolved_comm} in {district or state or 'target area'} within checked-in Agmarknet snapshot. Local APMC verification required.",
                    verification_status="NEEDS_VERIFICATION"
                )
            ]
            return ProviderResult(
                provider_name=self.provider_name,
                data_category=self.data_category,
                success=True,
                evidence_items=evidence,
                raw_payload={
                    "commodity": resolved_comm,
                    "district": district,
                    "state": state,
                    "verification_status": "NEEDS_VERIFICATION",
                    "price_observations": []
                },
                observed_at=now_iso,
                expires_at=expires_at,
                freshness_hours=self.freshness_hours,
                is_stale=False
            )

        # Build structured price observations
        primary_record = matching_records[0]
        modal_price = primary_record.get("modal_price", 0.0)
        min_price = primary_record.get("min_price", 0.0)
        max_price = primary_record.get("max_price", 0.0)
        unit = primary_record.get("price_unit", "INR/quintal")
        market_name = primary_record.get("market_name", "APMC Mandi")
        dist_name = primary_record.get("district_name", district)
        st_name = primary_record.get("state_name", state)
        arrival_date = primary_record.get("arrival_date", "")
        variety = primary_record.get("variety", "")

        # Unit conversion: 1 quintal = 100 kg
        price_per_kg = None
        unit_str_display = unit
        if "quintal" in unit.lower():
            price_per_kg = round(modal_price / 100.0, 2)
            unit_str_display = f"₹{modal_price:,.2f}/quintal (₹{price_per_kg:.2f}/kg)"
        else:
            unit_str_display = f"₹{modal_price:,.2f} / {unit}"

        # Parse arrival date for display
        date_formatted = arrival_date
        try:
            d_obj = datetime.strptime(arrival_date, "%Y-%m-%d")
            date_formatted = d_obj.strftime("%d %b %Y")
        except Exception:
            pass

        evidence = [
            EvidenceItem(
                indicator=f"Observed Mandi Modal Price: {resolved_comm}",
                value=unit_str_display,
                unit=unit,
                evidence_type=EvidenceType.OBSERVED,
                confidence=1.0,
                source=self.provider_name,
                source_title=source_title,
                source_url=source_url,
                source_last_verified=source_last_verified,
                notes=(
                    f"Reported mandi modal price observed on {date_formatted} at {market_name} APMC ({dist_name}, {st_name}) "
                    f"for variety '{variety}'. Reference market observation only; not a retail selling price recommendation."
                ),
                verification_status="VERIFIED_SOURCE"
            )
        ]

        # Populate observation list for payload
        observations_payload = []
        for rec in matching_records:
            m_p = rec.get("modal_price", 0.0)
            u = rec.get("price_unit", "INR/quintal")
            p_kg = round(m_p / 100.0, 2) if "quintal" in u.lower() else None
            observations_payload.append({
                "commodity": rec.get("commodity"),
                "variety": rec.get("variety"),
                "market_name": rec.get("market_name"),
                "district_name": rec.get("district_name"),
                "state_name": rec.get("state_name"),
                "arrival_date": rec.get("arrival_date"),
                "min_price": rec.get("min_price"),
                "max_price": rec.get("max_price"),
                "modal_price": m_p,
                "price_unit": u,
                "price_per_kg": p_kg,
                "currency": rec.get("currency", "INR"),
                "evidence_type": "OBSERVED",
                "confidence": 1.0,
                "source": self.provider_name,
                "source_url": source_url,
                "source_title": source_title,
                "source_last_verified": source_last_verified,
                "verification_status": "VERIFIED_SOURCE"
            })

        return ProviderResult(
            provider_name=self.provider_name,
            data_category=self.data_category,
            success=True,
            evidence_items=evidence,
            raw_payload={
                "commodity": resolved_comm,
                "variety": variety,
                "market_name": market_name,
                "district_name": dist_name,
                "state_name": st_name,
                "arrival_date": arrival_date,
                "min_price": min_price,
                "max_price": max_price,
                "modal_price": modal_price,
                "price_unit": unit,
                "price_per_kg": price_per_kg,
                "currency": "INR",
                "evidence_type": "OBSERVED",
                "confidence": 1.0,
                "source": self.provider_name,
                "source_url": source_url,
                "source_title": source_title,
                "source_department": source_department,
                "source_last_verified": source_last_verified,
                "verification_status": "VERIFIED_SOURCE",
                "price_observations": observations_payload
            },
            observed_at=now_iso,
            expires_at=expires_at,
            freshness_hours=self.freshness_hours,
            is_stale=False
        )

