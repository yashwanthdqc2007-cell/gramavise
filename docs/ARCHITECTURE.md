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
    │  - LGD / Census 2011    │ │- Unit Economics │ │ - Vernacular Explainer  │
    │  - Agmarknet Mandi Price│ │- Break-Even     │ │ - Structured Output     │
    │  - OSM / Overpass POIs  │ │- Sensitivity    │ │ - Grounded on Trace     │
    │  - Udyam MSME Registry  │ │- DSCR & EMI     │ └────────────┬────────────┘
    └────────────┬────────────┘ └────────┬────────┘              │
                 │                       │                       │
                 └───────────────────────┼───────────────────────┘
                                         │
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │               RULE ENGINE               │
                    │  - FeasibilityRules (Single Authority)  │
                    │  - Deterministic Decision Trace         │
                    │  - Scheme Matching (PMEGP/Mudra/PMFME)  │
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
- **AI Layer:** Plain language generation, translation, and contextual explanation grounded strictly in the deterministic decision trace.

### 2. Evidence-Based Decision Traceability
Every output data point carries metadata regarding its lineage:
- `OBSERVED`: Raw data fetched from open/government datasets (LGD, Census 2011, Agmarknet, OpenStreetMap, Udyam OGD).
- `CALCULATED`: Deterministically computed through audited formulas.
- `MODELLED`: Statistical or heuristic projection (e.g. geometric catchment model).
- `ASSUMED`: User-provided or default industry baseline assumption.
- `NEEDS_VERIFICATION`: Highlighted parameter requiring on-ground verification or when rural mapping is incomplete.

---

## 3. Step 4H — Evidence Intelligence, Confidence & Decision Trace

```text
Pipeline Analysis Context
       ↓
FeasibilityRules.evaluate_with_trace()
       ↓
RuleEvaluation[] (PASS / WARNING / FAIL)
       ↓
DecisionTrace (Authoritative Verdict + Rationale + Positive/Caution factors)
       ↓
EvidenceCollector (Evidence Ledger + Verification Checklist Synthesis)
       ↓
AI Service Grounding (Summary & Vernacular Narrative grounded on Trace)
```

- **Single Authority**: `FeasibilityRules` remains the sole authority for recommendation status (`PROCEED`, `VALIDATE_FIRST`, `RECONSIDER`).
- **Explainability Layer**: Traces all conditions evaluated (Operating surplus, Solvency DSCR, Strong DSCR buffer, Financial viability, Catchment competitor density, Coverage confidence).
- **Confidence Model**: Discrete quality indicators (`HIGH`, `MEDIUM`, `LOW`, `UNKNOWN`) representing evidence data reliability / calculation basis, NOT probability of business success or loan approval.
- **Actionable Verification Checklist**: Dynamically synthesized from unresolved `NEEDS_VERIFICATION` items and applicant assumptions to provide pre-borrowing due diligence.
- **AI Safety & Grounding**: AI Explainer receives the structured decision trace and financial metrics; AI failure falls back cleanly to deterministic explanation.

---

## 4. Step 4I — Pre-Loan Action Plan & Bank-Readiness

```text
Evidence Ledger + FeasibilityRules + Scheme Match + Risk Analysis
       ↓
ActionPlanGenerator.generate_action_plan()
       ↓
ActionPlan (Prioritized, Traceable Actions with ActionSource & Related IDs)
       ↓
ActionPlanGenerator.generate_document_readiness()
       ↓
DocumentReadiness (Derived strictly from verified scheme prerequisites)
       ↓
ActionPlanGenerator.generate_bank_readiness()
       ↓
BankReadiness (5 Dimensions: FINANCIAL_CASE, MARKET_EVIDENCE, SCHEME_FIT, DOCUMENT_READINESS, ASSUMPTION_QUALITY)
```

