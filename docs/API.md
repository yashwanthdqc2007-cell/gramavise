# API Specifications — GRAMAVISE REST API

Base URL: `http://localhost:8000/api`  
Interactive OpenAPI / Swagger UI: `http://localhost:8000/docs`

---

## 1. Endpoints Overview

| Method | Endpoint | Description | Implementation Status |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | System health, database connection, and uptime check | Active |
| `POST` | `/financial/calculate` | Compute financial metrics (Capex, Revenue, Profit, Break-even, EMI, DSCR) | **Deterministic Engine** |
| `POST` | `/financial/sensitivity` | Compute sensitivity matrix under demand, price, and cost shocks | **Deterministic Engine** |
| `POST` | `/analyze` | Run full business feasibility analysis pipeline & persist immutable snapshot | **Active (Phase 6D)** |
| `GET` | `/analyze/{analysis_id}` | Retrieve stored historical immutable analysis snapshot (read-only) | **Active (Phase 6D)** |
| `POST` | `/analyze/scenario` | Run Scenario Lab: stateless on-the-fly preview calculation | **Scenario Lab (Step 4J)** |
| `POST` | `/analyze/{analysis_id}/scenarios` | Persist a new Scenario Record atomically against parent baseline (max 3) | **Active (Phase 6E)** |
| `GET` | `/analyze/{analysis_id}/scenarios` | List saved scenarios for an analysis (read-only, no recalculation) | **Active (Phase 6E)** |
| `GET` | `/analyze/{analysis_id}/scenarios/{scenario_id}` | Retrieve single saved scenario with parent verification (read-only) | **Active (Phase 6E)** |
| `GET` | `/market/evidence` | Fetch hyper-local market indicators & competitor density | Verified OSM/Udyam/Agmarknet |
| `GET` | `/schemes` | List active government schemes and their current active versions | **Active (Phase 6F)** |
| `GET` | `/schemes/{scheme_code}` | Fetch active scheme definition by statutory code (e.g. PMEGP) | **Active (Phase 6F)** |
| `GET` | `/schemes/{scheme_code}/versions` | Fetch immutable historical version history for a scheme | **Active (Phase 6F)** |
| `POST` | `/ai/explain` | Generate vernacular, plain-language advisory explanation | AI Explainer (Mock/LLM) |


---

## 2. Request & Response Payloads

### `POST /api/analyze`
Executes the composite business analysis pipeline. The pipeline components operate under strict separation:
- **Financial Result**: 100% Deterministic mathematical computations (Revenue, Margins, EMI, DSCR, Break-Even)
- **Market Result**: Real OpenStreetMap POIs (OBSERVED), Agmarknet mandi prices (OBSERVED), Census 2011 (OBSERVED), LGD hierarchy (OBSERVED), and Udyam district MSME context (OBSERVED)
- **Scheme Result**: Verified statutory scheme eligibility matching (PMEGP / MUDRA / PMFME)
- **Feasibility Verdict**: Authoritative rule engine (`FeasibilityRules`)
- **Risk Assessment**: Deterministic financial & operational risk checks
- **Evidence List**: Traceable evidence records with provenance (`CALCULATED`, `OBSERVED`, `MODELLED`, `ASSUMED`, `NEEDS_VERIFICATION`)
- **AI Explanation**: Plain-language vernacular translation with resilient fallback

