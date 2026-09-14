# Financial Engine Specifications — GRAMAVISE

## 1. Engine Philosophy
The GramaVise Financial Engine is **100% deterministic**. No machine learning models, heuristics, or LLMs are involved in numerical computations. All formulas are mathematically verified, unit-tested, and audited against standard microfinance banking practices (NABARD / SIDBI guidelines).

---

## 2. Core Formulas & Mathematical Definitions

### 2.1 Total Project Outlay (Capex) & Loan Requirement
$$\text{Total Capex} = \text{Startup Cost} + \text{Equipment Cost} + \text{Initial Inventory}$$
$$\text{Loan Requirement} = \max(0.0, \text{Total Capex} - \text{Own Capital})$$
*(If the user explicitly specifies a positive `desired_loan`, that amount is used as the loan principal).*

### 2.2 Monthly Revenue
$$\text{Daily Revenue} = \text{Customers per Day} \times \text{Average Ticket Price}$$
$$\text{Monthly Revenue} = \text{Daily Revenue} \times \text{Working Days per Month}$$

### 2.3 Monthly Variable Costs & Gross Profit
$$\text{Monthly Variable Cost} = \text{Monthly Revenue} \times \left(\frac{\text{Variable Cost \%}}{100}\right)$$
$$\text{Monthly Gross Profit} = \text{Monthly Revenue} - \text{Monthly Variable Cost}$$

### 2.4 Monthly Net Profit & Operating Income
$$\text{Monthly Net Operating Income (NOI)} = \text{Monthly Gross Profit} - \text{Monthly Fixed Costs}$$
$$\text{Monthly Net Profit} = \text{Monthly Net Operating Income} - \text{Monthly Loan EMI}$$
$$\text{Net Profit Margin \%} = \left(\frac{\text{Monthly Net Profit}}{\text{Monthly Revenue}}\right) \times 100$$

### 2.5 Break-Even Analysis
$$\text{Contribution Margin Ratio (CMR)} = 1 - \left(\frac{\text{Variable Cost \%}}{100}\right)$$
$$\text{Break-Even Monthly Revenue} = \frac{\text{Monthly Fixed Costs} + \text{Monthly EMI}}{\text{CMR}}$$
$$\text{Break-Even Daily Units} = \left\lceil\frac{\text{Break-Even Monthly Revenue}}{\text{Avg Ticket Price} \times \text{Working Days}}\right\rceil$$

*Edge cases:* If $\text{CMR} \le 0$, $\text{Avg Ticket Price} \le 0$, or $\text{Working Days} \le 0$, the engine returns `0.0` revenue and `0` units without division-by-zero errors.

### 2.6 Equated Monthly Installment (EMI)
$$\text{EMI} = P \cdot r \cdot \frac{(1+r)^n}{(1+r)^n - 1}$$
*where:*
- $P$ = Loan Principal
- $r$ = Monthly interest rate ($\frac{\text{Annual Rate}}{12 \times 100}$)
- $n$ = Loan tenure in months

*Special Cases:*
- If $P \le 0$ or $n \le 0$: $\text{EMI} = 0.0$
- If $r = 0$ ($0\%$ interest rate): $\text{EMI} = \frac{P}{n}$

### 2.7 Debt Service Coverage Ratio (DSCR) & Repayment Capacity
$$\text{DSCR} = \frac{\text{Monthly Net Operating Income}}{\text{Monthly EMI}}$$
*where:*
- **Numerator**: Net Operating Income (Cash available for debt service before EMI).
- **Debt-Free Case ($\text{EMI} = 0$)**: When there is no debt, DSCR returns `0.0` and the rule engine marks the business as `DEBT_FREE` / `is_financially_viable = (Net Profit > 0)`.
- **DSCR $\ge 1.5$**: Strong repayment capacity (`STRONG` / `PROCEED` candidate)
- **$1.25 \le \text{DSCR} < 1.5$**: Adequate repayment capacity (`ADEQUATE`)
- **$1.0 \le \text{DSCR} < 1.25$**: Tight margin (`TIGHT` / `VALIDATE_FIRST`)
- **$\text{DSCR} < 1.0$**: Insolvent / Deficit (`DEFICIT` / `RECONSIDER`)

---

## 3. Sensitivity & Stress Testing
The engine evaluates robustness under 4 deterministic stress scenarios:
1. **Demand Dip**: $-20\%$ daily footfall / customer volume
2. **Price Shock**: $-10\%$ average ticket price realization
3. **Cost Escalation**: $+15\%$ variable / raw material costs
4. **Combined Worst Case**: $-15\%$ customer volume, $+10\%$ variable cost

Each scenario computes stressed revenue, net profit, break-even revenue, DSCR, and status (`VIABLE`, `STRESSED`, `INSOLVENT`).
Overall resilience is rated as:
- **`HIGH`**: 0 insolvent scenarios and $\le 1$ stressed scenario
- **`MODERATE`**: $\le 1$ insolvent scenario
- **`LOW`**: $\ge 2$ insolvent scenarios

---

## 5. Step 4J — Scenario Lab ("Test Before You Borrow")
The Scenario Lab provides a controlled sandbox for micro-entrepreneurs to simulate alternative business assumptions (capex, equity, loan, footfall, pricing, costs, tenure).

### Core Architectural Invariants:
1. **Pure Financial Engine Reuse**: The Scenario Lab does **NOT** introduce any separate financial calculations or formulas. It calls the authoritative `FinancialService.calculate()` for every simulated scenario.
2. **Pure Feasibility Rule Reuse**: Scenario recommendation verdicts (`PROCEED`, `VALIDATE_FIRST`, `RECONSIDER`) and decision traces are evaluated exclusively by `FeasibilityRules.evaluate_with_trace()`.
3. **Baseline Immutability**: The primary analysis baseline (capex, EMI, net profit, DSCR, recommendation, decision trace) is strictly read-only and immutable. Scenarios are evaluated in isolation without mutating baseline state.
4. **Market Invariance**: Geospatial competitor counts, census demographics, and mandi prices remain invariant across scenario evaluations.
5. **Deterministic Delta Calculations**: `ScenarioComparator` computes absolute and percentage differences between baseline and scenario metrics with safe zero-denominator handling.
6. **Distinction from Sensitivity Analysis**:
   - **Automated Sensitivity Analysis**: GramaVise's 4 predefined stress shock tests (Demand Dip, Price Shock, Cost Escalation, Combined Worst Case).
   - **Scenario Lab**: User-directed exploratory assumption adjustments to test feasibility before borrowing.
7. **No Approval Prediction or Optimization**: The Scenario Lab provides decision support simulation only. It does not predict loan approval, calculate credit scores, or recommend an "optimal" loan amount.


