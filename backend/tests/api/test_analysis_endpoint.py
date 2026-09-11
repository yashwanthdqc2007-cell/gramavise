from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_analyze_pipeline_endpoint():
    payload = {
        "profile": {
            "business_name": "Gramin Agro Processing",
            "category": "Food Processing",
            "description": "Small pulse grading unit",
            "location": {
                "state": "Madhya Pradesh",
                "district": "Ujjain",
                "village": "Nagda"
            },
            "experience_years": 2,
            "own_capital": 30000.0,
            "desired_loan": 120000.0,
            "is_new_business": True
        },
        "financials": {
            "startup_cost": 15000.0,
            "equipment_cost": 100000.0,
            "inventory_cost": 35000.0,
            "monthly_fixed_cost": 6000.0,
            "customers_per_day": 20,
            "avg_ticket_price": 80.0,
            "working_days_per_month": 26,
            "variable_cost_pct": 35.0,
            "interest_rate_pct": 10.5,
            "loan_tenure_months": 36
        },
        "preferred_language": "hi"
    }

    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommendation_status" in data
    assert "financial_result" in data
    assert "market_result" in data
    assert "scheme_result" in data
    assert "evidence_list" in data
    assert "ai_explanation" in data
