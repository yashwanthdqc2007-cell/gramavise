from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.evidence import EvidenceType


class GeographyLevel(str, Enum):
    NATIONAL = "NATIONAL"
    STATE = "STATE"
    DISTRICT = "DISTRICT"
    BLOCK = "BLOCK"
    VILLAGE = "VILLAGE"
    CATCHMENT = "CATCHMENT"


class MarketConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class MarketRiskSignal(str, Enum):
    LOW_COMPETITION = "LOW_COMPETITION"
    MODERATE_COMPETITION = "MODERATE_COMPETITION"
    HIGH_COMPETITION = "HIGH_COMPETITION"
    DEMAND_UNCERTAIN = "DEMAND_UNCERTAIN"
    PRICE_UNCERTAIN = "PRICE_UNCERTAIN"
    DATA_INSUFFICIENT = "DATA_INSUFFICIENT"


class CompetitorRelationship(str, Enum):
    DIRECT = "DIRECT"
    ADJACENT = "ADJACENT"
    UNRELATED = "UNRELATED"


class CoverageConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class CompetitorInfo(BaseModel):
    """Legacy backward-compatible competitor representation."""
    name: str = Field(..., description="Business or amenity name")
    distance_km: float = Field(..., description="Straight-line distance from target village/location in km")
    category: str = Field(..., description="Amenity / business tag")
    relationship: Optional[str] = "DIRECT"


class CompetitorDetail(BaseModel):
    """Structured competitor record with explicit OpenStreetMap / Overpass provenance."""
    competitor_id: str
    business_name: str
    category: str
    subcategory: Optional[str] = None
    distance_km: float = Field(..., description="Straight-line Haversine distance in km")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    osm_object_id: Optional[str] = None
    osm_object_type: Optional[str] = None
    tags: dict = Field(default_factory=dict)
    relationship: str = "DIRECT"
    match_reason: Optional[str] = None
    price_indicator: Optional[str] = None
    evidence_type: EvidenceType = EvidenceType.OBSERVED
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    source: str = "OpenStreetMap"
    source_type: str = "OPEN_GEODATA"
    source_url: Optional[str] = "https://www.openstreetmap.org/"
    observed_at: Optional[str] = None
    verification_status: str = "VERIFIED_SOURCE"
    notes: Optional[str] = None


class UdyamDistrictContext(BaseModel):
    """District-level formal MSME registration aggregates from Ministry of MSME / data.gov.in."""
    state_name: str
    district_name: str
    lgd_district_code: Optional[str] = None
    registered_msme_count: int
    micro_count: Optional[int] = None
    small_count: Optional[int] = None
    medium_count: Optional[int] = None
    manufacturing_count: Optional[int] = None
    services_count: Optional[int] = None
    geography_level: GeographyLevel = GeographyLevel.DISTRICT
    evidence_type: EvidenceType = EvidenceType.OBSERVED
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    source: str = "Ministry of Micro, Small and Medium Enterprises / data.gov.in"
    source_url: Optional[str] = "https://udyamregistration.gov.in/"
    dataset_name: str = "Udyam Registration District-wise MSME Aggregates"
    observed_at: Optional[str] = None
    verification_status: str = "VERIFIED_SOURCE"
    notes: str = "District-level formal MSME context only; not a count of nearby competitors."


class CatchmentModel(BaseModel):
    """Catchment and demographic estimates with strict methodology tracking."""
    radius_km: float
    estimated_population: Optional[int] = None
    estimated_households: Optional[int] = None
    estimated_daily_demand: Optional[str] = None
    methodology: str = "Prototype geometric catchment estimation [DEMO]"
    evidence_type: EvidenceType = EvidenceType.MODELLED
    confidence: float = Field(0.5, ge=0.0, le=1.0)
    verification_status: str = "NEEDS_VERIFICATION"