**Request Body:**
```json
{
  "profile": {
    "business_name": "Sai Krupa Flour Mill",
    "category": "Flour & Spice Milling (Atta Chakki)",
    "description": "Small flour mill and spice grinding unit",
    "location": {
      "state": "Maharashtra",
      "district": "Pune",
      "village": "Baramati",
      "latitude": 18.1550,
      "longitude": 74.5780
    },
    "experience_years": 2,
    "own_capital": 40000.0,
    "desired_loan": 110000.0,
    "is_new_business": true
  },
  "financials": {
    "startup_cost": 25000.0,
    "equipment_cost": 100000.0,
    "inventory_cost": 25000.0,
    "monthly_fixed_cost": 6000.0,
    "customers_per_day": 50,
    "avg_ticket_price": 30.0,
    "working_days_per_month": 26,
    "variable_cost_pct": 50.0,
    "interest_rate_pct": 10.0,
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
  "confidence_score": 0.9,
  "financial_result": {
    "total_capex": 150000.0,
    "required_loan_amount": 110000.0,
    "monthly_revenue": 39000.0,
    "monthly_variable_cost": 19500.0,
    "monthly_gross_profit": 19500.0,
    "monthly_fixed_cost": 6000.0,
    "monthly_emi": 3549.46,
    "monthly_net_profit": 9950.54,
    "net_profit_margin_pct": 25.51,
    "break_even_revenue_monthly": 19098.92,
    "break_even_units_daily": 25,
    "dscr": 3.8,
    "is_financially_viable": true
  },
  "market_result": {
    "location_summary": "Baramati, Pune, Maharashtra",
    "competitor_count": 1,
    "direct_competitor_count": 1,
    "adjacent_competitor_count": 0,
    "catchment_radius_km": 5.0,
    "coverage_confidence": "MEDIUM",
    "coverage_warning": "Competition is based on mapped OpenStreetMap locations within the configured catchment (5 km). Rural and informal businesses may be missing.",
    "competitor_list": [
      {
        "name": "Baramati Flour Mill & Atta Chakki",
        "distance_km": 0.54,
        "category": "flour_mill",
        "relationship": "DIRECT"
      }
    ],
    "competitors": [
      {
        "competitor_id": "OSM-N-4581290125",
        "business_name": "Baramati Flour Mill & Atta Chakki",
        "category": "Flour & Spice Milling (Atta Chakki)",
        "subcategory": "flour_mill",
        "distance_km": 0.54,
        "latitude": 18.1510,
        "longitude": 74.5750,
        "osm_object_id": "node/4581290125",
        "osm_object_type": "node",
        "tags": {
          "craft": "flour_mill",
          "shop": "general"
        },
        "relationship": "DIRECT",
        "match_reason": "Matched because craft=flour_mill (DIRECT)",
        "evidence_type": "OBSERVED",
        "confidence": 1.0,
        "source": "OpenStreetMap",
        "source_type": "OPEN_GEODATA",
        "source_url": "https://www.openstreetmap.org/node/4581290125",
        "observed_at": "2024-09-10T08:30:00Z",
        "verification_status": "VERIFIED_SOURCE"
      }
    ],
    "demand_indicator": "HIGH",
    "catchment_population_estimate": 4500,
    "geography": {
      "state_name": "Maharashtra",
      "district_name": "Pune",
      "village_name": "Baramati",
      "state_lgd_code": "27",
      "district_lgd_code": "492",
      "verification_status": "VERIFIED_SOURCE",
      "source": "Ministry of Panchayati Raj / Local Government Directory (LGD)",
      "source_url": "https://lgdirectory.gov.in/"
    },
    "udyam_context": {
      "state_name": "Maharashtra",
      "district_name": "Pune",
      "lgd_district_code": "492",
      "registered_msme_count": 312450,
      "micro_count": 298120,
      "small_count": 13210,
      "medium_count": 1120,
      "manufacturing_count": 89400,
      "services_count": 223050,
      "geography_level": "DISTRICT",
      "evidence_type": "OBSERVED",
      "confidence": 1.0,
      "source": "Ministry of Micro, Small and Medium Enterprises, Government of India",
      "source_url": "https://udyamregistration.gov.in/",
      "dataset_name": "Udyam Registration District-wise MSME Aggregates",
      "verification_status": "VERIFIED_SOURCE",
      "notes": "District-level formal MSME context only; not a count of nearby competitors."
    }
  },
  "scheme_result": {
    "eligible_schemes_count": 2,
    "schemes": [
      {
        "scheme_code": "PMEGP",
        "scheme_name": "Prime Minister's Employment Generation Programme",
        "subsidy_eligible_amount": 52500.0,
        "own_contribution_required": 7500.0,
        "max_bank_loan": 90000.0,
        "eligibility_status": "PARTIALLY_ELIGIBLE",
        "reasons": [
          "Micro enterprise project cost (₹1.5L) is within PMEGP statutory limits",
          "Special category rural subsidy (35%) potentially applicable upon caste/category certificate verification"
        ],
        "conditions_to_verify": [
          "Social category documentary proof (SC/ST/OBC/Women/Minority)",
          "Rural residency certificate from Gram Panchayat"
        ],
        "portal_url": "https://www.pmegp.msme.gov.in/"
      }
    ],
    "total_potential_subsidy": 52500.0
  },
  "action_plan": {
    "recommendation_status": "PROCEED",
    "total_actions": 3,
    "critical_actions_count": 0,
    "actions": [
      {
        "action_id": "ACT-CAP-001",
        "title": "Confirm Final Financing Structure",
        "description": "Review capex requirements: Total Project Outlay ₹150,000.00, Promoter Contribution ₹40,000.00, Required Bank Borrowing ₹110,000.00.",
        "priority": "HIGH",
        "category": "FINANCIAL",
        "status": "RECOMMENDED",
        "action_source": "FINANCIAL_RESULT",
        "reason": "Modelled business case is financially feasible; finalize equity contribution and borrowing request.",
        "related_evidence_ids": ["EV-FIN-SURPLUS"],
        "related_rule_ids": ["FINANCIAL_VIABILITY"],
        "estimated_effort": "1 day",
        "verification_required": false,
        "completion_effect": "Prepares exact capital numbers for lender application discussion."
      }
    ]
  },
  "document_readiness": {
    "required_count": 0,
    "verified_count": 0,
    "pending_count": 2,
    "documents": [
      {
        "document_id": "DOC-PMEGP-1",
        "name": "PMEGP Prerequisite: Social category documentary proof (SC/ST/OBC/Women/Minority)",
        "purpose": "Documentary verification required for Prime Minister's Employment Generation Programme sanction and subsidy disbursement.",
        "status": "VERIFY",
        "required_for": "Prime Minister's Employment Generation Programme",
        "source": "Official Scheme Guidelines",
        "verification_status": "NEEDS_VERIFICATION"
      }
    ]
  },
  "bank_readiness": {
    "overall_status": "READY",
    "summary": "Business case and unit economics are well-structured for initial lender exploration. Address remaining documentation items.",
    "categories": [
      {
        "category": "FINANCIAL_CASE",
        "title": "Financial Viability & Debt Coverage",
        "status": "READY",
        "reason": "Viable unit economics: Positive monthly net profit (₹9,950.54) and strong debt coverage (DSCR 3.80x >= 1.50x).",
        "supporting_evidence_ids": ["EV-FIN-SURPLUS", "EV-FIN-BREAKEVEN"]
      }
    ],
    "top_actions": [
      "Confirm Final Financing Structure",
      "Verify Matched Scheme Prerequisites",
      "Review Repayment Cushion Under Stress"
    ],
    "disclaimer": "This readiness assessment evaluates information completeness and mathematical feasibility for lender discussions. It is NOT a credit score, loan approval guarantee, or probability of success."
  },
  "overall_verdict": "PROCEED",
  "risk_factors": [],
  "evidence_list": []
}
```

