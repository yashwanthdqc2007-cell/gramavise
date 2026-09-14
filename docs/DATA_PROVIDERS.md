# Real Data Provider Research & Integration Boundaries — GRAMAVISE

> **Core Architectural Principle**
> External data providers augment hyper-local context but **never** override the deterministic financial calculator or feasibility decision engine. If an external API is down, rate-limited, or unmapped, GramaVise falls back gracefully to `NEEDS_VERIFICATION` without crashing or fabricating proxy data.

---

## 1. Provider Layer Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                      External Data Source                   │
│   (Agmarknet / LGD / Census 2011 / MoFPI ODOP / OSM)        │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JSON API / Static Data
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      BaseDataProvider                       │
│    (Boundary Isolation: Timeout, Rate Limit, Error Catch)   │
└──────────────────────────────┬──────────────────────────────┘
                               │ Normalization
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                       ProviderResult                        │
│   (success, evidence_items, observed_at, expires_at)        │
└──────────────────────────────┬──────────────────────────────┘
                               │ Evidence Classification
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     EvidenceCollector                       │
│    (OBSERVED / CALCULATED / MODELLED / NEEDS_VERIFICATION)  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  POST /api/analyze Response                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Integrated Official Sources

### A. Ministry of Food Processing Industries (MoFPI) — PMFME ODOP Registry (Step 4D)
- **Source URL**: [https://pmfme.mofpi.gov.in/](https://pmfme.mofpi.gov.in/) / [https://mofpi.gov.in/pmfme/one-district-one-product](https://mofpi.gov.in/pmfme/one-district-one-product)
- **Publication**: Approved National One District One Product (ODOP) Master List
- **Nodal Ministry**: Ministry of Food Processing Industries, Government of India
- **Dataset Path**: `backend/app/data/odop/odop_national_master.json` (Checked-in normalized snapshot of the official MoFPI/PMFME ODOP source covering 713 districts in 35 States/UTs)
- **Normalization Policy**:
  - State aliases (e.g. `MP` / `M.P.` $\rightarrow$ `Madhya Pradesh`, `MH` $\rightarrow$ `Maharashtra`, `UP` $\rightarrow$ `Uttar Pradesh`) normalized deterministically.
  - District suffixes (`District`, `Dist.`, `Taluka`) stripped before matching.
  - Ambiguous or non-resolving names return `NEEDS_VERIFICATION`.
- **Scheme Matching Semantics (MoFPI Official Distinction)**:
  - **ODOP-Aligned New/Existing Unit**: Enterprise category & activities match notified district produce $\rightarrow$ Reason states *"District ODOP alignment observed"* with prioritization.
  - **Non-ODOP Existing Food Unit**: Existing individual micro-units producing other products may also be supported under PMFME for upgradation.
  - **Non-ODOP New Food Unit**: New individual/group units under PMFME are supported only for notified ODOP products; unaligned new enterprises are marked `NOT_ELIGIBLE`.
  - **Unmapped District / Insufficient Facts**: Returns `PARTIALLY_ELIGIBLE` with `NEEDS_VERIFICATION` for on-ground verification.
- **Important Non-Overclaiming Guarantee**:
  - An ODOP match is **not** an eligibility sanction. It is classified as `OBSERVED` alignment, while statutory eligibility remains `PARTIALLY_ELIGIBLE` pending bank credit appraisal.

### B. Local Government Directory (LGD) — Ministry of Panchayati Raj (Step 4E)
- **Source URL**: [https://lgdirectory.gov.in/](https://lgdirectory.gov.in/) / [https://data.gov.in/catalog/local-government-directory-lgd](https://data.gov.in/catalog/local-government-directory-lgd)
- **Authority**: Ministry of Panchayati Raj, Government of India
- **Dataset Path**: `backend/app/data/geo/lgd_master.json` (Checked-in verified snapshot/sample of official LGD administrative entities)
- **Core Function**: Answers *"Is this state/district/sub-district/village an identifiable administrative entity?"*
- **Provenance**: `OBSERVED` / `HIGH` confidence (`1.0`) / `VERIFIED_SOURCE`
- **Fields Extracted**: `state_name`, `state_lgd_code`, `district_name`, `district_lgd_code`, `sub_district_name`, `sub_district_lgd_code`, `village_name`, `village_lgd_code`.
- **Failure Behavior**: If village is outside the snapshot, returns verified district-level identity with `NEEDS_VERIFICATION` for the unmapped village.

### C. Census of India 2011 — Primary Census Abstract (Step 4E)
- **Source URL**: [https://censusindia.gov.in/census.website/data/population-finder](https://censusindia.gov.in/census.website/data/population-finder) / [https://censusindia.gov.in/nada/index.php/catalog/42555](https://censusindia.gov.in/nada/index.php/catalog/42555)
- **Authority**: Office of the Registrar General & Census Commissioner, India
- **Dataset Path**: `backend/app/data/demographics/census_2011_master.json` (Checked-in verified snapshot/sample of official Census 2011 PCA records)
- **Core Function**: Answers *"What population and household counts were recorded for that entity in Census 2011?"*
- **Explicit 2011 Handling**:
  - `reference_year = 2011`
  - `data_status = "HISTORICAL_OFFICIAL"`
  - `evidence_type = OBSERVED` / `confidence = 1.0 (HIGH)`
  - **CRITICAL**: Census 2011 population is historical official evidence, NOT a current population estimate.
- **Independence Guarantee**: Observed Census 2011 records remain strictly distinct from prototype geometric catchment models (`MODELLED`).

### D. Directorate of Marketing & Inspection (DMI) — Agmarknet / OGD Mandi Price Feed (Step 4F)
- **Source URL**: [https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi](https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi) / [https://agmarknet.gov.in/](https://agmarknet.gov.in/)
- **Dataset Title**: "Current Daily Price of Various Commodities from Various Markets (Mandi)"
- **Source Department**: Directorate of Marketing & Inspection (DMI), Department of Agriculture & Farmers Welfare, Ministry of Agriculture and Farmers Welfare
- **Dataset Path**: `backend/app/data/pricing/mandi_prices_master.json` (Option B: Checked-in verified snapshot/sample of official Agmarknet / OGD mandi price observations)
- **Extraction Date / Version**: Extraction Date 2024-09-12 / Publication Version "Agmarknet Daily Mandi Price Snapshot 2024"
- **Coverage**: Verified sample snapshot of major agricultural markets across Maharashtra, Madhya Pradesh, Uttar Pradesh, Rajasthan, Bihar, and Karnataka (covering Tomato, Onion, Garlic, Wheat, Chilli, Potato, Soybean, Banana, and Kodo Millet).
- **Core Function**: Answers *"What agricultural commodity prices were observed in reported agricultural markets on the reporting date?"*
- **Price Semantics & Fields**:
  - `min_price`: Minimum reported wholesale market price (₹/quintal)
  - `max_price`: Maximum reported wholesale market price (₹/quintal)
  - `modal_price`: Observed mandi modal price (primary reference metric)
  - `price_unit`: Original reported unit ("INR/quintal")
  - `price_per_kg`: Derived price per kg strictly via documented unit conversion (1 quintal = 100 kg)
  - `arrival_date`: Exact observation date from official source (e.g., "2024-09-10")
- **Provenance Classification**:
  - Official OGD/Agmarknet record: `OBSERVED` / `HIGH` confidence (`1.0`) / `VERIFIED_SOURCE`
  - Unmapped / outside snapshot: `NEEDS_VERIFICATION`
- **Conservative Matching**:
  - Normalizes case, whitespace, and documented commodity synonyms (e.g. "tomato" / "tamatar" $\leftrightarrow$ "Tomato", "lahsun" $\leftrightarrow$ "Garlic").
  - Aggressive fuzzy matching is strictly rejected (e.g. "tomato sauce" or "garlic bread" never matches agricultural commodities).
- **Market Hierarchy**:
  1. Exact APMC market match in district & state
  2. District APMC market evidence
  3. State APMC market evidence
  4. Outside snapshot $\rightarrow$ `NEEDS_VERIFICATION`
- **Strict Separation from Financial Engine**:
  - Mandi prices are market observations and are never substituted for user retail prices (`avg_ticket_price`), nor do they alter financial engine formulas (revenue, profit, EMI, DSCR, break-even) or feasibility recommendations (`PROCEED`, `VALIDATE_FIRST`, `RECONSIDER`).
  - Mandatory disclaimer: *"Agmarknet/OGD market prices are reference market observations and are not retail selling-price recommendations."*

---

## 3. Comprehensive Candidate Sources Research

| Provider / Source | Data Category | Official URL | Geographic Resolution | Freshness / Frequency | Licensing & Usage | Safe to Integrate? | Integration Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MoFPI PMFME ODOP Master Registry** | ODOP Approved Products | [https://pmfme.mofpi.gov.in/](https://pmfme.mofpi.gov.in/) | 713 districts in 35 States/UTs | Annual / Gazetted notifications | Govt Official Public Gazette | **INTEGRATED (Step 4D)** | Checked-in normalized snapshot of the official MoFPI/PMFME ODOP source + `OdopDataProvider`. |
| **Local Government Directory (LGD)** | Geographic Hierarchy | [https://lgdirectory.gov.in/](https://lgdirectory.gov.in/) | Village / Sub-district / District / State | Quarterly updates | Open Govt Data (OGDL India) | **INTEGRATED (Step 4E)** | Checked-in verified snapshot/sample (`lgd_master.json`) + `GeoDataProvider`. |
| **Census of India 2011 (PCA)** | Village Demographics | [https://censusindia.gov.in/](https://censusindia.gov.in/) | Village / Ward level | Decennial (2011 base) | Public Domain / Open Data | **INTEGRATED (Step 4E)** | Checked-in verified snapshot/sample (`census_2011_master.json`) + `DemographicDataProvider`. |
| **Agmarknet / OGD Mandi Feed** | Agricultural Commodity Wholesale Prices | [https://data.gov.in/](https://data.gov.in/) / [https://agmarknet.gov.in/](https://agmarknet.gov.in/) | APMC Mandi / District | Daily / Periodic | Open Govt Data (OGDL India) | **INTEGRATED (Step 4F)** | Checked-in verified snapshot/sample (`mandi_prices_master.json`) + `PriceDataProvider`. |
| **Udyam MSME Registration Statistics** | Formal Micro-Enterprise Density | [https://udyamregistration.gov.in/](https://udyamregistration.gov.in/) | District level | Monthly open aggregates | Open Govt Data | **YES (Medium Priority)** | District-level formal micro-enterprise density baseline. |
| **OpenStreetMap (OSM / Overpass)** | Commercial POIs & Village Roadways | [https://www.openstreetmap.org/](https://www.openstreetmap.org/) | Coordinate / Point radius | Continuous community updates | ODbL (Open Database License) | **YES (Conditional)** | Semi-urban / taluka POIs. Tagged `MEDIUM` confidence in towns, `LOW` in interior villages. |

---

## 4. Explicitly Rejected Data Sources

The following sources were evaluated and **strictly rejected** from GramaVise:

1. **Google Maps / Google Places API**:
   - *Reason for Rejection*: Strict commercial terms prohibiting caching, storing, or offline usage for hackathons/micro-finance applications. Cost-prohibitive for rural credit cooperatives.
2. **Justdial / IndiaMART / Web Scraping**:
   - *Reason for Rejection*: Unofficial, anti-scraping protections, zero coverage of informal rural artisans, high risk of fake business data.
3. **LLM Synthetic Data Generation for Prices/Competitors**:
   - *Reason for Rejection*: Generates plausible-sounding hallucinations violating GramaVise's non-fabrication commitment.

---

## 5. Provider Failure & Fallback Policy

To ensure 100% operational resilience:
1. **Network Timeouts (HTTP > 3s)**: Provider wraps execution in a try-catch block and returns `ProviderResult(success=False, errors=["Timeout"])`.
2. **Empty / Incomplete Data**: If a district or village has no entry in the external database, the engine creates an `EvidenceItem` with `evidence_type = EvidenceType.NEEDS_VERIFICATION`.
3. **Zero Financial Impact**: Feasibility verdicts (`PROCEED`, `VALIDATE_FIRST`, `RECONSIDER`) remain deterministic based on audited financial inputs regardless of provider outages.

---

## 6. Security & Credential Hygiene

- All external API tokens (`DATA_GOV_IN_API_KEY`, etc.) are read exclusively via Pydantic `Settings` from environment variables (`.env`).
- Zero API keys are hardcoded in source code or test fixtures.
- Test suites run 100% offline without live network dependencies.
