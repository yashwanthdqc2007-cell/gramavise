from typing import List, Optional
import uuid
from fastapi import APIRouter, HTTPException, status, Depends, Header
from sqlalchemy.exc import IntegrityError
from app.schemas.analysis import AnalysisRequest, AnalysisResultResponse
from app.schemas.ai import AIExplanationRequest, AIExplanationResponse
from app.schemas.market import MarketEvidenceQuery, MarketResultResponse
from app.schemas.financial import FinancialAssumptionsInput
from app.services.financial.calculator import FinancialService
from app.services.financial.validation import (
    validate_financial_assumptions,
    validate_capital_inputs
)
from app.services.geo.market import MockMarketService
from app.services.schemes.matcher import SchemeService
from app.services.evidence.collector import EvidenceCollector
from app.services.recommendation.feasibility import evaluate_feasibility_with_trace
from app.services.recommendation.risk import assess_business_risks
from app.services.recommendation.action_plan import ActionPlanGenerator
from app.services.recommendation.scenario_comparator import ScenarioComparator
from app.schemas.scenario import (
    ScenarioEvaluationRequest,
    ScenarioEvaluationResponse,
    CreateScenarioRequest,
    ScenarioRecordResponse,
)
from app.services.ai.explanation import AIService
from app.repositories import UnitOfWork, get_uow, ScenarioLimitExceededError
from app.models.idempotency import IdempotencyRecord
from app.utils.fingerprint import compute_request_fingerprint
from app.services.persistence import (
    map_response_to_models,
    map_models_to_response,
    map_scenario_evaluation_to_model,
    map_model_to_scenario_response,
)
from app.utils.logging import logger

router = APIRouter()


financial_service = FinancialService()
market_service = MockMarketService()
scheme_service = SchemeService()
evidence_collector = EvidenceCollector()
scenario_comparator = ScenarioComparator(financial_service=financial_service)
ai_service = AIService()


