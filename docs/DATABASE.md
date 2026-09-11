# Database Schema & Entity Relationships — GRAMAVISE

## 1. Entity-Relationship Overview

```text
┌──────────────────────────┐
│          users           │
├──────────────────────────┤
│ id (PK, UUID)            │
│ phone_number (VARCHAR)   │
│ full_name (VARCHAR)      │
│ preferred_language (VAR) │
│ created_at (TIMESTAMP)   │
└────────────┬─────────────┘
             │ 1
             │
             │ N
┌────────────▼─────────────┐
│    business_profiles     │
├──────────────────────────┤
│ id (PK, UUID)            │
│ user_id (FK -> users.id) │
│ business_name (VARCHAR)  │
│ category (VARCHAR)       │
│ description (TEXT)       │
│ state, district, village │
│ lat, lon (FLOAT)         │
│ experience_years (INT)   │
│ own_capital (FLOAT)      │
│ desired_loan (FLOAT)     │
│ is_new_business (BOOL)   │
│ created_at (TIMESTAMP)   │
└────────────┬─────────────┘
             │
     ┌───────┼────────────────────────┐
     │ 1     │ 1                      │ 1
     │       │                        │
     │ N     │ N                      │ N
┌────▼───────┴──────┐ ┌───────────────▼────┐ ┌────────────────────────┐
│financial_assumptions│local_evidence      │ │        analyses        │
├───────────────────┤ ├────────────────────┤ ├────────────────────────┤
│ id (PK, UUID)     │ │ id (PK, UUID)      │ │ id (PK, UUID)          │
│ profile_id (FK)   │ │ profile_id (FK)    │ │ profile_id (FK)        │
│ startup_cost      │ │ indicator (VARCHAR)│ │ status (PROCEED/...)   │
│ equipment_cost    │ │ value (FLOAT/STR)  │ │ feasibility_score      │
│ inventory_cost    │ │ unit (VARCHAR)     │ │ financial_summary(JSON)│
│ monthly_fixed_cost│ │ evidence_type (ENUM│ │ market_summary (JSON)  │
│ customers_per_day │ │ confidence (FLOAT) │ │ matched_schemes (JSON) │
│ avg_ticket_price  │ │ source_url (STR)   │ │ ai_explanation (TEXT)  │
│ working_days_month│ │ created_at (TS)    │ │ risk_factors (JSON)    │
│ variable_cost_pct │ └────────────────────┘ │ created_at (TIMESTAMP) │
│ interest_rate_pct │                        └────────────────────────┘
│ loan_tenure_months│
└───────────────────┘

┌──────────────────────────────────────┐
│               schemes                │
├──────────────────────────────────────┤
│ id (PK, UUID)                        │
│ scheme_code (VARCHAR, UNIQUE)        │
│ scheme_name (VARCHAR)                │
│ ministry_or_dept (VARCHAR)           │
│ max_loan_amount (FLOAT)              │
│ subsidy_percentage_general (FLOAT)   │
│ subsidy_percentage_special (FLOAT)   │
│ interest_subvention_pct (FLOAT)      │
│ eligibility_criteria (JSONB)         │
│ required_documents (JSONB)           │
│ official_portal_url (VARCHAR)        │
└──────────────────────────────────────┘
```

---

## 2. Table Specifications

### 2.1 `users`
Represents registered entrepreneurs or CSC operators.

### 2.2 `business_profiles`
Represents an enterprise venture submitted for analysis. Linked to a user, with geo-demographic and capital details.

### 2.3 `financial_assumptions`
Stores the micro-entrepreneur's baseline expectations for Capex, Opex, unit pricing, customer volume, and loan tenure.

### 2.4 `local_evidence`
Maintains individual data items gathered from OSM, public portals, or benchmark standards, tagged by evidence classification.

### 2.5 `schemes`
Master database of state and central credit/subsidy schemes (e.g., PMEGP, Mudra, PMFME).

### 2.6 `analyses`
Historical audit logs of evaluation runs containing computed metrics, risk flags, matched schemes, and generated explanations.

---

## 3. Migration Roadmap
* Migrations will be managed using Alembic.
* Initial migration script placeholder is located in `backend/app/alembic/`.
