from typing import Tuple, List, Optional
from app.schemas.financial import FinancialResultResponse

# Benchmark constants
MIN_DSCR_ACCEPTABLE = 1.25
PRIME_DSCR_THRESHOLD = 1.50
MAX_RECOMMENDED_DEBT_SHARE = 0.85  # Max 85% debt financing


class FinancialRules:
    """Deterministic financial integrity and safety rules."""

    @staticmethod
    def evaluate_dscr(dscr: float, monthly_emi: float = 1.0) -> Tuple[str, str]:
        """Evaluate Debt Service Coverage Ratio viability.
        
        Thresholds:
            - EMI == 0 / Debt-Free: DEBT_FREE
            - DSCR >= 1.50: STRONG
            - 1.25 <= DSCR < 1.50: ADEQUATE
            - 1.00 <= DSCR < 1.25: TIGHT
            - DSCR < 1.00: DEFICIT
        """
        if monthly_emi <= 0.0 or dscr >= 999.0:
            return ("DEBT_FREE", "No loan debt obligation; 100% equity financed.")
        if dscr >= PRIME_DSCR_THRESHOLD:
            return ("STRONG", "Healthy operating cash flows comfortably exceed monthly debt servicing.")
        elif dscr >= MIN_DSCR_ACCEPTABLE:
            return ("ADEQUATE", "Meets minimum banking repayment safety thresholds.")
        elif dscr >= 1.0:
            return ("TIGHT", "Marginal cash flows; business vulnerable to minor demand contractions.")
        else:
            return ("DEFICIT", "Operating income insufficient to service projected debt burden.")

    @staticmethod
    def evaluate_capex_structure(total_capex: float, own_capital: float) -> List[str]:
        """Check equity margin money sufficiency."""
        warnings = []
        if total_capex > 0:
            equity_share = own_capital / total_capex
            if equity_share < 0.05:
                warnings.append("Own capital contribution is below 5% (mandatory minimum for most credit schemes).")
        return warnings

