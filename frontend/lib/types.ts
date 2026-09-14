/**
 * GRAMAVISE FRONTEND SHARED TYPE DEFINITIONS
 */

export type RecommendationStatus = "PROCEED" | "VALIDATE_FIRST" | "RECONSIDER";
export type EvidenceType = "OBSERVED" | "CALCULATED" | "MODELLED" | "ASSUMED" | "NEEDS_VERIFICATION";
export type GeographyLevel = "NATIONAL" | "STATE" | "DISTRICT" | "BLOCK" | "VILLAGE" | "CATCHMENT";
export type VerificationStatus = "VERIFIED" | "CALCULATED" | "SELF_REPORTED" | "UNVERIFIED" | "ASSUMPTION" | "ESTIMATED" | "DERIVED" | "UNVERIFIED_PROTOTYPE" | "NEEDS_VERIFICATION";

export interface LocationData {
  state: string;
  district: string;
  village: string;
  block?: string;
  pincode?: string;
  lgd_village_code?: string;
  census_2011_code?: string;
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
  entrepreneur_name?: string;
  age?: number;
  gender?: string;
  social_category?: string;
  education?: string;
  commodity?: string;
  market?: string;
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
  own_capital?: number;
  desired_loan?: number;
}

export interface NumberInputParameter {
  name: string;
  label: string;
  raw_value: number | string | boolean;
  formatted_value: string;
  provenance: EvidenceType;
  source_description: string;
  related_evidence_id?: string;
}

export interface NumberExplanation {
  metric_id: string;
  metric_name: string;
  plain_meaning: string;
  displayed_value: string;
  numeric_value: number;
  unit: string;
  provenance: EvidenceType;
  formula_label: string;
  formula_expression: string;
  substituted_expression: string;
  inputs: NumberInputParameter[];
  calculation_steps: string[];
  related_evidence_ids: string[];
  limitations: string[];
  is_debt_free?: boolean;
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
  explanations?: Record<string, NumberExplanation>;
}

export interface CompetitorInfo {
  name: string;
  distance_km: number;
  category: string;
  relationship?: "DIRECT" | "ADJACENT" | "UNRELATED" | string;
}

export interface CompetitorDetail {
  competitor_id: string;
  business_name: string;
  category: string;
  subcategory?: string;
  distance_km: number;
  latitude?: number;
  longitude?: number;
  osm_object_id?: string;
  osm_object_type?: string;
  tags?: Record<string, string>;
  relationship: "DIRECT" | "ADJACENT" | "UNRELATED" | string;
  match_reason?: string;
  price_indicator?: string;
  evidence_type: EvidenceType;
  confidence: number;
  source: string;
  source_type?: string;
  source_url?: string;
  observed_at?: string;
  verification_status: string;
  notes?: string;
}

export interface UdyamDistrictContext {
  state_name: string;
  district_name: string;
  lgd_district_code?: string;
  registered_msme_count: number;
  micro_count?: number;
  small_count?: number;
  medium_count?: number;
  manufacturing_count?: number;
  services_count?: number;
  geography_level: string;
  evidence_type: EvidenceType;
  confidence: number;
  source: string;
  source_url?: string;
  dataset_name: string;
  observed_at?: string;
  verification_status: string;
  notes: string;
}

export interface CatchmentData {
  radius_km: number;
  estimated_population?: number;
  estimated_households?: number;
  estimated_daily_demand?: string;
  methodology: string;
  verification_status: string;
}

export interface GeographyIdentity {
  state_name?: string;
  state_lgd_code?: string;
  district_name?: string;
  district_lgd_code?: string;
  sub_district_name?: string;
  sub_district_lgd_code?: string;
  village_name?: string;
  village_lgd_code?: string;
  verification_status?: string;
  source?: string;
  source_url?: string;
}

export interface DemographicObservation {
  population?: number;
  households?: number;
  reference_year: number;
  data_status?: string;
  geography_level?: string;
  evidence_type?: EvidenceType;
  confidence?: number;
  source?: string;
  source_url?: string;
  verification_status?: string;
}

export interface PriceObservationDetail {
  commodity: string;
  variety?: string;
  market_name: string;
  district_name: string;
  state_name: string;
  arrival_date: string;
  min_price: number;
  max_price: number;
  modal_price: number;
  price_unit: string;
  price_per_kg?: number;
  currency: string;
  evidence_type: EvidenceType;
  confidence: number;
  source: string;
  source_url?: string;
  source_title?: string;
  source_last_verified?: string;
  verification_status: string;
}

