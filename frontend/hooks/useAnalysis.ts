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
      return data;
    } catch (err: any) {
      const msg = err.message || "Failed to execute business feasibility analysis.";
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, result, executeAnalysis, setResult };
}
