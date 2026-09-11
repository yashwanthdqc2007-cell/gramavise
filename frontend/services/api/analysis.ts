import { apiClient } from "@/lib/api";
import { BusinessProfile, FinancialAssumptions, AnalysisResult } from "@/lib/types";

export interface AnalyzePayload {
  profile: BusinessProfile;
  financials: FinancialAssumptions;
  preferred_language: string;
}

export async function runAnalysis(payload: AnalyzePayload): Promise<AnalysisResult> {
  // TODO [Frontend Lead]: Add analytics tracking and cache layer
  return apiClient<AnalysisResult>("/analyze", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