@router.post("/analyze", response_model=AnalysisResultResponse, summary="Execute Full Business Feasibility & Advisory Pipeline")
async def analyze_business(
    request: AnalysisRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    uow: UnitOfWork = Depends(get_uow),
):
    """Orchestrate end-to-end evaluation pipeline with optional idempotency protection."""
    # 0. Idempotency Check (if key provided)
    fingerprint = None
    if idempotency_key:
        fingerprint = compute_request_fingerprint(request)
        existing_rec = uow.idempotency.get(idempotency_key, "ANALYSIS")
        if existing_rec:
            if existing_rec.request_fingerprint == fingerprint:
                if existing_rec.resource_id:
                    existing_analysis = uow.analyses.get_by_id(existing_rec.resource_id)
                    if existing_analysis:
                        logger.info(f"Idempotency hit for key '{idempotency_key}'. Replaying analysis '{existing_analysis.id}'.")
                        return map_models_to_response(existing_analysis)
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Idempotency key '{idempotency_key}' was previously used with a different request payload."
                )

    # 1. Validate Financial & Capital Inputs
    is_valid_f, errors_f = validate_financial_assumptions(request.financials)
    is_valid_c, errors_c = validate_capital_inputs(request.profile.own_capital, request.profile.desired_loan)
    
    all_errors = errors_f + errors_c
    if all_errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": all_errors}
        )

    # 2. Deterministic Financial Computation
    financial_res = financial_service.calculate(
        own_capital=request.profile.own_capital,
        desired_loan=request.profile.desired_loan,
        financials=request.financials
    )

    # 3. Market & Geospatial Indicators (OSM, Mandi, Census 2011, LGD, Udyam)
    market_query = MarketEvidenceQuery(
        state=request.profile.location.state,
        district=request.profile.location.district,
        village=request.profile.location.village,
        category=request.profile.category,
        latitude=request.profile.location.latitude,
        longitude=request.profile.location.longitude
    )
    market_res = market_service.get_market_indicators(market_query)

    # 4. Scheme Matching Baseline (PMEGP / MUDRA / PMFME)
    scheme_res = scheme_service.match_schemes(request.profile, financial_res)

    # 5. Deterministic Feasibility Status, Decision Trace & Risk Analysis
    rec_status, decision_trace = evaluate_feasibility_with_trace(financial_res, market_res)
    risks = assess_business_risks(financial_res, market_res)

    # 6. Evidence Ledger Collection & Verification Checklist Generation
    evidence_context = {
        "monthly_net_profit": financial_res.monthly_net_profit,
        "break_even_units_daily": financial_res.break_even_units_daily,
        "competitor_count": market_res.competitor_count,
        "customers_per_day": request.financials.customers_per_day,
        "schemes": scheme_res.schemes,
        "market_result": market_res,
        "state": request.profile.location.state,
        "district": request.profile.location.district,
        "village": request.profile.location.village,
        "location": request.profile.location,
        "category": request.profile.category
    }
    evidence_items = evidence_collector.collect(evidence_context)
    confidence = evidence_collector.calculate_confidence(evidence_items)
    verification_checklist = evidence_collector.generate_verification_checklist(evidence_items)

    from app.services.financial.explainer import FinancialExplainer
    financial_res.explanations = FinancialExplainer.generate_explanations(
        own_capital=request.profile.own_capital,
        desired_loan=request.profile.desired_loan,
        financials=request.financials,
        result=financial_res,
        evidence_ledger=evidence_items
    )

    # 7. Action Plan, Document Readiness & Bank-Readiness (Step 4I)
    action_plan = ActionPlanGenerator.generate_action_plan(
        recommendation_status=rec_status,
        financial_result=financial_res,
        market_result=market_res,
        scheme_result=scheme_res,
        evidence_ledger=evidence_items,
        decision_trace=decision_trace,
        risks=risks,
        customers_per_day=request.financials.customers_per_day
    )
    document_readiness = ActionPlanGenerator.generate_document_readiness(
        scheme_result=scheme_res,
        evidence_ledger=evidence_items
    )
    bank_readiness = ActionPlanGenerator.generate_bank_readiness(
        recommendation_status=rec_status,
        financial_result=financial_res,
        market_result=market_res,
        scheme_result=scheme_res,
        evidence_ledger=evidence_items,
        action_plan=action_plan,
        document_readiness=document_readiness
    )

    # 8. AI Plain-Language / Vernacular Explanation (with resilient fallback)
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
    try:
        ai_explanation = ai_service.explain_analysis(ai_req)
    except Exception as e:
        logger.warning(f"AI advisory explanation generation failed ({e}). Providing deterministic fallback.")
        ai_explanation = AIExplanationResponse(
            language=request.preferred_language,
            summary=decision_trace.summary,
            strengths=decision_trace.key_positive_factors or ["Mathematical unit economics and safety margin checks completed."],
            cautions_and_risks=decision_trace.key_caution_factors or [r.factor for r in risks],
            actionable_next_steps=[a.title for a in action_plan.actions[:3]] or [
                f"Review daily order break-even target ({financial_res.break_even_units_daily} units/day) against local footfall.",
                "Verify local competitor density and supplier pricing.",
                "Consult local Lead District Bank officer for scheme application."
            ],
            disclaimer="Automated fallback advisory narrative grounded in deterministic analysis. Please consult a banking professional."
        )

    # 9. Stable Persistent Analysis ID & Response Payload
    persistent_analysis_id = str(uuid.uuid4())
    response = AnalysisResultResponse(
        analysis_id=persistent_analysis_id,
        recommendation_status=rec_status,
        overall_verdict=rec_status,
        confidence_score=confidence,
        financial_result=financial_res,
        market_result=market_res,
        scheme_result=scheme_res,
        risk_factors=risks,
        evidence_list=evidence_items,
        evidence_ledger=evidence_items,
        decision_trace=decision_trace,
        verification_checklist=verification_checklist,
        action_plan=action_plan,
        document_readiness=document_readiness,
        bank_readiness=bank_readiness,
        ai_explanation=ai_explanation
    )

    # 10. Atomic Persistence via Unit of Work
    try:
        analysis_orm, input_snapshot, result_snapshot, business_profile = map_response_to_models(
            request=request,
            response=response,
        )
        uow.business_profiles.create(business_profile)
        uow.analyses.create(
            analysis_orm,
            input_snapshot=input_snapshot,
            result_snapshot=result_snapshot,
        )
        if idempotency_key:
            idempotency_rec = IdempotencyRecord(
                key=idempotency_key,
                scope="ANALYSIS",
                request_fingerprint=fingerprint,
                resource_id=persistent_analysis_id,
                status="COMPLETED",
            )
            uow.idempotency.add(idempotency_rec)
        uow.commit()
    except IntegrityError as ie:
        uow.rollback()
        if idempotency_key:
            existing_rec = uow.idempotency.get(idempotency_key, "ANALYSIS")
            if existing_rec and existing_rec.request_fingerprint == fingerprint:
                if existing_rec.resource_id:
                    existing_analysis = uow.analyses.get_by_id(existing_rec.resource_id)
                    if existing_analysis:
                        return map_models_to_response(existing_analysis)
            elif existing_rec:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Idempotency key '{idempotency_key}' was previously used with a different request payload."
                )
        logger.error(f"Integrity error persisting analysis: {ie}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Feasibility analysis completed but failed to persist analysis record."
        )
    except Exception as exc:
        logger.error(f"Failed to persist analysis snapshot: {exc}")
        uow.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Feasibility analysis completed but failed to persist analysis record."
        )

    return response


