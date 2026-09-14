# GramaVise — Demo Scenario Playbook & Demo Data System

This guide outlines four realistic, pre-configured micro-business input profiles for the **Smart India Hackathon (SIH) / RMK Evaluation Demo**. 

> [!IMPORTANT]
> **Data Integrity & Functional Architecture**:
> - These profiles are **illustrative user-entered input assumptions** to demonstrate the onboarding and advisory workflow. They are **not** government statistics, market survey databases, or pre-computed fake results.
> - GramaVise features **zero hardcoded recommendations** or duplicate calculation engines. Selecting a demo scenario in the onboarding wizard simply populates the standard form fields. Every recommendation, financial figure, DSCR, break-even point, risk analysis, and scheme match is computed deterministically by the live FastAPI backend (`POST /api/analyze`).
> - The live backend values documented below are **actual outputs** returned by the running engine.

---

## 1. Demo Scenario Overview

| Profile | Category | Location | Own Equity | Desired Loan | Live Verdict | Live DSCR | Net Margin | Demo Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A. Kisan Flour Mill** | Food Processing | Baramati, MH | ₹1,50,000 | ₹1,50,000 | **PROCEED** | 71.42x | 49.90% | Hero Case: Strong unit economics, high margin, prime scheme match |
| **B. Lakshmi Tailoring** | Garment Services | Melur, TN | ₹1,00,000 | ₹70,000 | **PROCEED** | 32.25x | 53.85% | Service Micro-Business: Low debt, sustainable footfall |
| **C. Village Dairy Unit** | Dairy & Livestock | Ramnagar, UP | ₹80,000 | ₹3,00,000 | **VALIDATE_FIRST** | 1.40x | 2.67% | Risk & Stress Case: High leverage, thin cushion, tight DSCR |
| **D. Sri Amman Tea & Snacks** | Food & Beverage | Nanjangud, KA | ₹60,000 | ₹1,00,000 | **PROCEED** | 2.11x | 5.46% | Volume-Sensitive Case: High footfall required to break even |

---

## 2. Detailed Profile Playbooks

### Profile A: Kisan Flour Mill (Hero Demonstration Case)

- **Business Name**: Kisan Flour Mill
- **Type**: Greenfield New Business
- **Category**: Flour & Spice Milling (Atta Chakki)
- **Location**: Baramati, Pune District, Maharashtra
- **Entrepreneur Profile**: 5 years prior grain handling experience
- **Inputs**:
  - **Own Capital**: ₹1,50,000
  - **Equipment / Machinery**: ₹2,00,000 (Commercial pulverizer, sieving machinery)
  - **Working Inventory**: ₹50,000 (Whole wheat, whole spices)
  - **Startup / Civil / Electrical Costs**: ₹50,000
  - **Total Capex**: ₹3,00,000
  - **Desired Bank Loan**: ₹1,50,000 (10.5% interest, 60 months tenure)
  - **Operational Parameters**: 35 customers/day, ₹500 avg ticket, 26 working days/month, 45% variable COGS, ₹20,000 monthly fixed overheads
- **Verified Live Engine Results**:
  - **Recommendation**: `PROCEED` (Confidence: 74%)
  - **Monthly Revenue**: ₹4,55,000
  - **Monthly Net Profit**: ₹2,27,025.91 (Net Margin: 49.90%)
  - **Monthly EMI**: ₹3,224.09
  - **DSCR**: `71.42x` (Extremely robust debt service coverage)
  - **Break-Even Target**: `4 customers / day` (₹42,225.62 monthly turnover)
  - **Identified Risks**: None detected (Low risk profile)
  - **Matched Government Schemes**:
    - *PMEGP* (Partially Eligible — ₹87,500 25% margin money subsidy)
    - *MUDRA Kishore* (Eligible — Collateral-free loan up to ₹5,00,000)
- **What to Highlight in Demo**:
  1. High capital efficiency and low break-even threshold (needs only 4 out of 35 customers daily to pay fixed costs and EMI).
  2. Explainable financial formula provenance: Click on DSCR or Net Profit to show step-by-step substitutions.
  3. Government scheme subsidy matching: Shows PMEGP rural subsidy eligibility.

---

### Profile B: Lakshmi Tailoring Centre (Service Sector Case)

