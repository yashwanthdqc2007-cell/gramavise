"use client";

import { useState } from "react";
import { AnalysisResult, BusinessProfile, FinancialAssumptions } from "@/lib/types";
import { runAnalysis } from "@/services/api/analysis";

export function useAnalysis() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const executeAnalysis = async (
    profile: BusinessProfile,
    financials: FinancialAssumptions,
    preferredLanguage: string = "en"
  ) => {
    setLoading(true);
    setError(null);
    try {
      const data = await runAnalysis({
        profile,
        financials,
        preferred_language: preferredLanguage,
      });
      setResult(data);
      if (typeof window !== "undefined") {
        try {
          sessionStorage.setItem("gramavise_latest_result", JSON.stringify(data));
          sessionStorage.setItem("gramavise_result_timestamp", new Date().toISOString());
        } catch {
          // ignore
        }
      }
      try {
        const { saveHistoryEntry } = await import("@/lib/storage/historyStorage");
        saveHistoryEntry({
          analysis_id: data.analysis_id,
          business_name: profile.business_name || "Untitled Business",
          business_category: profile.category || "General",
          recommendation_status: data.recommendation_status,
          created_at: new Date().toISOString(),
        });
      } catch {
        // ignore
      }
      return data;
    } catch (err: any) {
      const msg = err?.message || "Failed to execute business feasibility analysis.";
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, result, executeAnalysis, setResult };
}

