# Hyper-Local Market Evidence Architecture — GRAMAVISE

> **Core Principle**
> **"Absence of market evidence is not evidence of market demand."**
> Market data in rural catchments is frequently sparse, delayed, or unmapped. GramaVise never fabricates real-time business presence or local consumer spending. Any data without an authoritative, verified ground-truth feed is explicitly marked as `MODELLED` or `NEEDS_VERIFICATION`.

---

## 1. Market Evidence Provenance Taxonomy

Every market metric, catchment observation, and competitive indicator is assigned an immutable provenance class:

| Classification | Meaning & Scope in Market Layer | Example Indicator |
| :--- | :--- | :--- |
| **`OBSERVED`** | Direct, factual observation from an authorized registry or physical provider. | Official APMC Mandi commodity rates, Census 2011 village population. |
| **`CALCULATED`** | Mathematical derivation from audited inputs and formulas. | Required Break-Even customer transactions per day. |
| **`MODELLED`** | Statistical estimations, radius spatial models, or prototype demo data. | Catchment population radius estimate, simulated competitor density. |
| **`ASSUMED`** | Unverified self-declarations provided by the entrepreneur during onboarding. | Stated expected customers per day (e.g., 25 orders/day), expected ticket price. |
| **`NEEDS_VERIFICATION`** | Critical data points where no authoritative local source exists. | Local raw material price bands, unmapped village informal competitors. |

---

## 2. Geography Levels & Spatial Scope

Market indicators operate across structured hierarchical geographic layers:

```text
NATIONAL  ────────► All-India baseline benchmarks / Central scheme rules
   │
 STATE     ────────► State MSME policies, regional APMC guidelines
   │
DISTRICT  ────────► District Lead Bank credit limits, ODOP classifications
   │
 BLOCK     ────────► Taluka/Tehsil hub supply chains & weekly haat markets
   │
VILLAGE   ────────► Gram Panchayat resident population, local shops
   │
CATCHMENT ────────► 3km - 10km spatial radius around proposed enterprise unit
```

---

## 3. Confidence Framework

GramaVise evaluates reliability using a 4-tier transparent confidence matrix:

| Confidence Level | Criteria | Example Data Point |
| :--- | :--- | :--- |
| **`HIGH`** | Sourced directly from official government gazettes, Census data, or authenticated bank registers. | Statutory scheme ceilings (PMEGP ₹50L), verified loan interest rate. |
| **`MEDIUM`** | Secondary verified databases, aggregated open maps with regular updates. | Mapped bank branch locations, state highway proximity. |
| **`LOW`** | Prototype simulation models, unverified spatial algorithms, or self-reported assumptions. | Catchment competitor simulation (`[DEMO / PROTOTYPE DATA]`), user footfall assumption. |
| **`UNKNOWN`** | Completely unmapped data requiring on-ground physical field survey. | Local unorganized vendor price list, seasonal agricultural haat volume. |

---

## 4. Current Mock / Prototype Provider Policy

For offline hackathon demonstrations and prototype development:
1. **Clear Synthetic Identification**: All mock competitors use synthetic labels (e.g. `"Prototype Competitor A (Category) [DEMO]"`). Real local shop names are never invented.
2. **Zero Fake URLs**: No simulated Google Maps, Google Places, or phone listings are generated.
3. **Explicit Provenance Tags**:
   - `evidence_type = MODELLED`
   - `source = "GramaVise Prototype Market Model"`
   - `notes = "[DEMO / PROTOTYPE DATA] Simulated competitor density within 5km radius."`
   - `verification_status = "UNVERIFIED_PROTOTYPE"`

---

## 5. Catchment & Price Benchmark Models

### Catchment Representation
- **Radius**: Standard 5.0 km rural economic zone.
- **Population & Households**: Derived from prototype geometric models; tagged `NEEDS_VERIFICATION`.
- **Methodology**: Stored explicitly in `CatchmentModel.methodology`.

### Price Benchmarks
- **Rule**: If an authoritative live APMC Mandi feed or Department of Consumer Affairs price feed is not active, price bands are returned with `evidence_type = NEEDS_VERIFICATION` and `confidence = 0.0`.
- **LLM Restriction**: Large Language Models are strictly prohibited from hallucinating local commodity rates.

---

## 6. Market Risk Signals (Advisory Only)

The market layer generates deterministic risk signals to guide the entrepreneur:
- `LOW_COMPETITION`: Zero or 1 mapped competitor in catchment.
- `MODERATE_COMPETITION`: 2 to 3 mapped units.
- `HIGH_COMPETITION`: $\ge$ 4 mapped units.
- `DEMAND_UNCERTAIN`: High dependence on unverified customer traffic.
- `PRICE_UNCERTAIN`: Volatile or unverified commodity price bands.
- `DATA_INSUFFICIENT`: Village catchment unmapped in official open registries.

> **CRITICAL RULE**: Market risk signals are advisory only. They do **not** override the deterministic financial feasibility decision (`PROCEED`, `VALIDATE_FIRST`, `RECONSIDER`) produced by the authoritative financial engine.

---

## 7. Future Real Data Provider Interface