- **Business Name**: Lakshmi Tailoring Centre
- **Type**: Greenfield New Business
- **Category**: Tailoring & Garment Making
- **Location**: Melur, Madurai District, Tamil Nadu
- **Entrepreneur Profile**: 3 years vocational stitching experience
- **Inputs**:
  - **Own Capital**: ₹1,00,000
  - **Equipment**: ₹1,20,000 (Commercial motorized sewing machines, overlock machines)
  - **Inventory**: ₹30,000 (Threads, lining, fabric rolls)
  - **Other Startup Cost**: ₹20,000
  - **Total Capex**: ₹1,70,000
  - **Desired Bank Loan**: ₹70,000 (10.5% interest, 48 months tenure)
  - **Operational Parameters**: 8 customers/day, ₹500 avg ticket, 26 working days/month, 30% variable COGS, ₹15,000 monthly fixed overheads
- **Verified Live Engine Results**:
  - **Recommendation**: `PROCEED` (Confidence: 58%)
  - **Monthly Revenue**: ₹1,04,000
  - **Monthly Net Profit**: ₹56,007.76 (Net Margin: 53.85%)
  - **Monthly EMI**: ₹1,792.24
  - **DSCR**: `32.25x`
  - **Break-Even Target**: `2 customers / day` (₹24,000 monthly turnover)
  - **Identified Risks**: None detected
  - **Matched Government Schemes**:
    - *PMEGP* (Partially Eligible — ₹42,500 subsidy)
    - *MUDRA Kishore* (Eligible)
- **What to Highlight in Demo**:
  1. Micro-service business dynamics: Low inventory requirement and higher labor/service value-add (30% COGS).
  2. Low debt burden (₹1,792 EMI vs ₹56k monthly profit) yielding 32x repayment cushion.

---

### Profile C: Village Dairy Unit (Risk & Stress Testing Case)

- **Business Name**: Village Dairy Unit
- **Type**: Greenfield New Business
- **Category**: Dairy Farming & Milk Chilling
- **Location**: Ramnagar, Varanasi District, Uttar Pradesh
- **Entrepreneur Profile**: 2 years family dairy experience
- **Inputs**:
  - **Own Capital**: ₹80,000 (High leverage: only 22.8% equity)
  - **Equipment / Livestock**: ₹2,50,000 (Milch cattle, milking equipment, can chillers)
  - **Inventory / Fodder**: ₹50,000
  - **Other Startup Cost**: ₹50,000 (Cattle shed preparation)
  - **Total Capex**: ₹3,50,000
  - **Desired Bank Loan**: ₹3,00,000 (11.0% interest, 60 months tenure)
  - **Operational Parameters**: 15 customers/day (or 15 milk supply units/day), ₹250 avg ticket, 26 working days/month, 65% variable COGS (feed, fodder, veterinary medicines), ₹25,000 monthly fixed costs (shed rent, labor, utility)
- **Verified Live Engine Results**:
  - **Recommendation**: `VALIDATE_FIRST` (Confidence: 71%)
  - **Monthly Revenue**: ₹97,500
  - **Monthly Net Profit**: ₹2,602.27 (Net Margin: 2.67%)
  - **Monthly EMI**: ₹6,522.73
  - **DSCR**: `1.40x` (Borderline debt cushion; close to commercial banking minimum of 1.25x–1.50x)
  - **Break-Even Target**: `14 customers / day` (93.3% of capacity required just to break even)
  - **Identified Risk Factor**:
    - **Tight Loan Repayment Cushion** (Severity: `MEDIUM`): Monthly surplus is narrow; adverse fluctuations in milk procurement prices or cattle feed costs can lead to immediate debt default.
  - **Matched Government Schemes**:
    - *PMEGP* (Partially Eligible — ₹87,500 subsidy)
    - *MUDRA Kishore* (Eligible)
- **What to Highlight in Demo**:
  1. Shows that GramaVise is **not** a rubber-stamp tool; it actively identifies financially risky micro-enterprises.
  2. Highlight the `VALIDATE_FIRST` status and the high break-even requirement (14 out of 15 daily units).

---

### Profile D: Sri Amman Tea & Snacks (Volume-Sensitive Borderline Case)

- **Business Name**: Sri Amman Tea & Snacks
- **Type**: Greenfield New Business
- **Category**: Kirana & General Store / F&B Food Stall
- **Location**: Nanjangud, Mysuru District, Karnataka
- **Entrepreneur Profile**: 4 years small catering experience
- **Inputs**:
  - **Own Capital**: ₹60,000
  - **Equipment**: ₹1,00,000 (Commercial stove, tea urns, display counter, fryer)
  - **Inventory**: ₹25,000 (Tea, milk, sugar, oil, flour)
  - **Other Startup Cost**: ₹25,000 (Stall advance & electrical setup)
  - **Total Capex**: ₹1,50,000
  - **Desired Bank Loan**: ₹1,00,000 (10.5% interest, 48 months tenure)
  - **Operational Parameters**: 40 customers/day, ₹50 avg ticket, 26 working days/month, 55% variable COGS, ₹18,000 monthly fixed overheads