export interface PriceBenchmark {
  category: string;
  low_price?: number;
  median_price?: number;
  high_price?: number;
  unit?: string;
  price_per_kg?: number;
  market_name?: string;
  arrival_date?: string;
  variety?: string;
  geography?: string;
  evidence_type: EvidenceType;
  source?: string;
  source_url?: string;
  source_title?: string;
  confidence: number;
  verification_status: string;
  notes?: string;
}

export interface MarketResult {
  location_summary: string;
  competitor_count: number;
  direct_competitor_count?: number;
  adjacent_competitor_count?: number;
  catchment_radius_km?: number;
  coverage_confidence?: "HIGH" | "MEDIUM" | "LOW" | "UNKNOWN" | string;
  coverage_warning?: string;
  competitor_list: CompetitorInfo[];
  competitors?: CompetitorDetail[];
  demand_indicator: "HIGH" | "MEDIUM" | "LOW" | "UNKNOWN";
  catchment_population_estimate?: number;
  catchment?: CatchmentData;
  price_benchmark?: PriceBenchmark;
  price_observations?: PriceObservationDetail[];
  geography?: GeographyIdentity;
  demographics?: DemographicObservation;
  udyam_context?: UdyamDistrictContext;
  market_signals?: string[];
  indicators?: any[];
  confidence_level?: "HIGH" | "MEDIUM" | "LOW" | "UNKNOWN";
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
  conditions_to_verify?: string[];
  source_url?: string;
  source_title?: string;
  evidence_type?: string;
}

export interface SchemeResult {
  eligible_schemes_count: number;
  schemes: MatchedScheme[];
  total_potential_subsidy: number;
}

export interface EvidenceItem {
  evidence_id?: string;
  indicator: string;
  claim?: string;
  value: string;
  unit?: string;
  evidence_type: EvidenceType;
  confidence: number;
  confidence_level?: "HIGH" | "MEDIUM" | "LOW" | "UNKNOWN" | string;
  confidence_explanation?: string;
  source?: string;
  source_url?: string;
  source_title?: string;
  observed_at?: string;
  geography_level?: string;
  verification_status?: string;
  methodology?: string;
  supports?: string;
  limitations?: string;
  notes?: string;
}

export interface RuleEvaluation {
  rule_id: string;
  rule_name: string;
  condition: string;
  result: "PASS" | "FAIL" | "WARNING" | "INFO" | string;
  severity: "CRITICAL" | "WARNING" | "INFO" | string;
  explanation: string;
  source: string;
}

export interface DecisionTrace {
  recommendation_status: RecommendationStatus;
  summary: string;
  rule_evaluations: RuleEvaluation[];
  key_positive_factors: string[];
  key_caution_factors: string[];
  authority: string;
}

export interface VerificationCheckItem {
  item_id: string;
  title: string;
  description: string;
  category: "MARKET" | "PRICING" | "SCHEME" | "DEMOGRAPHICS" | "ASSUMPTION" | string;
  source_evidence_id?: string;
  action_type: "ON_GROUND_SURVEY" | "DOCUMENT_VERIFICATION" | "BANK_CONSULTATION" | "SUPPLIER_CHECK" | string;
  is_completed?: boolean;
}

export interface RiskFactor {
  factor: string;
  severity: "HIGH" | "MEDIUM" | "LOW";
  mitigation: string;
}

export type ActionPriority = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
export type ActionCategory = "FINANCIAL" | "MARKET" | "SCHEME" | "DOCUMENTATION" | "BUSINESS_OPERATIONS" | "VALIDATION";
export type ActionStatus = "TODO" | "RECOMMENDED" | "COMPLETED" | "NOT_APPLICABLE";
export type ActionSource = "DECISION_TRACE" | "EVIDENCE_LEDGER" | "VERIFICATION_CHECKLIST" | "FINANCIAL_RESULT" | "SCHEME_RESULT" | "MARKET_RESULT";

export interface ActionItem {
  action_id: string;
  title: string;
  description: string;
  priority: ActionPriority;
  category: ActionCategory;
  status: ActionStatus;
  action_source: ActionSource;
  reason: string;
  related_evidence_ids: string[];
  related_rule_ids: string[];
  estimated_effort?: string;
  verification_required: boolean;
  completion_effect?: string;
}