- **Core Principle**: **Evidence → Calculate → Explain → Decide → Act**
- **Action Traceability**: Every generated `ActionItem` contains explicit `related_evidence_ids`, `related_rule_ids`, and `action_source` (`DECISION_TRACE`, `EVIDENCE_LEDGER`, `VERIFICATION_CHECKLIST`, `FINANCIAL_RESULT`, `SCHEME_RESULT`, `MARKET_RESULT`).
- **Recommendation-Specific Roadmaps**:
  - `PROCEED`: Targeted finalization actions (capital structure review, scheme prerequisites, repayment stress check).
  - `VALIDATE_FIRST`: Unresolved assumption & market verification actions (footfall counts, competitor walk, selling price distinction).
  - `RECONSIDER`: Business restructuring actions (rework capex/fixed costs, break-even reassessment, smaller financing exploration).
- **Document Readiness Safety**: No universal documents inferred from capex or loan size; document checklist is synthesized strictly from matched scheme guidelines and verified statutory conditions.
- **Bank-Readiness Dimensions**: 5 deterministic categories evaluated as `READY`, `PARTIALLY_READY`, `NOT_READY`, or `UNKNOWN`. Clearly disclaimed as preparation for lender discussion, **NOT** loan approval probability, credit score, or success likelihood.
- **Action Completion Invariant**: UI `TODO → COMPLETED` toggle is strictly local task tracking; completing an action does not mutate underlying financial formulas or recommendation status without re-running analysis.

---

## 5. Step 4J — Scenario Lab ("Test Before You Borrow")

```text
Baseline Analysis (Immutable) + User Scenario Overrides
       ↓
FinancialService.calculate() (Reused)
       ↓
FeasibilityRules.evaluate_with_trace() (Reused)
       ↓
ScenarioComparator.evaluate_scenario()
       ↓
Deterministic Metric Deltas + Rule Comparison + Recommendation Change
       ↓
Frontend Side-by-Side Comparison Table + "What Changed?" & "Why Did It Change?"
```

- **Core Principle**: **Evidence → Calculate → Explain → Decide → Act → Test**
- **Financial & Rule Engine Reuse**: Reuses existing `FinancialService.calculate()` and `FeasibilityRules.evaluate_with_trace()`. Zero duplicate formulas or alternative threshold logic.
- **Baseline Immutability**: Baseline metrics, recommendation status, decision trace, and evidence ledger remain strictly read-only and immutable. Scenarios are evaluated in isolated sandboxes.
- **Market Invariance**: Geospatial competitor counts, census demographics, and mandi prices remain invariant across scenario evaluations.
- **Deterministic Delta Calculations**: `ScenarioComparator` computes absolute and percentage differences between baseline and scenario metrics with safe zero-denominator handling.
- **Safety Boundaries**: No credit scoring, no loan approval probabilities, no automated loan optimization or "optimal loan" recommendations.
- **Clear Distinction**: Explicit separation between **Scenario Lab** (user-driven assumptions) and **Sensitivity Analysis** (predefined stress shocks).

---

## 6. Step 5A — Full Local-Language i18n Engine

```text
User Language Selection (LanguageToggle / SessionStorage)
       ↓
LanguageProvider Context (React Context & window CustomEvent synchronization)
       ↓
useTranslation() Hook [ t("path.to.key", params) ]
       ↓
Canonical English Key Schema (en.ts) ↔ 100% Parity Indicator Dictionaries (hi, mr, bn, te, ta)
       ↓
Seamless Localization across 100% of User Journey:
  - Landing (/)
  - Onboarding (/onboarding) Wizard (Profile, Location, Business, Financial)
  - Analysis Loading State (/analysis/loading)
  - Results (/results) Dashboard (Feasibility, Financials, Market, Trace, Plan, Lab)
  - Schemes Directory (/schemes)
  - Common Headers, Footers, Modals, Loading, Error & Retry States
```

### 1. Supported Languages
1. **English** (`en`) — Canonical standard
2. **Hindi** (`hi`) — हिन्दी
3. **Marathi** (`mr`) — मराठी
4. **Bengali** (`bn`) — বাংলা
5. **Telugu** (`te`) — తెలుగు
6. **Tamil** (`ta`) — தமிழ்