---

### `GET /api/analyze/{analysis_id}`
Retrieves a previously computed, immutable historical analysis snapshot by its unique UUID.
* **Pure Read-Only**: Does **not** recalculate financial metrics, does **not** call live external providers (OSM, Udyam, Census, Mandi), does **not** re-run recommendation rules, and does **not** invoke AI explanations.
* Returns exact historical outputs as computed at analysis creation time.
* If the ID is not found, returns `HTTP 404 Not Found`.
* If the ID format is invalid, returns `HTTP 422 Unprocessable Entity`.

**URL Parameters:**
* `analysis_id` (string, required): UUID identifier of the persisted analysis.

**Response (200 OK):**
Returns the identical `AnalysisResultResponse` payload generated at evaluation time (see `POST /api/analyze` response structure above).

---

### `POST /api/analyze/scenario`
Executes Step 4J Scenario Lab analysis. Re-evaluates overridden financial parameters through the deterministic `FinancialService` and `FeasibilityRules` while preserving the exact baseline market evidence and provenance invariants.

**Request Body:**
```json
{
  "baseline_analysis_id": "c1f72e90-0000-4000-8000-000000000001",
  "scenario_name": "Scenario 1 — Higher Borrowing & Conservative Demand",
  "baseline_profile": {
    "business_name": "Sai Krupa Flour Mill",
    "category": "Flour & Spice Milling (Atta Chakki)",
    "description": "Small flour mill and spice grinding unit",
    "location": {
      "state": "Maharashtra",
      "district": "Pune",
      "village": "Baramati",
      "latitude": 18.1550,
      "longitude": 74.5780
    },
    "experience_years": 2,
    "own_capital": 40000.0,
    "desired_loan": 110000.0,
    "is_new_business": true
  },
  "baseline_financials": {
    "startup_cost": 25000.0,
    "equipment_cost": 100000.0,
    "inventory_cost": 25000.0,
    "monthly_fixed_cost": 6000.0,
    "customers_per_day": 50,
    "avg_ticket_price": 30.0,
    "working_days_per_month": 26,
    "variable_cost_pct": 50.0,
    "interest_rate_pct": 10.0,
    "loan_tenure_months": 36
  },
  "overrides": {
    "desired_loan": 130000.0,
    "customers_per_day": 40
  },
  "market_context": {
    "competitor_count": 1,
    "district": "Pune",
    "state": "Maharashtra",
    "village": "Baramati"
  }
}
```

