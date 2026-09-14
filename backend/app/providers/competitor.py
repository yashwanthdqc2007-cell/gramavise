import json
import os
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone
from app.providers.base import BaseDataProvider, ProviderResult
from app.schemas.evidence import EvidenceItem, EvidenceType
from app.schemas.market import (
    CompetitorDetail,
    CompetitorRelationship,
    CoverageConfidenceLevel,
    GeographyLevel
)
from app.services.geo.category_matching import match_competitor_category
from app.utils.geo_distance import haversine_distance
from app.utils.logging import logger


class OSMCompetitorProvider(BaseDataProvider):
    """Provider for OpenStreetMap (OSM) / Overpass hyper-local commercial POI evidence.
    
    Authoritative Geodata Source:
    OpenStreetMap Contributors / Overpass API
    Portal: https://www.openstreetmap.org/
    License: Open Database License (ODbL)
    
    IMPORTANT COVERAGE PRINCIPLES:
    1. Coverage is acknowledged as potentially incomplete, especially in rural catchments.
    2. A query returning 0 direct competitors does NOT prove absence of competition -> emits LOW confidence + NEEDS_VERIFICATION.
    3. Straight-line Haversine distance is calculated and explicitly labeled (not driving/walking distance).
    4. Category matching is conservative (DIRECT, ADJACENT, UNRELATED) and deterministic.
    5. Provider failures/timeouts NEVER crash analysis; they fail gracefully to NEEDS_VERIFICATION.
    6. No scraping of private directories (Google Maps, Justdial, Yelp, IndiaMART) or synthetic business names in production.
    """

    DEFAULT_OVERPASS_URL = "https://overpass-api.de/api/interpreter"
    USER_AGENT = "GramaVise-Advisory-Engine/1.0 (https://github.com/gramavise/gramavise)"

    def __init__(
        self,
        data_file_path: Optional[str] = None,
        overpass_url: Optional[str] = None,
        request_timeout: int = 10,
        enable_network: bool = False,
        is_mock: bool = False,
        **kwargs
    ):
        super().__init__(
            provider_name="OpenStreetMap / Overpass API",
            data_category="COMPETITOR_GEODATA"
        )
        if data_file_path is None:
            self._data_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "data", "osm", "osm_poi_snapshot.json"
            )
        else:
            self._data_file = data_file_path
        
        self._overpass_url = overpass_url or os.environ.get("OVERPASS_API_URL", self.DEFAULT_OVERPASS_URL)
        self._request_timeout = request_timeout
        self._enable_network = enable_network or os.environ.get("GRAMAVISE_ENABLE_OVERPASS_NETWORK", "").lower() in ("1", "true")
        self.is_mock = is_mock
        
        self._dataset: Optional[Dict[str, Any]] = None
        self._snapshot_records: List[Dict[str, Any]] = []
        self._query_cache: Dict[str, Tuple[List[CompetitorDetail], str, Optional[str]]] = {}
        self._load_dataset()

    def _load_dataset(self) -> None:
        """Load checked-in verified OSM POI snapshot."""
        if os.path.exists(self._data_file):
            try:
                with open(self._data_file, "r", encoding="utf-8") as f:
                    self._dataset = json.load(f)
                    self._snapshot_records = self._dataset.get("records", [])
            except Exception as e:
                logger.error(f"Failed to load OSM POI snapshot from {self._data_file}: {e}")
                self._dataset = None
                self._snapshot_records = []

    def is_available(self) -> bool:
        return bool(self._snapshot_records) or self._enable_network

    def _fetch_overpass_pois(self, lat: float, lon: float, radius_meters: int = 5000) -> Optional[List[Dict[str, Any]]]:
        """Fetch real-time POIs from Overpass API if network is enabled."""
        if not self._enable_network:
            return None

        query = f"""
        [out:json][timeout:{self._request_timeout}];
        (
          node["amenity"](around:{radius_meters},{lat},{lon});
          node["shop"](around:{radius_meters},{lat},{lon});
          node["craft"](around:{radius_meters},{lat},{lon});
          node["tourism"](around:{radius_meters},{lat},{lon});
          way["amenity"](around:{radius_meters},{lat},{lon});
          way["shop"](around:{radius_meters},{lat},{lon});
        );
        out center body;
        """
        try:
            req = urllib.request.Request(
                self._overpass_url,
                data=urllib.parse.urlencode({"data": query}).encode("utf-8"),
                headers={"User-Agent": self.USER_AGENT}
            )
            with urllib.request.urlopen(req, timeout=self._request_timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    elements = data.get("elements", [])
                    records = []
                    for elem in elements:
                        el_lat = elem.get("lat") or (elem.get("center", {}).get("lat"))
                        el_lon = elem.get("lon") or (elem.get("center", {}).get("lon"))
                        if el_lat is not None and el_lon is not None:
                            tags = elem.get("tags", {})
                            name = tags.get("name")
                            records.append({
                                "osm_object_id": f"{elem.get('type')}/{elem.get('id')}",
                                "osm_object_type": elem.get("type", "node"),
                                "name": name,
                                "latitude": float(el_lat),
                                "longitude": float(el_lon),
                                "tags": tags,
                                "observed_at": datetime.now(timezone.utc).isoformat()
                            })
                    return records
        except Exception as e:
            logger.warning(f"Overpass network request failed: {e}. Falling back to verified snapshot.")
            return None

    def get_competitors(
        self,
        lat: Optional[float],
        lon: Optional[float],
        category: str,
        radius_km: float = 5.0
    ) -> Tuple[List[CompetitorDetail], str, Optional[str]]:
        """Fetch, filter, and classify nearby commercial POIs.
        
        Returns:
            (competitors, coverage_confidence, coverage_warning)
        """
        if lat is None or lon is None:
            return (
                [],
                CoverageConfidenceLevel.UNKNOWN.value,
                "Coordinates unavailable. Catchment competitor query requires latitude/longitude."
            )

        cache_key = f"{round(lat, 4)}:{round(lon, 4)}:{category.lower().strip()}:{radius_km}"
        if cache_key in self._query_cache:
            return self._query_cache[cache_key]

        # 1. Try Overpass if network enabled, otherwise use verified snapshot
        raw_pois = None
        if self._enable_network:
            raw_pois = self._fetch_overpass_pois(lat, lon, int(radius_km * 1000))
        
        if raw_pois is None:
            raw_pois = self._snapshot_records

        # 2. Process and filter POIs
        competitors: List[CompetitorDetail] = []
        for poi in raw_pois:
            poi_lat = poi.get("latitude")
            poi_lon = poi.get("longitude")
            if poi_lat is None or poi_lon is None:
                continue

            dist = haversine_distance(lat, lon, poi_lat, poi_lon)
            if dist > radius_km:
                continue

            tags = poi.get("tags", {})
            rel_res, reason, subcat = match_competitor_category(category, tags)
            rel_str = rel_res.value if hasattr(rel_res, "value") else str(rel_res)
            if rel_str == "UNRELATED":
                continue

            name = poi.get("name")
            obj_id_full = str(poi.get("osm_object_id", ""))
            obj_type = poi.get("osm_object_type", "node")
            raw_id = obj_id_full.split("/")[-1] if "/" in obj_id_full else obj_id_full

            display_name = name if name else f"Mapped {subcat.replace('_', ' ').title() if subcat else category.title()} Unit"
            osm_url = f"https://www.openstreetmap.org/{obj_type}/{raw_id}" if raw_id else "https://www.openstreetmap.org/"

            competitors.append(
                CompetitorDetail(
                    competitor_id=f"OSM-{obj_type[:1].upper()}-{raw_id}" if raw_id else f"OSM-POI-{len(competitors)+1}",
                    business_name=display_name,
                    category=category,
                    subcategory=subcat,
                    distance_km=round(dist, 2),
                    latitude=poi_lat,
                    longitude=poi_lon,
                    osm_object_id=obj_id_full or None,
                    osm_object_type=obj_type,
                    tags=tags,
                    relationship=rel_str,
                    match_reason=reason,
                    price_indicator="STANDARD",
                    evidence_type=EvidenceType.OBSERVED,
                    confidence=1.0,
                    source="OpenStreetMap",
                    source_type="OPEN_GEODATA",
                    source_url=osm_url,
                    observed_at=poi.get("observed_at", datetime.now(timezone.utc).isoformat()),
                    verification_status="VERIFIED_SOURCE",
                    notes=f"Mapped OpenStreetMap POI located {round(dist, 2)} km away (straight-line distance)."
                )
            )

        # Sort closest first
        competitors.sort(key=lambda c: c.distance_km)

        # 3. Assess coverage and confidence
        direct_count = sum(1 for c in competitors if c.relationship == CompetitorRelationship.DIRECT.value or c.relationship == "DIRECT")
        if direct_count == 0:
            coverage_confidence = CoverageConfidenceLevel.LOW.value
            coverage_warning = (
                f"Competition is based on mapped OpenStreetMap locations within the configured catchment ({radius_km:g} km). "
                "Rural and informal businesses may be missing. A low mapped count does not prove low competition."
            )
        elif direct_count >= 3:
            coverage_confidence = CoverageConfidenceLevel.HIGH.value
            coverage_warning = (
                f"Competition is based on mapped OpenStreetMap locations within the configured catchment ({radius_km:g} km). "
                "Rural and informal businesses may be missing."
            )
        else:
            coverage_confidence = CoverageConfidenceLevel.MEDIUM.value
            coverage_warning = (
                f"Competition is based on mapped OpenStreetMap locations within the configured catchment ({radius_km:g} km). "
                "Rural and informal businesses may be missing."
            )

        result_tuple = (competitors, coverage_confidence, coverage_warning)
        self._query_cache[cache_key] = result_tuple
        return result_tuple

    def fetch_evidence(self, query: Dict[str, Any]) -> ProviderResult:
        """Fetch competitor evidence for evidence collector."""
        lat = query.get("latitude")
        lon = query.get("longitude")
        category = query.get("category", "General")
        radius_km = float(query.get("radius_km", 5.0))
        now_iso = datetime.now(timezone.utc).isoformat()

        if lat is None or lon is None:
            return self.create_fallback_result(
                indicator="Catchment Mapped Competitors",
                reason="Geographic coordinates missing for catchment competitor query",
                geography="Catchment"
            )

        competitors, confidence_str, warning = self.get_competitors(lat, lon, category, radius_km)
        direct_count = sum(1 for c in competitors if c.relationship == CompetitorRelationship.DIRECT.value or c.relationship == "DIRECT")
        adjacent_count = sum(1 for c in competitors if c.relationship == CompetitorRelationship.ADJACENT.value or c.relationship == "ADJACENT")

        if direct_count > 0:
            ev_item = EvidenceItem(
                indicator="Catchment Mapped Competitors",
                value=f"{direct_count} direct mapped units" + (f" ({adjacent_count} adjacent)" if adjacent_count > 0 else ""),
                unit="units",
                evidence_type=EvidenceType.OBSERVED,
                confidence=1.0 if confidence_str == "HIGH" else 0.75,
                source="OpenStreetMap (Overpass API)",
                source_url="https://www.openstreetmap.org/",
                source_title="OpenStreetMap Commercial POI Layer",
                notes=(
                    f"Observed {direct_count} direct competitors within {radius_km:g} km catchment. "
                    "Straight-line distance; informal or unmapped rural units may also exist."
                ),
                verification_status="VERIFIED_SOURCE"
            )
        else:
            ev_item = EvidenceItem(
                indicator="Catchment Mapped Competitors",
                value="0 direct mapped units",
                unit="units",
                evidence_type=EvidenceType.NEEDS_VERIFICATION,
                confidence=0.50,
                source="OpenStreetMap (Overpass API)",
                source_url="https://www.openstreetmap.org/",
                source_title="OpenStreetMap Commercial POI Layer",
                notes=(
                    f"No direct commercial units mapped in OpenStreetMap within {radius_km:g} km. "
                    "Rural mapping coverage is often incomplete; physical local survey required to verify absence of competition."
                ),
                verification_status="NEEDS_VERIFICATION"
            )

        return ProviderResult(
            provider_name=self.provider_name,
            data_category=self.data_category,
            success=True,
            evidence_items=[ev_item],
            raw_payload={
                "direct_competitor_count": direct_count,
                "adjacent_competitor_count": adjacent_count,
                "total_matched": len(competitors),
                "coverage_confidence": confidence_str,
                "coverage_warning": warning,
                "competitors": [c.model_dump() for c in competitors]
            },
            observed_at=now_iso
        )
