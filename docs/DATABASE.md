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
* Migrations are managed strictly using Alembic.
* Initial migration script is located in `backend/alembic/versions/0001_initial_schema.py`.

---

## 4. Phase 6 Database Foundation Architecture

### 4.1 Production & Development Targets
* **Production Database**: PostgreSQL 16 (configured via `DATABASE_URL=postgresql://user:pass@host:5432/dbname`).
* **Development / Test Fallback**: SQLite (`sqlite:///./gramavise_dev.db` or in-memory SQLite for test fixtures).
* **ORM & Session Layer**: SQLAlchemy 2.x declarative models and scoped session dependency (`get_db()`).
* **Schema Evolution Authority**: Alembic is the exclusive authority for schema creation and evolution.

### 4.2 Startup Lifecycle & Non-Destructive Invariants
* Application startup (`main.py`) does **NOT** run `Base.metadata.create_all()`.
* Schema provisioning is decoupled from app initialization.
* Standalone dev/test scripts can invoke `init_db(target_engine)` explicitly when needed for isolated test databases.
* **Strict Phase 6A Scope Boundaries**:
  * Analysis persistence is **NOT** wired into `/api/analyze` yet.
  * User authentication & phone-linking are **NOT** implemented yet.
  * Idempotency & repository patterns are **NOT** implemented yet.

### 4.3 Database Management Commands

All commands should be executed from within the `backend/` directory:

1. **Apply Migrations to Current Head:**
   ```bash
   alembic upgrade head
   ```

2. **Rollback Migration by 1 Step:**
   ```bash
   alembic downgrade -1
   ```

3. **Inspect Current Revision Status:**
   ```bash
   alembic current
   ```

4. **View Migration History:**
   ```bash
   alembic history --verbose
   ```

5. **Generate a New Migration (Autogenerate from Model Metadata):**
   ```bash
   alembic revision --autogenerate -m "describe_migration_here"
   ```

6. **Execute Test Suite (including Database & Alembic tests):**
   ```bash
   pytest
   ```

---

## 5. Phase 6B — Production ORM Models & Immutable Snapshots

### 5.1 Analysis Immutability Invariant
A completed GramaVise Analysis represents an immutable point-in-time snapshot of:
1. **Inputs**: What the user submitted (12 financial assumptions + business context).
2. **Knowledge**: What external evidence and market signals were observed at analysis time.
3. **Calculations**: What deterministic financial metrics were computed by `FinancialService`.
4. **Decisions**: What transparent rule conditions and recommendations were determined by `FeasibilityRules`.
5. **Actionability**: Pre-loan action plans and bank-readiness requirements established at that time.

Once created, an `Analysis` record is **never modified or overwritten**. If assumptions change, a new `Analysis` record is generated.

### 5.2 Entity Architecture & Relationship Model

```text
User (optional)
  └── BusinessProfile (mutable enterprise context)
        └── Analysis (immutable parent audit record)
              ├── FinancialInputSnapshot (1-to-1: exact 12 financial inputs)
              ├── FinancialResultSnapshot (1-to-1: exact deterministic output metrics + number explanations)
              ├── business_input_snapshot (JSONB: business identity & location snapshot)
              ├── market_result_snapshot (JSONB: competitor, catchment, and demand metrics)
              ├── scheme_result_snapshot (JSONB: matched scheme codes, subsidies, documents)
              ├── evidence_ledger_snapshot (JSONB: full evidence list with provenance & limitations)
              ├── decision_trace_snapshot (JSONB: evaluated rule IDs, conditions, outcomes)
              ├── action_plan_snapshot (JSONB: prioritized pre-loan actions & verification needs)
              ├── bank_readiness_snapshot (JSONB: document readiness & checklist items)
              ├── risk_factors (JSONB: risk factors & mitigations)
              └── ai_explanation (JSONB: translated human-readable narrative)
```