**Response (200 OK):**
```json
{
  "scenario_id": "scen-c1f72e90-1",
  "scenario_name": "Scenario 1 — Higher Borrowing & Conservative Demand",
  "baseline_analysis_id": "c1f72e90-0000-4000-8000-000000000001",
  "applied_overrides": {
    "desired_loan": 130000.0,
    "customers_per_day": 40
  },
  "scenario_financials": {
    "startup_cost": 25000.0,
    "equipment_cost": 100000.0,
    "inventory_cost": 25000.0,
    "monthly_fixed_cost": 6000.0,
    "customers_per_day": 40,
    "avg_ticket_price": 30.0,
    "working_days_per_month": 26,
    "variable_cost_pct": 50.0,
    "interest_rate_pct": 10.0,
    "loan_tenure_months": 36
  },
  "scenario_financial_result": {
    "total_capex": 150000.0,
    "required_loan_amount": 130000.0,
    "monthly_revenue": 31200.0,
    "monthly_variable_cost": 15600.0,
    "monthly_gross_profit": 15600.0,
    "monthly_fixed_cost": 6000.0,
    "monthly_emi": 4194.82,
    "monthly_net_profit": 5405.18,
    "net_profit_margin_pct": 17.32,
    "break_even_revenue_monthly": 20389.64,
    "break_even_units_daily": 27,
    "dscr": 2.29,
    "is_financially_viable": true
  },
  "scenario_recommendation": {
    "status": "PROCEED",
    "confidence_score": 0.9,
    "rule_evaluations": []
  },
  "comparisons": [
    {
      "metric_key": "monthly_revenue",
      "display_name": "Monthly Revenue",
      "baseline_value": 39000.0,
      "scenario_value": 31200.0,
      "absolute_change": -7800.0,
      "percentage_change": -20.0,
      "unit": "₹",
      "direction": "WORSE",
      "provenance": "CALCULATED"
    },
    {
      "metric_key": "monthly_emi",
      "display_name": "Monthly EMI",
      "baseline_value": 3549.46,
      "scenario_value": 4194.82,
      "absolute_change": 645.36,
      "percentage_change": 18.18,
      "unit": "₹",
      "direction": "WORSE",
      "provenance": "CALCULATED"
    },
    {
      "metric_key": "dscr",
      "display_name": "Debt Service Coverage Ratio (DSCR)",
      "baseline_value": 3.80,
      "scenario_value": 2.29,
      "absolute_change": -1.51,
      "percentage_change": -39.74,
      "unit": "x",
      "direction": "WORSE",
      "provenance": "CALCULATED"
    }
  ],
  "rule_comparisons": [],
  "recommendation_change": {
    "baseline_status": "PROCEED",
    "scenario_status": "PROCEED",
    "has_changed": false,
    "changed_rules": [],
    "summary": "Feasibility recommendation remains PROCEED."
  },
  "what_changed": [
    "Desired Loan: ₹110,000.00 → ₹130,000.00 (Assumed)",
    "Customers Per Day: 50.00 → 40.00 (Assumed)"
  ],
  "why_did_it_change": [
    "Monthly Revenue decreased by 20.00% (₹39,000.00 → ₹31,200.00) due to overridden demand / pricing assumptions.",
    "Monthly EMI increased by 18.18% (₹3,549.46 → ₹4,194.82) due to higher loan borrowing.",
    "Debt Service Coverage Ratio (DSCR) worsened from 3.80x to 2.29x but remains above the 1.50x safe threshold."
  ],
  "disclaimer": "Scenario projections are mathematical simulations based on user-assumed overrides and do not guarantee future commercial outcomes, lender approval, or loan sanction."
}
```

