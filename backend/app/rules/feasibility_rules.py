from app.schemas.analysis import RecommendationStatus
from app.schemas.financial import FinancialResultResponse
from app.schemas.market import MarketResultResponse


class FeasibilityRules:
    """Deterministic business feasibility verdict rules."""

    @staticmethod
    def determine_status(financials: FinancialResultResponse, market: MarketResultResponse) -> RecommendationStatus:
        """Evaluate hard decision rules for enterprise viability.
        
        TODO [Rules Lead]: Add industry specific rules (e.g. food vs retail vs transport).
        """
        # Hard fail condition 1: Insolvent or cash flow deficit
        if financials.monthly_net_profit <= 0 or financials.dscr < 1.0:
            return RecommendationStatus.RECONSIDER
        
        # Safe pass condition
        if financials.dscr >= 1.5 and financials.is_financially_viable:
            if market.competitor_count <= 3:
                return RecommendationStatus.PROCEED

        # Boundary condition: Needs validation on ground
        return RecommendationStatus.VALIDATE_FIRST