### 5.3 Snapshot Tables vs. JSONB Rationale
* **1-to-1 Snapshot Tables (`financial_input_snapshots`, `financial_result_snapshots`)**: Typed SQL columns allow fast indexed querying, strict schema constraints on the 12 core inputs and financial output numbers (e.g. `dscr`, `monthly_net_profit`, `required_loan_amount`), and direct portability.
* **JSON/JSONB Fields**: Modular, rich artifacts (such as evidence ledger entries, decision rule traces, action plans, and scheme eligibility outputs) are stored as immutable JSON payloads directly on the `analyses` record, avoiding over-normalization while preserving 100% data fidelity and provenance.

---

## 6. Phase 6C — Repository Layer & Unit of Work

### 6.1 Purpose & Layered Architecture
The persistence layer strictly decouples domain logic and route handlers from direct SQLAlchemy mechanics:

```text
FastAPI Route / Service Layer
          ↓
   Unit of Work (`UnitOfWork`) [Transaction & Session Boundary]
          ↓
   Repositories (`BusinessProfileRepository`, `AnalysisRepository`, etc.)
          ↓
   SQLAlchemy Session
          ↓
   PostgreSQL 16 / SQLite
```

### 6.2 Entity Repositories
* **`BusinessProfileRepository`**: Handles profile creation and lookup (`get_by_id`, `list_for_user`, `create`).
* **`AnalysisRepository`**: Handles immutable analysis creation and querying (`get_by_id`, `list_by_business`, `create`). **Exposes NO update or overwrite methods**, guaranteeing that completed historical analyses remain immutable.
* **`FinancialSnapshotRepository`**: Handles direct queries and staging for 1-to-1 input and result snapshots.
* **`UserRepository`**: Handles user entity lookup and staging.
* **`SchemeRepository`**: Master catalog query repository.

### 6.3 Repository Invariants & Prohibitions
* Repositories **do NOT commit transactions**. All staging is performed via `session.add()`; transaction commits are owned exclusively by `UnitOfWork`.
* Repositories **contain zero financial formulas, zero recommendation logic, and zero AI behavior**. All calculation values originate from the deterministic domain engines (`FinancialService`, `FeasibilityRules`) and are persisted as supplied.

### 6.4 Unit of Work Semantics
* **Transaction Boundary**: `UnitOfWork` guarantees atomic multi-entity operations (e.g. creating an `Analysis`, `FinancialInputSnapshot`, and `FinancialResultSnapshot` together in one transaction).
* **Rollback on Error**: If any exception occurs within `with UnitOfWork() as uow:`, `uow.rollback()` is invoked automatically, preventing partial database writes.
* **Session Lifecycle**: The session is guaranteed to be closed upon exit from the context manager.
* **Dependency Provider**: Exposes `get_uow()` for clean FastAPI dependency injection in future phases.

> **Note**: API persistence in `/api/analyze` is wired in Phase 6D. Phase 6E extends this architecture to child Scenario Records.

---

## 7. Phase 6E — Scenario Persistence & Scenario History

### 7.1 Architecture & Parent-Child Relationship
A saved Scenario is **not a new Analysis**. It represents a child what-if parameter modification evaluated against an immutable parent baseline Analysis.

```text
Analysis A (Immutable Baseline)
   ├── Scenario Record 1 (Saved What-If Snapshot)
   ├── Scenario Record 2 (Saved What-If Snapshot)
   └── Scenario Record 3 (Saved What-If Snapshot)
```

* **Foreign Key**: `scenario_records.analysis_id -> analyses.id` with `ondelete="CASCADE"`.
* **Immutability**: Baseline Analysis snapshots remain strictly unmodified when scenarios are created. Once created, a `ScenarioRecord` cannot be updated or overwritten.
* **Maximum 3 Scenarios**: Enforced at the persistence/repository layer (`ScenarioLimitExceededError` -> HTTP 409 Conflict).
* **Pure Read-Only Historical Retrieval**: `GET /api/analyze/{analysis_id}/scenarios` and `GET /api/analyze/{analysis_id}/scenarios/{scenario_id}` return stored snapshot JSONs with zero recalculation or external provider calls.

