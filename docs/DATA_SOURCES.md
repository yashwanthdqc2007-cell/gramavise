# Data Sources & Evidence Provenance Foundation — GRAMAVISE

> **Statutory Notice & Disclaimer**
> Government scheme and market information is informational and requires verification with official scheme authorities, APMCs, and local ground surveys. Final sanctions, subsidies, and credit approvals are subject to formal verification by financing institutions and regulatory bodies.

---

## 1. Evidence Provenance Architecture

GramaVise implements a strict provenance hierarchy to ensure complete auditability, preventing fabricated data from being misrepresented as verified ground truth:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                            EVIDENCE PROVENANCE                              │
├──────────────────────┬──────────────────────────────────────────────────────┤
│ Classification       │ Definition & Operational Scope                       │
├──────────────────────┼──────────────────────────────────────────────────────┤
│ CALCULATED           │ Deterministic outputs from the audited Financial     │
│                      │ Engine formulas (Revenue, Margins, EMI, Break-Even). │
├──────────────────────┼──────────────────────────────────────────────────────┤
│ OBSERVED             │ Verifiable statutory rules, LGD codes, Census 2011,  │
│                      │ Agmarknet mandi prices, OSM POIs, and Udyam data.    │
├──────────────────────┼──────────────────────────────────────────────────────┤
│ MODELLED             │ Statistical estimates, simulations, or prototype     │
│                      │ mock indicators (e.g. geometric catchment model).    │
│                      │ MUST be labelled [DEMO / PROTOTYPE DATA].            │
├──────────────────────┼──────────────────────────────────────────────────────┤
│ ASSUMED              │ Self-declared applicant inputs (footfall, ticket     │
│                      │ price, working days) requiring local verification.   │
├──────────────────────┼──────────────────────────────────────────────────────┤
│ NEEDS_VERIFICATION   │ Preconditions where applicant data is missing,       │
│                      │ commodities unmapped, or rural OSM coverage low.     │
└──────────────────────┴──────────────────────────────────────────────────────┘
```

---

## 2. Verified Statutory Scheme Sources (Step 4A)

### A. Prime Minister's Employment Generation Programme (PMEGP)
- **Nodal Ministry**: Ministry of Micro, Small and Medium Enterprises (MSME)
- **Implementing Agency**: Khadi and Village Industries Commission (KVIC)
- **Authoritative Portal**: [https://www.pmegp.msme.gov.in/](https://www.pmegp.msme.gov.in/) | [https://msme.gov.in/](https://msme.gov.in/)
- **Scope & Project Cost Ceilings**:
  - Manufacturing: Up to ₹50,00,000 (₹50 Lakh)
  - Services / Business: Up to ₹20,00,000 (₹20 Lakh)
  - Exclusively for setting up **new micro-enterprises (Greenfield)**
- **Margin Money Subsidy Structure**:
  - General Category (Rural): 25% subsidy, 10% own equity contribution
  - Special Category (Rural - SC/ST/OBC/Women/Minorities/Ex-Servicemen): 35% subsidy, 5% own equity contribution
  - General Category (Urban): 15% subsidy, 10% own contribution
  - Special Category (Urban): 25% subsidy, 5% own contribution

---

### B. Pradhan Mantri MUDRA Yojana (PMMY)
- **Nodal Ministry**: Department of Financial Services (DFS), Ministry of Finance
- **Authoritative Portal**: [https://financialservices.gov.in/pradhan-mantri-mudra-yojana-pmmy](https://financialservices.gov.in/pradhan-mantri-mudra-yojana-pmmy)
- **Scope**: Institutional credit up to ₹20 Lakh for non-corporate, non-farm micro and small enterprises.
- **Tiers & Caps**:
  1. **Shishu**: Loans up to ₹50,000 (0% margin, zero collateral)
  2. **Kishore**: Loans from ₹50,001 to ₹5,00,000 (up to 15% margin, zero third-party collateral)
  3. **Tarun**: Loans from ₹5,00,001 to ₹10,00,000 (up to 15% margin, zero third-party collateral)
  4. **Tarun Plus**: Loans from ₹10,00,001 to ₹20,00,000 (strictly requires verified prior Tarun repayment)

---

### C. PM Formalisation of Micro Food Processing Enterprises (PMFME)
- **Nodal Ministry**: Ministry of Food Processing Industries (MoFPI)
- **Authoritative Portal**: [https://pmfme.mofpi.gov.in/](https://pmfme.mofpi.gov.in/) | [https://www.mofpi.gov.in/](https://www.mofpi.gov.in/)
- **Scope**: Credit-linked capital subsidy for individual micro food processing enterprises.
- **Subsidy Structure**:
  - Credit-linked capital subsidy at **35% of eligible project cost**
  - Statutory subsidy ceiling: **Maximum ₹10,00,000 (₹10 Lakh)** per individual unit
  - Minimum **10% beneficiary contribution**; balance financed through institutional bank loan

---

## 3. Official ODOP Master Registry (Step 4D)
- **Nodal Ministry**: Ministry of Food Processing Industries (MoFPI)
- **Dataset**: MoFPI PMFME One District One Product Master Registry
- **Coverage**: 713 districts in 35 States/UTs.

---

## 4. Local Government Directory & Census 2011 (Step 4E)
- **LGD Authority**: Ministry of Panchayati Raj ([https://lgdirectory.gov.in/](https://lgdirectory.gov.in/))
- **Census Authority**: Office of the Registrar General & Census Commissioner, India ([https://censusindia.gov.in/](https://censusindia.gov.in/))

---

## 5. Official Agmarknet Mandi Price Evidence (Step 4F)
- **Authority**: Directorate of Marketing & Inspection (DMI), Department of Agriculture & Farmers Welfare, Ministry of Agriculture & Farmers Welfare
- **Portal**: [https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi](https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi)

---

## 6. OpenStreetMap & Udyam Competitor / Location Evidence (Step 4G)

### A. OpenStreetMap / Overpass API (Hyper-Local Nearby Commercial POIs)
- **Source**: OpenStreetMap Contributors / Overpass API
- **Portal**: [https://www.openstreetmap.org/](https://www.openstreetmap.org/) | [https://overpass-api.de/api/interpreter](https://overpass-api.de/api/interpreter)
- **License**: Open Database License (ODbL)
- **Scope**: Mapped commercial amenities, shops, and craft units within configured straight-line radius (default 5 km Haversine distance).
- **Matching Methodology**:
  - Conservative deterministic rule engine matching OSM tags (`amenity`, `shop`, `craft`, `cuisine`) to enterprise categories.
  - Classifies into `DIRECT` (direct competitors), `ADJACENT` (contextual competition), and `UNRELATED` (excluded).
- **Coverage-Aware Interpretation**:
  - Rural and informal micro-units may be unmapped in OSM.
  - 0 mapped units does **NOT** prove absence of competition; it emits `Coverage Confidence: LOW` and `NEEDS_VERIFICATION`.
  - Every competitor section displays a mandatory coverage disclaimer.
- **Prohibited Practices**:
  - No scraping of Google Maps, Justdial, Yelp, IndiaMART, or private directories.
  - No synthetic fallback names in production (`Prototype Competitor A`).

### B. Udyam OGD Data (District-Level Formal MSME Context)
- **Authority**: Ministry of Micro, Small and Medium Enterprises (MoMSME) / data.gov.in
- **Portal**: [https://udyamregistration.gov.in/](https://udyamregistration.gov.in/)
- **Scope**: District-level formal MSME registration aggregates (total, micro, small, medium, manufacturing, services breakdown).
- **Crucial Boundary**:
  - Labeled explicitly as `DISTRICT_LEVEL_CONTEXT`.
  - Strictly separated from nearby competitor counts.
  - Never converted into a statement such as *"X competitors within 5 km"*.

---

## 7. Step 4I — Pre-Loan Action Plan & Bank-Readiness

### A. Pre-Loan Action Plan Generation
- **Source of Truth**: Consumes existing analysis outputs (`financial_result`, `market_result`, `scheme_result`, `evidence_ledger`, `decision_trace`, `verification_checklist`, `risks`).
- **Traceability**: Every action carries `action_source`, `related_evidence_ids`, and `related_rule_ids`.
- **Action Categories**: `FINANCIAL`, `MARKET`, `SCHEME`, `DOCUMENTATION`, `BUSINESS_OPERATIONS`, `VALIDATION`.
- **Priority Levels**: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.

### B. Document Readiness
- **Rule of Provenance**: Document items are generated **only** from explicitly supported existing scheme evidence and verified statutory criteria.
- **Safety Boundary**: No universal bank document checklist is inferred from loan amount or capex.
- **Statuses**: `REQUIRED`, `VERIFY`, `NOT_REQUIRED`, `UNKNOWN`.

### C. Bank-Readiness Evaluation
- **Dimensions**: Evaluated across 5 deterministic categories:
  1. `FINANCIAL_CASE`: Positive net profit and DSCR solvency benchmarks.
  2. `MARKET_EVIDENCE`: Mapped competitor coverage and local survey verification.
  3. `SCHEME_FIT`: Verified match with central credit/subsidy schemes.
  4. `DOCUMENT_READINESS`: Completeness of scheme-supported prerequisites.
  5. `ASSUMPTION_QUALITY`: Distinction between self-declared assumptions and verified ground truth.
- **Strict Independence Disclaimer**: Readiness assesses case completeness for lender exploration; it is **NOT** loan approval probability, credit score, or success guarantee.

