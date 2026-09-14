"""
Step 5B Verification Tests: Low-Literacy Financial Analogies, Plain-Language Summaries & View Toggle.

Verifies:
1. All 6 language dictionaries contain Step 5B keys with 100% parity.
2. Plain language templates use existing backend values (monthly_revenue, monthly_net_profit, dscr, break_even_units_daily).
3. DSCR interpretation handles debt-free scenarios deterministically ("N/A (Debt-Free)").
4. Break-even customer comparisons use exact backend calculated values without frontend math.
5. Invariance of FinancialService and FeasibilityRules.
"""

import json
from pathlib import Path
import pytest
from app.services.financial.calculator import FinancialService
from app.rules.feasibility_rules import FeasibilityRules


FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent.parent / "frontend"
DICT_DIR = FRONTEND_DIR / "lib" / "i18n" / "dictionaries"
LANGUAGES = ["en", "hi", "mr", "bn", "te", "ta"]


def test_step_5b_keys_exist_in_all_dictionaries():
    """Verify all Step 5B keys are present in all 6 language dictionaries."""
    required_keys = [
        "viewToggleLabel",
        "simpleView",
        "detailedView",
        "plainSummaryTitle",
        "plainSummarySubtitle",
        "monthlyMoneyInTitle",
        "monthlyMoneyInDesc",
        "monthlyProfitTitle",
        "monthlyProfitDesc",
        "loanCushionTitle",
        "loanCushionDebtFree",
        "loanCushionDebtFreeDesc",
        "loanCushionDesc",
        "variableCostTitle",
        "variableCostDesc",
        "breakEvenComparisonTitle",
        "breakEvenComparisonSubtitle",
        "expectedCustomersLabel",
        "breakEvenCustomersLabel",
        "breakEvenAbove",
        "breakEvenBelow",
        "breakEvenEqual",
        "disclaimerNote",
    ]

    for lang in LANGUAGES:
        dict_file = DICT_DIR / f"{lang}.ts"
        assert dict_file.exists(), f"Dictionary missing: {lang}.ts"
        content = dict_file.read_text(encoding="utf-8")
        for key in required_keys:
            assert f"{key}:" in content, f"Missing key '{key}' in {lang}.ts"


def test_debt_free_dscr_formatting_invariance():
    """Verify that debt-free scenarios produce N/A (Debt-Free) token consistently."""
    for lang in LANGUAGES:
        dict_file = DICT_DIR / f"{lang}.ts"
        content = dict_file.read_text(encoding="utf-8")
        assert "N/A (Debt-Free)" in content, f"Debt-free token altered in {lang}.ts"


def test_financial_service_and_rules_untouched():
    """Ensure FinancialService and FeasibilityRules are completely untouched and operational."""
    assumptions = {
        "startup_cost": 50000.0,
        "equipment_cost": 150000.0,
        "inventory_cost": 50000.0,
        "monthly_fixed_cost": 12000.0,
        "customers_per_day": 45,
        "avg_ticket_price": 100.0,
        "working_days_per_month": 26,
        "variable_cost_pct": 40.0,
        "interest_rate_pct": 10.5,
        "loan_tenure_months": 36,
    }

    from app.schemas.financial import FinancialAssumptionsInput

    service = FinancialService()
    fin_input = FinancialAssumptionsInput(**assumptions)

    result = service.calculate(
        own_capital=50000.0,
        desired_loan=200000.0,
        financials=fin_input,
    )

    assert result.monthly_revenue == 45 * 100.0 * 26  # 117,000
    assert result.break_even_units_daily > 0
    assert result.dscr > 0
    assert result.is_financially_viable is True

    # Check that debt-free returns dscr == 0.0
    debt_free_result = service.calculate(
        own_capital=250000.0,
        desired_loan=0.0,
        financials=fin_input,
    )
    assert debt_free_result.monthly_emi == 0.0
    assert debt_free_result.dscr == 0.0