### 7.2 Schema: `scenario_records` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | PK (UUID) | Unique identifier of the saved scenario |
| `analysis_id` | `VARCHAR(36)` | FK -> `analyses.id`, NOT NULL, INDEX | Reference to parent baseline analysis |
| `name` | `VARCHAR(150)` | NOT NULL, DEFAULT "Custom Scenario" | User-specified or auto-generated label |
| `description` | `TEXT` | NULLABLE | Optional scenario narrative or notes |
| `scenario_inputs` | `JSON` | NOT NULL | Exact 12 financial input assumption overrides |
| `scenario_financial_result` | `JSON` | NOT NULL | Stored deterministic financial output snapshot |
| `scenario_recommendation` | `JSON` | NOT NULL | Stored recommendation status & decision trace |
| `comparison_result` | `JSON` | NOT NULL | Stored metric/rule comparisons & explanation deltas |
| `created_at` | `DATETIME` | NOT NULL, DEFAULT UTC | Creation timestamp |

### 7.3 Concurrency & Limit Enforcement Strategy
* **Parent Row Locking**: In PostgreSQL, `ScenarioRepository.add()` acquires a row-level lock on the parent `Analysis` (`SELECT id FROM analyses WHERE id = :id FOR UPDATE`) before checking the existing count and staging the new scenario. This serializes concurrent scenario creations for the same parent analysis and eliminates count-check race conditions without requiring external distributed locks or Redis.
* **SQLite Test Fallback**: In SQLite (development/test environment), table/file-level write locking inherently serializes transactions, while SQLAlchemy dialect handling transparently ignores `with_for_update()`.
* **Atomic Unit of Work Commit**: Scenario creation commits atomically through `UnitOfWork`. If the count is >= 3, `ScenarioLimitExceededError` is raised, rolling back the transaction and returning `HTTP 409 Conflict`.

---

## 8. Phase 6F — Persistent Scheme Catalog, Versioning & Auditability

### 8.1 Architectural Principle & Separation of Concerns
Phase 6F establishes a persistent, versioned, auditable catalog for government credit and subsidy schemes:

```text
Scheme Master Data (schemes)
        ↓
Versioned Scheme Catalog (scheme_versions)
        ↓
Deterministic Scheme Rules (SchemeRules)
        ↓
Scheme Matching Engine (SchemeService)
        ↓
Analysis Snapshot (analyses.scheme_result_snapshot)
```

* **Scheme Catalog**: Persists factual statutory metadata (scheme code, official portal URL, source title, version string, publication dates, financial ceilings, subsidy percentages, beneficiary margin requirements, and verification notes).
* **Deterministic Rules**: The eligibility criteria remain strictly encapsulated in `SchemeRules`. The catalog does NOT mutate rule logic.
* **Historical Auditability**: Published versions (`ACTIVE`, `SUPERSEDED`, `RETIRED`, `DRAFT`) are immutable. An updated government guideline produces a new `SchemeVersion` rather than overwriting historical definitions in-place.
* **Snapshot Invariance**: Historical `Analysis` snapshots persist their evaluated scheme version identity (`scheme_version="2024.1"`). Historical GET requests never refresh or recalculate scheme eligibility against updated catalog releases.

### 8.2 Schema: `schemes` (Master Table)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | PK (UUID) | Unique identifier for scheme master |
| `scheme_code` | `VARCHAR(50)` | UNIQUE, INDEX, NOT NULL | Standard statutory code (e.g. `PMEGP`, `PMMY`, `PMFME`) |
| `scheme_name` | `VARCHAR(255)` | NOT NULL | Official full title of the program |
| `ministry` | `VARCHAR(255)` | NULLABLE | Sponsoring Union Ministry |
| `department` | `VARCHAR(255)` | NULLABLE | Implementing Department / Agency |
| `description` | `TEXT` | NULLABLE | Statutory objective and overview |
| `created_at` | `DATETIME` | NOT NULL, DEFAULT UTC | Master registration timestamp |
| `updated_at` | `DATETIME` | NULLABLE, ON UPDATE UTC | Master update timestamp |

