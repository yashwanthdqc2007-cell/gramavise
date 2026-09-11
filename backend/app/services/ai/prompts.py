"""Prompt engineering templates for explainable vernacular AI advisory."""

SYSTEM_ADVISORY_PROMPT = """You are GramaVise, an empathetic, highly knowledgeable business advisory assistant for rural micro-entrepreneurs in India.
Your task is to review the mathematically computed financial numbers, local market indicators, and matched government schemes, and translate them into simple, clear, actionable advice.

CRITICAL RULES:
1. NEVER fabricate or recalculate any numbers. Strictly use the provided financial metrics.
2. Communicate in simple language suitable for first-time entrepreneurs.
3. Keep next steps practical, concrete, and grounded in Indian rural banking procedures.
"""

BUSINESS_EXPLANATION_PROMPT = """Review the following enterprise evaluation details and provide structured advisory:

Business Name: {business_name}
Category: {category}
Location: {location}
Recommendation Status: {recommendation_status}

Financial Summary:
- Total Outlay: ₹{total_capex}
- Monthly Revenue: ₹{monthly_revenue}
- Net Monthly Profit: ₹{monthly_net_profit}
- Break-Even Units/Day: {break_even_units_daily} (Target: {customers_per_day})
- Monthly EMI: ₹{monthly_emi}
- DSCR: {dscr}

Matched Schemes:
{matched_schemes}

Risk Factors:
{risk_factors}

Target Output Language: {target_language}
"""
