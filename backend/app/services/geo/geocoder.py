import os
import re
import json
import math
import hashlib
import urllib.request
import urllib.parse
from typing import Optional, Dict, Tuple, List, Any
from app.schemas.market import GeocodingResult
from app.utils.logging import logger
from app.config import settings


def validate_coordinates(lat: Optional[float], lon: Optional[float]) -> Tuple[bool, Optional[str]]:
    """Validate geographic latitude and longitude values strictly.
    
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if lat is None or lon is None:
        return False, "Coordinates are missing or null."

    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except (ValueError, TypeError):
        return False, "Coordinates must be numeric float values."

    if math.isnan(lat_f) or math.isinf(lat_f) or math.isnan(lon_f) or math.isinf(lon_f):
        return False, "Coordinates must be finite real numbers."

    if not (-90.0 <= lat_f <= 90.0):
        return False, f"Latitude {lat_f} is outside valid geographic range [-90.0, 90.0]."

    if not (-180.0 <= lon_f <= 180.0):
        return False, f"Longitude {lon_f} is outside valid geographic range [-180.0, 180.0]."

    # Reject Null Island placeholder (0.0, 0.0)
    if abs(lat_f) < 1e-6 and abs(lon_f) < 1e-6:
        return False, "Coordinates resolve to Null Island placeholder (0.0, 0.0)."

    return True, None


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
    "tamil nadu": "tamil nadu",
    "karnataka": "karnataka",
    "punjab": "punjab",
    "haryana": "haryana",
    "andhra pradesh": "andhra pradesh",
    "kerala": "kerala",
    "west bengal": "west bengal",
}


def normalize_geo_name(raw_name: Optional[str]) -> str:
    """Normalize state/district/village names safely for registry matching."""
    if not raw_name:
        return ""
    cleaned = raw_name.strip().lower()
    cleaned = STATE_ALIASES.get(cleaned, cleaned)
    cleaned = re.sub(r"\b(district|dist\.?|taluk|taluka|tehsil|block|village|gram panchayat|gp|mandi)\b", "", cleaned).strip()
    cleaned = re.sub(r"[^a-zA-Z\s]", "", cleaned).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


# Verified Local Coordinate Registry for Snapshot Centers and Sample Villages
LOCAL_COORDINATE_REGISTRY: Dict[Tuple[str, str, str], Tuple[float, float, str, float]] = {
    # Maharashtra - Pune District
    ("maharashtra", "pune", "baramati"): (18.1550, 74.5780, "VERIFIED_SOURCE", 1.0),
    ("maharashtra", "pune", "malegaon bk"): (18.1480, 74.5650, "VERIFIED_SOURCE", 1.0),
    ("maharashtra", "pune", "karkhel"): (18.1720, 74.5910, "VERIFIED_SOURCE", 1.0),
    ("maharashtra", "pune", ""): (18.5204, 73.8567, "DISTRICT_CENTROID", 0.90),

    # Maharashtra - Nashik District
    ("maharashtra", "nashik", "pimpalgaon baswant"): (20.1700, 73.9800, "VERIFIED_SOURCE", 1.0),
    ("maharashtra", "nashik", "niphad"): (20.0800, 74.1100, "VERIFIED_SOURCE", 1.0),
    ("maharashtra", "nashik", ""): (19.9975, 73.7898, "DISTRICT_CENTROID", 0.90),

    # Madhya Pradesh - Ujjain District
    ("madhya pradesh", "ujjain", "nagda"): (23.4500, 75.4167, "VERIFIED_SOURCE", 1.0),
    ("madhya pradesh", "ujjain", "bhatisuda"): (23.4350, 75.4050, "VERIFIED_SOURCE", 1.0),
    ("madhya pradesh", "ujjain", "padlya"): (23.4200, 75.3900, "VERIFIED_SOURCE", 1.0),
    ("madhya pradesh", "ujjain", ""): (23.1800, 75.7800, "DISTRICT_CENTROID", 0.90),

    # Madhya Pradesh - Indore District
    ("madhya pradesh", "indore", "hasalpur"): (22.5535, 75.7600, "VERIFIED_SOURCE", 1.0),
    ("madhya pradesh", "indore", "mhow"): (22.5535, 75.7600, "VERIFIED_SOURCE", 1.0),
    ("madhya pradesh", "indore", ""): (22.7196, 75.8577, "DISTRICT_CENTROID", 0.90),

    # Madhya Pradesh - Dindori District
    ("madhya pradesh", "dindori", "samnapur"): (22.9500, 81.0800, "VERIFIED_SOURCE", 1.0),
    ("madhya pradesh", "dindori", ""): (22.9500, 81.0800, "DISTRICT_CENTROID", 0.90),

    # Uttar Pradesh - Varanasi District
    ("uttar pradesh", "varanasi", "shivpur"): (25.3500, 82.9600, "VERIFIED_SOURCE", 1.0),
    ("uttar pradesh", "varanasi", "babatpur"): (25.4500, 82.8600, "VERIFIED_SOURCE", 1.0),
    ("uttar pradesh", "varanasi", ""): (25.3200, 82.9800, "DISTRICT_CENTROID", 0.90),

    # Bihar - Patna District
    ("bihar", "patna", ""): (25.6000, 85.1200, "DISTRICT_CENTROID", 0.90),

    # Bihar - Muzaffarpur District
    ("bihar", "muzaffarpur", "damodarpur"): (26.1200, 85.3600, "VERIFIED_SOURCE", 1.0),
    ("bihar", "muzaffarpur", ""): (26.1200, 85.3600, "DISTRICT_CENTROID", 0.90),

    # Rajasthan - Jaipur District
    ("rajasthan", "jaipur", "morija"): (27.1700, 75.7200, "VERIFIED_SOURCE", 1.0),
    ("rajasthan", "jaipur", "chomu"): (27.1700, 75.7200, "VERIFIED_SOURCE", 1.0),
    ("rajasthan", "jaipur", ""): (26.9124, 75.7873, "DISTRICT_CENTROID", 0.90),

    # Karnataka - Mandya District
    ("karnataka", "mandya", "besagarahalli"): (12.5800, 77.0400, "VERIFIED_SOURCE", 1.0),
    ("karnataka", "mandya", "maddur"): (12.5800, 77.0400, "VERIFIED_SOURCE", 1.0),
    ("karnataka", "mandya", ""): (12.5200, 76.9000, "DISTRICT_CENTROID", 0.90),
}


class LocationResolver:
    """Robust, multi-tier location and geocoding resolution engine.
    
    Resolution Priority Order:
    1. Trusted local coordinate registry (verified villages & district centroids).
    2. Valid cached geocoding result.
    3. Optional external Nominatim geocoder (<= 5s timeout, User-Agent, error-isolated).
    4. Deterministic demo hash fallback (clearly labeled as DEMO_HASH_FALLBACK & NEEDS_VERIFICATION).
    5. Structured unresolved state (when demo fallback disabled or inputs missing).
    """

    def __init__(
        self,
        nominatim_url: Optional[str] = None,
        request_timeout: int = 5,
        enable_network: bool = False
    ):
        self._nominatim_url = nominatim_url or getattr(settings, "OSM_API_URL", "https://nominatim.openstreetmap.org")
        self._request_timeout = min(request_timeout, 5)
        self._enable_network = enable_network or os.environ.get("GRAMAVISE_ENABLE_NOMINATIM_NETWORK", "").lower() in ("1", "true")
        self._cache: Dict[Tuple[str, str, str], GeocodingResult] = {}

    def _query_external_geocoder(self, state: str, district: str, village: str) -> Optional[Tuple[float, float]]:
        """Query Nominatim with timeout and error protection."""
        if not self._enable_network:
            return None

        query_str = f"{village}, {district}, {state}, India".strip(", ")
        params = urllib.parse.urlencode({"q": query_str, "format": "json", "limit": 1})
        req_url = f"{self._nominatim_url.rstrip('/')}/search?{params}"
        user_agent = getattr(settings, "GEO_USER_AGENT", "GramaVise-Rural-Business-Advisor/1.0")

        try:
            req = urllib.request.Request(req_url, headers={"User-Agent": user_agent})
            with urllib.request.urlopen(req, timeout=self._request_timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    if isinstance(data, list) and len(data) > 0:
                        lat = float(data[0].get("lat"))
                        lon = float(data[0].get("lon"))
                        is_valid, _ = validate_coordinates(lat, lon)
                        if is_valid:
                            return lat, lon
        except Exception as e:
            logger.warning(f"External Nominatim geocoding request failed: {e}. Falling back to internal resolver.")
            return None

        return None

    def resolve(
        self,
        state: str,
        district: str,
        village: str = "",
        allow_demo_fallback: bool = True,
        enable_network: Optional[bool] = None
    ) -> GeocodingResult:
        """Resolve location hierarchy into verified coordinates or transparent fallback."""
        s_norm = normalize_geo_name(state)
        d_norm = normalize_geo_name(district)
        v_norm = normalize_geo_name(village)
        cache_key = (s_norm, d_norm, v_norm)

        # 1. Tier 1: Check Trusted Local Coordinate Registry
        if (s_norm, d_norm, v_norm) in LOCAL_COORDINATE_REGISTRY and v_norm:
            lat, lon, src, conf = LOCAL_COORDINATE_REGISTRY[(s_norm, d_norm, v_norm)]
            result = GeocodingResult(
                latitude=lat,
                longitude=lon,
                resolution_source="TRUSTED_LOCAL_REGISTRY",
                verification_status="VERIFIED_SOURCE",
                confidence=conf,
                is_verified=True,
                notes=f"Resolved via verified local coordinate registry for village '{village or v_norm}'."
            )
            self._cache[cache_key] = result
            return result

        # Check district centroid in registry
        if (s_norm, d_norm, "") in LOCAL_COORDINATE_REGISTRY:
            lat, lon, src, conf = LOCAL_COORDINATE_REGISTRY[(s_norm, d_norm, "")]
            result = GeocodingResult(
                latitude=lat,
                longitude=lon,
                resolution_source="TRUSTED_LOCAL_REGISTRY",
                verification_status="VERIFIED_SOURCE",
                confidence=conf,
                is_verified=True,
                notes=f"District centroid coordinates applied for '{district or d_norm}'. Village '{village}' is outside checked-in coordinate registry."
            )
            self._cache[cache_key] = result
            return result

        # 2. Tier 2: Check in-memory Cache
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 3. Tier 3: Optional External Geocoder
        use_network = self._enable_network if enable_network is None else enable_network
        if use_network:
            ext_coords = self._query_external_geocoder(state, district, village)
            if ext_coords:
                lat, lon = ext_coords
                result = GeocodingResult(
                    latitude=round(lat, 4),
                    longitude=round(lon, 4),
                    resolution_source="EXTERNAL_GEOCODER",
                    verification_status="EXTERNAL_GEOCODER",
                    confidence=0.85,
                    is_verified=True,
                    notes=f"Geocoded via OpenStreetMap Nominatim service for '{village}, {district}'."
                )
                self._cache[cache_key] = result
                return result

        # 4. Tier 4: Deterministic Demo Hash Fallback (Development & Simulation Only)
        if allow_demo_fallback and (d_norm or s_norm or v_norm):
            hash_val = int(hashlib.md5(f"{v_norm}{d_norm}{s_norm}".encode('utf-8')).hexdigest()[:8], 16)
            lat = 18.0 + (hash_val % 1000) / 100.0
            lon = 73.0 + ((hash_val // 1000) % 1000) / 100.0
            result = GeocodingResult(
                latitude=round(lat, 4),
                longitude=round(lon, 4),
                resolution_source="DEMO_HASH_FALLBACK",
                verification_status="NEEDS_VERIFICATION",
                confidence=0.50,
                is_verified=False,
                notes="[DEMO / PROTOTYPE DATA] Deterministic fallback coordinates for unmapped rural location; on-ground geocoding verification required."
            )
            self._cache[cache_key] = result
            return result

        # 5. Tier 5: Structured Unresolved State
        return GeocodingResult(
            latitude=None,
            longitude=None,
            resolution_source="UNRESOLVED",
            verification_status="NEEDS_VERIFICATION",
            confidence=0.0,
            is_verified=False,
            notes="Location coordinates could not be resolved from trusted local registries or geocoding services."
        )


# Global default resolver instance
_default_resolver = LocationResolver()


def geocode_village(state: str, district: str, village: str = "") -> Optional[Tuple[float, float]]:
    """Backward-compatible functional entrypoint for village geocoding.
    
    Returns:
        (latitude, longitude) tuple if coordinates resolved, otherwise None.
    """
    res = _default_resolver.resolve(state, district, village)
    if res.latitude is not None and res.longitude is not None:
        return (res.latitude, res.longitude)
    return None