class PriceObservationDetail(BaseModel):
    """Structured agricultural market / mandi price observation with full provenance."""
    commodity: str
    variety: Optional[str] = None
    market_name: str
    district_name: str
    state_name: str
    arrival_date: str
    min_price: float
    max_price: float
    modal_price: float
    price_unit: str = "INR/quintal"
    price_per_kg: Optional[float] = None
    currency: str = "INR"
    evidence_type: EvidenceType = EvidenceType.OBSERVED
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    source: str = "Directorate of Marketing & Inspection (DMI) / OGD"
    source_url: Optional[str] = "https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi"
    source_title: Optional[str] = "Current Daily Price of Various Commodities from Various Markets (Mandi)"
    source_last_verified: Optional[str] = None
    verification_status: str = "VERIFIED_SOURCE"


class PriceBenchmark(BaseModel):
    """Product/service price band with authoritative provenance."""
    category: str
    low_price: Optional[float] = None
    median_price: Optional[float] = None
    high_price: Optional[float] = None
    unit: Optional[str] = None
    price_per_kg: Optional[float] = None
    market_name: Optional[str] = None
    arrival_date: Optional[str] = None
    variety: Optional[str] = None
    geography: Optional[str] = None
    evidence_type: EvidenceType = EvidenceType.NEEDS_VERIFICATION
    source: Optional[str] = None
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    verification_status: str = "NEEDS_VERIFICATION"
    notes: Optional[str] = None


class MarketIndicatorItem(BaseModel):
    """Standard market indicator record."""
    indicator_id: str
    name: str
    value: str
    unit: Optional[str] = None
    geography: str
    geography_level: GeographyLevel
    evidence_type: EvidenceType
    confidence: float = Field(0.5, ge=0.0, le=1.0)
    source: str
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    observed_at: Optional[str] = None
    notes: Optional[str] = None
    verification_status: str


class GeographyIdentity(BaseModel):
    """Verified administrative entity identity and official LGD codes."""
    state_name: Optional[str] = None
    state_lgd_code: Optional[str] = None
    district_name: Optional[str] = None
    district_lgd_code: Optional[str] = None
    sub_district_name: Optional[str] = None
    sub_district_lgd_code: Optional[str] = None
    village_name: Optional[str] = None
    village_lgd_code: Optional[str] = None
    verification_status: str = "NEEDS_VERIFICATION"
    source: Optional[str] = "Ministry of Panchayati Raj / Local Government Directory (LGD)"
    source_url: Optional[str] = "https://lgdirectory.gov.in/"


class DemographicObservation(BaseModel):
    """Historical official population and household counts from Census 2011."""
    population: Optional[int] = None
    households: Optional[int] = None
    reference_year: int = 2011
    data_status: str = "HISTORICAL_OFFICIAL"
    geography_level: GeographyLevel = GeographyLevel.VILLAGE
    evidence_type: EvidenceType = EvidenceType.OBSERVED
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    source: Optional[str] = "Office of the Registrar General & Census Commissioner, India"
    source_url: Optional[str] = "https://censusindia.gov.in/census.website/data/population-finder"
    verification_status: str = "VERIFIED_SOURCE"


class MarketEvidenceQuery(BaseModel):
    state: str
    district: str
    village: str
    category: str
    commodity: Optional[str] = None
    market: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: float = Field(5.0, description="Search radius in kilometers")


class MarketResultResponse(BaseModel):
    location_summary: str
    competitor_count: int = 0
    direct_competitor_count: int = 0
    adjacent_competitor_count: int = 0
    catchment_radius_km: float = 5.0
    coverage_confidence: str = "LOW"
    coverage_warning: Optional[str] = None
    competitor_list: List[CompetitorInfo] = Field(default_factory=list)
    competitors: List[CompetitorDetail] = Field(default_factory=list)
    demand_indicator: str = Field(..., description="HIGH, MEDIUM, LOW, UNKNOWN")
    catchment_population_estimate: Optional[int] = None
    catchment: Optional[CatchmentModel] = None
    price_benchmark: Optional[PriceBenchmark] = None
    price_observations: List[PriceObservationDetail] = Field(default_factory=list)
    geography: Optional[GeographyIdentity] = None
    demographics: Optional[DemographicObservation] = None
    udyam_context: Optional[UdyamDistrictContext] = None
    market_signals: List[MarketRiskSignal] = Field(default_factory=list)
    indicators: List[MarketIndicatorItem] = Field(default_factory=list)
    confidence_level: MarketConfidenceLevel = MarketConfidenceLevel.LOW
    notes: Optional[str] = None
