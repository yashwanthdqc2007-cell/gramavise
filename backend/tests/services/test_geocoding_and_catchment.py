import pytest
from unittest.mock import patch, MagicMock
from app.services.geo.geocoder import (
    validate_coordinates,
    LocationResolver,
    LOCAL_COORDINATE_REGISTRY,
    geocode_village
)
from app.schemas.market import (
    GeocodingResult,
    MarketEvidenceQuery,
    MarketRiskSignal,
    CoverageConfidenceLevel
)
from app.schemas.evidence import EvidenceType
from app.services.geo.market import MockMarketService
from app.providers.competitor import OSMCompetitorProvider
from app.utils.geo_distance import haversine_distance



class TestCoordinateValidation:
    """Test rigorous validation of geographic coordinates."""

    def test_valid_coordinates(self):
        is_valid, err = validate_coordinates(18.1550, 74.5780)
        assert is_valid is True
        assert err is None

    def test_boundary_coordinates(self):
        assert validate_coordinates(90.0, 180.0)[0] is True
        assert validate_coordinates(-90.0, -180.0)[0] is True

    def test_invalid_latitude_overflow(self):
        is_valid, err = validate_coordinates(95.0, 74.5780)
        assert is_valid is False
        assert "Latitude 95.0 is outside" in err

    def test_invalid_latitude_underflow(self):
        is_valid, err = validate_coordinates(-90.001, 74.5780)
        assert is_valid is False
        assert "Latitude -90.001 is outside" in err

    def test_invalid_longitude_overflow(self):
        is_valid, err = validate_coordinates(18.1550, 185.0)
        assert is_valid is False
        assert "Longitude 185.0 is outside" in err

    def test_invalid_longitude_underflow(self):
        is_valid, err = validate_coordinates(18.1550, -180.5)
        assert is_valid is False
        assert "Longitude -180.5 is outside" in err

    def test_null_coordinates(self):
        is_valid, err = validate_coordinates(None, 74.5780)
        assert is_valid is False
        assert "missing or null" in err

        is_valid, err = validate_coordinates(18.1550, None)
        assert is_valid is False

        is_valid, err = validate_coordinates(None, None)
        assert is_valid is False

    def test_null_island_rejection(self):
        is_valid, err = validate_coordinates(0.0, 0.0)
        assert is_valid is False
        assert "Null Island" in err

    def test_nan_and_inf_rejection(self):
        is_valid, err = validate_coordinates(float('nan'), 74.0)
        assert is_valid is False
        assert "finite real numbers" in err

        is_valid, err = validate_coordinates(18.0, float('inf'))
        assert is_valid is False
        assert "finite real numbers" in err