export interface ActionPlan {
  recommendation_status: RecommendationStatus;
  actions: ActionItem[];
  total_actions: number;
  critical_actions_count: number;
}

export type DocumentStatus = "REQUIRED" | "VERIFY" | "NOT_REQUIRED" | "UNKNOWN";

export interface DocumentItem {
  document_id: string;
  name: string;
  purpose: string;
  status: DocumentStatus;
  required_for: string;
  source?: string;
  verification_status: string;
}

export interface DocumentReadiness {
  documents: DocumentItem[];
  required_count: number;
  verified_count: number;
  pending_count: number;
}

export type ReadinessStatus = "READY" | "PARTIALLY_READY" | "NOT_READY" | "UNKNOWN";

export interface BankReadinessCategory {
  category: string;
  title: string;
  status: ReadinessStatus;
  reason: string;
  supporting_evidence_ids: string[];
}

export interface BankReadiness {
  overall_status: ReadinessStatus;
  summary: string;
  categories: BankReadinessCategory[];
  top_actions: string[];
  disclaimer: string;
}

export interface AIExplanation {
  language: string;
  summary: string;
  strengths: string[];
  cautions_and_risks: string[];
  actionable_next_steps: string[];
  disclaimer: string;
}

export type ComparisonDirection = "IMPROVED" | "WORSENED" | "UNCHANGED" | "NEUTRAL";

export interface MetricComparison {
  metric_key: string;
  metric_name: string;
  baseline_value: number;
  scenario_value: number;
  unit: string;
  absolute_change: number;
  percentage_change?: number;
  direction: ComparisonDirection;
  explanation: string;
}

export interface RuleComparison {
  rule_id: string;
  rule_name: string;
  baseline_result: string;
  scenario_result: string;
  changed: boolean;
  explanation: string;
}

export interface RecommendationChange {
  baseline_status: RecommendationStatus;
  scenario_status: RecommendationStatus;
  changed: boolean;
  summary: string;
  reasons: string[];
}


export interface ScenarioEvaluationRequest {
  scenario_id?: string;
  name: string;
  description?: string;
  baseline_own_capital: number;
  baseline_desired_loan?: number;
  baseline_financials: FinancialAssumptions;
  scenario_own_capital: number;
  scenario_desired_loan?: number;
  scenario_financials: FinancialAssumptions;
  market_context?: MarketResult;
}

export interface ScenarioEvaluationResponse {
  scenario_id: string;
  name: string;
  description?: string;
  baseline_result: FinancialResult;
  scenario_result: FinancialResult;
  baseline_status: RecommendationStatus;
  scenario_status: RecommendationStatus;
  baseline_decision_trace?: DecisionTrace;
  scenario_decision_trace?: DecisionTrace;
  metric_comparisons: MetricComparison[];
  rule_comparisons: RuleComparison[];
  recommendation_change: RecommendationChange;
  what_changed: string[];
  why_it_changed: string[];
  risk_factors: RiskFactor[];
  disclaimer: string;
}

export interface CreateScenarioRequest {
  name: string;
  description?: string;
  scenario_own_capital: number;
  scenario_desired_loan?: number;
  scenario_financials: FinancialAssumptions;
}

export interface ScenarioRecordResponse extends ScenarioEvaluationResponse {
  analysis_id: string;
  created_at?: string;
  scenario_inputs?: Record<string, any>;
}


export interface AnalysisResult {
  analysis_id: string;
  recommendation_status: RecommendationStatus;
  overall_verdict?: RecommendationStatus;
  confidence_score: number;
  financial_result: FinancialResult;
  market_result: MarketResult;
  scheme_result: SchemeResult;
  risk_factors: RiskFactor[];
  evidence_list: EvidenceItem[];
  evidence_ledger?: EvidenceItem[];
  decision_trace?: DecisionTrace;
  verification_checklist?: VerificationCheckItem[];
  action_plan?: ActionPlan;
  document_readiness?: DocumentReadiness;
  bank_readiness?: BankReadiness;
  ai_explanation?: AIExplanation;
  business_input_snapshot?: BusinessProfile;
  financial_input_snapshot?: FinancialAssumptions;
  verdict_reasons?: string[];
  evaluation_metadata?: {
    evaluated_at: string;
    engine_version: string;
    confidence_score: number;
  };
}

export type AnalysisResponse = AnalysisResult;