- **Verified Live Engine Results**:
  - **Recommendation**: `PROCEED` (Confidence: 58%)
  - **Monthly Revenue**: ₹52,000
  - **Monthly Net Profit**: ₹2,839.66 (Net Margin: 5.46%)
  - **Monthly EMI**: ₹2,560.34
  - **DSCR**: `2.11x`
  - **Break-Even Target**: `36 customers / day` (Must serve at least 36 out of 40 daily footfalls to stay profitable)
  - **Identified Risk Factor**:
    - **High Daily Volume Break-Even Target** (Severity: `MEDIUM`): Requires 90% of expected footfall daily to avoid operational losses.
  - **Matched Government Schemes**:
    - *PMEGP* (Partially Eligible — ₹37,500 subsidy)
    - *MUDRA Kishore* (Eligible)
    - *PMFME* (Partially Eligible — Micro Food Processing credit-linked subsidy)
- **What to Highlight in Demo**:
  1. Demonstrates granular micro-retail modeling where daily unit footfall is high but transaction ticket size is low (₹50).
  2. Multi-scheme matching including the PMFME (Food Processing) scheme.

---

## 3. Scenario Lab Demonstration Playbook

### Best Scenario A: Kisan Flour Mill (Demand Stress Testing)

Demonstrate what happens when local grain demand drops by 20% due to monsoon fluctuations or localized competition:

```
Baseline Analysis:
- Customers / Day: 35
- Monthly Revenue: ₹4,55,000
- Monthly Net Profit: ₹2,27,025.91
- DSCR: 71.42x
- Recommendation: PROCEED

Action in Scenario Lab:
1. Open Scenario Lab tab.
2. Select Preset: "Conservative Demand (-20% Footfall)"
3. Customers / Day adjusts from 35 → 28.
4. Click "Recalculate Scenario".

Recalculated Output:
- Monthly Revenue: ₹3,64,000 (-₹91,000 / -20.0%)
- Monthly Net Profit: ₹1,76,975.91 (-₹50,050 / -22.05%)
- DSCR: 55.89x (Remains exceptionally strong > 1.5x)
- Break-Even Units: 4 customers / day (Safe)
- Recommendation: PROCEED

Conclusion for Judges:
"Even in a 20% demand downturn, the enterprise generates ₹1.76L/mo disposable surplus and easily covers its ₹3,224 loan EMI 55 times over."
```

### Best Scenario B: Village Dairy Unit (Downside Break-Point Demonstration)

Demonstrate what happens when a borderline high-leverage business faces a moderate 20% demand reduction:

```
Baseline Analysis:
- Customers / Units / Day: 15
- Monthly Revenue: ₹97,500
- Monthly Net Profit: ₹2,602.27
- DSCR: 1.40x
- Recommendation: VALIDATE_FIRST

Action in Scenario Lab:
1. Open Scenario Lab tab.
2. Select Preset: "Conservative Demand (-20% Footfall)"
3. Customers / Day adjusts from 15 → 12.
4. Click "Recalculate Scenario".

Recalculated Output:
- Monthly Revenue: ₹78,000
- Monthly Net Profit: -₹4,222.73 (DEFICIT / LOSS)
- DSCR: 0.35x (Critical debt default zone < 1.0x)
- Recommendation: RECONSIDER (Risk severity escalates to HIGH)

Conclusion for Judges:
"GramaVise detects vulnerability before money is borrowed: a 3-customer drop in daily milk volume turns the monthly surplus into a ₹4,222 deficit, collapsing the DSCR to 0.35x and triggering a RECONSIDER warning."
```

---

## 4. How to Use During SIH / RMK Presentations

1. Navigate to **New Advisory** (`/onboarding`).
2. At the top of Step 1, locate the **Demo Scenarios** control grid.
3. Click any of the 4 demo cards (**Kisan Flour Mill**, **Lakshmi Tailoring Centre**, **Village Dairy Unit**, **Sri Amman Tea & Snacks**).
4. Notice that the form fields populate instantly with realistic operational assumptions across Step 1, Step 2, and Step 3.
5. Click **Next Step** through the wizard to show reviewers that standard input validation and localized field helpers remain active.
6. Click **Generate AI Advisory** on Step 3 to initiate the live `POST /api/analyze` request.
7. Point out the deterministic results on `/results`:
   - Verdict & Confidence Badges
   - Financial Metrics & Formulas (Click metric cards for breakdown modal)
   - Identified Risk & Mitigation Warnings
   - Matched Government Schemes with official portal links
   - Market Evidence from Mandi & MSME benchmarks
8. Open **Scenario Lab** to demonstrate real-time stress testing with instant diff visualization.