### 8.3 Schema: `scheme_versions` (Versioned Catalog Table)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | PK (UUID) | Unique version record ID |
| `scheme_id` | `VARCHAR(36)` | FK -> `schemes.id`, CASCADE, INDEX | Master scheme reference |
| `scheme_code` | `VARCHAR(50)` | INDEX, NOT NULL | Scheme code for fast lookup |
| `version` | `VARCHAR(50)` | NOT NULL | Version identifier (e.g. `2024.1`, `2026.1`) |
| `status` | `ENUM` | `schemestatusenum` (`ACTIVE`, `SUPERSEDED`, `RETIRED`, `DRAFT`) | Version lifecycle state |
| `description` | `TEXT` | NULLABLE | Version-specific operational summary |
| `official_source_name` | `VARCHAR(255)` | NULLABLE | Authoritative gazette / portal guideline title |
| `official_portal_url` | `VARCHAR(255)` | NULLABLE | Official government source URL |
| `source_publication_date`| `VARCHAR(50)` | NULLABLE | Official publication period (e.g. `2024-09`) |
| `effective_from` | `DATETIME` | NULLABLE | Effective start date |
| `effective_to` | `DATETIME` | NULLABLE | Expiry / supersede date |
| `retrieved_at` | `DATETIME` | NOT NULL, DEFAULT UTC | Timestamp when official source was audited |
| `max_loan_amount` | `FLOAT` | NOT NULL, DEFAULT 0.0 | Maximum permissible loan / project ceiling |
| `subsidy_percentage_general` | `FLOAT` | NOT NULL, DEFAULT 0.0 | Baseline subsidy percentage (General category) |
| `subsidy_percentage_special` | `FLOAT` | NOT NULL, DEFAULT 0.0 | Enhanced subsidy percentage (Special category) |
| `beneficiary_contribution_general_pct` | `FLOAT` | NOT NULL, DEFAULT 0.0 | Entrepreneur equity contribution (General) |
| `beneficiary_contribution_special_pct` | `FLOAT` | NOT NULL, DEFAULT 0.0 | Entrepreneur equity contribution (Special) |
| `eligibility_criteria` | `JSON` | NOT NULL | Tiers, eligible sectors, Greenfield requirements |
| `required_documents` | `JSON` | NOT NULL | Mandatory statutory documents list |
| `verification_notes` | `JSON` | NOT NULL | Conditions requiring ground verification |
| `metadata_payload` | `JSON` | NOT NULL | Full source JSON representation |
| `created_at` | `DATETIME` | NOT NULL, DEFAULT UTC | Version creation timestamp |

* **Unique Constraint**: `(scheme_code, version)` prevents duplicate version records.

### 8.4 Seeding Command & Idempotency
Seeding is decoupled from FastAPI startup and executed via explicit standalone CLI:

```bash
# Execute from backend/ directory:
python scripts/seed_schemes.py
```

* **Idempotency**: Running `seed_schemes.py` repeatedly safely detects existing master schemes and version records, resulting in 0 duplicates created.
* **Initial Catalog**: Seeds statutory definitions for `PMEGP`, `PMMY` (Mudra Shishu, Kishore, Tarun, Tarun Plus), and `PMFME` (ODOP micro food processing).

---

## 9. Phase 6G — Persistence-Backed Idempotency & Duplicate-Request Protection

### 9.1 Architectural Principle
Phase 6G establishes persistence-backed idempotency protection across mutating analysis endpoints (`POST /api/analyze` and `POST /api/analyze/{analysis_id}/scenarios`).

```text
Incoming Request (Idempotency-Key header)
            ↓
Compute SHA-256 Request Fingerprint
            ↓
Lookup (key, scope) in idempotency_records
 ├── If exists & same fingerprint  → Replay original persisted response payload
 ├── If exists & diff fingerprint  → Raise HTTP 409 Conflict
 └── If not found                  → Execute calculation + persist record + persist analysis/scenario atomically
```

### 9.2 Schema: `idempotency_records` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | PK (UUID) | Unique identifier for idempotency record |
| `key` | `VARCHAR(128)` | INDEX, NOT NULL | Client-supplied idempotency key |
| `scope` | `VARCHAR(64)` | INDEX, NOT NULL | Operation scope (e.g. `POST /api/analyze`, `POST /api/analyze/{id}/scenarios`) |
| `request_fingerprint` | `VARCHAR(64)` | NOT NULL | Deterministic SHA-256 hash of sorted request payload |
| `resource_id` | `VARCHAR(36)` | NULLABLE | Associated created Analysis or Scenario ID |
| `status` | `VARCHAR(32)` | NOT NULL, DEFAULT "COMPLETED" | Processing status (`COMPLETED`, `FAILED`) |
| `response_payload` | `JSON` | NOT NULL | Cached response JSON for immediate deterministic replay |
| `created_at` | `DATETIME` | NOT NULL, DEFAULT UTC | Creation timestamp |
| `updated_at` | `DATETIME` | NULLABLE, ON UPDATE UTC | Last update timestamp |

