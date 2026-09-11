# Data Sources & Providers — GRAMAVISE

## 1. Provider Abstraction Architecture

To maintain high testability and enable offline hackathon development, all external data sources are accessed through a unified interface:

```text
                  ┌──────────────────────┐
                  │     DataProvider     │
                  │     (Base Class)     │
                  └──────────┬───────────┘
                             │
     ┌───────────────────────┼───────────────────────┐
     │                       │                       │
     ▼                       ▼                       ▼
┌──────────────┐     ┌──────────────┐     ┌─────────────────────┐
│ OSMProvider  │     │ GovData      │     │ MarketPriceProvider │
│ (Overpass)   │     │ (myScheme)   │     │ (Agmarknet/Mandi)   │
└──────────────┘     └──────────────┘     └─────────────────────┘
     │                       │                       │
     └───────────────────────┼───────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
   ┌──────────────────────┐      ┌──────────────────────┐
   │  CachedDataProvider  │      │   DemoDataProvider   │
   │  (Redis / Local JSON)│      │  (Zero-Network Mock) │
   └──────────────────────┘      └──────────────────────┘
```

---

## 2. Data Provider Registry

| Provider | Purpose | Primary Endpoints / Sources | Fallback Provider |
| :--- | :--- | :--- | :--- |
| `OSMProvider` | Geocoding & Village amenity POIs | Nominatim / Overpass API | `DemoDataProvider` |
| `GovernmentDataProvider` | Scheme eligibility & subsidies | myScheme / Data.gov.in / PMEGP | `CachedDataProvider` |
| `MarketPriceProvider` | Mandi commodity prices & unit rates | Agmarknet open data | `DemoDataProvider` |
| `CensusProvider` | Village population & household counts | Census 2011 / SECC aggregates | `DemoDataProvider` |
| `CachedDataProvider` | Fast offline access to pre-fetched datasets | `data/processed/` local JSON | N/A |
| `DemoDataProvider` | Deterministic canned data for testing | `data/seeds/` | N/A |
