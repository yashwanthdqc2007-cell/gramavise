# Developer Setup & Contribution Guide — GRAMAVISE

## 1. Quick Start

### 1.1 Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 1.2 Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 2. Directory Conventions

### Backend Code Placement Rules
- **Route definitions ONLY** in `backend/app/api/routes/`. No business logic inside controllers.
- **Formulas & calculations** in `backend/app/services/financial/`.
- **Eligibility criteria & status evaluations** in `backend/app/rules/`.
- **Database models** in `backend/app/models/`.
- **Schemas for I/O serialization** in `backend/app/schemas/`.

### Frontend Code Placement Rules
- **Pages / Routing** in `frontend/app/`.
- **Presentational / Modular Components** in `frontend/components/`.
- **Data Fetching Hooks** in `frontend/hooks/`.
- **API Callers** in `frontend/services/api/`.
- **Shared Types** in `frontend/lib/types.ts`.

---

## 3. Running Tests
```bash
# Run all backend tests
cd backend && pytest

# Run specific financial module tests
pytest tests/financial/

# Run frontend type checking
cd frontend && npm run type-check
```
