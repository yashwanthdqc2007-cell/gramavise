import { apiClient } from "@/lib/api";

export interface SchemeInfo {
  scheme_code: string;
  scheme_name: string;
  ministry_or_dept?: string;
  max_loan_amount: number;
  subsidy_percentage_general: number;
  subsidy_percentage_special: number;
  official_portal_url?: string;
}

export async function fetchSchemes(category?: string): Promise<SchemeInfo[]> {
  const query = category ? `?category=${encodeURIComponent(category)}` : "";
  return apiClient<SchemeInfo[]>(`/schemes${query}`);
}
