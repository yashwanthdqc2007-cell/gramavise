import { BusinessProfile, FinancialAssumptions } from "@/lib/types";

export const DRAFT_STORAGE_KEY = "gramavise_draft_v1";
export const DRAFT_SCHEMA_VERSION = 1;
export const DRAFT_EXPIRY_MS = 7 * 24 * 60 * 60 * 1000; // 7 days

export interface OnboardingDraft {
  version: number;
  updated_at: string; // ISO timestamp
  step: number;
  language: string;
  profile: BusinessProfile;
  financials: FinancialAssumptions;
  entrepreneur: {
    full_name?: string;
  };
}

/**
 * Validate that an unknown object adheres to the expected OnboardingDraft schema.
 */
export function isValidDraft(data: any): data is OnboardingDraft {
  if (!data || typeof data !== "object") return false;
  if (data.version !== DRAFT_SCHEMA_VERSION) return false;
  if (!data.updated_at || typeof data.updated_at !== "string") return false;
  if (typeof data.step !== "number" || data.step < 1 || data.step > 5) return false;
  if (!data.profile || typeof data.profile !== "object") return false;
  if (!data.financials || typeof data.financials !== "object") return false;

  // Verify timestamp is not expired (7 days)
  const draftTime = new Date(data.updated_at).getTime();
  if (isNaN(draftTime)) return false;
  if (Date.now() - draftTime > DRAFT_EXPIRY_MS) return false;

  return true;
}

/**
 * Load draft from browser localStorage safely.
 */
export function loadDraft(): OnboardingDraft | null {
  if (typeof window === "undefined") return null;

  try {
    const raw = localStorage.getItem(DRAFT_STORAGE_KEY);
    if (!raw) return null;

    const parsed = JSON.parse(raw);
    if (!isValidDraft(parsed)) {
      // Discard invalid or expired draft
      localStorage.removeItem(DRAFT_STORAGE_KEY);
      return null;
    }

    return parsed;
  } catch (err) {
    console.error("Failed to load draft from localStorage; removing corrupted data:", err);
    try {
      localStorage.removeItem(DRAFT_STORAGE_KEY);
    } catch {
      // ignore
    }
    return null;
  }
}

/**
 * Save draft to browser localStorage safely.
 * Non-blocking, data-minimized (excludes sensitive PII like passwords, aadhaar, pan, audio).
 */
export function saveDraft(
  step: number,
  language: string,
  profile: BusinessProfile,
  financials: FinancialAssumptions,
  fullName?: string
): boolean {
  if (typeof window === "undefined") return false;

  try {
    const draft: OnboardingDraft = {
      version: DRAFT_SCHEMA_VERSION,
      updated_at: new Date().toISOString(),
      step: Math.min(5, Math.max(1, step)),
      language: language || "en",
      profile: {
        business_name: profile.business_name || "",
        category: profile.category || "",
        description: profile.description || "",
        location: {
          state: profile.location?.state || "",
          district: profile.location?.district || "",
          village: profile.location?.village || "",
          latitude: profile.location?.latitude,
          longitude: profile.location?.longitude,
        },
        experience_years: Number(profile.experience_years) || 0,
        own_capital: Number(profile.own_capital) || 0,
        desired_loan: Number(profile.desired_loan) || 0,
        is_new_business: profile.is_new_business !== false,
      },
      financials: {
        startup_cost: Number(financials.startup_cost) || 0,
        equipment_cost: Number(financials.equipment_cost) || 0,
        inventory_cost: Number(financials.inventory_cost) || 0,
        monthly_fixed_cost: Number(financials.monthly_fixed_cost) || 0,
        customers_per_day: Number(financials.customers_per_day) || 0,
        avg_ticket_price: Number(financials.avg_ticket_price) || 0,
        working_days_per_month: Number(financials.working_days_per_month) || 26,
        variable_cost_pct: Number(financials.variable_cost_pct) || 0,
        interest_rate_pct: Number(financials.interest_rate_pct) || 10.5,
        loan_tenure_months: Number(financials.loan_tenure_months) || 36,
      },
      entrepreneur: {
        full_name: fullName?.trim() || "",
      },
    };

    localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify(draft));
    return true;
  } catch (err) {
    console.error("Failed to save draft to localStorage:", err);
    return false;
  }
}

/**
 * Clear stored draft from localStorage.
 */
export function clearDraft(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(DRAFT_STORAGE_KEY);
  } catch (err) {
    console.error("Failed to clear draft:", err);
  }
}

/**
 * Check if a valid, unexpired draft currently exists.
 */
export function hasDraft(): boolean {
  return loadDraft() !== null;
}
