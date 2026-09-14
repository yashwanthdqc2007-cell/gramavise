# GRAMAVISE

> **AI-Driven Hyper-Local Business Advisory and Financial Structuring Assistant for Rural Micro-Entrepreneurs**  
> Problem Statement: **SIH26091**

---

## 1. Project Overview

**GramaVise** is an intelligent advisory and financial structuring platform tailored for rural micro-entrepreneurs, self-help groups (SHGs), and local enterprise creators in India. It bridges the gap between grassroots business ideas and institutional viability by combining hyper-local geospatial market insights, deterministic financial modeling, government scheme matching, and explainable AI.

---

## 2. Problem & Solution

### The Problem
* **Information Asymmetry:** Rural micro-entrepreneurs lack access to localized market intelligence, demand patterns, and competition density.
* **Complex Financial Structuring:** Navigating capital requirements, cash flow cycles, EMI repayments, and break-even thresholds is difficult without formal financial training.
* **Underutilized Government Schemes:** Central and state financial assistance programs (PMEGP, Mudra, PMFME, DAY-NRLM) often remain unaccessed due to complex eligibility criteria and paperwork hurdles.
* **Unexplainable / Hallucinating Advice:** Generic AI chatbots provide generic or factually misleading advice without local grounding or verifiable financial formulas.

### The Solution
* **Deterministic Rule & Financial Engine:** Hardcoded, verifiable financial formulas (break-even, EMI, DSCR, sensitivity) ensuring numerical accuracy.
* **Hyper-Local Geographic Context:** Integration interfaces for OpenStreetMap (OSM) and local data indicators to assess business viability by pin code/village cluster.
* **Scheme Eligibility Matcher:** Transparent matching engine linking business profiles to relevant state & central credit-linked subsidies.
* **Evidence-Backed Recommendations:** Every advisory output is backed by an evidence classification system (`OBSERVED`, `CALCULATED`, `MODELLED`, `ASSUMED`, `NEEDS_VERIFICATION`).
* **Explainable AI Layer:** LLM integration strictly restricted to interpreting and translating deterministic calculations into simple, multilingual, vernacular advisory narratives.

---

## 3. Architecture

```text
                    GRAMAVISE
                        │
                        ▼
                ┌───────────────┐
                │   FRONTEND    │
                │   Next.js     │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │   REST API    │
                │   FastAPI     │
                └───────┬───────┘
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
     GEO/DATA       FINANCIAL       AI/RAG
      SERVICE         SERVICE       SERVICE
          │             │             │
          └─────────────┼─────────────┘
                        │
                        ▼
                ┌───────────────┐
                │   DATABASE    │
                │  PostgreSQL   │
                └───────────────┘
```

---

## 4. Tech Stack

* **Frontend:** Next.js 14+ (App Router), TypeScript, Tailwind CSS, Lucide Icons
* **Backend:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy, Uvicorn
* **Database:** PostgreSQL 16 (Relational database with migration readiness)
* **AI/LLM Abstraction:** Modular provider layer (Mock / Gemini / OpenAI) for structured JSON outputs & vernacular explanations
* **Testing:** Pytest (Backend), Jest/React Testing Library (Frontend)
* **Containerization:** Docker & Docker Compose

---

## 5. Repository Structure

```text
gramavise/
├── frontend/             # Next.js App Router frontend
│   ├── app/              # Routes: onboarding, analysis, results, schemes
│   ├── components/       # UI, onboarding, dashboard, financial, market, evidence
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # API client, types, constants, utilities
│   └── services/api/     # Modular frontend API service callers
├── backend/              # FastAPI Python backend
│   ├── app/
│   │   ├── api/          # Route controllers & API routers
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   ├── services/     # Core domain services (Financial, Geo, Schemes, AI, Evidence)
│   │   ├── repositories/ # Database persistence layer
│   │   ├── rules/        # Deterministic business & feasibility rules
│   │   └── utils/        # Error handlers, logging, validators
│   └── tests/            # Unit, service, and integration tests
├── data/                 # Data provider interfaces & mock datasets
├── docs/                 # Developer, architecture, PRD, and API documentation
├── scripts/              # Setup, database seeding, and verification scripts
├── tests/                # Top-level integration & health verification
├── .env.example          # Environment variable template
├── .gitignore            # Git ignore specification
├── docker-compose.yml    # Multi-container orchestration
├── LICENSE               # MIT License
└── README.md             # This document
```

---

## 6. Local Setup & Quickstart

### Prerequisites
* **Node.js**: v18.0 or higher
* **Python**: v3.10 or higher
* **Docker & Docker Compose** (Optional, for containerized run)

### Step 1: Environment Setup
```bash
cp .env.example .env
```

### Step 2: Backend Setup
```bash
cd backend
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1
# Or Linux/macOS:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend API server
uvicorn app.main:app --reload --port 8000
```
Backend Swagger API documentation will be available at: `http://localhost:8000/docs`

### Step 3: Frontend Setup
```bash
cd frontend
# Install dependencies
npm install

# Start Next.js development server
npm run dev
```
Frontend application will be accessible at: `http://localhost:3000`

---

## 7. Docker Quickstart

To run the entire stack (PostgreSQL + FastAPI Backend + Next.js Frontend) using Docker:

```bash
docker-compose up --build
```

---

## 8. Team Development Workflow

Refer to [`docs/TEAM_WORKFLOW.md`](docs/TEAM_WORKFLOW.md) for branch strategy, coding conventions, and PR workflows.

| Track | Module Focus | Core Directories |
| :--- | :--- | :--- |
| **Track 1: Frontend** | UI, Onboarding Forms, Results Dashboard | `frontend/` |
| **Track 2: Financial Engine** | Formulas, Sensitivity, Feasibility Rules | `backend/app/services/financial/`, `backend/app/rules/` |
| **Track 3: Geo & Data Providers**| OSM, Location Intelligence, Evidence Engine | `backend/app/services/geo/`, `data/` |
| **Track 4: Schemes & DB** | Government Schemes Matcher, Repositories | `backend/app/services/schemes/`, `backend/app/models/` |
| **Track 5: AI & Vernacular** | Explanations, Prompt Engineering, Summaries | `backend/app/services/ai/` |

---

## 9. Verification & Health Checks

* **Process Liveness Probe**: `GET http://localhost:8000/health` (or `http://localhost:8000/api/health`)
* **Readiness Probe**: `GET http://localhost:8000/ready` (or `http://localhost:8000/api/ready`)
* **Run Database Migrations**: `cd backend && alembic upgrade head`
* **Seed Scheme Catalog**: `cd backend && python scripts/seed_schemes.py`
* **Run Backend Test Suite**: `cd backend && pytest`
* **Verify Frontend Types & i18n**: `cd frontend && npm run type-check && npm run test:i18n`
* **Run Frontend Production Build**: `cd frontend && npm run build`
