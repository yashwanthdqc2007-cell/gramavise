from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.schemas.market import (
    MarketResultResponse,
    CompetitorInfo,
    CompetitorDetail,
    CatchmentModel,
    PriceBenchmark,
    PriceObservationDetail,
    MarketIndicatorItem,
    MarketEvidenceQuery,
    MarketConfidenceLevel,
    MarketRiskSignal,
    GeographyLevel,
    GeographyIdentity,
    DemographicObservation,
    UdyamDistrictContext,
    CompetitorRelationship,
    CoverageConfidenceLevel,
    GeocodingResult
)
from app.schemas.analysis import EvidenceType
from app.providers.geo import GeoDataProvider
from app.providers.demographics import DemographicDataProvider
from app.providers.price import PriceDataProvider
from app.providers.competitor import OSMCompetitorProvider
from app.providers.udyam import UdyamContextProvider
from app.services.geo.geocoder import LocationResolver, validate_coordinates


class MarketServiceInterface(ABC):
    """Abstract interface defining required geospatial market intelligence operations."""

    @abstractmethod
    def get_location(self, state: str, district: str, village: str) -> Dict[str, float]:
        """Geocode village/block name into lat/lon coordinates."""
        pass

    @abstractmethod
    def get_local_businesses(self, lat: float, lon: float, category: str, radius_km: float) -> List[CompetitorDetail]:
        """Fetch nearby competitor POIs from data provider or local snapshot."""
        pass

    @abstractmethod
    def get_market_indicators(self, query: MarketEvidenceQuery) -> MarketResultResponse:
        """Aggregate catchment population, competitor density, demand signals, and provenance."""
        pass


