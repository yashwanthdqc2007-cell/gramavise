import { apiClient } from "@/lib/api";

/**
 * Matches the SchemeVersionResponse shape returned by the backend.
 */
export interface SchemeVersionInfo {
  id: string;
  scheme_code: string;
  version: string;
  status: string;
  description?: string;
  official_source_name?: string;
  official_portal_url?: string;
  max_loan_amount: number;
  subsidy_percentage_general: number;
  subsidy_percentage_special: number;
  beneficiary_contribution_general_pct: number;
  beneficiary_contribution_special_pct: number;
  eligibility_criteria: Record<string, unknown>;
}

/**
 * Matches the SchemeCatalogItem shape returned by GET /schemes.
 * Financial details live inside active_version.
 */
export interface SchemeCatalogItem {
  id: string;
  scheme_code: string;
  scheme_name: string;
  ministry?: string;
  department?: string;
  description?: string;
  active_version?: SchemeVersionInfo | null;
  total_versions: number;
}

/**
 * Legacy flat interface used by scheme card UI.
 * Use getSchemDisplayValues() to populate from SchemeCatalogItem.
 */
export interface SchemeInfo {
  scheme_code: string;
  scheme_name: string;
  ministry_or_dept?: string;
  /** null means "Not Applicable / field does not apply to this scheme" */
  max_loan_amount: number | null;
  /** null means "Not Applicable" */
  subsidy_percentage_general: number | null;
  /** null means "Not Applicable" */
  subsidy_percentage_special: number | null;
  official_portal_url?: string;
}

/**
 * Convert SchemeCatalogItem (API response) → SchemeInfo (UI display model).
 * Uses null for fields that are absent or 0-by-default-but-not-meaningful.
 */
export function catalogItemToSchemeInfo(item: SchemeCatalogItem): SchemeInfo {
  const ver = item.active_version;
  return {
    scheme_code: item.scheme_code,
    scheme_name: item.scheme_name,
    ministry_or_dept: item.ministry ?? item.department,
    max_loan_amount:
      ver && typeof ver.max_loan_amount === "number" && ver.max_loan_amount > 0
        ? ver.max_loan_amount
        : null,
    subsidy_percentage_general:
      ver && typeof ver.subsidy_percentage_general === "number"
        ? ver.subsidy_percentage_general
        : null,
    subsidy_percentage_special:
      ver && typeof ver.subsidy_percentage_special === "number"
        ? ver.subsidy_percentage_special
        : null,
    official_portal_url: ver?.official_portal_url,
  };
}

export async function fetchSchemes(category?: string): Promise<SchemeInfo[]> {
  const query = category ? `?category=${encodeURIComponent(category)}` : "";
  const catalogItems = await apiClient<SchemeCatalogItem[]>(`/schemes${query}`);
  return catalogItems.map(catalogItemToSchemeInfo);
}