### 2. Language State Flow & Architecture
- **Single Source of Truth**: `LanguageProvider` wraps the application in `app/layout.tsx`.
- **Session Persistence**: Language selection persists across page refreshes and route transitions via `sessionStorage` key `gramavise_language`.
- **Inter-Component Synchronization**: The existing `LanguageToggle.tsx` seamlessly dispatches and listens to the `gramavise_language_changed` `CustomEvent`, synchronizing with `LanguageProvider` state.
- **Backend AI Payload Propagation**: The active `preferred_language` (`en`, `hi`, `mr`, `bn`, `te`, `ta`) is forwarded to `/api/v1/analyze` so the backend vernacular explanation engine generates AI narratives in the matching user language.

### 3. Translation Key Schema & Parity Enforcement
- **Canonical English Dictionary**: `frontend/lib/i18n/dictionaries/en.ts` defines 226 translation keys covering all user-facing strings.
- **100% Key Parity**: All 5 Indic dictionaries (`hi.ts`, `mr.ts`, `bn.ts`, `te.ts`, `ta.ts`) maintain identical hierarchical structure and 100% key parity with `en.ts`.
- **Automated Verification**: Enforced via `npm run test:i18n` and `backend/tests/services/test_i18n_parity.py`.
- **Deterministic Fallback**: If a key path is unresolved, `t(path)` safely falls back to the English dictionary, and then to the raw path string to eliminate runtime rendering crashes.

### 4. Statutory & Financial Preservation Rules
- **Recommendation Status Tokens**: `PROCEED`, `VALIDATE_FIRST`, and `RECONSIDER` remain strictly unchanged across all languages.
- **Evidence Provenance Tokens**: `OBSERVED`, `CALCULATED`, `MODELLED`, `ASSUMED`, and `NEEDS_VERIFICATION` are preserved as immutable statutory markers.
- **Official Programs & Sources**: `PMEGP`, `MUDRA`, `PMFME`, `LGD`, `Census 2011`, `Agmarknet / DMI`, and `OpenStreetMap` retain their authoritative identifiers.
- **Financial Notation**: Indian Rupee currency symbol `₹` and percentage sign `%` remain standard and uncorrupted across all locales.
- **Financial Safety**: Zero modifications to `FinancialService` calculations, `FeasibilityRules` thresholds, scenario evaluators, or provider boundaries.

---

## 7. Step 5B — Low-Literacy Financial Analogies & Plain-Language Summaries

```text
Results Page Financial Area
       ↓
[ Simple View ] (Default) ◄─────── Toggle ───────► [ Detailed View ]
       ↓                                                  ↓
PlainLanguageSummary.tsx                           Technical Financial Grid
  - Monthly Money In (Gross Revenue)                 - Total Capex (₹)
  - Estimated Monthly Take-Home (Net Profit)          - Monthly Gross Profit (₹)
  - Loan Repayment Cushion (DSCR interpretation)      - Fixed Overheads (₹) & EMI (₹)
  - Direct Production & Stock Cost (Variable Cost %)  - DSCR Metric & Buffer
  - Break-Even Customer Daily Comparison Bar          - Cost & Revenue Breakdown Table
```

### 1. Architectural Invariants
- **Zero Frontend Financial Arithmetic**: Frontend React components perform zero arithmetic calculations (e.g. no `revenue = customers * price * days` or `buffer = expected - breakeven`). All values rendered originate from backend `FinancialResult` or `FinancialAssumptions`.
- **Sole Source of Truth**: `FinancialService` remains the sole mathematical engine, and `FeasibilityRules` remains the sole decision authority.
- **Provenance Integrity**: Explicitly retains data origin labels (`ASSUMED` for user inputs, `CALCULATED` for derived unit economics).

### 2. Everyday Business Explanations
- **Monthly Revenue**: "About ₹{amount} comes into the business each month based on your expected customers, average sale, and working days."
- **Net Profit**: "What remains after your business costs and monthly loan payment. Based on your inputs, the model estimates ₹{amount} per month."
- **Loan Repayment Cushion (DSCR)**:
  - *Standard*: "Your business generates about ₹{dscr} before loan payment for every ₹1 of monthly loan payment."
  - *Debt-Free*: `N/A (Debt-Free)` ("Your business does not require a monthly bank loan repayment.")
