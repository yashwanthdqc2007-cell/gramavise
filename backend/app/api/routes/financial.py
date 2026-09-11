from fastapi import APIRouter, HTTPException, status
from app.schemas.financial import (
    FinancialCalculationRequest,
    FinancialResultResponse,
    SensitivityRequest,
    SensitivityResponse
)
from app.services.financial.calculator import FinancialService
from app.services.financial.sensitivity import run_sensitivity_analysis
from app.services.financial.validation import validate_financial_assumptions

router = APIRouter()
financial_service = FinancialService()


@router.post("/financial/calculate", response_model=FinancialResultResponse, summary="Compute Unit Economics & Break-Even")
async def calculate_financials(request: FinancialCalculationRequest):
    """Compute Capex, monthly revenue, gross/net margins, break-even thresholds, and EMI.
    
    TODO [Financial Lead]: Connect to database session to log calculation history if user_id present.
    """
    is_valid, errors = validate_financial_assumptions(request.financials)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": errors}
        )

    result = financial_service.calculate(
        own_capital=request.own_capital,
        desired_loan=request.desired_loan or 0.0,
        financials=request.financials
    )
    return result


@router.post("/financial/sensitivity", response_model=SensitivityResponse, summary="Run Sensitivity Stress Test")
async def calculate_sensitivity(request: SensitivityRequest):
    """Stress test financial projections across price shocks, footfall drop, and cost escalations.
    
    TODO [Financial Lead]: Implement user-customizable shock parameter ranges.
    """
    is_valid, errors = validate_financial_assumptions(request.calculation.financials)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": errors}
        )

    return run_sensitivity_analysis(request.calculation)