---

### `POST /api/analyze/{analysis_id}/scenarios`
Persists a new `ScenarioRecord` evaluated against the specified immutable parent baseline `Analysis`.

**Invariants:**
- **Parent Verification**: Parent Analysis must exist (returns 404 if not found).
- **Max 3 Scenarios**: Enforced at the persistence layer. Returns HTTP 409 Conflict if attempting to save a 4th scenario.
- **Baseline Immutability**: The parent Analysis record and its snapshots remain 100% unchanged.
- **Deterministic Evaluation**: Reuses existing `ScenarioComparator`, `FinancialService`, and `FeasibilityRules`.

**Request Body (`CreateScenarioRequest`):**
```json
{
  "name": "Increased Customer Volume",
  "description": "Evaluate impact of expanding marketing to gain 60 customers/day",
  "scenario_own_capital": 50000.0,
  "scenario_desired_loan": 100000.0,
  "scenario_financials": {
    "startup_cost": 25000.0,
    "equipment_cost": 100000.0,
    "inventory_cost": 25000.0,
    "monthly_fixed_cost": 7000.0,
    "customers_per_day": 60,
    "avg_ticket_price": 35.0,
    "working_days_per_month": 26,
    "variable_cost_pct": 48.0,
    "interest_rate_pct": 10.0,
    "loan_tenure_months": 36
  }
}
```

**Response (201 Created — `ScenarioRecordResponse`):**
Returns the persisted scenario record with `scenario_id`, `analysis_id`, `created_at`, `scenario_inputs`, `scenario_result`, `scenario_status`, `baseline_result`, `baseline_status`, `metric_comparisons`, `rule_comparisons`, `recommendation_change`, `what_changed`, `why_it_changed`, `risk_factors`, and `disclaimer`.

---

### `GET /api/analyze/{analysis_id}/scenarios`
Lists all saved scenarios for the specified parent baseline `Analysis` in chronological order of creation.

**Characteristics:**
- **Pure Read-Only**: Stored snapshots are mapped directly to `List[ScenarioRecordResponse]`. Zero recalculation and zero external provider calls.
- **Parent Verification**: Returns 404 if parent `analysis_id` does not exist.

---

### `GET /api/analyze/{analysis_id}/scenarios/{scenario_id}`
Retrieves a single saved scenario record ensuring parent analysis ownership (`scenario.analysis_id == analysis_id`).

**Characteristics:**
- **Pure Read-Only**: Stored snapshots are mapped directly to `ScenarioRecordResponse`. Zero recalculation.
- **Parent Isolation**: Returns 404 if the scenario belongs to a different analysis or does not exist.

---

## 3. Scheme Catalog & Version History API (Phase 6F)

### `GET /api/schemes`
Retrieves master government credit and subsidy schemes and their current active version definitions.

**Query Parameters:**
- `category` (optional): Filter schemes by business sector (e.g. `MANUFACTURING`, `FOOD_PROCESSING`, `TRADING`, `SERVICES`).

