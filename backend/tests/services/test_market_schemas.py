import pytest
from pydantic import ValidationError
from app.schemas.evidence import EvidenceType
from app.schemas.market import (
    SWOTItem,
    SWOTAnalysis,
    PurchasingPowerIndex,
    SeasonalThreatDetail,
    SupplyChainRiskDetail,
    MarketResultResponse,
    GeographyLevel,
    MarketConfidenceLevel
)
from app.schemas.analysis import (
    AnalysisResultResponse,
    RecommendationStatus
)
from app.schemas.financial import FinancialResultResponse
from app.schemas.scheme import SchemeMatchResult


def test_swot_schema_serialization_and_deserialization():
    swot = SWOTAnalysis(
        strengths=[
            SWOTItem(
                id="STR-001",
                title="Manageable Competition",
                explanation="Only 1 direct competitor mapped within 5 km catchment radius.",
                category="MARKET",
                importance="HIGH",
                evidence_ids=["EV-MKT-COMPETITORS"],
                evidence_type=EvidenceType.OBSERVED,
                confidence=1.0,
                source="OpenStreetMap"
            )
        ],
        weaknesses=[
            SWOTItem(
                id="WKN-001",
                title="Customer Footfall Reliance",
                explanation="Break-even target depends on self-declared customer count.",
                category="FINANCIAL",
                importance="MEDIUM",
                evidence_ids=["EV-USER-CUSTOMERS"],
                evidence_type=EvidenceType.ASSUMED,
                confidence=0.75,
                source="Entrepreneur Assumption"
            )
        ],
        opportunities=[
            SWOTItem(
                id="OPP-001",
                title="PMFME ODOP Scheme Alignment",
                explanation="District notified crop matches enterprise activity.",
                category="REGULATORY",
                importance="HIGH",
                evidence_ids=["EV-MKT-ODOP-1"],
                evidence_type=EvidenceType.OBSERVED,
                confidence=1.0,
                source="MoFPI PMFME Registry"
            )
        ],
        threats=[
            SWOTItem(
                id="THR-001",
                title="Monsoon Road Inaccessibility",
                explanation="Heavy rains in July-August may slow customer visits.",
                category="OPERATIONAL",
                importance="MEDIUM",
                evidence_ids=["EV-MKT-THREAT-MONSOON"],
                evidence_type=EvidenceType.NEEDS_VERIFICATION,
                confidence=0.5,
                source="Seasonal Weather Model"
            )
        ],
        evidence_type=EvidenceType.CALCULATED,
        confidence=0.9,
        verification_status="DERIVED"
    )

    data = swot.model_dump()
    assert len(data["strengths"]) == 1
    assert data["strengths"][0]["id"] == "STR-001"
    assert data["strengths"][0]["evidence_type"] == "OBSERVED"
    assert data["threats"][0]["evidence_type"] == "NEEDS_VERIFICATION"

    reconstructed = SWOTAnalysis.model_validate(data)
    assert reconstructed.strengths[0].title == "Manageable Competition"
    assert reconstructed.weaknesses[0].confidence == 0.75


def test_purchasing_power_index_schema():
    ppi = PurchasingPowerIndex(
        purchasing_power_level="MODERATE",
        affordability_level="AFFORDABLE",
        target_price=250.0,
        reference_income_or_proxy=12000.0,
        affordability_ratio=0.02,
        evidence_ids=["EV-MKT-UDYAM-1", "EV-DEMO-CENSUS2011-1"],
        methodology="Rural consumption proxy",
        limitations="Based on district secondary data; field validation needed",
        evidence_type=EvidenceType.MODELLED,
        confidence=0.6,
        verification_status="NEEDS_VERIFICATION"
    )

    data = ppi.model_dump()
    assert data["target_price"] == 250.0
    assert data["affordability_level"] == "AFFORDABLE"
    assert "EV-MKT-UDYAM-1" in data["evidence_ids"]

    reconstructed = PurchasingPowerIndex.model_validate(data)
    assert reconstructed.purchasing_power_level == "MODERATE"


def test_seasonal_threat_detail_schema():
    threat = SeasonalThreatDetail(
        threat_id="THR-SEA-001",
        threat_type="MONSOON",
        title="Monsoon Supply Interruption",
        explanation="Raw material procurement delayed during monsoon months.",
        affected_period="Jul-Aug",
        severity="HIGH",
        likelihood="MEDIUM",
        evidence_ids=["EV-MKT-MANDI-PRICE-1"],
        evidence_type=EvidenceType.NEEDS_VERIFICATION,
        confidence=0.5,
        mitigation_hint="Build 30 days buffer stock ahead of July.",
        verification_required=True,
        verification_status="NEEDS_VERIFICATION"
    )

    data = threat.model_dump()
    assert data["threat_id"] == "THR-SEA-001"
    assert data["threat_type"] == "MONSOON"
    assert data["verification_required"] is True

    reconstructed = SeasonalThreatDetail.model_validate(data)
    assert reconstructed.severity == "HIGH"


