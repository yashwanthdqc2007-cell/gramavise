from app.schemas.analysis import RecommendationStatus
from app.schemas.financial import FinancialResultResponse
from app.schemas.market import MarketResultResponse


def evaluate_feasibility_status(financials: FinancialResultResponse, market: MarketResultResponse) -> RecommendationStatus:
    """Deterministic feasibility verdict generator based on mathematical safety margins.
    
    RULES:
    1. PROCEED: Net profit > 0, DSCR >= 1.5, daily break-even <= 70% of projected volume.
    2. VALIDATE_FIRST: Net profit > 0, 1.0 <= DSCR < 1.5, or high competitor density.
    3. RECONSIDER: Net profit <= 0 or DSCR < 1.0 (Insolvent/Cash flow negative).
    
    TODO [Rules Lead]: Add sector-specific viability thresholds and custom state rules.
    """
    if financials.monthly_net_profit <= 0 or financials.dscr < 1.0:
        return RecommendationStatus.RECONSIDER
    
    if financials.dscr >= 1.5 and financials.is_financially_viable:
        if market.demand_indicator == "HIGH" or market.competitor_count <= 2:
            return RecommendationStatus.PROCEED
    
    return RecommendationStatus.VALIDATE_FIRST
