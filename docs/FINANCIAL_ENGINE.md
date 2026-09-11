# Financial Engine Specifications — GRAMAVISE

## 1. Engine Philosophy
The GramaVise Financial Engine is **100% deterministic**. No machine learning models, heuristics, or LLMs are involved in numerical computations. All formulas are mathematically verified, unit-tested, and audited against standard microfinance banking practices (NABARD / SIDBI guidelines).

---

## 2. Core Formulas & Mathematical Definitions

### 2.1 Total Project Outlay (Capex)
$$\text{Total Capex} = \text{Startup Cost} + \text{Equipment Cost} + \text{Initial Inventory}$$

### 2.2 Monthly Revenue
$$\text{Monthly Revenue} = \text{Customers per Day} \times \text{Average Ticket Price} \times \text{Working Days per Month}$$

### 2.3 Monthly Variable Costs & Gross Profit
$$\text{Monthly Variable Cost} = \text{Monthly Revenue} \times \left(\frac{\text{Variable Cost \%}}{100}\right)$$
$$\text{Monthly Gross Profit} = \text{Monthly Revenue} - \text{Monthly Variable Cost}$$

### 2.4 Monthly Net Profit
$$\text{Monthly Net Profit} = \text{Monthly Gross Profit} - \text{Monthly Fixed Costs} - \text{Monthly Loan EMI}$$

### 2.5 Break-Even Analysis
$$\text{Contribution Margin Ratio (CMR)} = 1 - \left(\frac{\text{Variable Cost \%}}{100}\right)$$
$$\text{Break-Even Monthly Revenue} = \frac{\text{Monthly Fixed Costs} + \text{Monthly EMI}}{\text{CMR}}$$
$$\text{Break-Even Customers/Day} = \frac{\text{Break-Even Monthly Revenue}}{\text{Avg Ticket Price} \times \text{Working Days}}$$

### 2.6 Equated Monthly Installment (EMI)
$$\text{EMI} = P \cdot r \cdot \frac{(1+r)^n}{(1+r)^n - 1}$$
*where:*
- $P$ = Loan Principal (Desired Loan Amount)
- $r$ = Monthly interest rate ($\frac{\text{Annual Rate}}{12 \times 100}$)
- $n$ = Loan tenure in months

### 2.7 Debt Service Coverage Ratio (DSCR)
$$\text{DSCR} = \frac{\text{Monthly Net Operating Income}}{\text{Monthly EMI}}$$
- **DSCR $\ge 1.5$**: Strong repayment capacity (`PROCEED`)
- **$1.0 \le \text{DSCR} < 1.5$**: Tight margin (`VALIDATE_FIRST`)
- **DSCR $< 1.0$**: Insolvent / Deficit (`RECONSIDER`)

---

## 3. Sensitivity & Stress Testing
The engine evaluates robustness under 4 baseline scenarios:
1. **Demand Dip (-20% daily footfall)**
2. **Price Shock (-10% average selling price)**
3. **Cost Escalation (+15% raw material/variable cost)**
4. **Combined Worst Case (-15% volume, +10% cost)**
