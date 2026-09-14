"""Bidirectional mapping between Scenario Pydantic schemas and ScenarioRecord ORM models.

Maintains exact data fidelity for persistence and historical scenario retrieval without
performing any calculations, financial formulas, or external provider queries.
"""
from datetime import datetime
from typing import Dict, Any, Optional

from app.models.scenario import ScenarioRecord
from app.schemas.scenario import (
    ScenarioEvaluationResponse,
    ScenarioRecordResponse,
    MetricComparison,
    RuleComparison,
    RecommendationChange,
)
from app.schemas.financial import FinancialResultResponse
from app.schemas.analysis import RecommendationStatus, DecisionTrace, RiskFactor


def map_scenario_evaluation_to_model(
    analysis_id: str,
    evaluation: ScenarioEvaluationResponse,
    scenario_inputs: Dict[str, Any],
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> ScenarioRecord:
    """Map in-memory scenario evaluation and input parameters to a persistent ORM ScenarioRecord."""
    return ScenarioRecord(
        id=evaluation.scenario_id,
        analysis_id=analysis_id,
        name=name or evaluation.name,
        description=description or evaluation.description,
        scenario_inputs=scenario_inputs,
        scenario_financial_result=evaluation.scenario_result.model_dump(),
        scenario_recommendation={
            "scenario_status": evaluation.scenario_status.value,
            "scenario_decision_trace": evaluation.scenario_decision_trace.model_dump() if evaluation.scenario_decision_trace else None,
            "risk_factors": [r.model_dump() for r in evaluation.risk_factors],
        },
        comparison_result={
            "baseline_result": evaluation.baseline_result.model_dump(),
            "baseline_status": evaluation.baseline_status.value,
            "baseline_decision_trace": evaluation.baseline_decision_trace.model_dump() if evaluation.baseline_decision_trace else None,
            "metric_comparisons": [m.model_dump() for m in evaluation.metric_comparisons],
            "rule_comparisons": [r.model_dump() for r in evaluation.rule_comparisons],
            "recommendation_change": evaluation.recommendation_change.model_dump() if evaluation.recommendation_change else None,
            "what_changed": evaluation.what_changed,
            "why_it_changed": evaluation.why_it_changed,
            "disclaimer": evaluation.disclaimer,
        },
        created_at=datetime.utcnow(),
    )


def map_model_to_scenario_response(scenario_record: ScenarioRecord) -> ScenarioRecordResponse:
    """Map a persistent ORM ScenarioRecord to ScenarioRecordResponse without recalculating."""
    rec_data = scenario_record.scenario_recommendation or {}
    comp_data = scenario_record.comparison_result or {}

    rec_change_data = comp_data.get("recommendation_change")
    rec_change = (
        RecommendationChange(**rec_change_data)
        if rec_change_data
        else RecommendationChange(
            baseline_status=RecommendationStatus(comp_data.get("baseline_status", RecommendationStatus.RECONSIDER.value)),
            scenario_status=RecommendationStatus(rec_data.get("scenario_status", RecommendationStatus.RECONSIDER.value)),
            changed=False,
            summary="Feasibility recommendation remains unchanged.",
        )
    )

    return ScenarioRecordResponse(
        scenario_id=scenario_record.id,
        analysis_id=scenario_record.analysis_id,
        name=scenario_record.name,
        description=scenario_record.description,
        created_at=scenario_record.created_at.isoformat() if scenario_record.created_at else None,
        scenario_inputs=scenario_record.scenario_inputs or {},
        scenario_result=FinancialResultResponse(**scenario_record.scenario_financial_result),
        scenario_status=RecommendationStatus(rec_data.get("scenario_status", RecommendationStatus.RECONSIDER.value)),
        scenario_decision_trace=DecisionTrace(**rec_data["scenario_decision_trace"]) if rec_data.get("scenario_decision_trace") else None,
        risk_factors=[RiskFactor(**r) for r in rec_data.get("risk_factors", [])],
        baseline_result=FinancialResultResponse(**comp_data["baseline_result"]),
        baseline_status=RecommendationStatus(comp_data.get("baseline_status", RecommendationStatus.RECONSIDER.value)),
        baseline_decision_trace=DecisionTrace(**comp_data["baseline_decision_trace"]) if comp_data.get("baseline_decision_trace") else None,
        metric_comparisons=[MetricComparison(**m) for m in comp_data.get("metric_comparisons", [])],
        rule_comparisons=[RuleComparison(**r) for r in comp_data.get("rule_comparisons", [])],
        recommendation_change=rec_change,
        what_changed=comp_data.get("what_changed", []),
        why_it_changed=comp_data.get("why_it_changed", []),
        disclaimer=comp_data.get("disclaimer", "Scenario outputs are decision support simulations based on user-entered assumptions. They do not guarantee financial viability, subsidy eligibility, or loan approval."),
    )
