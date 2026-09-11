# Team Development Workflow & Branch Strategy — GRAMAVISE

## 1. Branch Strategy for 5-Person Hackathon Team

```text
main (Production / Stable Demo)
  │
  ├── develop (Integration branch)
  │     ├── feature/frontend-ui         (Developer 1: Frontend & Onboarding Forms)
  │     ├── feature/financial-engine    (Developer 2: Formulas, Sensitivity & DSCR)
  │     ├── feature/geo-data-providers  (Developer 3: OSM, Overpass & Market Data)
  │     ├── feature/schemes-and-db      (Developer 4: Scheme Matcher & DB Repos)
  │     └── feature/ai-vernacular       (Developer 5: Prompts, Vernacular & AI)
```

---

## 2. Developer Role Allocation & Responsibilities

| Role / Track | Primary Tasks | Target Modules |
| :--- | :--- | :--- |
| **Dev 1: Frontend Lead** | Build multi-step onboarding wizard, results dashboard, metric cards, charts, and language toggle. | `frontend/app/`, `frontend/components/`, `frontend/hooks/` |
| **Dev 2: Financial Lead** | Implement Break-Even, DSCR, Capex/Opex math, EMI calculator, and sensitivity matrix. | `backend/app/services/financial/`, `backend/app/rules/financial_rules.py` |
| **Dev 3: Geospatial & Data** | Implement OSM Nominatim/Overpass client, competitor density aggregation, and evidence collectors. | `backend/app/services/geo/`, `data/providers/`, `backend/app/services/evidence/` |
| **Dev 4: Schemes & DB Lead** | Populate scheme rules (PMEGP, Mudra, PMFME), write repository queries, and setup PostgreSQL migrations. | `backend/app/services/schemes/`, `backend/app/repositories/`, `backend/app/models/` |
| **Dev 5: AI & Vernacular** | Implement prompt templates, vernacular language translation helpers, and AI provider integration. | `backend/app/services/ai/`, `backend/app/api/routes/ai.py` |

---

## 3. Pull Request & Merging Protocol
1. Pull latest `develop` branch before starting work.
2. Ensure unit tests pass (`pytest`) and TypeScript compiles (`npm run build`).
3. Create short-lived feature branches (`feature/<track-name>`).
4. Merge into `develop` with code review from at least one teammate.