**Response (200 OK — `List[SchemeCatalogItem]`):**
```json
[
  {
    "id": "e91b4a3a-d68f-43b9-a359-000000000001",
    "scheme_code": "PMEGP",
    "scheme_name": "Prime Minister's Employment Generation Programme",
    "ministry": "Ministry of Micro, Small and Medium Enterprises (MSME)",
    "department": "KVIC / MSME",
    "description": "Credit-linked subsidy programme to generate continuous and sustainable employment opportunities in rural and urban areas through setting up of new micro-enterprises.",
    "active_version": {
      "id": "b188c03e-8f5b-4395-8a8b-000000000001",
      "scheme_code": "PMEGP",
      "version": "2024.1",
      "status": "ACTIVE",
      "description": "Credit-linked subsidy programme...",
      "official_source_name": "KVIC PMEGP Official Portal & Operational Guidelines, Ministry of MSME",
      "official_portal_url": "https://www.pmegp.msme.gov.in/",
      "source_publication_date": "2024-09",
      "effective_from": "2024-09-01T00:00:00",
      "effective_to": null,
      "retrieved_at": "2026-09-12T17:47:52",
      "max_loan_amount": 5000000.0,
      "subsidy_percentage_general": 25.0,
      "subsidy_percentage_special": 35.0,
      "beneficiary_contribution_general_pct": 10.0,
      "beneficiary_contribution_special_pct": 5.0,
      "interest_subvention_pct": 0.0,
      "eligibility_criteria": {
        "eligible_business_types": ["MANUFACTURING", "SERVICES", "BUSINESS"],
        "eligible_enterprise_types": ["MICRO"],
        "new_or_existing": "NEW",
        "minimum_age": 18,
        "maximum_project_cost": {
          "MANUFACTURING": 5000000.0,
          "SERVICES": 2000000.0
        }
      },
      "required_documents": [
        "Applicant social category certificate (for 35% Special category subsidy rate).",
        "8th standard pass certificate if project cost exceeds ₹10L (Mfg) / ₹5L (Services).",
        "Rural area certificate issued by Gram Panchayat / Block Development Officer."
      ],
      "verification_notes": [
        "Educational qualification: At least 8th standard pass for project costs above ₹10 Lakh in manufacturing and above ₹5 Lakh in services.",
        "Applicant category (General vs Special) must be verified via official certificate for 35% margin money rate.",
        "First assistance is strictly for new enterprise establishment (Greenfield)."
      ],
      "metadata_payload": {},
      "created_at": "2026-09-12T17:47:52"
    },
    "total_versions": 1,
    "created_at": "2026-09-12T17:47:52"
  }
]
```

---

### `GET /api/schemes/{scheme_code}`
Retrieves active catalog entry and detailed statutory definitions for a specific scheme code (e.g. `PMEGP`, `PMMY`, `PMFME`).

**Response (200 OK — `SchemeCatalogItem`):**
Returns master scheme metadata and currently `ACTIVE` version details. Returns `404 Not Found` if the scheme code is not recognized.

---

### `GET /api/schemes/{scheme_code}/versions`
Retrieves the complete immutable historical version registry for a scheme code (ordered chronologically descending).

**Response (200 OK — `List[SchemeVersionResponse]`):**
Returns all published versions (`ACTIVE`, `SUPERSEDED`, `RETIRED`, `DRAFT`) with full source provenance, timestamps, subsidy rates, and statutory conditions.

---

## 4. Idempotency & Duplicate Request Protection (Phase 6G)

State-modifying endpoints support the standard `Idempotency-Key` HTTP header:

- `POST /api/analyze`
- `POST /api/analyze/{analysis_id}/scenarios`

### Header Specification
```http
Idempotency-Key: <unique-uuid-or-client-generated-string>
```

### Behavior & Status Codes
1. **First Request**: The operation executes normally, persists the result, and stores the idempotency record. Returns `200 OK` (or `201 Created`).
2. **Replayed Request (Identical Payload)**: Returns the stored response immediately with identical payload. Zero recalculation or external provider calls occur.
3. **Conflicting Request (Different Payload under same Key & Scope)**: Returns `409 Conflict` with error details:
   ```json
   {
     "detail": "Idempotency key '...' has already been used with a different request payload."
   }
   ```
4. **Scope Isolation**: An idempotency key is scoped to the specific endpoint path and method. Reusing a key across `/analyze` and `/analyze/{id}/scenarios` operates in independent namespaces.
5. **No Header Provided**: If `Idempotency-Key` is omitted, the endpoint processes normally without persistence-backed idempotency tracking.

---

## 5. Analysis History & Historical UX (Phase 6H)

