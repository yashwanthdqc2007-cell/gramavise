from typing import Dict, Any, Tuple


class SchemeRules:
    """Deterministic eligibility rules for government credit and subsidy schemes."""

    @staticmethod
    def check_pmegp_eligibility(project_cost: float, is_rural: bool = True) -> Tuple[bool, float, float]:
        """PMEGP rules: Manufacturing max ₹50L, Service max ₹20L.
        Subsidy: 35% for Special/Rural, 25% General Rural.
        """
        if project_cost > 5000000.0:
            return (False, 0.0, 0.0)
        
        subsidy_pct = 35.0 if is_rural else 25.0
        own_contrib_pct = 5.0 if is_rural else 10.0
        
        return (True, subsidy_pct, own_contrib_pct)

    @staticmethod
    def check_mudra_eligibility(loan_amount: float) -> Tuple[bool, str]:
        """Mudra categories:
        - Shishu: up to ₹50,000
        - Kishore: ₹50,001 to ₹5,00,000
        - Tarun: ₹5,00,001 to ₹10,00,000
        """
        if loan_amount <= 50000:
            return (True, "MUDRA_SHISHU")
        elif loan_amount <= 500000:
            return (True, "MUDRA_KISHORE")
        elif loan_amount <= 1000000:
            return (True, "MUDRA_TARUN")
        else:
            return (False, "EXCEEDS_MUDRA_LIMIT")
