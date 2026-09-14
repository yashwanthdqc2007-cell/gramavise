import pytest
from app.providers.geo import GeoDataProvider
from app.providers.demographics import DemographicDataProvider
from app.schemas.evidence import EvidenceType
from app.schemas.market import MarketEvidenceQuery, GeographyLevel
from app.services.geo.market import MockMarketService
from app.services.evidence.collector import EvidenceCollector


@pytest.fixture
def geo_provider():
    return GeoDataProvider()


@pytest.fixture
def demographics_provider():
    return DemographicDataProvider()


@pytest.fixture
def market_service():
    return MockMarketService()


@pytest.fixture
def evidence_collector():
    return EvidenceCollector()


# Test 1: Known LGD state/district/village resolves with official entity
def test_known_lgd_village_resolves(geo_provider):
    res = geo_provider.fetch_evidence({
        "state": "Madhya Pradesh",
        "district": "Ujjain",
        "village": "Bhatisuda"
    })
    assert res.success is True
    assert len(res.evidence_items) == 1
    assert res.evidence_items[0].evidence_type == EvidenceType.OBSERVED
    assert res.evidence_items[0].confidence == 1.0
    assert res.raw_payload["village_name"] == "Bhatisuda"
    assert res.raw_payload["district_name"] == "Ujjain"
    assert res.raw_payload["state_name"] == "Madhya Pradesh"


# Test 2: LGD codes are preserved exactly from official registry
def test_lgd_codes_preserved_exactly(geo_provider):
    rec = geo_provider.get_lgd_record(
        state="Maharashtra",
        district="Pune",
        village="Malegaon Bk"
    )
    assert rec is not None
    assert rec["village_lgd_code"] == "555893"
    assert rec["district_lgd_code"] == "492"
    assert rec["state_lgd_code"] == "27"
    assert rec["sub_district_lgd_code"] == "04179"


# Test 3: Known Census 2011 population record
def test_known_census_2011_population(demographics_provider):
    res = demographics_provider.fetch_evidence({
        "state": "Madhya Pradesh",
        "district": "Ujjain",
        "village": "Bhatisuda"
    })
    assert res.success is True
    pop_item = [i for i in res.evidence_items if i.indicator == "Census 2011 Population"][0]
    assert pop_item.evidence_type == EvidenceType.OBSERVED
    assert pop_item.confidence == 1.0
    assert "3,142" in pop_item.value
    assert res.raw_payload["population"] == 3142


# Test 4: Known Census 2011 household record
def test_known_census_2011_households(demographics_provider):
    res = demographics_provider.fetch_evidence({
        "state": "Madhya Pradesh",
        "district": "Ujjain",
        "village": "Bhatisuda"
    })
    hh_item = [i for i in res.evidence_items if i.indicator == "Census 2011 Households"][0]
    assert hh_item.evidence_type == EvidenceType.OBSERVED
    assert "621" in hh_item.value
    assert res.raw_payload["households"] == 621


# Test 5: Reference year is strictly 2011 and data_status is HISTORICAL_OFFICIAL
def test_census_reference_year_is_2011(demographics_provider):
    res = demographics_provider.fetch_evidence({
        "state": "Maharashtra",
        "district": "Pune",
        "village": "Malegaon Bk"
    })
    assert res.raw_payload["reference_year"] == 2011
    assert res.raw_payload["data_status"] == "HISTORICAL_OFFICIAL"
    for item in res.evidence_items:
        assert "2011" in item.notes
        assert "not a current population estimate" in item.notes or "Census 2011" in item.notes


# Test 6: LGD evidence is OBSERVED with HIGH (1.0) confidence
def test_lgd_evidence_observed_and_high(geo_provider):
    res = geo_provider.fetch_evidence({
        "state": "Uttar Pradesh",
        "district": "Varanasi",
        "village": "Shivpur"
    })
    item = res.evidence_items[0]
    assert item.evidence_type == EvidenceType.OBSERVED
    assert item.confidence == 1.0
    assert item.source == "Ministry of Panchayati Raj / Local Government Directory (LGD)"
    assert item.verification_status == "VERIFIED_SOURCE"


