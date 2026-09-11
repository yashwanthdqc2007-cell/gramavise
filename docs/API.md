# API Specifications — GRAMAVISE REST API

Base URL: `http://localhost:8000/api`  
Interactive OpenAPI / Swagger UI: `http://localhost:8000/docs`

---

## 1. Endpoints Overview

| Method | Endpoint | Description | Status |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | System health, database connection, and uptime check | Active Stub |
| `GET` | `/market/evidence` | Fetch hyper-local market indicators & competitor density | Active Stub |
| `GET` | `/schemes` | Fetch and filter government loan & subsidy schemes | Active Stub |
| `POST` | `/analyze` | Run full business feasibility analysis pipeline | Active Stub |
| `POST` | `/financial/calculate` | Compute financial metrics (Revenue, Capex, Break-even, EMI) | Active Stub |
| `POST` | `/financial/sensitivity` | Compute sensitivity matrix under varied demand & price shocks | Active Stub |
| `POST` | `/ai/explain` | Generate vernacular, plain-language advisory explanation | Active Stub |

---

## 2. Request & Response Payloads

### `GET /api/health`
**Response (200 OK):**
```json
{
  "status": "healthy",
  "app_name": "GramaVise Backend",
  "version": "1.0.0",
  "timestamp": "2026-09-11T18:15:00Z",
  "services": {
    "database": "connected",
    "rule_engine": "ready",
    "ai_provider": "mock"
  }
}
```

---

### `POST /api/analyze`
**Request Body:**
```json
{
  "profile": {
    "business_name": "Kishan Flour Mill",
    "category": "Food Processing / Atta Chakki",
    "description": "Small-scale grain milling and packaging unit in Rampur village",
    "location": {
      "state": "Uttar Pradesh",
      "district": "Varanasi",
      "village": "Rampur",
      "latitude": 25.3176,
      "longitude": 82.9739
    },
    "experience_years": 3,
    "own_capital": 50000.0,
    "desired_loan": 150000.0,
    "is_new_business": true
  },
  "financials": {
    "startup_cost": 20000.0,
    "equipment_cost": 120000.0,
    "inventory_cost": 30000.0,
    "monthly_fixed_cost": 8000.0,
    "customers_per_day": 25,
    "avg_ticket_price": 60.0,
    "working_days_per_month": 26,
    "variable_cost_pct": 35.0,
    "interest_rate_pct": 10.5,
    "loan_tenure_months": 36
  },
  "preferred_language": "hi"
}
```

**Response (200 OK):**
```json
{
  "analysis_id": "c1f72e90-0000-4000-8000-000000000001",
  "recommendation_status": "PROCEED",
  "confidence_score": 0.85,
  "financial_result": {
    "total_capex": 170000.0,
    "monthly_revenue": 39000.0,
    "monthly_gross_profit": 25350.0,
    "monthly_net_profit": 12650.0,
    "break_even_revenue_monthly": 12307.69,
    "break_even_units_daily": 8,
    "monthly_emi": 4875.0,
    "dscr": 2.6
  },
  "market_result": {
    "location_summary": "Rampur, Varanasi, Uttar Pradesh",
    "competitor_count": 2,
    "demand_indicator": "HIGH",
    "notes": "Low local mill concentration within 3km radius."
  },
  "scheme_result": {
    "eligible_schemes_count": 2,
    "schemes": [
      {
        "scheme_code": "PMEGP",
        "scheme_name": "Prime Minister Employment Generation Programme",
        "subsidy_eligible_amount": 52500.0,
        "own_contribution_required": 10000.0
      }
    ]
  },
  "risk_factors": [
    {
      "factor": "Raw Material Price Fluctuation",
      "severity": "MEDIUM",
      "mitigation": "Maintain a 1-month buffer stock during harvest season."
    }
  ],
  "evidence_list": [
    {
      "indicator": "Average Daily Milling Demand",
      "value": "25-35 customers",
      "unit": "footfall/day",
      "evidence_type": "OBSERVED",
      "confidence": 0.88,
      "source": "Local Market Benchmark",
      "notes": "Verified from baseline village surveys."
    }
  ],
  "ai_explanation": {
    "language": "hi",
    "summary": "यह व्यवसाय वित्तीय रूप से व्यवहार्य प्रतीत होता है।",
    "actionable_next_steps": [
      "PMEGP पोर्टल पर आवेदन करें",
      "बिजली कनेक्शन की उपलब्धता की जांच करें"
    ]
  }
}
```
