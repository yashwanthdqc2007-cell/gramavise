from app.rules.financial_rules import FinancialRules
from app.rules.scheme_rules import SchemeRules


def test_dscr_rule_evaluation():
    status, msg = FinancialRules.evaluate_dscr(1.8)
    assert status == "STRONG"

    status, msg = FinancialRules.evaluate_dscr(0.8)
    assert status == "DEFICIT"


def test_scheme_rules():
    eligible, subsidy, own = SchemeRules.check_pmegp_eligibility(1000000.0, is_rural=True)
    assert eligible is True
    assert subsidy == 35.0

    eligible, category = SchemeRules.check_mudra_eligibility(45000.0)
    assert eligible is True
    assert category == "MUDRA_SHISHU"
