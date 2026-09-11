from app.services.financial.calculator import FinancialService
from app.services.geo.market import MockMarketService
from app.services.schemes.matcher import SchemeService
from app.services.recommendation.feasibility import evaluate_feasibility_status
from app.schemas.business import BusinessProfileBase, LocationSchema
from app.schemas.financial import FinancialAssumptionsInput


def test_full_domain_service_orchestration():
    fin_service = FinancialService()
    market_service = MockMarketService()
    scheme_service = SchemeService()

    location = LocationSchema(state="Rajasthan", district="Jaipur", village="Chomu")
    profile = BusinessProfileBase(
        business_name="Chomu Dairy Unit",
        category="Dairy",
        description="Milk chilling and curd packaging",
        location=location,
        experience_years=4,
        own_capital=50000.0,
        desired_loan=200000.0,
        is_new_business=True
    )
    financials = FinancialAssumptionsInput(
        startup_cost=20000.0,
        equipment_cost=180000.0,
        inventory_cost=50000.0,
        monthly_fixed_cost=10000.0,
        customers_per_day=40,
        avg_ticket_price=75.0,
        working_days_per_month=30,
        variable_cost_pct=50.0,
        interest_rate_pct=9.5,
        loan_tenure_months=48
    )

    fin_result = fin_service.calculate(profile.own_capital, profile.desired_loan, financials)
    market_result = market_service.get_market_indicators(query=None or type("Obj", (), {
        "state": "Rajasthan", "district": "Jaipur", "village": "Chomu",
        "category": "Dairy", "latitude": None, "longitude": None, "radius_km": 5.0
    })())
    scheme_result = scheme_service.match_schemes(profile, fin_result)
    status = evaluate_feasibility_status(fin_result, market_result)

    assert fin_result.monthly_revenue == 90000.0
    assert scheme_result.eligible_schemes_count >= 1
    assert status.value in ["PROCEED", "VALIDATE_FIRST", "RECONSIDER"]
