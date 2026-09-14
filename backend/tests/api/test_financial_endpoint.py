from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_calculate_financial_endpoint():
    payload = {
        "own_capital": 50000.0,
        "desired_loan": 100000.0,
        "financials": {
            "startup_cost": 20000.0,
            "equipment_cost": 100000.0,
            "inventory_cost": 30000.0,
            "monthly_fixed_cost": 8000.0,
            "customers_per_day": 25,
            "avg_ticket_price": 60.0,
            "working_days_per_month": 26,
            "variable_cost_pct": 35.0,
            "interest_rate_pct": 10.5,
            "loan_tenure_months": 36
        }
    }
    response = client.post("/api/financial/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_capex"] == 150000.0
    assert data["required_loan_amount"] == 100000.0
    assert data["monthly_revenue"] == 39000.0
    assert data["monthly_variable_cost"] == 13650.0
    assert data["monthly_gross_profit"] == 25350.0
    assert data["monthly_fixed_cost"] == 8000.0
    assert data["monthly_emi"] > 0
    assert data["monthly_net_profit"] > 0
    assert data["is_financially_viable"] is True


def test_calculate_financial_endpoint_validation_error():
    payload = {
        "own_capital": -5000.0,
        "desired_loan": 100000.0,
        "financials": {
            "startup_cost": 20000.0,
            "equipment_cost": 100000.0,
            "inventory_cost": 30000.0,
            "monthly_fixed_cost": 8000.0,
            "customers_per_day": 25,
            "avg_ticket_price": 60.0,
            "working_days_per_month": 26,
            "variable_cost_pct": 35.0,
            "interest_rate_pct": 10.5,
            "loan_tenure_months": 36
        }
    }
    response = client.post("/api/financial/calculate", json=payload)
    assert response.status_code == 422


def test_sensitivity_financial_endpoint():
    payload = {
        "calculation": {
            "own_capital": 50000.0,
            "desired_loan": 100000.0,
            "financials": {
                "startup_cost": 20000.0,
                "equipment_cost": 100000.0,
                "inventory_cost": 30000.0,
                "monthly_fixed_cost": 8000.0,
                "customers_per_day": 25,
                "avg_ticket_price": 60.0,
                "working_days_per_month": 26,
                "variable_cost_pct": 35.0,
                "interest_rate_pct": 10.5,
                "loan_tenure_months": 36
            }
        }
    }
    response = client.post("/api/financial/sensitivity", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "baseline" in data
    assert "scenarios" in data
    assert len(data["scenarios"]) == 4
    assert data["resilience_rating"] in ["HIGH", "MODERATE", "LOW"]
