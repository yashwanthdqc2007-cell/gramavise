import uuid
from fastapi import APIRouter, HTTPException, status
from app.schemas.analysis import AnalysisRequest, AnalysisResultResponse
from app.schemas.ai import AIExplanationRequest
from app.schemas.market import MarketEvidenceQuery
from app.services.financial.calculator import FinancialService
from app.services.financial.validation import validate_financial_assumptions
from app.services.geo.market import MockMarketService
from app.services.schemes.matcher import SchemeService
from app.services.evidence.collector import EvidenceCollector
from app.services.recommendation.feasibility import evaluate_feasibility_status
from app.services.recommendation.risk import assess_business_risks
from app.services.ai.explanation import AIService

router = APIRouter()

financial_service = FinancialService()
market_service = MockMarketService()
scheme_service = SchemeService()
evidence_collector = EvidenceCollector()
ai_service = AIService()


@router.post("/analyze", response_model=AnalysisResultResponse, summary="Execute Full Business Feasibility & Advisory Pipeline")
async def analyze_business(request: AnalysisRequest):
    """Orchestrate end-to-end evaluation pipeline:
    1. Financial unit economics & break-even calculation
    2. Geo & market competitor density lookup
    3. Government scheme eligibility matching
    4. Deterministic feasibility status assignment (PROCEED / VALIDATE_FIRST / RECONSIDER)
    5. Evidence tagging & confidence score aggregation
    6. Explainable vernacular narrative generation
    
    TODO [Backend Lead]: Persist full analysis execution into AnalysisRepository (PostgreSQL).
    """
    # 1. Validate Financial Inputs
    is_valid, errors = validate_financial_assumptions(request.financials)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": errors}
        )

    # 2. Financial Computation
    financial_res = financial_service.calculate(
        own_capital=request.profile.own_capital,
        desired_loan=request.profile.desired_loan,
        financials=request.financials
    )

    # 3. Market & Geospatial Indicators
    market_query = MarketEvidenceQuery(
        state=request.profile.location.state,
        district=request.profile.location.district,
        village=request.profile.location.village,
        category=request.profile.category,
        latitude=request.profile.location.latitude,
        longitude=request.profile.location.longitude
    )
    market_res = market_service.get_market_indicators(market_query)

    # 4. Scheme Matching
    scheme_res = scheme_service.match_schemes(request.profile, financial_res)

    # 5. Deterministic Feasibility Status & Risk Analysis
    rec_status = evaluate_feasibility_status(financial_res, market_res)
    risks = assess_business_risks(financial_res, market_res)

    # 6. Evidence Collection & Confidence Scoring
    evidence_context = {
        "monthly_net_profit": financial_res.monthly_net_profit,
        "break_even_units_daily": financial_res.break_even_units_daily,
        "competitor_count": market_res.competitor_count,
        "customers_per_day": request.financials.customers_per_day
    }
    evidence_items = evidence_collector.collect(evidence_context)
    confidence = evidence_collector.calculate_confidence(evidence_items)

    # 7. AI Plain-Language / Vernacular Explanation
    ai_req = AIExplanationRequest(
        business_name=request.profile.business_name,
        category=request.profile.category,
        location=f"{request.profile.location.village}, {request.profile.location.district}",
        recommendation_status=rec_status.value,
        financial_summary=financial_res.model_dump(),
        matched_schemes=[s.model_dump() for s in scheme_res.schemes],
        risk_factors=[r.model_dump() for r in risks],
        preferred_language=request.preferred_language
    )
    ai_explanation = ai_service.explain_analysis(ai_req)

    return AnalysisResultResponse(
        analysis_id=str(uuid.uuid4()),
        recommendation_status=rec_status,
        confidence_score=confidence,
        financial_result=financial_res,
        market_result=market_res,
        scheme_result=scheme_res,
        risk_factors=risks,
        evidence_list=evidence_items,
        ai_explanation=ai_explanation
    )