class MockMarketService(MarketServiceInterface):
    """Production/Development provider for MarketService with verified LGD, Census, Agmarknet, OSM & Udyam integrations.
    
    CRITICAL POLICY:
    - Catchment competitor POIs are from OpenStreetMap / Overpass (OBSERVED or NEEDS_VERIFICATION).
    - District MSME context is from Ministry of MSME / Udyam OGD (OBSERVED, district-level only).
    - LGD administrative identity and Census 2011 demographics are OBSERVED.
    - Mandi price benchmarks are OBSERVED from Agmarknet / OGD.
    - No fake external URLs, synthetic competitor names, or private directory scraping.
    """

    def __init__(
        self,
        geo_provider: Optional[GeoDataProvider] = None,
        demographics_provider: Optional[DemographicDataProvider] = None,
        price_provider: Optional[PriceDataProvider] = None,
        competitor_provider: Optional[OSMCompetitorProvider] = None,
        udyam_provider: Optional[UdyamContextProvider] = None,
        location_resolver: Optional[LocationResolver] = None
    ):
        self._geo_provider = geo_provider or GeoDataProvider()
        self._demographics_provider = demographics_provider or DemographicDataProvider()
        self._price_provider = price_provider or PriceDataProvider()
        self._competitor_provider = competitor_provider or OSMCompetitorProvider()
        self._udyam_provider = udyam_provider or UdyamContextProvider()
        self._location_resolver = location_resolver or LocationResolver()

    def get_location(self, state: str, district: str, village: str) -> Dict[str, float]:
        """Multi-tier location resolution returning latitude and longitude dictionary."""
        geo_res = self._location_resolver.resolve(state, district, village, allow_demo_fallback=True)
        if geo_res.latitude is not None and geo_res.longitude is not None:
            return {"latitude": geo_res.latitude, "longitude": geo_res.longitude}
        # Fallback to standard baseline if completely unresolved
        return {"latitude": 18.1550, "longitude": 74.5780}

    def get_local_businesses(self, lat: float, lon: float, category: str, radius_km: float) -> List[CompetitorDetail]:
        """Fetch nearby commercial POIs from OpenStreetMap provider."""
        competitors, _, _ = self._competitor_provider.get_competitors(lat, lon, category, radius_km)
        return competitors

    def get_market_indicators(self, query: MarketEvidenceQuery) -> MarketResultResponse:
        """Produce structured, provenance-explicit market intelligence response."""
        cat_val = getattr(query, "category", "") or getattr(query, "commodity", "") or ""
        comm_val = getattr(query, "commodity", None) or getattr(query, "category", "") or ""
        market_val = getattr(query, "market", None) or ""
        st_val = getattr(query, "state", "")
        dist_val = getattr(query, "district", "")
        vill_val = getattr(query, "village", "")
        rad_val = getattr(query, "radius_km", 5.0)

        # Coordinate Validation and Resolution
        query_lat = getattr(query, "latitude", None)
        query_lon = getattr(query, "longitude", None)
        is_valid_coords, _ = validate_coordinates(query_lat, query_lon)

        if is_valid_coords and query_lat is not None and query_lon is not None:
            lat_val: Optional[float] = query_lat
            lon_val: Optional[float] = query_lon
            geocoding_res = GeocodingResult(
                latitude=query_lat,
                longitude=query_lon,
                resolution_source="USER_PROVIDED",
                verification_status="USER_PROVIDED",
                confidence=1.0,
                is_verified=True,
                notes="Coordinates explicitly provided in request query."
            )
        else:
            geocoding_res = self._location_resolver.resolve(st_val, dist_val, vill_val, allow_demo_fallback=True)
            lat_val = geocoding_res.latitude
            lon_val = geocoding_res.longitude

        # 1. OpenStreetMap Competitor & POI Evidence
        competitor_details, coverage_conf, coverage_warning = self._competitor_provider.get_competitors(
            lat=lat_val,
            lon=lon_val,
            category=cat_val,
            radius_km=rad_val
        )

        direct_count = sum(1 for c in competitor_details if c.relationship == CompetitorRelationship.DIRECT.value or c.relationship == "DIRECT")
        adjacent_count = sum(1 for c in competitor_details if c.relationship == CompetitorRelationship.ADJACENT.value or c.relationship == "ADJACENT")

        # Legacy backward-compatible competitor info list
        competitor_legacy = [
            CompetitorInfo(
                name=c.business_name,
                distance_km=c.distance_km,
                category=c.subcategory or c.category,
                relationship=c.relationship
            )
            for c in competitor_details
        ]

        # 2. Verified LGD Administrative Hierarchy
        geo_res = self._geo_provider.fetch_evidence({
            "state": st_val,
            "district": dist_val,
            "village": vill_val
        })
        geo_payload = geo_res.raw_payload or {}
        geography = GeographyIdentity(
            state_name=geo_payload.get("state_name") or st_val,
            state_lgd_code=geo_payload.get("state_lgd_code"),
            district_name=geo_payload.get("district_name") or dist_val,
            district_lgd_code=geo_payload.get("district_lgd_code"),
            sub_district_name=geo_payload.get("sub_district_name"),
            sub_district_lgd_code=geo_payload.get("sub_district_lgd_code"),
            village_name=geo_payload.get("village_name") or vill_val,
            village_lgd_code=geo_payload.get("village_lgd_code"),
            latitude=lat_val,
            longitude=lon_val,
            resolution_source=geocoding_res.resolution_source,
            is_geocoded=geocoding_res.is_verified,
            verification_status=geo_payload.get("verification_status", "NEEDS_VERIFICATION"),
            source=geo_payload.get("source"),
            source_url=geo_payload.get("source_url")
        )

        # 3. Verified Census 2011 Historical Demographics
        demo_res = self._demographics_provider.fetch_evidence({
            "state": st_val,
            "district": dist_val,
            "village": vill_val
        })
        demo_payload = demo_res.raw_payload or {}
        demographics = None
        if demo_payload.get("population") is not None:
            demographics = DemographicObservation(
                population=demo_payload.get("population"),
                households=demo_payload.get("households"),
                reference_year=demo_payload.get("reference_year", 2011),
                data_status=demo_payload.get("data_status", "HISTORICAL_OFFICIAL"),
                geography_level=GeographyLevel.VILLAGE,
                evidence_type=EvidenceType.OBSERVED,
                confidence=1.0,
                source=demo_payload.get("source"),
                source_url=demo_payload.get("source_url"),
                verification_status=demo_payload.get("verification_status", "VERIFIED_SOURCE")
            )

        # 4. Modelled Prototype Catchment (geometric estimation baseline)
        catchment = CatchmentModel(
            radius_km=rad_val,
            estimated_population=4500,
            estimated_households=900,
            estimated_daily_demand=f"Estimated {cat_val} demand baseline [PROTOTYPE]",
            methodology="Prototype geometric catchment estimation [DEMO]",
            evidence_type=EvidenceType.MODELLED,
            confidence=0.50,
            verification_status="NEEDS_VERIFICATION"
        )

        # 5. Verified Agmarknet / OGD Agricultural Mandi Price Evidence
        price_res = self._price_provider.fetch_evidence({
            "category": cat_val,
            "commodity": comm_val,
            "state": st_val,
            "district": dist_val,
            "market": market_val
        })
        price_payload = price_res.raw_payload or {}
        price_obs_list: List[PriceObservationDetail] = []
        raw_obs = price_payload.get("price_observations", [])
        for o in raw_obs:
            price_obs_list.append(PriceObservationDetail(
                commodity=o.get("commodity", ""),
                variety=o.get("variety"),
                market_name=o.get("market_name", ""),
                district_name=o.get("district_name", ""),
                state_name=o.get("state_name", ""),
                arrival_date=o.get("arrival_date", ""),
                min_price=o.get("min_price", 0.0),
                max_price=o.get("max_price", 0.0),
                modal_price=o.get("modal_price", 0.0),
                price_unit=o.get("price_unit", "INR/quintal"),
                price_per_kg=o.get("price_per_kg"),
                currency=o.get("currency", "INR"),
                evidence_type=EvidenceType.OBSERVED,
                confidence=1.0,
                source=o.get("source", "Directorate of Marketing & Inspection (DMI) / OGD"),
                source_url=o.get("source_url"),
                source_title=o.get("source_title"),
                source_last_verified=o.get("source_last_verified"),
                verification_status=o.get("verification_status", "VERIFIED_SOURCE")
            ))

        if price_obs_list:
            top_obs = price_obs_list[0]
            price_benchmark = PriceBenchmark(
                category=top_obs.commodity,
                low_price=top_obs.min_price,
                median_price=top_obs.modal_price,
                high_price=top_obs.max_price,
                unit=top_obs.price_unit,
                price_per_kg=top_obs.price_per_kg,
                market_name=top_obs.market_name,
                arrival_date=top_obs.arrival_date,
                variety=top_obs.variety,
                geography=f"{top_obs.market_name} APMC, {top_obs.district_name}, {top_obs.state_name}",
                evidence_type=EvidenceType.OBSERVED,
                source=top_obs.source,
                source_url=top_obs.source_url,
                source_title=top_obs.source_title,
                confidence=1.0,
                verification_status="VERIFIED_SOURCE",
                notes="Observed mandi modal price from Agmarknet / OGD. Market observation only; not a retail selling price recommendation."
            )
        else:
            price_benchmark = PriceBenchmark(
                category=comm_val,
                low_price=None,
                median_price=None,
                high_price=None,
                unit=None,
                price_per_kg=None,
                market_name=None,
                arrival_date=None,
                variety=None,
                geography=f"{dist_val}, {st_val}",
                evidence_type=EvidenceType.NEEDS_VERIFICATION,
                source=None,
                source_url=None,
                source_title=None,
                confidence=0.0,
                verification_status="NEEDS_VERIFICATION",
                notes="Mandi price feed outside checked-in Agmarknet snapshot. Local wholesale verification required."
            )

        # 6. Official Udyam District MSME Context (Strictly separate from nearby competitors)
        udyam_context = self._udyam_provider.get_district_context(st_val, dist_val)

        # 7. Conservative Market Risk Signals
        market_signals: List[MarketRiskSignal] = []
        is_loc_verified = geocoding_res.is_verified and lat_val is not None and lon_val is not None

        if not is_loc_verified:
            # Unverified or synthetic fallback coordinates must never assert low competition certainty
            market_signals.append(MarketRiskSignal.DATA_INSUFFICIENT)
            market_signals.append(MarketRiskSignal.DEMAND_UNCERTAIN)
            if direct_count > 2:
                market_signals.append(MarketRiskSignal.HIGH_COMPETITION)
            elif direct_count > 0:
                market_signals.append(MarketRiskSignal.MODERATE_COMPETITION)
        elif direct_count == 0:
            market_signals.append(MarketRiskSignal.LOW_COMPETITION)
            market_signals.append(MarketRiskSignal.DEMAND_UNCERTAIN)
        elif direct_count <= 2:
            market_signals.append(MarketRiskSignal.MODERATE_COMPETITION)
        else:
            market_signals.append(MarketRiskSignal.HIGH_COMPETITION)

        if not price_obs_list:
            market_signals.append(MarketRiskSignal.PRICE_UNCERTAIN)
        if (coverage_conf == CoverageConfidenceLevel.LOW.value or not is_loc_verified) and MarketRiskSignal.DATA_INSUFFICIENT not in market_signals:
            market_signals.append(MarketRiskSignal.DATA_INSUFFICIENT)

        # 8. Structured Indicators
        price_indicator_val = (
            f"₹{price_benchmark.median_price:,.2f}/{price_benchmark.unit}"
            if price_benchmark.median_price is not None
            else "Unverified"
        )
        price_indicator_ev_type = (
            EvidenceType.OBSERVED if price_obs_list else EvidenceType.NEEDS_VERIFICATION
        )
        price_indicator_conf = 1.0 if price_obs_list else 0.0
        price_indicator_status = "VERIFIED_SOURCE" if price_obs_list else "NEEDS_VERIFICATION"

        competitor_indicator_val = (
            f"{direct_count} direct mapped units" + (f" ({adjacent_count} adjacent)" if adjacent_count > 0 else "")
            if len(competitor_details) > 0
            else "0 direct mapped units"
        )
        competitor_ev_type = (
            EvidenceType.OBSERVED if direct_count > 0 else EvidenceType.NEEDS_VERIFICATION
        )
        competitor_conf = 1.0 if coverage_conf == CoverageConfidenceLevel.HIGH.value else (0.75 if direct_count > 0 else 0.50)

        indicators = [
            MarketIndicatorItem(
                indicator_id="MKT-COMP-COUNT",
                name="Catchment Mapped Competitors",
                value=competitor_indicator_val,
                unit="units",
                geography=f"{vill_val}, {dist_val} ({rad_val:g} km radius)",
                geography_level=GeographyLevel.CATCHMENT,
                evidence_type=competitor_ev_type,
                confidence=competitor_conf,
                source="OpenStreetMap (Overpass API)",
                source_url="https://www.openstreetmap.org/",
                source_title="OpenStreetMap Commercial POI Layer",
                notes=(
                    f"Mapped commercial POIs within {rad_val:g} km catchment. "
                    "Coverage may be incomplete in rural areas; 0 mapped competitors does not prove absence of competition."
                ),
                verification_status="VERIFIED_SOURCE" if direct_count > 0 else "NEEDS_VERIFICATION"
            ),
            MarketIndicatorItem(
                indicator_id="MKT-CATCH-POP",
                name="Estimated Catchment Population",
                value="4,500 residents",
                unit="persons",
                geography=f"{vill_val} Catchment ({rad_val:g} km)",
                geography_level=GeographyLevel.CATCHMENT,
                evidence_type=EvidenceType.MODELLED,
                confidence=0.50,
                source="GramaVise Prototype Market Model",
                source_title="Catchment Demographic Model",
                notes="[DEMO / PROTOTYPE DATA] Catchment population estimate.",
                verification_status="NEEDS_VERIFICATION"
            ),
            MarketIndicatorItem(
                indicator_id="MKT-PRICE-BENCH",
                name="Observed Mandi Modal Price" if price_obs_list else "Local Category Price Benchmark",
                value=price_indicator_val,
                unit=price_benchmark.unit or "INR",
                geography=price_benchmark.geography or f"{dist_val}, {st_val}",
                geography_level=GeographyLevel.DISTRICT,
                evidence_type=price_indicator_ev_type,
                confidence=price_indicator_conf,
                source=price_benchmark.source or "District Price Intelligence",
                source_url=price_benchmark.source_url,
                source_title=price_benchmark.source_title,
                notes=price_benchmark.notes or "Official mandi price index required.",
                verification_status=price_indicator_status
            )
        ]

        if udyam_context:
            indicators.append(
                MarketIndicatorItem(
                    indicator_id="MKT-UDYAM-MSME",
                    name="District Registered MSMEs",
                    value=f"{udyam_context.registered_msme_count:,} registered enterprises",
                    unit="enterprises",
                    geography=f"{dist_val}, {st_val}",
                    geography_level=GeographyLevel.DISTRICT,
                    evidence_type=EvidenceType.OBSERVED,
                    confidence=1.0,
                    source=udyam_context.source,
                    source_url=udyam_context.source_url,
                    source_title=udyam_context.dataset_name,
                    notes=(
                        f"District formal MSME context ({udyam_context.micro_count or 0:,} micro units). "
                        "District-level formal registration context only; not a count of nearby competitors."
                    ),
                    verification_status="VERIFIED_SOURCE"
                )
            )

        return MarketResultResponse(
            location_summary=f"{vill_val}, {dist_val}, {st_val}",
            competitor_count=direct_count,
            direct_competitor_count=direct_count,
            adjacent_competitor_count=adjacent_count,
            catchment_radius_km=rad_val,
            coverage_confidence=coverage_conf,
            coverage_warning=coverage_warning,
            competitor_list=competitor_legacy,
            competitors=competitor_details,
            demand_indicator="HIGH" if direct_count < 3 else "MEDIUM",
            catchment_population_estimate=catchment.estimated_population,
            catchment=catchment,
            price_benchmark=price_benchmark,
            price_observations=price_obs_list,
            geography=geography,
            demographics=demographics,
            udyam_context=udyam_context,
            market_signals=market_signals,
            indicators=indicators,
            confidence_level=MarketConfidenceLevel.MEDIUM if direct_count > 0 else MarketConfidenceLevel.LOW,
            notes="Catchment competitor evidence from OpenStreetMap; district MSME context from Udyam OGD."
        )

