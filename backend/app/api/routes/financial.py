from fastapi import APIRouter, HTTPException, status
from app.schemas.financial import (
    FinancialCalculationRequest,
    FinancialResultResponse,
    SensitivityRequest,
    SensitivityResponse
)
from app.services.financial.calculator import FinancialService
from app.services.financial.sensitivity import run_sensitivity_analysis
from app.services.financial.validation import (
    validate_financial_assumptions,
    validate_capital_inputs
)

router = APIRouter()
financial_service = FinancialService()


@router.post("/financial/calculate", response_model=FinancialResultResponse, summary="Compute Unit Economics & Break-Even")
async def calculate_financials(request: FinancialCalculationRequest):
    """Compute Capex, monthly revenue, gross/net margins, break-even thresholds, and EMI."""
    is_valid_f, errors_f = validate_financial_assumptions(request.financials)
    is_valid_c, errors_c = validate_capital_inputs(request.own_capital, request.desired_loan)
    
    all_errors = errors_f + errors_c
    if all_errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": all_errors}
        )

    result = financial_service.calculate(
        own_capital=request.own_capital,
        desired_loan=request.desired_loan,
        financials=request.financials
    )
    return result


@router.post("/financial/sensitivity", response_model=SensitivityResponse, summary="Run Sensitivity Stress Test")
async def calculate_sensitivity(request: SensitivityRequest):
    """Stress test financial projections across price shocks, footfall drop, and cost escalations."""
    is_valid_f, errors_f = validate_financial_assumptions(request.calculation.financials)
    is_valid_c, errors_c = validate_capital_inputs(request.calculation.own_capital, request.calculation.desired_loan)
    
    all_errors = errors_f + errors_c
    if all_errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": all_errors}
        )

    return run_sensitivity_analysis(request.calculation)

