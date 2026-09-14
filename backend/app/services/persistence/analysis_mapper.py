"""Bidirectional mapping between Pydantic analysis schemas and SQLAlchemy ORM models.

Maintains data fidelity for persistence and historical retrieval without
performing any calculations or business logic.
"""
from typing import Tuple, Optional, List
import uuid

from app.models.analysis import Analysis, RecommendationStatusEnum
from app.models.financial_snapshot import FinancialInputSnapshot, FinancialResultSnapshot
from app.models.business import BusinessProfile
from app.schemas.analysis import (
    AnalysisRequest,
    AnalysisResultResponse,
    RecommendationStatus,
    RiskFactor,
    DecisionTrace,
)
from app.schemas.financial import FinancialResultResponse, NumberExplanation
from app.schemas.market import MarketResultResponse
from app.schemas.scheme import SchemeMatchResult
from app.schemas.evidence import EvidenceItem, VerificationCheckItem
from app.schemas.action_plan import ActionPlan, DocumentReadiness, BankReadiness
from app.schemas.ai import AIExplanationResponse


def map_response_to_models(
    request: AnalysisRequest,
    response: AnalysisResultResponse,
) -> Tuple[Analysis, FinancialInputSnapshot, FinancialResultSnapshot, BusinessProfile]:
    """Convert an in-memory analysis request & result response into ORM snapshot models."""
    profile_id = str(uuid.uuid4())
    business_profile = BusinessProfile(
        id=profile_id,
        business_name=request.profile.business_name,
        category=request.profile.category,
        description=request.profile.description,
        state=request.profile.location.state,
        district=request.profile.location.district,
        village=request.profile.location.village,
        latitude=request.profile.location.latitude,
        longitude=request.profile.location.longitude,
        experience_years=request.profile.experience_years,
        own_capital=request.profile.own_capital,
        desired_loan=request.profile.desired_loan or 0.0,
        is_new_business=request.profile.is_new_business,
    )

    analysis = Analysis(
        id=response.analysis_id,
        business_id=profile_id,
        recommendation_status=RecommendationStatusEnum(response.recommendation_status.value),
        overall_verdict=response.overall_verdict.value if response.overall_verdict else response.recommendation_status.value,
        confidence_score=response.confidence_score,
        schema_version="1.0.0",
        rules_version="1.0.0",
        business_input_snapshot=request.profile.model_dump(),
        market_result_snapshot=response.market_result.model_dump(),
        scheme_result_snapshot=response.scheme_result.model_dump(),
        evidence_ledger_snapshot=[e.model_dump() for e in (response.evidence_ledger or response.evidence_list or [])],
        decision_trace_snapshot=response.decision_trace.model_dump() if response.decision_trace else {},
        action_plan_snapshot=response.action_plan.model_dump() if response.action_plan else {},
        bank_readiness_snapshot=response.bank_readiness.model_dump() if response.bank_readiness else {},
        risk_factors=[r.model_dump() for r in response.risk_factors],
        ai_explanation=response.ai_explanation.model_dump() if response.ai_explanation else {},
    )

    input_snapshot = FinancialInputSnapshot(
        analysis_id=response.analysis_id,
        own_capital=request.profile.own_capital,
        desired_loan=request.profile.desired_loan,
        startup_cost=request.financials.startup_cost,
        equipment_cost=request.financials.equipment_cost,
        inventory_cost=request.financials.inventory_cost,
        monthly_fixed_cost=request.financials.monthly_fixed_cost,
        customers_per_day=request.financials.customers_per_day,
        avg_ticket_price=request.financials.avg_ticket_price,
        working_days_per_month=request.financials.working_days_per_month,
        variable_cost_pct=request.financials.variable_cost_pct,
        interest_rate_pct=request.financials.interest_rate_pct,
        loan_tenure_months=request.financials.loan_tenure_months,
    )

    explanations_dict = {}
    if response.financial_result.explanations:
        for k, v in response.financial_result.explanations.items():
            if hasattr(v, "model_dump"):
                explanations_dict[k] = v.model_dump()
            else:
                explanations_dict[k] = v

    result_snapshot = FinancialResultSnapshot(
        analysis_id=response.analysis_id,
        total_capex=response.financial_result.total_capex,
        required_loan_amount=response.financial_result.required_loan_amount,
        monthly_revenue=response.financial_result.monthly_revenue,
        monthly_variable_cost=response.financial_result.monthly_variable_cost,
        monthly_gross_profit=response.financial_result.monthly_gross_profit,
        monthly_fixed_cost=response.financial_result.monthly_fixed_cost,
        monthly_emi=response.financial_result.monthly_emi,
        monthly_net_profit=response.financial_result.monthly_net_profit,
        net_profit_margin_pct=response.financial_result.net_profit_margin_pct,
        break_even_revenue_monthly=response.financial_result.break_even_revenue_monthly,
        break_even_units_daily=response.financial_result.break_even_units_daily,
        dscr=response.financial_result.dscr,
        is_financially_viable=response.financial_result.is_financially_viable,
        explanations=explanations_dict,
    )

    return analysis, input_snapshot, result_snapshot, business_profile


