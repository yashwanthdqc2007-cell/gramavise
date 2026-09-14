export type VoiceFieldType =
  | "own_capital"
  | "desired_loan"
  | "startup_cost"
  | "equipment_cost"
  | "inventory_cost"
  | "monthly_fixed_cost"
  | "customers_per_day"
  | "avg_ticket_price"
  | "working_days_per_month"
  | "variable_cost_pct"
  | "interest_rate_pct"
  | "loan_tenure_months";

export type ParseResultStatus = "SUCCESS" | "AMBIGUOUS" | "INVALID" | "OUT_OF_RANGE";

export interface ParseResult {
  status: ParseResultStatus;
  raw_transcript: string;
  parsed_value: number | null;
  formatted_display: string;
  unit?: string;
  ambiguity_reason?: string;
}

export interface VoiceFieldConfig {
  fieldType: VoiceFieldType;
  labelKey: string;
  min: number;
  max: number;
  isFloat: boolean;
  unit: "INR" | "PERCENT" | "DAYS" | "MONTHS" | "UNITS";
  isRolloutActive: boolean; // Initial 8 active; remaining 4 architected for later rollout
}

export type VoiceListeningState =
  | "IDLE"
  | "REQUESTING_PERMISSION"
  | "LISTENING"
  | "RECOGNIZED"
  | "PARSING"
  | "AWAITING_CONFIRMATION"
  | "PERMISSION_DENIED"
  | "UNSUPPORTED"
  | "NO_SPEECH"
  | "RECOGNITION_ERROR"
  | "CANCELLED";
