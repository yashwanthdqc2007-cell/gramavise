# GRAMAVISE

> **AI-Driven Hyper-Local Business Advisory and Financial Structuring Assistant for Rural Micro-Entrepreneurs**  
> Problem Statement: **SIH26091**  
> *"Know the market. Calculate the risk. Decide before you borrow."*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-black?logo=next.js&logoColor=white)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Alembic](https://img.shields.io/badge/Alembic-1.13-red)](https://alembic.sqlalchemy.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 1. Executive Summary

**GramaVise** is an intelligent, rural-first pre-loan advisory and financial structuring platform tailored for micro-entrepreneurs, Self-Help Groups (SHGs), and local enterprise creators in rural India.

Before taking on high-interest informal loans or applying for institutional bank credit, rural entrepreneurs often lack:
1. **Hyper-local market clarity** (competitor density, demand patterns, nearby market prices).
2. **Deterministic unit economics** (monthly cash flow, debt service coverage, break-even unit targets).
3. **Transparent scheme navigation** (PMEGP, MUDRA, PMFME eligibility and subsidy calculations).
4. **Verifiable, trustworthy advice** free from AI hallucinations.

GramaVise solves this by enforcing a strict architectural philosophy:
```text
Evidence  ──>  Calculate  ──>  Explain  ──>  Decide  ──>  Act  ──>  Test
```

* **Formulas and verdicts are 100% deterministic** — calculated directly with banking math and audited rule engines.
* **Evidence is classified by provenance** — every data point is tagged (`OBSERVED`, `CALCULATED`, `MODELLED`, `ASSUMED`, `NEEDS_VERIFICATION`).
* **AI is restricted to explanation** — editorial translation into vernacular languages without authority over mathematical verdicts.
* **Point-in-time snapshot immutability** — historical queries replay frozen inputs and results without drift.

---

## 2. Key Capabilities & Feature Highlights

### 🧮 Deterministic Financial Engine
* **Unit Economics:** Capex aggregation, monthly revenue, variable cost margins, gross profit, fixed cost burdens, and net operating income (NOI).
* **Loan Structuring & EMI:** Standard amortization formula with zero-interest edge-case protection; auto-calculates loan requirements from capital gaps.
* **Debt Service Coverage Ratio (DSCR):** Validates debt repayment cushion ($NOI / EMI$) with explicit thresholds ($< 1.0$ critical failure, $1.0 - 1.49$ warning, $\ge 1.50$ safe).
* **Break-Even Diagnostics:** Computes break-even monthly revenue, daily unit sales targets, and margin-of-safety buffers.
* **Built-in Sensitivity Stress Testing:** Simulates 4 stress cases (demand drops by 20%, ticket price compresses by 10%, variable cost inflates by 15%, and combined stress) to rate business resilience (`HIGH`, `MODERATE`, `LOW`).

### 📍 Hyper-Local Evidence & Multi-Provider Intelligence
* **OpenStreetMap (OSM) POI Adapter:** Mapped competitor counts with Haversine distance, classified into `DIRECT` and `ADJACENT` competitors within a 5 km catchment.
* **Local Government Directory (LGD):** Administrative district, sub-district, and village classification with official census identifiers.
* **Census 2011 Demographics:** Baseline village and sub-district population counts and rural indicators.
* **Agmarknet Mandi Price Adapter:** Wholesale commodity pricing lookup from nearby APMCs (e.g., wheat, paddy, milk, oilseeds) with freshness metadata.
* **One District One Product (ODOP):** District-level agro-processing specializations aligned with PMFME priorities.
* **Udyam MSME Density:** Enterprise concentration context across micro, small, and medium manufacturing/services.
* **Audit Evidence Ledger:** Displays confidence scores, limitations, and an actionable ground verification checklist.

### 🏛️ Government Scheme Eligibility Matcher
* **Versioned Scheme Catalog (`2024.1`):** Immutable scheme versions with eligibility rules and subsidy models.
* **PMEGP (Prime Minister’s Employment Generation Programme):** Greenfield manufacturing/service loans up to ₹50L/₹20L with rural subsidies (15%–35%) and 5%–10% own contribution.
* **MUDRA / PMMY:** Category selection across **Shishu** ($\le$ ₹50,000), **Kishore** (₹50,001–₹5,00,000), **Tarun** (₹5L–₹10L), and **Tarun Plus** (₹10L–₹20L).
* **PMFME (PM Formalisation of Micro food processing Enterprises):** 35% capital subsidy up to ₹10L with ODOP alignment checks for new or upgrading units.

### 🧪 Scenario Lab (What-If Simulator)
* Real-time assumption overrides (alter daily customers, unit pricing, or operating costs).
* Side-by-side comparison against the frozen baseline with "what changed" and "why it changed" delta tracking.
* Save up to 3 persistent scenarios per analysis with parent-locked idempotency.

### 🗣️ Vernacular & Rural-First UX
* **6 Indic Languages Supported:** English (`en`), Hindi (`hi`), Telugu (`te`), Tamil (`ta`), Marathi (`mr`), and Bengali (`bn`) with 100% dictionary key parity (501 canonical keys).
* **Voice-Assisted Numeric Input:** Browser Web Speech API integration in 6 locales (`en-IN`, `hi-IN`, `te-IN`, etc.) with a multilingual numeric parser supporting Indian numbering (lakhs, crores, thousands, percentages). Includes an accessible confirmation modal.
* **Offline Draft Recovery:** Auto-saves progress to `localStorage` (`gramavise_draft_v1`) with 300 ms debounce and 7-day TTL.
* **Anonymous History Management:** Browser-scoped history indexing (`gramavise_history_v1`, up to 20 entries) with one-click "Use as Starting Point" advisory cloning.
* **Plain-Language Financial Explanations:** "Explain Number" modal converting complex metrics (DSCR, Break-even, Variable Costs) into relatable rural analogies (e.g., daily cups of tea, harvest buffers).

---

## 3. High-Level Architecture

```text
                                 GRAMAVISE PLATFORM
                                         │
        ┌────────────────────────────────┴────────────────────────────────┐
        ▼                                                                 ▼
 ┌───────────────┐                                                 ┌───────────────┐
 │   FRONTEND    │  Next.js 14 App Router (TypeScript + Tailwind)   │  RURAL UX     │
 │               │  • 4-Step Adaptive Onboarding Wizard            │  • 6-Lang i18n │
 │               │  • Decision Hero & Interactive Trace            │  • Voice Input │
 │               │  • Scenario Lab & Break-Even Chart              │  • Draft Cache │
 └───────┬───────┘                                                 └───────────────┘
         │ HTTP / JSON (Typed API Client)
         ▼
 ┌───────────────┐
 │  FASTAPI API  │  FastAPI 0.111 + Pydantic v2
 │               │  • Request-ID & Size Limiting Middlewares (1 MB max)
 │               │  • Idempotency-Key Fingerprint Replay Protection
 └───────┬───────┘
         │
 ┌───────┴────────────────────────────────────────────────────────────────┐
 │ SERVICES & ENGINES                                                     │
 │ • FinancialService: Deterministic formulas (Revenue, EMI, DSCR, BEP)   │
 │ • FeasibilityRules: PROCEED / VALIDATE_FIRST / RECONSIDER verdicts     │
 │ • SchemeMatcher: PMEGP, MUDRA, PMFME versioned rule catalog            │
 │ • EvidenceCollector: 5-Tier Ledger with heuristic confidence scoring   │
 │ • ScenarioComparator: Delta analysis preserving baseline integrity     │
 │ • AIService: Plain-language translation layer (Mock / LLM Provider)    │
 └───────┬────────────────────────────────────────────────────────────────┘
         │
    ┌────┴───────────────────────────┬────────────────────────────┐
    ▼                                ▼                            ▼
┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
│  PROVIDER ADAPTERS   │   │ PERSISTENCE LAYER    │   │ DATABASE             │
│  • OpenStreetMap POI │   │ • SQLAlchemy 2.0 ORM │   │ • SQLite (Dev/Test)  │
│  • Census 2011       │   │ • Unit of Work (UoW) │   │ • PostgreSQL 16      │
│  • Agmarknet Mandi   │   │ • Immutable Snapshot │   │   (Production)       │
│  • PMFME ODOP Master │   │   Repositories       │   │ • Alembic Migrations │
│  • Udyam MSME Stats  │   │ • Idempotency Store  │   │   (0001 - 0005)      │
└──────────────────────┘   └──────────────────────┘   └──────────────────────┘
```

---

## 4. Tech Stack & Dependencies

| Layer | Technology | Manifest Version | Role |
| :--- | :--- | :--- | :--- |
| **Frontend** | [Next.js](https://nextjs.org/) | `^14.2.4` | App Router, SSR & Client State |
| | [React](https://react.dev/) | `^18.3.1` | Component UI Library |
| | [TypeScript](https://www.typescriptlang.org/) | `^5.4.5` | Strict static typing across routes and payloads |
| | [Tailwind CSS](https://tailwindcss.com/) | `^3.4.4` | Design system, mobile-first responsive layouts |
| | [Lucide React](https://lucide.dev/) | `^0.395.0` | Accessible vector icon set |
| **Backend** | [Python](https://www.python.org/) | `3.11+` | Runtime environment |
| | [FastAPI](https://fastapi.tiangolo.com/) | `>=0.111,<0.112` | High-performance asynchronous REST API |
| | [Pydantic](https://docs.pydantic.dev/) | `>=2.7,<3` | Schema validation and settings management |
| | [SQLAlchemy](https://www.sqlalchemy.org/) | `>=2.0.30,<2.1` | Relational ORM & Unit of Work transactions |
| | [Alembic](https://alembic.sqlalchemy.org/) | `>=1.13,<1.14` | Database schema migrations (`0001`–`0005`) |
| | [Uvicorn](https://www.uvicorn.org/) | `>=0.30,<0.31` | ASGI production web server |
| | [HTTPX](https://www.python-httpx.org/) | `>=0.27,<0.28` | Async HTTP client for provider queries |
| **Database** | [PostgreSQL](https://www.postgresql.org/) / SQLite | `16` (Docker) / 3 | Persistent relational storage & immutable snapshots |
| **Testing** | [Pytest](https://pytest.org/) | `>=8.2,<9` | Test suite (30+ backend test modules) |

---

## 5. Repository Structure

```text
gramavise/
├── backend/
│   ├── alembic/                      # Database schema migrations
│   │   ├── versions/                 # Migrations 0001 through 0005
│   │   └── env.py
│   ├── alembic.ini                   # Alembic configuration
│   ├── app/
│   │   ├── api/routes/               # FastAPI route controllers (analyze, financial, schemes, health)
│   │   ├── data/                     # Local provider snapshot datasets
│   │   │   ├── demographics/         # Census 2011 demographic data
│   │   │   ├── geo/                  # Local Government Directory (LGD) master
│   │   │   ├── odop/                 # National ODOP product master
│   │   │   ├── osm/                  # OpenStreetMap POI snapshot
│   │   │   ├── pricing/              # Agmarknet mandi wholesale prices
│   │   │   ├── schemes/              # PMEGP, MUDRA, PMFME scheme specs
│   │   │   └── udyam/                # Udyam MSME district density master
│   │   ├── middleware/               # Request-ID & request size limiting
│   │   ├── models/                   # SQLAlchemy ORM models (Analysis, Snapshots, Scenarios, Idempotency)
│   │   ├── providers/                # Pluggable data provider adapters
│   │   ├── repositories/             # Repository pattern & Unit of Work (UoW)
│   │   ├── rules/                    # Deterministic feasibility, financial, and scheme rules
│   │   ├── schemas/                  # Pydantic request and response schemas
│   │   ├── services/                 # Domain logic (Financial, Evidence, Geo, Schemes, AI, Scenario)
│   │   ├── utils/                    # Geo distance (Haversine), logging, request fingerprinting
│   │   ├── config.py                 # Pydantic Settings configuration
│   │   ├── database.py               # Database engine & sessionmaker
│   │   └── main.py                   # FastAPI application factory
│   ├── scripts/                      # Seed scripts (seed_schemes.py)
│   └── tests/                        # 30+ Pytest modules (unit, integration, resilience, hardening)
├── docs/                             # Architectural specifications and master audit report
│   ├── API.md                        # Complete REST API reference
│   ├── ARCHITECTURE.md               # System design & component interactions
│   ├── DATABASE.md                   # Database schema & snapshot design
│   ├── DATA_PROVIDERS.md             # Provider boundary documentation
│   ├── DEMO_SCENARIOS.md             # 4 Verified benchmark profiles
│   ├── FINANCIAL_ENGINE.md           # Mathematical formulas & test matrices
│   ├── GRAMAVISE_MASTER_PROJECT_REPORT.md  # Comprehensive project audit report
│   └── MARKET_EVIDENCE.md            # Evidence hierarchy & scoring specification
├── frontend/
│   ├── app/                          # Next.js 14 App Router pages
│   │   ├── analysis/loading/         # Submission loading state & error handler
│   │   ├── history/                  # Local advisory history & historical replay view
│   │   ├── onboarding/               # 4-step interactive business profile wizard
│   │   ├── results/                  # Comprehensive advisory results dashboard
│   │   ├── schemes/                  # Government schemes directory
│   │   ├── layout.tsx                # Root layout with language context & navbar
│   │   └── page.tsx                  # Landing page
│   ├── components/                   # Modular React components
│   │   ├── analysis/                 # Analysis progress bar
│   │   ├── common/                   # Header, Footer, LanguageToggle, NetworkStatusBar
│   │   ├── dashboard/                # DecisionHero, DecisionTrace, NumbersAtAGlance, ScenarioLab
│   │   ├── evidence/                 # EvidenceBadge, EvidenceDrawer
│   │   ├── financial/                # BreakEvenChart, MetricCard, ExplainNumberModal
│   │   ├── market/                   # CompetitorList, MarketSnapshot
│   │   ├── onboarding/               # ProfileForm, LocationForm, BusinessForm, FinancialForm
│   │   ├── ui/                       # Badge, Button, Card, Input primitive components
│   │   └── voice/                    # VoiceInputButton, VoiceConfirmationModal
│   ├── hooks/                        # Custom React hooks (useAnalysis, useVoiceInput, useNetworkStatus)
│   ├── lib/                          # Client utilities
│   │   ├── demo/                     # Pre-configured demo scenario profiles
│   │   ├── i18n/                     # 6-language dictionaries (en, hi, te, ta, mr, bn)
│   │   ├── storage/                  # Local storage managers (drafts, history)
│   │   ├── voice/                    # Multilingual speech-to-number parser
│   │   └── api.ts                    # Robust fetch client with error classification
│   └── scripts/                      # Frontend evaluation & verification scripts
├── docker-compose.yml                # Multi-container orchestration (Postgres + Backend + Frontend)
├── start.bat                         # 1-Click Windows development launcher
└── README.md                         # Project documentation
```

---

## 6. Quickstart & Local Setup

### Prerequisites
* **Node.js**: `v18.0` or higher
* **Python**: `v3.11` or higher
* **Docker & Docker Compose** (Optional, for containerized run)

---

### Option A: One-Click Windows Launcher (`start.bat`)
On Windows machines, you can start both frontend and backend in one step:
```cmd
start.bat
```
This script will:
1. Verify Node.js and Python.
2. Initialize virtual environments and install dependencies if missing.
3. Start FastAPI on `http://localhost:8000` and Next.js on `http://localhost:3000`.
4. Launch your browser automatically.

---

### Option B: Manual Setup

#### Step 1: Clone and Configure
```bash
git clone https://github.com/yashwanthdqc2007-cell/gramavise.git
cd gramavise
cp .env.example .env
```

#### Step 2: Backend Setup
```bash
cd backend
python -m venv .venv

# Activate virtual environment:
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux / macOS:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed government scheme catalog
python scripts/seed_schemes.py

# Start backend server
uvicorn app.main:app --reload --port 8000
```
* Interactive API Documentation (Swagger): `http://localhost:8000/docs`
* Health Check Endpoint: `http://localhost:8000/health`

#### Step 3: Frontend Setup
```bash
# In a new terminal window
cd frontend
npm install
npm run dev
```
* Application URL: `http://localhost:3000`

---

### Option C: Docker Compose Setup
Run the entire stack (PostgreSQL + FastAPI + Next.js):
```bash
docker-compose up --build
```

---

## 7. Pre-Configured Benchmark Scenarios

GramaVise includes 4 audited benchmark profiles in the onboarding wizard:

| Profile | Business Concept | Investment / Loan | Monthly Revenue / Net Profit | EMI / DSCR | Recommendation Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Kisan Flour Mill** | Rural agro-processing (Atta Chakki) | ₹3,00,000 / ₹1,50,000 | ₹4,55,000 / ₹2,27,025 | ₹3,224 / **71.4x** | `PROCEED` (Eligible for PMEGP & MUDRA Kishore) |
| **Lakshmi Tailoring** | Garment & custom tailoring unit | ₹1,70,000 / ₹70,000 | ₹1,04,000 / ₹56,007 | ₹1,792 / **32.2x** | `PROCEED` (Low break-even volume of 2 customers/day) |
| **Village Dairy Unit** | Milk collection & chilling unit | ₹3,50,000 / ₹3,00,000 | ₹97,500 / ₹2,602 | ₹6,522 / **1.40x** | `VALIDATE_FIRST` (Tight repayment buffer, 65% variable costs) |
| **Sri Amman Snacks** | Tea, bakery, and snack stall | ₹1,50,000 / ₹1,00,000 | ₹52,000 / ₹2,839 | ₹2,560 / **2.11x** | `PROCEED` (Watch break-even volume; eligible for PMFME) |

---

## 8. REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` / `/api/health` | Liveness probe returning process status. |
| `GET` | `/ready` / `/api/ready` | Readiness probe confirming database connectivity. |
| `POST` | `/api/analyze` | Full advisory pipeline: validates inputs, computes financials, queries providers, evaluates rules, and persists immutable snapshots. Supports `Idempotency-Key`. |
| `GET` | `/api/analyze/{id}` | Retrieves frozen historical analysis snapshot without recalculation. |
| `POST` | `/api/analyze/scenario` | Transient in-memory Scenario Lab calculation comparing baseline vs. overrides. |
| `POST` | `/api/analyze/{id}/scenarios` | Calculates and saves a scenario record under parent analysis (max 3 per analysis). |
| `GET` | `/api/analyze/{id}/scenarios` | Lists all saved scenario records for an analysis. |
| `POST` | `/api/financial/calculate` | Standalone deterministic financial calculation. |
| `POST` | `/api/financial/sensitivity` | Evaluates 4 sensitivity stress cases and returns resilience grade. |
| `GET` | `/api/market/evidence` | Queries competitor, demographic, and price provider context. |
| `GET` | `/api/schemes` | Returns active government schemes catalog. |
| `GET` | `/api/schemes/{code}` | Fetches details and active version for a specific scheme. |

For exhaustive request/response schemas and examples, see [`docs/API.md`](docs/API.md).

---

## 9. Verification & Quality Assurance

### Running Backend Test Suite
The repository includes comprehensive Pytest suites covering unit calculations, sensitivity tests, provider boundaries, idempotency, and production hardening:
```bash
cd backend
pytest -v
```

### Running Frontend Verification
```bash
cd frontend
# TypeScript type check
npm run type-check

# 6-language i18n parity check (verifies 100% dictionary key coverage)
node scripts/test_i18n.js

# Voice input numeric parser test suite
node scripts/test_voice_parser.js

# Offline draft & history storage test suite
node scripts/test_draft_storage.js
node scripts/test_history_storage.js

# Production Next.js build validation
npm run build
```

---

## 10. Core Team & Project Context

* **Event:** Smart India Hackathon (SIH)
* **Problem Statement:** SIH26091
* **Theme:** AI-Driven Hyper-Local Business Advisory and Financial Structuring Assistant for Rural Micro-Entrepreneurs
* **Repository:** [https://github.com/yashwanthdqc2007-cell/gramavise](https://github.com/yashwanthdqc2007-cell/gramavise)

---

## 11. License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
