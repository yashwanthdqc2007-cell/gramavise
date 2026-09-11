from typing import List
from app.schemas.analysis import RiskFactor
from app.schemas.financial import FinancialResultResponse
from app.schemas.market import MarketResultResponse


def assess_business_risks(financials: FinancialResultResponse, market: MarketResultResponse) -> List[RiskFactor]:
    """Identify key vulnerability triggers from financial and geospatial models.
    
    TODO [Rules Lead]: Integrate dynamic risk matrix based on raw material volatility and seasonality.
    """
    risks: List[RiskFactor] = []

    # 1. Debt Service Risk
    if financials.dscr < 1.5:
        risks.append(RiskFactor(
            factor="Tight Loan Repayment Cushion",
            severity="HIGH" if financials.dscr < 1.1 else "MEDIUM",
            mitigation="Consider increasing own equity contribution or extending loan tenure to reduce monthly EMI."
        ))

    # 2. Break-Even Pressure
    if financials.break_even_units_daily > 20:
        risks.append(RiskFactor(
            factor="High Daily Volume Break-Even Target",
            severity="MEDIUM",
            mitigation="Explore offering value-added services or bulk institutional tie-ups to ensure steady minimum orders."
        ))

    # 3. Market Density Risk
    if market.competitor_count >= 3:
        risks.append(RiskFactor(
            factor="Competitive Pressure in Catchment Area",
            severity="MEDIUM",
            mitigation="Differentiate on quality, home delivery, or competitive credit terms for trusted repeat customers."
        ))

    return risks