- **Direct Variable Cost**: "About ₹{pct} of every ₹100 in sales goes toward direct production or stock costs."

### 3. Visual Break-Even Guidance & Accessibility
- **Daily Customer Comparison**: Directly contrasts `customers_per_day` (`ASSUMED`) with `break_even_units_daily` (`CALCULATED`).
- **Accessible Visual Bars**: Styled proportionally with CSS, with high-contrast text and numerical values visible in text and ARIA attributes.
- **Explicit Context Messages**: Textual and icon indicators clearly announce whether expected customers are above or below break-even level without relying on color alone.
- **Semantic Toggle**: Screen-reader and keyboard accessible `[ Simple View ]` / `[ Detailed View ]` switch using `role="tablist"` and `role="tab"`.

---

## 8. Step 5C — "Explain This Number" Inspector

```text
Financial Result / Scenario Result
        ↓
FinancialService.calculate() (Deterministic Math Engine)
        ↓
FinancialExplainer.generate_explanations() (Declarative Metadata Assembly)
        ↓
explanations: Record<string, NumberExplanation> (Attached to /api/v1/analyze & /api/v1/analyze/scenario)
        ↓
ExplainNumberModal.tsx (Accessible React Dialog - ZERO Financial Math)
  - Plain Meaning ("What does this number mean?")
  - Formula & Substituted Calculation ("Formula & Step-by-Step trace")
  - Input Variables & Data Provenance (ASSUMED, CALCULATED, OBSERVED)
  - Supporting Evidence IDs (Agmarknet, Schemes, OSM)
  - Practical Limitations & Caveats
```

### 1. Architectural Invariants
- **FinancialService as Sole Calculator**: `FinancialExplainer` does not duplicate, recalculate, or modify any financial formula. It strictly consumes existing calculation results and inputs from `FinancialService`.
- **Declarative Only**: Assembles human-readable explanation metadata (`NumberExplanation`) including formula labels, mathematical expressions with substituted values, provenance tags, and limitations.
- **Zero Frontend Arithmetic**: The frontend UI (`ExplainNumberModal.tsx`, `MetricCard.tsx`, `FinancialSummary.tsx`, `ScenarioLabSection.tsx`) performs zero financial arithmetic. It renders backend-provided values, expressions, and steps.
- **Debt-Free DSCR Consistency**: For debt-free profiles (`monthly_emi = 0`), DSCR is presented as `N/A (Debt-Free)` with an explicit explanation that the business has no debt repayment obligations.
- **Baseline Immutability**: In Scenario Lab, baseline explanations remain completely untouched. Scenario explanations are generated with `is_scenario=True` and identify overridden parameters as `Scenario Override`.
- **No External Causality Fabrication**: User assumptions remain `ASSUMED`. Market evidence (e.g. Agmarknet Mandi prices) remains `OBSERVED` supporting context and is never claimed to calculate user prices or revenues.---

## 9. Step 5D — Controlled Voice Input

```text
Web Speech API / SpeechRecognition (Browser-handled)
        ↓ Transcript string (e.g., "2.5 lakh", "50 thousand rupees", "₹50,000")
Deterministic Numeric Parser (Zero AI / Zero LLM / Local RegEx & Word Map)
        ↓ ParseResult (SUCCESS, AMBIGUOUS, OUT_OF_RANGE, INVALID)
Field-Specific Validation Config (Range checks & existing form rules)
        ↓
VoiceConfirmationModal.tsx (Zero Silent Commits / Explicit User Selection)
   - Candidate Value Displayed vs Current Value
   - Explicit Actions: [Use this value] | [Try again] | [Enter manually]
        ↓ Upon explicit user confirmation
Existing React Form State & autoritative Form Validation
        ↓
FinancialService (Sole Deterministic Calculator)
```