@router.get("/analyze/{analysis_id}", response_model=AnalysisResultResponse, summary="Retrieve Stored Historical Analysis Snapshot")
async def get_historical_analysis(
    analysis_id: str,
    uow: UnitOfWork = Depends(get_uow),
):
    """Retrieve an immutable historical analysis snapshot by its unique ID.
    
    Guaranteed to be read-only: does NOT recalculate, re-evaluate rules, or query external live providers.
    """
    # 1. Validate ID format
    try:
        valid_uuid = str(uuid.UUID(analysis_id))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid analysis ID format: '{analysis_id}'. Expected a standard UUID string."
        )

    # 2. Retrieve Persisted Analysis Record
    analysis = uow.analyses.get_by_id(valid_uuid)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Historical analysis with ID '{analysis_id}' was not found."
        )

    # 3. Map Stored Snapshots Directly to Response Schema
    return map_models_to_response(analysis)


@router.post("/analyze/scenario", response_model=ScenarioEvaluationResponse, summary="Evaluate Scenario Lab Assumptions Against Baseline")
async def evaluate_scenario(request: ScenarioEvaluationRequest):
    """Calculate scenario financial model and compare deterministically against baseline.
    
    Reuses existing FinancialService and FeasibilityRules. Baseline remains immutable.
    """
    try:
        response = scenario_comparator.evaluate_scenario(request)
        return response
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": str(ve)}
        )


@router.post(
    "/analyze/{analysis_id}/scenarios",
    response_model=ScenarioRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save a New Scenario Against Parent Analysis",
)
async def create_saved_scenario(
    analysis_id: str,
    request: CreateScenarioRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    uow: UnitOfWork = Depends(get_uow),
):
    """Calculate and persist a what-if scenario record atomically against a baseline Analysis with idempotency protection.
    
    Invariants:
    1. Parent analysis must exist.
    2. Maximum 3 saved scenarios per parent analysis enforced (HTTP 409 on 4th).
    3. Baseline analysis is never mutated.
    4. Deterministic scenario calculation reuses existing ScenarioComparator.
    5. Duplicate requests with same Idempotency-Key replay existing scenario without consuming slots.
    """
    # 1. Validate UUID format
    try:
        valid_analysis_uuid = str(uuid.UUID(analysis_id))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid analysis ID format: '{analysis_id}'. Expected a standard UUID string."
        )

    # 1b. Idempotency Check (if key provided)
    fingerprint = None
    if idempotency_key:
        fingerprint = compute_request_fingerprint({"analysis_id": valid_analysis_uuid, "request": request.model_dump()})
        existing_rec = uow.idempotency.get(idempotency_key, "SCENARIO")
        if existing_rec:
            if existing_rec.request_fingerprint == fingerprint:
                if existing_rec.resource_id:
                    existing_scenario = uow.scenarios.get_by_id(existing_rec.resource_id)
                    if existing_scenario:
                        logger.info(f"Idempotency hit for scenario key '{idempotency_key}'. Replaying scenario '{existing_scenario.id}'.")
                        return map_model_to_scenario_response(existing_scenario)
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Idempotency key '{idempotency_key}' was previously used with a different scenario payload."
                )

    # 2. Validate Scenario Financial & Capital Inputs
    is_valid_f, errors_f = validate_financial_assumptions(request.scenario_financials)
    is_valid_c, errors_c = validate_capital_inputs(request.scenario_own_capital, request.scenario_desired_loan)
    all_errors = errors_f + errors_c
    if all_errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": all_errors}
        )

    # 3. Retrieve Parent Baseline Analysis
    parent_analysis = uow.analyses.get_by_id(valid_analysis_uuid)
    if not parent_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parent analysis with ID '{analysis_id}' was not found."
        )

    # 4. Enforce 3-scenario limit upfront
    current_count = uow.scenarios.count_by_analysis(valid_analysis_uuid)
    if current_count >= 3:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Maximum limit of 3 saved scenarios reached for parent analysis '{analysis_id}'."
        )

    # 5. Extract Baseline Parameters from Immutable Snapshots
    base_snap = parent_analysis.financial_input_snapshot
    baseline_financials = FinancialAssumptionsInput(
        startup_cost=base_snap.startup_cost,
        equipment_cost=base_snap.equipment_cost,
        inventory_cost=base_snap.inventory_cost,
        monthly_fixed_cost=base_snap.monthly_fixed_cost,
        customers_per_day=base_snap.customers_per_day,
        avg_ticket_price=base_snap.avg_ticket_price,
        working_days_per_month=base_snap.working_days_per_month,
        variable_cost_pct=base_snap.variable_cost_pct,
        interest_rate_pct=base_snap.interest_rate_pct,
        loan_tenure_months=base_snap.loan_tenure_months,
    )
    market_context = MarketResultResponse(**parent_analysis.market_result_snapshot) if parent_analysis.market_result_snapshot else None

    # 6. Execute Deterministic Scenario Calculation
    scenario_id = str(uuid.uuid4())
    eval_req = ScenarioEvaluationRequest(
        scenario_id=scenario_id,
        name=request.name,
        description=request.description,
        baseline_own_capital=base_snap.own_capital,
        baseline_desired_loan=base_snap.desired_loan,
        baseline_financials=baseline_financials,
        scenario_own_capital=request.scenario_own_capital,
        scenario_desired_loan=request.scenario_desired_loan,
        scenario_financials=request.scenario_financials,
        market_context=market_context,
    )

    try:
        eval_response = scenario_comparator.evaluate_scenario(eval_req)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": str(ve)}
        )

    # 7. Collect 12 Scenario Inputs for Provenance
    scenario_inputs_dict = {
        "own_capital": request.scenario_own_capital,
        "desired_loan": request.scenario_desired_loan,
        **request.scenario_financials.model_dump(),
    }

    # 8. Map to ORM Model & Persist Atomically via Unit of Work
    scenario_record = map_scenario_evaluation_to_model(
        analysis_id=valid_analysis_uuid,
        evaluation=eval_response,
        scenario_inputs=scenario_inputs_dict,
        name=request.name,
        description=request.description,
    )

    try:
        uow.scenarios.create(scenario_record)
        if idempotency_key:
            idempotency_rec = IdempotencyRecord(
                key=idempotency_key,
                scope="SCENARIO",
                request_fingerprint=fingerprint,
                resource_id=scenario_record.id,
                status="COMPLETED",
            )
            uow.idempotency.add(idempotency_rec)
        uow.commit()
    except ScenarioLimitExceededError as e:
        uow.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except IntegrityError as ie:
        uow.rollback()
        if idempotency_key:
            existing_rec = uow.idempotency.get(idempotency_key, "SCENARIO")
            if existing_rec and existing_rec.request_fingerprint == fingerprint:
                if existing_rec.resource_id:
                    existing_scenario = uow.scenarios.get_by_id(existing_rec.resource_id)
                    if existing_scenario:
                        return map_model_to_scenario_response(existing_scenario)
            elif existing_rec:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Idempotency key '{idempotency_key}' was previously used with a different scenario payload."
                )
        logger.error(f"Integrity error persisting scenario: {ie}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Scenario evaluated successfully but failed to persist record."
        )
    except Exception as exc:
        logger.error(f"Failed to persist scenario record: {exc}")
        uow.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Scenario evaluated successfully but failed to persist record."
        )

    return map_model_to_scenario_response(scenario_record)


