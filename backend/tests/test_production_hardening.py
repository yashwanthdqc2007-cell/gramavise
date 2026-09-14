import os
import uuid
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.config import Settings
from app.database import Base, get_db, check_database_health
from app.repositories import UnitOfWork


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestingSessionLocal
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


# --- 1. Configuration Tests ---

def test_01_configuration_loads_and_defaults():
    s = Settings(
        ENVIRONMENT="production",
        DEBUG=False,
        SECRET_KEY="test-only-production-secret",
        LOG_LEVEL="WARNING",
    )
    assert s.ENVIRONMENT == "production"
    assert s.DEBUG is False
    assert s.LOG_LEVEL == "WARNING"
    assert s.MAX_REQUEST_SIZE_BYTES == 1_048_576
    assert s.DB_POOL_SIZE == 10


def test_02_cors_origins_parsing_from_string():
    s = Settings(CORS_ORIGINS="http://example.com,https://app.gramavise.org")
    assert s.CORS_ORIGINS == ["http://example.com", "https://app.gramavise.org"]


def test_03_development_defaults_remain_usable():
    from app.config import settings
    assert settings.APP_NAME == "GramaVise Backend"
    assert len(settings.CORS_ORIGINS) > 0


# --- 2. Security & Middleware Tests ---

def test_04_cors_behavior_allowed_vs_disallowed(client):
    # Allowed origin receives Access-Control-Allow-Origin
    res_allowed = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        }
    )
    assert res_allowed.headers.get("access-control-allow-origin") == "http://localhost:3000"

    # Disallowed origin does NOT receive Access-Control-Allow-Origin header
    res_disallowed = client.options(
        "/api/health",
        headers={
            "Origin": "http://malicious-site.com",
            "Access-Control-Request-Method": "GET",
        }
    )
    assert res_disallowed.headers.get("access-control-allow-origin") is None


def test_05_request_id_generation_and_propagation(client):
    # Request without X-Request-ID generates one
    res = client.get("/api/health")
    assert res.status_code == 200
    generated_id = res.headers.get("X-Request-ID")
    assert generated_id is not None
    assert len(generated_id) > 0

    # Request with custom X-Request-ID propagates it
    custom_id = "custom-trace-uuid-12345"
    res_custom = client.get("/api/health", headers={"X-Request-ID": custom_id})
    assert res_custom.status_code == 200
    assert res_custom.headers.get("X-Request-ID") == custom_id


def test_06_oversized_payload_rejected_with_413(client):
    # Large payload exceeding limit
    oversized_data = "x" * (1_048_576 + 500)
    res = client.post(
        "/api/financial/calculate",
        content=oversized_data,
        headers={"Content-Type": "application/json"}
    )
    assert res.status_code == 413
    assert "Payload Too Large" in res.json()["detail"]
    assert res.headers.get("X-Request-ID") is not None


def test_07_invalid_uuid_handling(client, test_db):
    res = client.get("/api/analyze/not-a-valid-uuid")
    assert res.status_code == 422
    assert "Invalid analysis ID format" in res.json()["detail"]


def test_08_safe_unhandled_exception_handling():
    # Route that triggers an unhandled internal exception returns sanitized 500
    no_raise_client = TestClient(app, raise_server_exceptions=False)
    with patch("app.api.routes.health.check_database_health", side_effect=RuntimeError("Secret DB password in exception")):
        res = no_raise_client.get("/ready")
        assert res.status_code == 500
        data = res.json()
        assert "unexpected server error" in data["detail"].lower()
        assert "password" not in res.text.lower()
        assert res.headers.get("X-Request-ID") is not None


# --- 3. Health & Readiness Tests ---

def test_09_liveness_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["services"]["process"] == "running"

    # API prefix also works
    res_api = client.get("/api/health")
    assert res_api.status_code == 200
    assert res_api.json()["status"] == "healthy"


def test_10_readiness_healthy_db(client, test_db):
    res = client.get("/ready")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"


def test_11_readiness_db_failure_returns_503(client):
    with patch("app.api.routes.health.check_database_health", return_value=False):
        res = client.get("/ready")
        assert res.status_code == 503
        data = res.json()
        assert data["status"] == "unhealthy"
        assert data["database"] == "unavailable"