The `MarketServiceInterface` is prepared for zero-friction future integrations:
- **Agmarknet / e-NAM API**: Official wholesale commodity prices (`OBSERVED`).
- **OpenStreetMap / Overpass API**: Geocoded commercial POIs and village roads (`OBSERVED`/`MEDIUM`).
- **Census 2011 / SECC Open Data**: Village household demographics (`OBSERVED`).
- **Lead District Bank Reports**: District Credit Potential Plans (PLP) from NABARD (`OBSERVED`).

---

## 8. Integrated Real Data Sources

### MoFPI PMFME ODOP (One District One Product) Master Registry (Step 4D)
- **Source**: Ministry of Food Processing Industries (MoFPI), Government of India / PMFME Portal ([https://mofpi.gov.in/pmfme/one-district-one-product](https://mofpi.gov.in/pmfme/one-district-one-product)).
- **Classification**: `OBSERVED` / `HIGH` confidence / `VERIFIED_SOURCE`.
- **Dataset**: Checked-in normalized snapshot of the official MoFPI/PMFME ODOP source.
- **Scope**: District-level statutory notified product mapping for 713 districts in 35 States/UTs.
- **Matching Semantics**:
  - Exact/tokenized regex boundary matching against normalized enterprise business category and description.
  - Aligned produce yields `PARTIALLY_ELIGIBLE` with ODOP alignment noted under PMFME.
  - Non-ODOP existing food micro-units remain `PARTIALLY_ELIGIBLE` as existing units producing other products may also be supported for upgradation.
  - Non-ODOP new food micro-units are marked `NOT_ELIGIBLE` as new units under PMFME are supported only for notified ODOP products.
  - Unmapped or ambiguous districts emit `NEEDS_VERIFICATION` without crashing.
- **Authority Boundary**: ODOP alignment is an eligibility/prioritization signal, NOT proof of subsidy eligibility. Commercial bank sanction and statutory verification remain necessary.

### Local Government Directory (LGD) — Ministry of Panchayati Raj (Step 4E)
- **Source**: Ministry of Panchayati Raj, Government of India ([https://lgdirectory.gov.in/](https://lgdirectory.gov.in/)).
- **Classification**: `OBSERVED` / `HIGH` confidence (`1.0`) / `VERIFIED_SOURCE`.
- **Dataset**: Checked-in verified snapshot/sample of official LGD administrative entities (`lgd_master.json`).
- **Scope**: Administrative entity identification and authentic LGD codes across State, District, Sub-District, and Village levels.
- **Authority Scope**: Validates administrative entity existence and hierarchy; does not supply population or business statistics.

### Census of India 2011 — Primary Census Abstract (Step 4E)
- **Source**: Office of the Registrar General & Census Commissioner, India ([https://censusindia.gov.in/census.website/data/population-finder](https://censusindia.gov.in/census.website/data/population-finder)).
- **Classification**: `OBSERVED` / `HIGH` confidence (`1.0`) / `VERIFIED_SOURCE`.
- **Dataset**: Checked-in verified snapshot/sample of official Census 2011 PCA records (`census_2011_master.json`).
- **Scope**: Historical official resident population and household counts at village, sub-district, and district levels.
- **Explicit 2011 Caveat**:
  - `reference_year = 2011`, `data_status = "HISTORICAL_OFFICIAL"`.
  - **CRITICAL**: Census 2011 population is historical official evidence, NOT a current population estimate.
- **Catchment Independence**: Observed historical census records remain strictly separate from prototype geometric catchment models (`MODELLED`).

### Directorate of Marketing & Inspection (DMI) — Agmarknet / OGD Mandi Price Feed (Step 4F)
- **Source**: Directorate of Marketing & Inspection (DMI), Department of Agriculture & Farmers Welfare, Ministry of Agriculture & Farmers Welfare / Open Government Data (OGD) Platform ([https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi](https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi) / [https://agmarknet.gov.in/](https://agmarknet.gov.in/)).
- **Dataset Title**: "Current Daily Price of Various Commodities from Various Markets (Mandi)"
- **Classification**: `OBSERVED` / `HIGH` confidence (`1.0`) / `VERIFIED_SOURCE`.
- **Dataset**: Option B: Checked-in verified snapshot/sample of official Agmarknet / OGD mandi price observations (`mandi_prices_master.json`).
- **Price Semantics & Metrics**:
  - **Observed Mandi Modal Price**: Primary wholesale market benchmark (₹/quintal and converted ₹/kg).
  - **Reported Price Range**: Minimum to maximum wholesale auction price range observed on the reported arrival date.
  - **Arrival Date**: Actual date of observation in the mandi (e.g. "10 Sep 2024"). Never labeled as "current price" without date provenance.
- **Unit Handling & Normalization**:
  - Original source unit ("INR/quintal") preserved verbatim.
  - Explicit conversion strictly applied: 1 quintal = 100 kg ($\text{price per kg} = \text{modal price} / 100$).
- **Core Principle & Separation**:
  - *"Agmarknet/OGD market prices are reference market observations and are not retail selling-price recommendations."*
  - Mandi wholesale rates are never substituted for user retail assumptions (`avg_ticket_price`), nor do they alter financial engine calculations (revenue, profit, EMI, DSCR, break-even) or feasibility recommendations (`PROCEED`, `VALIDATE_FIRST`, `RECONSIDER`).
- **Failure & Ambiguity Behavior**:
  - Unmapped commodities or markets outside the verified snapshot gracefully return `NEEDS_VERIFICATION`.

