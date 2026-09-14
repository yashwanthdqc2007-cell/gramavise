from typing import Tuple
from app.schemas.analysis import RecommendationStatus, DecisionTrace
from app.schemas.financial import FinancialResultResponse
from app.schemas.market import MarketResultResponse
from app.rules.feasibility_rules import FeasibilityRules


def evaluate_feasibility_status(financials: FinancialResultResponse, market: MarketResultResponse) -> RecommendationStatus:
    """Evaluate business feasibility verdict by delegating to the authoritative FeasibilityRules engine."""
    return FeasibilityRules.determine_status(financials=financials, market=market)


def evaluate_feasibility_with_trace(
    financials: FinancialResultResponse,
    market: MarketResultResponse
) -> Tuple[RecommendationStatus, DecisionTrace]:
    """Evaluate business feasibility verdict and decision trace by delegating to FeasibilityRules."""
    return FeasibilityRules.evaluate_with_trace(financials=financials, market=market)
