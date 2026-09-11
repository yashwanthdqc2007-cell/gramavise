/**
 * GRAMAVISE FRONTEND SHARED TYPE DEFINITIONS
 */

export type RecommendationStatus = "PROCEED" | "VALIDATE_FIRST" | "RECONSIDER";

export type EvidenceType = "OBSERVED" | "CALCULATED" | "MODELLED" | "ASSUMED" | "NEEDS_VERIFICATION";

export interface LocationData {
  state: string;
  district: string;
  village: string;
  latitude?: number;
  longitude?: number;
}

export interface BusinessProfile {
  business_name: string;
  category: string;
  description?: string;
  location: LocationData;
  experience_years: number;
  own_capital: number;
  desired_loan: number;
  is_new_business: boolean;
}

export interface FinancialAssumptions {
  startup_cost: number;
  equipment_cost: number;
  inventory_cost: number;
  monthly_fixed_cost: number;
  customers_per_day: number;
  avg_ticket_price: number;
  working_days_per_month: number;
  variable_cost_pct: number;
  interest_rate_pct: number;
  loan_tenure_months: number;
}

export interface FinancialResult {
  total_capex: number;
  required_loan_amount: number;
  monthly_revenue: number;
  monthly_variable_cost: number;
  monthly_gross_profit: number;
  monthly_fixed_cost: number;
  monthly_emi: number;
  monthly_net_profit: number;
  net_profit_margin_pct: number;
  break_even_revenue_monthly: number;
  break_even_units_daily: number;
  dscr: number;
  is_financially_viable: boolean;
}

export interface CompetitorInfo {
  name: string;
  distance_km: number;
  category: string;
}

export interface MarketResult {
  location_summary: string;
  competitor_count: number;
  competitor_list: CompetitorInfo[];
  demand_indicator: "HIGH" | "MEDIUM" | "LOW" | "UNKNOWN";
  catchment_population_estimate?: number;
  notes?: string;
}

export interface MatchedScheme {
  scheme_code: string;
  scheme_name: string;
  subsidy_eligible_amount: number;
  own_contribution_required: number;
  max_bank_loan: number;
  eligibility_status: "ELIGIBLE" | "PARTIALLY_ELIGIBLE" | "NOT_ELIGIBLE";
  reasons: string[];
  portal_url?: string;
}

export interface SchemeResult {
  eligible_schemes_count: number;
  schemes: MatchedScheme[];
  total_potential_subsidy: number;
}

export interface EvidenceItem {
  indicator: string;
  value: string;
  unit?: string;
  evidence_type: EvidenceType;
  confidence: number;
  source?: string;
  source_url?: string;
  notes?: string;
}

export interface RiskFactor {
  factor: string;
  severity: "HIGH" | "MEDIUM" | "LOW";
  mitigation: string;
}

export interface AIExplanation {
  language: string;
  summary: string;
  strengths: string[];
  cautions_and_risks: string[];
  actionable_next_steps: string[];
  disclaimer: string;
}

export interface AnalysisResult {
  analysis_id: string;
  recommendation_status: RecommendationStatus;
  confidence_score: number;
  financial_result: FinancialResult;
  market_result: MarketResult;
  scheme_result: SchemeResult;
  risk_factors: RiskFactor[];
  evidence_list: EvidenceItem[];
  ai_explanation?: AIExplanation;
}
