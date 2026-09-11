# System Architecture & Technical Design — GRAMAVISE

## 1. High-Level Architecture Diagram

```text
                    ┌─────────────────────────────────────────┐
                    │               CLIENT LAYER              │
                    │        Next.js + React + Tailwind       │
                    └────────────────────┬────────────────────┘
                                         │ HTTPS / JSON
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │               API GATEWAY               │
                    │         FastAPI REST Endpoints          │
                    │  (Validation, Serialization, Routing)   │
                    └────────────────────┬────────────────────┘
                                         │
                 ┌───────────────────────┼───────────────────────┐
                 │                       │                       │
                 ▼                       ▼                       ▼
    ┌─────────────────────────┐ ┌─────────────────┐ ┌─────────────────────────┐
    │     GEO/DATA SERVICE    │ │FINANCIAL SERVICE│ │       AI SERVICE        │
    │  - Geocoding (OSM)      │ │- Unit Economics │ │ - Vernacular Explainer  │
    │  - Market Indicators    │ │- Break-Even     │ │ - Structured Output     │
    │  - Competitor Density   │ │- Sensitivity    │ │ - Risk Interpretation   │
    └────────────┬────────────┘ └────────┬────────┘ └────────────┬────────────┘
                 │                       │                       │
                 └───────────────────────┼───────────────────────┘
                                         │
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │               RULE ENGINE               │
                    │  - Deterministic Feasibility Evaluation │
                    │  - Scheme Matching Rules (PMEGP/Mudra)  │
                    │  - Risk Categorization Logic            │
                    └────────────────────┬────────────────────┘
                                         │
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │            PERSISTENCE LAYER            │
                    │      SQLAlchemy ORM + PostgreSQL        │
                    └─────────────────────────────────────────┘
```

---

## 2. Core Architectural Principles

### 1. Strict Boundary Separation
- **Frontend:** UI presentation, state handling, localized form inputs, visualization charts.
- **Backend API Layer:** Input validation (Pydantic), error handling, orchestration.
- **Financial Services:** Pure deterministic calculations with unit tests.
- **Rule Engine:** Business logic decisions independent of machine learning / LLM hallucinations.
- **AI Layer:** Plain language generation, translation, and contextual explanation of the deterministic results.

### 2. Evidence-Based Decision Traceability
Every output data point carries metadata regarding its lineage:
- `OBSERVED`: Raw data fetched from open/government datasets.
- `CALCULATED`: Deterministically computed through audited formulas.
- `MODELLED`: Statistical or heuristic projection.
- `ASSUMED`: User-provided or default industry baseline assumption.
- `NEEDS_VERIFICATION`: Highlighted parameter requiring on-ground verification.

---

## 3. Communication Flow

1. User submits business profile & financial assumptions on frontend.
2. `POST /api/analyze` receives and validates the payload.
3. Backend invokes:
   - `GeoService` -> resolves village coordinates and queries local business density.
   - `FinancialService` -> computes Capex, Opex, Revenue, Break-even, and Sensitivity.
   - `SchemeService` -> matches loan size and applicant demographics to scheme criteria.
   - `FeasibilityRules` -> evaluates hard financial safety thresholds (`PROCEED` / `VALIDATE_FIRST` / `RECONSIDER`).
   - `AIService` -> translates the results into a structured vernacular explanation.
4. Response is compiled, tagged with evidence items, and returned as a unified `AnalysisResult` JSON.