class TestLocationResolver:
    """Test multi-tier location resolution."""

    def test_trusted_local_registry_village_lookup(self):
        resolver = LocationResolver()
        res = resolver.resolve(state="Maharashtra", district="Pune", village="Baramati")
        assert res.resolution_source == "TRUSTED_LOCAL_REGISTRY"
        assert res.verification_status == "VERIFIED_SOURCE"
        assert res.confidence == 1.0
        assert res.is_verified is True
        assert res.latitude == pytest.approx(18.1550, abs=1e-4)
        assert res.longitude == pytest.approx(74.5780, abs=1e-4)

    def test_trusted_local_registry_district_centroid_fallback(self):
        resolver = LocationResolver()
        res = resolver.resolve(state="Madhya Pradesh", district="Ujjain", village="UnknownVillage123")
        assert res.resolution_source == "TRUSTED_LOCAL_REGISTRY"
        assert res.verification_status == "VERIFIED_SOURCE"
        assert res.confidence == 0.90
        assert res.is_verified is True
        assert res.latitude == pytest.approx(23.1800, abs=1e-4)
        assert res.longitude == pytest.approx(75.7800, abs=1e-4)

    def test_cache_reuse(self):
        resolver = LocationResolver()
        # First call populates cache
        res1 = resolver.resolve(state="Maharashtra", district="Pune", village="Baramati")
        # Second call returns cached result
        res2 = resolver.resolve(state="Maharashtra", district="Pune", village="Baramati")
        assert res1 == res2
        assert ("maharashtra", "pune", "baramati") in resolver._cache

    def test_deterministic_demo_hash_fallback(self):
        resolver = LocationResolver()
        res = resolver.resolve(state="Odisha", district="Kalahandi", village="RuralVillageX", allow_demo_fallback=True)
        assert res.resolution_source == "DEMO_HASH_FALLBACK"
        assert res.verification_status == "NEEDS_VERIFICATION"
        assert res.confidence == 0.50
        assert res.is_verified is False
        assert res.latitude is not None
        assert res.longitude is not None
        assert "[DEMO / PROTOTYPE DATA]" in res.notes

    def test_unresolved_when_fallback_disabled(self):
        resolver = LocationResolver()
        res = resolver.resolve(state="UnknownStateXYZ", district="UnknownDistXYZ", village="UnknownVillXYZ", allow_demo_fallback=False)
        assert res.resolution_source == "UNRESOLVED"
        assert res.verification_status == "NEEDS_VERIFICATION"
        assert res.confidence == 0.0
        assert res.is_verified is False
        assert res.latitude is None
        assert res.longitude is None

    @patch("urllib.request.urlopen")
    def test_external_geocoder_timeout_handled_safely(self, mock_urlopen):
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("Connection timeout")

        resolver = LocationResolver(enable_network=True)
        # For an unknown district with network enabled
        res = resolver.resolve(state="Nagaland", district="Kohima", village="CustomHamlet", allow_demo_fallback=True, enable_network=True)
        # Should gracefully fall back to DEMO_HASH_FALLBACK without crashing
        assert res.resolution_source == "DEMO_HASH_FALLBACK"
        assert res.verification_status == "NEEDS_VERIFICATION"

    @patch("urllib.request.urlopen")
    def test_external_geocoder_empty_response(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b"[]"
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        resolver = LocationResolver(enable_network=True)
        res = resolver.resolve(state="Nagaland", district="Kohima", village="CustomHamlet", allow_demo_fallback=False, enable_network=True)
        assert res.resolution_source == "UNRESOLVED"
        assert res.latitude is None

    def test_geocode_village_functional_helper(self):
        coords = geocode_village("Maharashtra", "Pune", "Baramati")
        assert coords is not None
        assert coords[0] == pytest.approx(18.1550, abs=1e-4)


class TestHaversineCatchmentCalculation:
    """Test geographic distance calculations and catchment boundaries."""

    def test_haversine_known_distance(self):
        # Baramati (18.1550, 74.5780) to Malegaon Bk (18.1480, 74.5650) ~ 1.58 km
        dist = haversine_distance(18.1550, 74.5780, 18.1480, 74.5650)
        assert 1.0 < dist < 2.0
        assert round(dist, 2) == 1.58

    def test_haversine_same_point_zero_distance(self):
        dist = haversine_distance(18.1550, 74.5780, 18.1550, 74.5780)
        assert dist == 0.0

    def test_competitor_catchment_boundary_filtering(self):
        provider = OSMCompetitorProvider()
        # In Baramati, radius 1.0 km vs 5.0 km
        comp_1km, _, _ = provider.get_competitors(18.1550, 74.5780, category="Grocery", radius_km=1.0)
        comp_5km, _, _ = provider.get_competitors(18.1550, 74.5780, category="Grocery", radius_km=5.0)
        assert len(comp_5km) >= len(comp_1km)
        for c in comp_1km:
            assert c.distance_km <= 1.0


class TestCompetitorProviderErrorHandling:
    """Test provider safety when coordinates are missing or unresolved."""

    def test_missing_coordinates_returns_unknown_coverage(self):
        provider = OSMCompetitorProvider()
        competitors, confidence, warning = provider.get_competitors(lat=None, lon=None, category="Grocery")
        assert len(competitors) == 0
        assert confidence == CoverageConfidenceLevel.UNKNOWN.value
        assert "Coordinates unavailable" in warning

    def test_mock_market_service_with_unresolved_coordinates(self):
        # Create MarketService where LocationResolver returns unresolved
        mock_resolver = MagicMock()
        mock_resolver.resolve.return_value = GeocodingResult(
            latitude=None,
            longitude=None,
            resolution_source="UNRESOLVED",
            verification_status="NEEDS_VERIFICATION",
            confidence=0.0,
            is_verified=False,
            notes="Unresolved"
        )
        service = MockMarketService(location_resolver=mock_resolver)
        query = MarketEvidenceQuery(
            category="Kirana Store",
            state="Unknown",
            district="Unknown",
            village="Unknown",
            radius_km=5.0
        )
        response = service.get_market_indicators(query)
        # Should not falsely claim LOW_COMPETITION or zero competitors with high confidence
        assert MarketRiskSignal.DATA_INSUFFICIENT in response.market_signals
        assert response.geography.latitude is None
        assert response.geography.is_geocoded is False

    def test_mock_market_service_with_valid_coordinates(self):
        service = MockMarketService()
        query = MarketEvidenceQuery(
            category="Kirana Store",
            state="Maharashtra",
            district="Pune",
            village="Malegaon Bk",
            radius_km=5.0
        )
        response = service.get_market_indicators(query)
        assert response.geography.latitude == pytest.approx(18.1480, abs=1e-4)
        assert response.geography.is_geocoded is True
        assert response.geography.resolution_source == "TRUSTED_LOCAL_REGISTRY"
        # Demographics from Census 2011 is strictly OBSERVED
        assert response.demographics is not None
        assert response.demographics.evidence_type == EvidenceType.OBSERVED
        assert response.demographics.population == 12382
        assert response.demographics.verification_status == "VERIFIED_SOURCE"

        # 5 km Catchment remains strictly MODELLED geometric estimation
        assert response.catchment.evidence_type == EvidenceType.MODELLED
        assert response.catchment.estimated_population == 4500
        assert response.catchment.verification_status == "NEEDS_VERIFICATION"

    def test_synthetic_fallback_zero_competitors_omits_low_competition(self):
        """Unverified/synthetic fallback coordinates must never emit LOW_COMPETITION signal."""
        service = MockMarketService()
        # Query an unmapped hamlet that triggers DEMO_HASH_FALLBACK
        query = MarketEvidenceQuery(
            category="Kirana Store",
            state="UnmappedStateXYZ",
            district="UnmappedDistrictXYZ",
            village="UnmappedHamletXYZ",
            radius_km=5.0
        )
        response = service.get_market_indicators(query)
        assert response.geography.resolution_source == "DEMO_HASH_FALLBACK"
        assert response.geography.is_geocoded is False
        assert MarketRiskSignal.DATA_INSUFFICIENT in response.market_signals
        assert MarketRiskSignal.DEMAND_UNCERTAIN in response.market_signals
        # Crucial safety invariant: Must NOT claim LOW_COMPETITION
        assert MarketRiskSignal.LOW_COMPETITION not in response.market_signals

    def test_verified_location_genuine_zero_competitors_emits_low_competition(self):
        """Verified coordinates with a genuine zero-competitor query preserve LOW_COMPETITION."""
        # Mock competitor provider to return empty list with HIGH coverage for a verified location
        mock_competitor_provider = MagicMock()
        mock_competitor_provider.get_competitors.return_value = ([], "HIGH", None)
        service = MockMarketService(competitor_provider=mock_competitor_provider)
        query = MarketEvidenceQuery(
            category="Custom Rare Category",
            state="Maharashtra",
            district="Pune",
            village="Malegaon Bk",
            radius_km=5.0
        )
        response = service.get_market_indicators(query)
        assert response.geography.resolution_source == "TRUSTED_LOCAL_REGISTRY"
        assert response.geography.is_geocoded is True
        # Verified zero-competitor results retain LOW_COMPETITION and DEMAND_UNCERTAIN
        assert MarketRiskSignal.LOW_COMPETITION in response.market_signals
        assert MarketRiskSignal.DEMAND_UNCERTAIN in response.market_signals



