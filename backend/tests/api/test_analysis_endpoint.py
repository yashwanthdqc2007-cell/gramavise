from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _get_valid_payload():
    return {
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


def test_analyze_pipeline_endpoint_success():
    payload = _get_valid_payload()
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert data["recommendation_status"] in ["PROCEED", "VALIDATE_FIRST", "RECONSIDER"]
    assert "financial_result" in data
    assert "market_result" in data
    assert "scheme_result" in data
    assert "evidence_list" in data
    assert "risk_factors" in data
    assert "ai_explanation" in data
    assert data["confidence_score"] > 0.0


def test_analyze_negative_own_capital_422():
    payload = _get_valid_payload()
    payload["profile"]["own_capital"] = -5000.0
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 422


def test_analyze_negative_desired_loan_422():
    payload = _get_valid_payload()
    payload["profile"]["desired_loan"] = -10000.0
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 422


def test_analyze_invalid_financials_422():
    payload = _get_valid_payload()
    payload["financials"]["variable_cost_pct"] = 110.0
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 422

    payload2 = _get_valid_payload()
    payload2["financials"]["customers_per_day"] = 0
    response2 = client.post("/api/analyze", json=payload2)
    assert response2.status_code == 422


def test_analyze_pipeline_determinism():
    payload = _get_valid_payload()
    response1 = client.post("/api/analyze", json=payload)
    response2 = client.post("/api/analyze", json=payload)
    response3 = client.post("/api/analyze", json=payload)

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200

    data1 = response1.json()
    data2 = response2.json()
    data3 = response3.json()

    # Deterministic components must match across invocations
    assert data1["financial_result"] == data2["financial_result"] == data3["financial_result"]
    assert data1["recommendation_status"] == data2["recommendation_status"] == data3["recommendation_status"]
    assert data1["risk_factors"] == data2["risk_factors"] == data3["risk_factors"]
    assert data1["market_result"] == data2["market_result"] == data3["market_result"]
    assert data1["scheme_result"] == data2["scheme_result"] == data3["scheme_result"]
    assert data1["confidence_score"] == data2["confidence_score"] == data3["confidence_score"]


def test_analyze_ai_failure_resilience():
    payload = _get_valid_payload()
    
    # Mock AI explanation failure
    with patch("app.api.routes.analysis.ai_service.explain_analysis", side_effect=RuntimeError("AI Provider Timeout")):
        response = client.post("/api/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["recommendation_status"] in ["PROCEED", "VALIDATE_FIRST", "RECONSIDER"]
        assert data["financial_result"]["monthly_revenue"] == 41600.0
        assert data["ai_explanation"] is not None
        assert "fallback" in data["ai_explanation"]["disclaimer"].lower() or "automated" in data["ai_explanation"]["disclaimer"].lower()