### 1. Architectural Invariants & Boundaries
- **Input Convenience Layer Only**: Voice is strictly an input convenience mechanism. It has zero authority over financial calculations, feasibility rules, recommendation logic, or credit assessment.
- **Zero AI / Zero External Voice Parsing**: The numeric parser runs entirely locally in the client browser using deterministic regex and magnitude word tokenizers (`lakh`, `crore`, `thousand`, `हजार`, `लाख`, etc.). Raw audio is never sent to an AI parsing service or stored by GramaVise.
- **Privacy & Quality Transparency**: Accurately discloses that speech recognition is handled by the user's browser engine, audio is not recorded/stored by GramaVise, and transcript quality is device/network dependent.
- **Zero Silent Commits**: Candidate values are NEVER silently written to form state. Every voice input requires explicit user confirmation via `VoiceConfirmationModal.tsx`.
- **Controlled Field Rollout**: All 12 financial fields are supported by the parser architecture, with voice buttons activated on the safest 8 numeric onboarding inputs (`own_capital`, `desired_loan`, `startup_cost`, `equipment_cost`, `inventory_cost`, `monthly_fixed_cost`, `customers_per_day`, `avg_ticket_price`).
- **Conservative Ambiguity Policy**: When transcripts are uncertain (e.g. standalone small integers like "50" on a large capital field), the parser returns `AMBIGUOUS` or `INVALID` rather than guessing.
- **100% i18n Dictionary Parity**: All voice status messages, modal notices, and aria labels are translated across all 6 supported languages (`en`, `hi`, `mr`, `bn`, `te`, `ta`).

---

## 10. Step 5E — Mobile + Poor-Network / Low-Connectivity UX

```text
Onboarding State / Form Inputs
        ↓ Debounced Autosave (300ms)
Durable Local Draft Storage (`gramavise_draft_v1` in localStorage)
        ├─ Schema Versioned (v1) & 7-Day Auto-Expiry
        ├─ Data-Minimized (Zero Passwords, Aadhaar, PAN, or Audio)
        └─ Preserved across Page Refresh & Language Switches
                 ↓
Analysis Initiation (Submit Lock + Online Check)
        ↓ 25-Second AbortController Timeout (apiClient)
POST /api/v1/analyze
        ├─ Online (200 OK) ──> Cache result timestamp -> Retain draft until handoff -> /results
        ├─ Timeout (25s)   ──> Abort -> ErrorState with preserved draft & non-destructive retry
        ├─ Offline / Drop  ──> Catch TypeError -> NetworkStatusBar alert -> Safe editing
        └─ Server Error    ──> Classified ApiError -> Preserved draft
                 ↓
Results Dashboard / Historical Offline Snapshot
        └─ If offline / cached: Explicit `🕒 Historical Snapshot` Badge with Timestamp & Freshness Warning
```

### 1. Architectural Invariants & Resilience Principles
- **No Fake Offline Intelligence**: Offline mode supports form filling, local boundary validation, language toggling, and draft persistence. It **NEVER** estimates, computes, or fabricates offline financials, EMI, profit, DSCR, break-even, market evidence, or scheme eligibility.
- **Durable Data-Minimized Drafts**: `draftStorage.ts` saves user business assumptions locally. Drafts are safely restored via `DraftRecoveryBanner.tsx` with explicit `[Continue]` and `[Start Fresh]` options.
- **Client-Side Timeout Policy**: `apiClient` enforces a 25-second `AbortController` timeout for transparent user recovery without indefinite blocking.
- **Double-Submission Protection**: Analysis submit buttons are immediately locked upon execution to prevent duplicate requests on laggy mobile screens.
- **Historical Evidence Transparency**: Previously calculated results viewed offline display an explicit timestamped historical snapshot badge, ensuring users are never misled into treating old mandi prices or competitor counts as live intelligence.
- **Offline Scenario Lab Guard**: When offline, Scenario Lab controls remain editable locally, but recalculation is safely blocked with a clear localized requirement for internet connectivity.

