import { apiClient } from "@/lib/api";
import { BusinessProfile, FinancialAssumptions, AnalysisResult } from "@/lib/types";

export interface AnalyzePayload {
  profile: BusinessProfile;
  financials: FinancialAssumptions;
  preferred_language: string;
}

export async function runAnalysis(
  payload: AnalyzePayload,
  idempotencyKey?: string
): Promise<AnalysisResult> {
  const headers: Record<string, string> = {};
  if (idempotencyKey) {
    headers["Idempotency-Key"] = idempotencyKey;
  }
  return apiClient<AnalysisResult>("/analyze", {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
}

export async function getHistoricalAnalysis(analysisId: string): Promise<AnalysisResult> {
  return apiClient<AnalysisResult>(`/analyze/${encodeURIComponent(analysisId)}`, {
    method: "GET",
  });
}