def test_supply_chain_risk_detail_schema():
    sc = SupplyChainRiskDetail(
        risk_id="SC-001",
        input_material="Wheat Grain",
        source_location="Baramati APMC Mandi",
        supplier_dependency="LOCAL_MARKET",
        estimated_distance_km=12.5,
        availability_status="STABLE",
        price_volatility="MODERATE",
        logistics_concern="Rural transport connectivity",
        evidence_ids=["EV-MKT-MANDI-PRICE-1"],
        evidence_type=EvidenceType.OBSERVED,
        confidence=0.85,
        verification_required=False,
        verification_status="VERIFIED_SOURCE"
    )

    data = sc.model_dump()
    assert data["input_material"] == "Wheat Grain"
    assert data["estimated_distance_km"] == 12.5

    reconstructed = SupplyChainRiskDetail.model_validate(data)
    assert reconstructed.supplier_dependency == "LOCAL_MARKET"


def test_market_result_response_backward_compatibility():
    # Construct legacy payload with zero new Phase 2B fields
    legacy_market = MarketResultResponse(
        location_summary="Baramati, Pune, Maharashtra",
        competitor_count=2,
        direct_competitor_count=2,
        adjacent_competitor_count=1,
        catchment_radius_km=5.0,
        coverage_confidence="HIGH",
        demand_indicator="HIGH",
        confidence_level=MarketConfidenceLevel.HIGH
    )

    assert legacy_market.swot is None
    assert legacy_market.purchasing_power is None
    assert legacy_market.seasonal_threats == []
    assert legacy_market.supply_chain == []

    dumped = legacy_market.model_dump()
    assert "swot" in dumped
    assert dumped["swot"] is None
    assert dumped["seasonal_threats"] == []

    # Re-validate dumped dictionary
    reconstructed = MarketResultResponse.model_validate(dumped)
    assert reconstructed.location_summary == "Baramati, Pune, Maharashtra"
    assert reconstructed.competitor_count == 2


def test_market_result_response_with_populated_phase2b_fields():
    market = MarketResultResponse(
        location_summary="Baramati, Pune, Maharashtra",
        competitor_count=1,
        demand_indicator="HIGH",
        swot=SWOTAnalysis(
            strengths=[
                SWOTItem(
                    id="STR-001",
                    title="Low Competition",
                    explanation="1 competitor mapped",
                    evidence_ids=["EV-MKT-1"]
                )
            ]
        ),
        purchasing_power=PurchasingPowerIndex(
            purchasing_power_level="MODERATE",
            affordability_level="AFFORDABLE"
        ),
        seasonal_threats=[
            SeasonalThreatDetail(
                threat_id="THR-001",
                threat_type="SEASONAL_DEMAND",
                title="Post-Harvest Dip",
                explanation="Demand reduces slightly in pre-monsoon"
            )
        ],
        supply_chain=[
            SupplyChainRiskDetail(
                input_material="Raw Spices",
                source_location="APMC Market",
                supplier_dependency="LOCAL_MARKET"
            )
        ]
    )

    dumped = market.model_dump()
    assert dumped["swot"]["strengths"][0]["id"] == "STR-001"
    assert dumped["purchasing_power"]["purchasing_power_level"] == "MODERATE"
    assert len(dumped["seasonal_threats"]) == 1
    assert len(dumped["supply_chain"]) == 1

    reconstructed = MarketResultResponse.model_validate(dumped)
    assert reconstructed.swot.strengths[0].title == "Low Competition"


def test_analysis_result_response_backward_compatibility():
    financial_res = FinancialResultResponse(
        total_capex=150000.0,
        required_loan_amount=100000.0,
        monthly_revenue=45000.0,
        monthly_variable_cost=18000.0,
        monthly_gross_profit=27000.0,
        monthly_fixed_cost=8000.0,
        monthly_emi=2100.0,
        monthly_net_profit=16900.0,
        net_profit_margin_pct=37.5,
        break_even_revenue_monthly=13333.33,
        break_even_units_daily=10,
        dscr=8.0,
        is_financially_viable=True
    )
    market_res = MarketResultResponse(
        location_summary="Baramati, Pune, Maharashtra",
        competitor_count=1,
        demand_indicator="HIGH"
    )
    scheme_res = SchemeMatchResult(
        eligible_schemes_count=1,
        schemes=[],
        total_potential_subsidy=25000.0
    )

    analysis_res = AnalysisResultResponse(
        analysis_id="test-analysis-12345",
        recommendation_status=RecommendationStatus.PROCEED,
        confidence_score=0.92,
        financial_result=financial_res,
        market_result=market_res,
        scheme_result=scheme_res
    )

    data = analysis_res.model_dump()
    assert data["analysis_id"] == "test-analysis-12345"
    assert data["market_result"]["swot"] is None
    assert data["market_result"]["seasonal_threats"] == []

    reconstructed = AnalysisResultResponse.model_validate(data)
    assert reconstructed.recommendation_status == RecommendationStatus.PROCEED
    assert reconstructed.market_result.location_summary == "Baramati, Pune, Maharashtra"


def test_invalid_confidence_raises_validation_error():
    with pytest.raises(ValidationError):
        SWOTItem(
            id="STR-ERR",
            title="Invalid",
            explanation="Invalid confidence > 1.0",
            confidence=1.5
        )

    with pytest.raises(ValidationError):
        PurchasingPowerIndex(
            confidence=-0.1
        )