# Test 7: Record where LGD resolves but Census is unavailable (e.g. Besagarahalli in Mandya, KA)
def test_lgd_resolves_but_census_unavailable(geo_provider, demographics_provider):
    geo_res = geo_provider.fetch_evidence({
        "state": "Karnataka",
        "district": "Mandya",
        "village": "Besagarahalli"
    })
    assert geo_res.success is True
    assert geo_res.raw_payload["village_lgd_code"] == "614210"

    demo_res = demographics_provider.fetch_evidence({
        "state": "Karnataka",
        "district": "Mandya",
        "village": "Besagarahalli"
    })
    assert demo_res.evidence_items[0].evidence_type == EvidenceType.NEEDS_VERIFICATION
    assert demo_res.raw_payload["population"] is None


# Test 8: Record where entity is outside the snapshot -> NEEDS_VERIFICATION
def test_out_of_snapshot_needs_verification(geo_provider, demographics_provider):
    geo_res = geo_provider.fetch_evidence({
        "state": "Goa",
        "district": "North Goa",
        "village": "Unmapped Village XYZ"
    })
    assert geo_res.evidence_items[0].evidence_type == EvidenceType.NEEDS_VERIFICATION
    assert geo_res.raw_payload["village_lgd_code"] is None

    demo_res = demographics_provider.fetch_evidence({
        "state": "Goa",
        "district": "North Goa",
        "village": "Unmapped Village XYZ"
    })
    assert demo_res.evidence_items[0].evidence_type == EvidenceType.NEEDS_VERIFICATION
    assert demo_res.raw_payload["population"] is None


# Test 9: Ambiguous / corrupted location input -> safe fallback
def test_ambiguous_location_fallback(geo_provider, demographics_provider):
    geo_res = geo_provider.fetch_evidence({
        "state": "123",
        "district": "!@#",
        "village": "$$$"
    })
    assert geo_res.success is False
    assert geo_res.evidence_items[0].evidence_type == EvidenceType.NEEDS_VERIFICATION

    demo_res = demographics_provider.fetch_evidence({
        "state": "123",
        "district": "!@#",
        "village": "$$$"
    })
    assert demo_res.success is False


# Test 10: Provider failure does not crash analysis pipeline
def test_geo_demographic_collector_failure_resilience():
    collector = EvidenceCollector(
        odop_provider=None,
        geo_provider=None,
        demographics_provider=None
    )
    items = collector.collect({
        "monthly_net_profit": 30000.0,
        "break_even_units_daily": 12,
        "competitor_count": 2,
        "customers_per_day": 35,
        "state": None,
        "district": None,
        "village": None
    })
    assert len(items) >= 4


# Test 11: Deterministic repeated lookup
def test_geo_demographic_deterministic_lookup(geo_provider, demographics_provider):
    query = {"state": "Madhya Pradesh", "district": "Ujjain", "village": "Bhatisuda"}
    geo_1 = geo_provider.fetch_evidence(query)
    geo_2 = geo_provider.fetch_evidence(query)
    assert geo_1.evidence_items[0].model_dump() == geo_2.evidence_items[0].model_dump()

    demo_1 = demographics_provider.fetch_evidence(query)
    demo_2 = demographics_provider.fetch_evidence(query)
    assert demo_1.evidence_items[0].model_dump() == demo_2.evidence_items[0].model_dump()


# Test 12: Modelled catchment remains distinct from observed Census 2011 data
def test_catchment_distinct_from_census(market_service):
    query = MarketEvidenceQuery(
        state="Madhya Pradesh",
        district="Ujjain",
        village="Bhatisuda",
        category="Grocery Retail",
        radius_km=5.0
    )
    res = market_service.get_market_indicators(query)
    
    # Catchment is strictly MODELLED
    assert res.catchment.evidence_type == EvidenceType.MODELLED
    assert res.catchment.estimated_population == 4500
    
    # Official Census is OBSERVED with 2011 reference year
    assert res.demographics is not None
    assert res.demographics.evidence_type == EvidenceType.OBSERVED
    assert res.demographics.population == 3142
    assert res.demographics.reference_year == 2011
    assert res.demographics.data_status == "HISTORICAL_OFFICIAL"

    # LGD geography is OBSERVED
    assert res.geography is not None
    assert res.geography.village_lgd_code == "472152"
    assert res.geography.district_lgd_code == "421"