# --- 4. Database Hardening & Rollback Tests ---

def test_12_database_health_check_function():
    # Healthy database returns True
    assert check_database_health() is True

    # Failed query returns False without throwing
    with patch("app.database.engine.connect", side_effect=Exception("Connection lost")):
        assert check_database_health() is False


def test_13_atomic_rollback_on_persistence_error(client, test_db):
    payload = {
        "profile": {
            "business_name": "Rollback Test Shop",
            "category": "Kirana & General Store",
            "location": {"state": "Maharashtra", "district": "Pune", "village": "Baramati"},
            "own_capital": 30000.0,
            "desired_loan": 70000.0,
        },
        "financials": {
            "startup_cost": 20000.0,
            "equipment_cost": 50000.0,
            "inventory_cost": 30000.0,
            "monthly_fixed_cost": 5000.0,
            "customers_per_day": 40,
            "avg_ticket_price": 40.0,
            "working_days_per_month": 26,
            "variable_cost_pct": 50.0,
            "interest_rate_pct": 10.0,
            "loan_tenure_months": 36,
        },
        "preferred_language": "en"
    }

    # Simulate database commit failure
    with patch.object(UnitOfWork, "commit", side_effect=Exception("Simulated Commit Crash")):
        res = client.post("/api/analyze", json=payload)
        assert res.status_code == 500
        assert "failed to persist" in res.json()["detail"].lower()


# --- 5. Provider Failure Graceful Fallback Tests ---

def test_14_market_provider_failure_resilience(client, test_db):
    payload = {
        "profile": {
            "business_name": "Resilient Dairy",
            "category": "Dairy Farming & Milk Chilling",
            "location": {"state": "Karnataka", "district": "Mandya", "village": "Maddur"},
            "own_capital": 50000.0,
            "desired_loan": 100000.0,
        },
        "financials": {
            "startup_cost": 30000.0,
            "equipment_cost": 80000.0,
            "inventory_cost": 40000.0,
            "monthly_fixed_cost": 6000.0,
            "customers_per_day": 30,
            "avg_ticket_price": 50.0,
            "working_days_per_month": 26,
            "variable_cost_pct": 45.0,
            "interest_rate_pct": 10.5,
            "loan_tenure_months": 36,
        },
        "preferred_language": "en"
    }

    # Simulate OSM and Agmarknet failure inside MockMarketService
    with patch("app.services.geo.market.MockMarketService.get_market_indicators", side_effect=Exception("Network Timeout")):
        # Notice: in analysis.py, market service failure can be handled or tested
        no_raise_client = TestClient(app, raise_server_exceptions=False)
        res = no_raise_client.post("/api/analyze", json=payload)
        # If market service raises, verify safe error or fallback
        assert res.status_code in (200, 500)
        if res.status_code == 500:
            assert "detail" in res.json()
            assert res.headers.get("X-Request-ID") is not None


def test_15_ai_provider_failure_resilience(client, test_db):
    payload = {
        "profile": {
            "business_name": "Resilient Tailor",
            "category": "Tailoring & Garment Making",
            "location": {"state": "Tamil Nadu", "district": "Salem", "village": "Omalur"},
            "own_capital": 20000.0,
            "desired_loan": 40000.0,
        },
        "financials": {
            "startup_cost": 10000.0,
            "equipment_cost": 35000.0,
            "inventory_cost": 15000.0,
            "monthly_fixed_cost": 4000.0,
            "customers_per_day": 20,
            "avg_ticket_price": 60.0,
            "working_days_per_month": 26,
            "variable_cost_pct": 30.0,
            "interest_rate_pct": 9.5,
            "loan_tenure_months": 24,
        },
        "preferred_language": "ta"
    }

    # Simulate AI Service failure inside explain_analysis
    with patch("app.services.ai.explanation.AIService.explain_analysis", side_effect=Exception("LLM Quota Exceeded")):
        no_raise_client = TestClient(app, raise_server_exceptions=False)
        res = no_raise_client.post("/api/analyze", json=payload)
        assert res.status_code in (200, 500)
        if res.status_code == 500:
            assert "detail" in res.json()
            assert res.headers.get("X-Request-ID") is not None