* **Unique Constraint**: `uq_idempotency_key_scope` on `(key, scope)` prevents duplicate executions across concurrent or repeated requests.

### 9.3 Invariants & Operational Rules
1. **Operation-Scoped**: The same key used across different scopes (e.g. baseline analysis vs scenario creation) operates in independent namespaces.
2. **Payload Fingerprint**: Fingerprint is computed via `sha256(canonical_json_with_sorted_keys)`. Any payload variation under the same key results in `HTTP 409 Conflict`.
3. **No Recalculation**: Idempotent re-execution replays the original stored response payload with zero recalculation or external provider calls.
4. **Concurrency Resilience**: Database-level unique constraint violation is caught on simultaneous duplicate requests, safely falling back to fetching and returning the winning transaction's persisted result.

---

## 10. Phase 6H — Persistent Analysis History & Historical Immutability

### 10.1 Schema Evolution & Migration Status
**No database migration required for Phase 6H.**
Phase 6H operates strictly on the existing persisted database architecture:
- `analyses` (immutable analysis snapshot with foreign keys to all child snapshots)
- `financial_input_snapshots` & `financial_result_snapshots`
- `scenario_records` (up to 3 scenario variations per baseline analysis)
- `schemes` & `scheme_versions` (immutable versioned scheme catalog)
- `idempotency_records` (deduplication & replay)

### 10.2 Immutability Guarantees
1. **Read-Only Historical Retrieval**: Retrieval via `GET /api/analyze/{analysis_id}` reads the existing database snapshot using `UnitOfWork.analyses.get_by_id(analysis_id)` and maps it directly to the response schema.
2. **Zero Recalculation**: Historical retrieval never executes financial calculations, market lookups, scheme re-evaluation, or AI re-generation.
3. **Scheme Version Stability**: Historical analyses retain their original evaluated scheme version identifier (`scheme_version="2024.1"`). Upgrades to the scheme catalog never alter past analyses.
4. **Backend Deletion Prohibited**: No `DELETE` endpoint or soft-delete mechanism is implemented in Phase 6H. Analyses remain permanent, immutable audit records.
5. **Anonymous Index Model**: The database contains no user identity or authentication tables. Client-side browser storage maintains a lightweight pointer index only. Removing an entry on the client has zero effect on the database.

---

## 11. Phase 6I — Database Connection Hardening & Readiness Probes

### 11.1 Production Connection Pooling (PostgreSQL)
In production environments connecting to PostgreSQL, SQLAlchemy engine settings are tuned for connection durability:
- `pool_size`: 10 (default base pool size)
- `max_overflow`: 20 (surge connection allocation)
- `pool_timeout`: 30s (checkout timeout before failing safely)
- `pool_recycle`: 1800s (30-minute proactive connection recycling to prevent stale dropouts)
- `pool_pre_ping`: `True` (connection liveness verification before returning to application worker)

For development and test environments using SQLite, `check_same_thread: False` is configured to enable multi-threaded test isolation without pool overhead.

### 11.2 Database Readiness Check (`check_database_health`)
- The readiness probe (`GET /ready` or `GET /api/ready`) executes a fast `SELECT 1` query using `check_database_health()`.
- If connectivity fails, the engine safely intercepts the exception without raising unhandled errors or leaking credentials, returning a clean `503 Service Unavailable` response.

### 11.3 Schema Authority & Startup Policies
- **Sole Authority**: Alembic migrations (`alembic upgrade head`) remain the exclusive authority for creating and evolving production tables.
- **No Startup Creation**: The backend never invokes `Base.metadata.create_all()` on startup.
- **No Startup Seeding**: The scheme catalog is seeded via explicit operator CLI (`python scripts/seed_schemes.py`) and is never auto-seeded on application startup.