def map_models_to_response(analysis: Analysis) -> AnalysisResultResponse:
    """Reconstruct an AnalysisResultResponse from a persisted Analysis and its snapshots."""
    # 1. Reconstruct FinancialResultResponse
    frs = analysis.financial_result_snapshot
    explanations = None
    if frs and frs.explanations:
        explanations = {}
        for k, v in frs.explanations.items():
            if isinstance(v, dict):
                explanations[k] = NumberExplanation(**v)

    financial_result = FinancialResultResponse(
        total_capex=frs.total_capex if frs else 0.0,
        required_loan_amount=frs.required_loan_amount if frs else 0.0,
        monthly_revenue=frs.monthly_revenue if frs else 0.0,
        monthly_variable_cost=frs.monthly_variable_cost if frs else 0.0,
        monthly_gross_profit=frs.monthly_gross_profit if frs else 0.0,
        monthly_fixed_cost=frs.monthly_fixed_cost if frs else 0.0,
        monthly_emi=frs.monthly_emi if frs else 0.0,
        monthly_net_profit=frs.monthly_net_profit if frs else 0.0,
        net_profit_margin_pct=frs.net_profit_margin_pct if frs else 0.0,
        break_even_revenue_monthly=frs.break_even_revenue_monthly if frs else 0.0,
        break_even_units_daily=frs.break_even_units_daily if frs else 0,
        dscr=frs.dscr if frs else 0.0,
        is_financially_viable=frs.is_financially_viable if frs else False,
        explanations=explanations,
    )

    # 2. Reconstruct MarketResultResponse
    market_result = MarketResultResponse(**analysis.market_result_snapshot)

    # 3. Reconstruct SchemeMatchResult
    scheme_result = SchemeMatchResult(**analysis.scheme_result_snapshot)

    # 4. Reconstruct Risk Factors
    risk_factors = [RiskFactor(**r) for r in (analysis.risk_factors or [])]

    # 5. Reconstruct Evidence Ledger
    evidence_items = [EvidenceItem(**e) for e in (analysis.evidence_ledger_snapshot or [])]

    # 6. Reconstruct Decision Trace
    decision_trace = None
    if analysis.decision_trace_snapshot:
        decision_trace = DecisionTrace(**analysis.decision_trace_snapshot)

    # 7. Reconstruct Action Plan & Bank Readiness
    action_plan = None
    if analysis.action_plan_snapshot and analysis.action_plan_snapshot.get("actions"):
        action_plan = ActionPlan(**analysis.action_plan_snapshot)

    bank_readiness = None
    if analysis.bank_readiness_snapshot and analysis.bank_readiness_snapshot.get("overall_rating"):
        bank_readiness = BankReadiness(**analysis.bank_readiness_snapshot)

    # 8. Reconstruct AI Explanation
    ai_explanation = None
    if analysis.ai_explanation and analysis.ai_explanation.get("summary"):
        ai_explanation = AIExplanationResponse(**analysis.ai_explanation)

    # 9. Verification checklist (generate from evidence if not directly in snapshot)
    from app.services.evidence.collector import EvidenceCollector
    verification_checklist = EvidenceCollector().generate_verification_checklist(evidence_items)

    rec_status_val = analysis.recommendation_status.value if hasattr(analysis.recommendation_status, "value") else str(analysis.recommendation_status)
    rec_status = RecommendationStatus(rec_status_val)

    overall_verdict = None
    if analysis.overall_verdict:
        overall_verdict = RecommendationStatus(analysis.overall_verdict)
    else:
        overall_verdict = rec_status

    return AnalysisResultResponse(
        analysis_id=analysis.id,
        recommendation_status=rec_status,
        overall_verdict=overall_verdict,
        confidence_score=analysis.confidence_score,
        financial_result=financial_result,
        market_result=market_result,
        scheme_result=scheme_result,
        risk_factors=risk_factors,
        evidence_list=evidence_items,
        evidence_ledger=evidence_items,
        decision_trace=decision_trace,
        verification_checklist=verification_checklist,
        action_plan=action_plan,
        document_readiness=None,
        bank_readiness=bank_readiness,
        ai_explanation=ai_explanation,
    )