### 5.1 Anonymous History Model
GramaVise operates on an anonymous-first architecture with no authentication, user accounts, passwords, or tokens.
- **Client-Side Index**: The browser maintains a minimal metadata index in `localStorage` under key `gramavise_history_v1`.
- **Bounded Storage**: The index is capped at a maximum of `MAX_HISTORY_ENTRIES = 20`. Oldest entries are purged on overflow (FIFO).
- **Stored Fields**: Minimal metadata only (`analysis_id`, `business_name`, `business_category`, `recommendation_status`, `created_at`, `last_opened_at`). No financial results, evidence ledgers, AI explanations, or sensitive data are stored in `localStorage`.

### 5.2 Historical Analysis Retrieval (`GET /api/analyze/{analysis_id}`)
When opening a previous analysis or accessing via direct deep link (`/history/{analysis_id}`):
1. The backend retrieves the persisted immutable snapshot from PostgreSQL/SQLite.
2. **Strict Invariants**:
   - Zero recalculation: `FinancialService` is NEVER invoked.
   - Zero live market calls: `MockMarketService` / OSM / Agmarknet are NEVER called.
   - Zero scheme catalog refresh: `SchemeService` is NEVER called.
   - Zero AI re-generation: `AIService` is NEVER called.
3. The response contains the exact point-in-time state, including original financial input/result snapshots, evidence ledger, scheme match version, action plan, and decision trace.

### 5.3 Direct URL / Deep Linking
- Any valid analysis UUID can be accessed directly at `/history/[analysis_id]`.
- Direct access does not require the analysis to already exist in local history.
- If the UUID does not exist on the backend, a clean `404` error state is displayed with an option to remove any stale local pointer.

### 5.4 Starting Point vs Immutability
- **Historical Analysis**: Purely read-only. Original assumptions and verdicts cannot be mutated in place.
- **"Use as Starting Point"**: Safely copies ONLY the user's input assumptions (`business_input_snapshot` and `financial_input_snapshot`) into a new draft in onboarding session storage. When submitted, a completely new analysis with a new UUID is calculated and persisted.
- **Local Removal vs Backend Immutability**: Removing an entry from local history only clears the client-side pointer. Backend records remain permanently immutable. No `DELETE /api/analyze/{id}` endpoint exists in 6H.

---

## 6. Production Hardening, Security & Deployment Readiness (Phase 6I)

### 6.1 Liveness and Readiness Probes
The API exposes lightweight health probe endpoints accessible at root and under `/api`:

| Probe Endpoint | HTTP Method | Target Purpose | Dependency Check | Status Codes |
| :--- | :--- | :--- | :--- | :--- |
| `/health` or `/api/health` | `GET` | Process Liveness | None (fast process check) | `200 OK` |
| `/ready` or `/api/ready` | `GET` | Traffic Readiness | PostgreSQL connectivity ping (`SELECT 1`) | `200 OK` (Healthy), `503 Service Unavailable` (DB Down) |

### 6.2 Request Correlation (`X-Request-ID`)
All requests process through `RequestIDMiddleware`:
- Incoming `X-Request-ID` headers are validated and propagated across downstream services and logs.
- If omitted, a standard UUID4 is generated automatically.
- Every HTTP response (including 2xx, 4xx, and 5xx error responses) includes the `X-Request-ID` header.
- **Separation of Concerns**: `X-Request-ID` is strictly for operational tracing and debugging; it does NOT replace or interact with `Idempotency-Key`.

### 6.3 Request Protection & Size Limits
`RequestSizeLimitMiddleware` protects mutating endpoints:
- Configurable maximum payload limit: `MAX_REQUEST_SIZE_BYTES` (default: 1 MB).
- Requests exceeding this threshold immediately receive `HTTP 413 Payload Too Large`.
- Requests without a `Content-Length` header are safely streamed and buffered up to the threshold without breaking valid small payloads.

### 6.4 Sanitized Error Responses
In production environments, unexpected server exceptions are logged with stack traces and request IDs on the server only. Clients receive a safe structured JSON response:
```json
{
  "detail": "An unexpected server error occurred. Please contact support or try again shortly.",
  "request_id": "469f3876-1c54-4255-a4ec-55b47e924e61"
}
```
API error responses never leak database connection credentials, internal SQL queries, file system paths, or environment variables.
