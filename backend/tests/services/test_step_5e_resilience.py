import pytest
from app.services.financial.calculator import FinancialService
from app.schemas.financial import FinancialAssumptionsInput
from app.rules.feasibility_rules import FeasibilityRules
from app.services.geo.market import MockMarketService
from app.schemas.market import MarketEvidenceQuery
from app.schemas.analysis import RecommendationStatus

def test_step_5e_invariance_guarantees():
    """Verify that Step 5E (Mobile & Network Resilience) leaves all financial engine calculations and feasibility rules 100% untouched."""
    service = FinancialService()
    fin_input = FinancialAssumptionsInput(
        startup_cost=25000,
        equipment_cost=100000,
        inventory_cost=25000,
        monthly_fixed_cost=6000,
        customers_per_day=50,
        avg_ticket_price=30,
        working_days_per_month=26,
        variable_cost_pct=50,
        interest_rate_pct=10.5,
        loan_tenure_months=60,
    )

    res = service.calculate(
        own_capital=30000.0,
        desired_loan=120000.0,
        financials=fin_input
    )

    # Invariant calculations
    assert res.total_capex == 150000.0
    assert res.required_loan_amount == 120000.0
    assert res.monthly_revenue == 39000.0
    assert res.monthly_variable_cost == 19500.0
    assert res.monthly_gross_profit == 19500.0
    assert res.monthly_fixed_cost == 6000.0
    assert res.monthly_emi == 2579.27
    assert res.monthly_net_profit == 10920.73
    assert res.dscr == 5.23
    assert res.break_even_revenue_monthly == 17158.54
    assert res.break_even_units_daily == 22

    # Feasibility rules verification
    market_service = MockMarketService()
    query = MarketEvidenceQuery(
        state="Maharashtra",
        district="Pune",
        village="Baramati",
        category="Bakery & Snacks",
        latitude=18.155,
        longitude=74.578
    )
    market = market_service.get_market_indicators(query)

    status, trace = FeasibilityRules.evaluate_with_trace(
        financials=res,
        market=market
    )

    assert status == RecommendationStatus.PROCEED
    assert trace.recommendation_status == RecommendationStatus.PROCEED
    assert trace.authority == "FeasibilityRules"
