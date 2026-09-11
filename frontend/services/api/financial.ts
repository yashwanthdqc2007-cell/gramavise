import { apiClient } from "@/lib/api";
import { FinancialAssumptions, FinancialResult } from "@/lib/types";

export interface CalculateFinancialsPayload {
  own_capital: number;
  desired_loan?: number;
  financials: FinancialAssumptions;
}

export async function calculateFinancials(payload: CalculateFinancialsPayload): Promise<FinancialResult> {
  return apiClient<FinancialResult>("/financial/calculate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