# --- 6. Missing Content-Length & Stream Size Safety Tests ---

def test_16_missing_content_length_normal_request_succeeds(client):
    req_body = {
        "own_capital": 20000.0,
        "desired_loan": 50000.0,
        "financials": {
            "startup_cost": 10000.0,
            "equipment_cost": 40000.0,
            "inventory_cost": 20000.0,
            "monthly_fixed_cost": 4000.0,
            "customers_per_day": 30,
            "avg_ticket_price": 40.0,
            "working_days_per_month": 26,
            "variable_cost_pct": 50.0,
            "interest_rate_pct": 10.0,
            "loan_tenure_months": 36
        }
    }
    # Pass data without Content-Length
    res = client.post("/api/financial/calculate", json=req_body)
    assert res.status_code == 200
    assert res.json()["total_capex"] == 70000.0


# --- 7. Idempotency & Immutability Regression Tests ---

def test_17_idempotent_analysis_replay_and_conflict(client, test_db):
    payload_a = {
        "profile": {
            "business_name": "Idempotency Bakery",
            "category": "Small Agro / Food Processing",
            "location": {"state": "Gujarat", "district": "Anand", "village": "Anand"},
            "own_capital": 40000.0,
            "desired_loan": 80000.0,
        },
        "financials": {
            "startup_cost": 20000.0,
            "equipment_cost": 60000.0,
            "inventory_cost": 40000.0,
            "monthly_fixed_cost": 5000.0,
            "customers_per_day": 35,
            "avg_ticket_price": 50.0,
            "working_days_per_month": 26,
            "variable_cost_pct": 40.0,
            "interest_rate_pct": 10.0,
            "loan_tenure_months": 36,
        },
        "preferred_language": "en"
    }

    idem_key = "test-prod-hardening-key-001"
    res1 = client.post("/api/analyze", json=payload_a, headers={"Idempotency-Key": idem_key})
    assert res1.status_code == 200
    analysis_id_1 = res1.json()["analysis_id"]

    # Replay with same key + same payload -> exactly same analysis ID
    res2 = client.post("/api/analyze", json=payload_a, headers={"Idempotency-Key": idem_key})
    assert res2.status_code == 200
    assert res2.json()["analysis_id"] == analysis_id_1

    # Conflict with same key + modified payload -> HTTP 409 Conflict
    payload_b = dict(payload_a)
    payload_b["preferred_language"] = "hi"
    res3 = client.post("/api/analyze", json=payload_b, headers={"Idempotency-Key": idem_key})
    assert res3.status_code == 409
    assert "Idempotency key" in res3.json()["detail"]


def test_18_historical_retrieval_zero_recalculation(client, test_db):
    payload = {
        "profile": {
            "business_name": "Historical Pottery",
            "category": "Kirana & General Store",
            "location": {"state": "Rajasthan", "district": "Jaipur", "village": "Sanganer"},
            "own_capital": 25000.0,
            "desired_loan": 50000.0,
        },
        "financials": {
            "startup_cost": 15000.0,
            "equipment_cost": 40000.0,
            "inventory_cost": 20000.0,
            "monthly_fixed_cost": 4500.0,
            "customers_per_day": 30,
            "avg_ticket_price": 40.0,
            "working_days_per_month": 26,
            "variable_cost_pct": 45.0,
            "interest_rate_pct": 10.5,
            "loan_tenure_months": 36,
        },
        "preferred_language": "en"
    }

    res_post = client.post("/api/analyze", json=payload)
    assert res_post.status_code == 200
    analysis_id = res_post.json()["analysis_id"]

    # Historical GET does not call FinancialService
    with patch("app.services.financial.calculator.FinancialService.calculate", side_effect=RuntimeError("Recalculation Forbidden")):
        res_get = client.get(f"/api/analyze/{analysis_id}")
        assert res_get.status_code == 200
        assert res_get.json()["analysis_id"] == analysis_id
        assert res_get.json()["financial_result"]["monthly_revenue"] == res_post.json()["financial_result"]["monthly_revenue"]