@router.get(
    "/analyze/{analysis_id}/scenarios",
    response_model=List[ScenarioRecordResponse],
    summary="List Saved Scenarios for an Analysis",
)
async def list_saved_scenarios(
    analysis_id: str,
    uow: UnitOfWork = Depends(get_uow),
):
    """Retrieve all saved scenarios for a specific parent analysis.
    
    Guaranteed pure read-only: does not recalculate or query live external providers.
    """
    try:
        valid_analysis_uuid = str(uuid.UUID(analysis_id))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid analysis ID format: '{analysis_id}'. Expected a standard UUID string."
        )

    parent_analysis = uow.analyses.get_by_id(valid_analysis_uuid)
    if not parent_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parent analysis with ID '{analysis_id}' was not found."
        )

    records = uow.scenarios.list_by_analysis(valid_analysis_uuid)
    return [map_model_to_scenario_response(r) for r in records]


@router.get(
    "/analyze/{analysis_id}/scenarios/{scenario_id}",
    response_model=ScenarioRecordResponse,
    summary="Retrieve Single Saved Scenario",
)
async def get_saved_scenario(
    analysis_id: str,
    scenario_id: str,
    uow: UnitOfWork = Depends(get_uow),
):
    """Retrieve a specific saved scenario ensuring parent analysis ownership.
    
    Guaranteed pure read-only: does not recalculate or query live external providers.
    """
    try:
        valid_analysis_uuid = str(uuid.UUID(analysis_id))
        valid_scenario_uuid = str(uuid.UUID(scenario_id))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid ID format. Expected standard UUID strings."
        )

    parent_analysis = uow.analyses.get_by_id(valid_analysis_uuid)
    if not parent_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parent analysis with ID '{analysis_id}' was not found."
        )

    record = uow.scenarios.get_by_id(valid_scenario_uuid)
    if not record or record.analysis_id != valid_analysis_uuid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with ID '{scenario_id}' was not found under analysis '{analysis_id}'."
        )

    return map_model_to_scenario_response(record)

