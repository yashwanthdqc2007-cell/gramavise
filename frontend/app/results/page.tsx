"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ReportWorkspace } from "@/components/dashboard/ReportWorkspace";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { AnalysisResult, FinancialAssumptions } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";

export default function ResultsPage() {
  const { t } = useTranslation();
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [financialAssumptions, setFinancialAssumptions] = useState<FinancialAssumptions | null>(null);
  const [resultTimestamp, setResultTimestamp] = useState<string | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      try {
        const rawResult = sessionStorage.getItem("gramavise_latest_result") || localStorage.getItem("gramavise_latest_result");
        const rawFinancials = sessionStorage.getItem("gramavise_financials") || localStorage.getItem("gramavise_financials");
        const rawTime = sessionStorage.getItem("gramavise_result_timestamp") || localStorage.getItem("gramavise_result_timestamp");

        if (rawResult && rawResult !== "undefined" && rawResult !== "null") {
          const parsed: AnalysisResult = JSON.parse(rawResult);
          if (parsed && parsed.analysis_id && parsed.financial_result && parsed.recommendation_status) {
            setResult(parsed);
          }
        }

        if (rawFinancials && rawFinancials !== "undefined" && rawFinancials !== "null") {
          setFinancialAssumptions(JSON.parse(rawFinancials));
        }

        if (rawTime && rawTime !== "undefined" && rawTime !== "null") {
          setResultTimestamp(rawTime);
        }
      } catch (err) {
        console.error("Failed to load cached analysis result:", err);
      } finally {
        setIsLoaded(true);
      }
    }
  }, []);

  if (!isLoaded) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <div className="animate-spin w-9 h-9 border-4 border-emerald-600 border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-slate-400 text-sm font-medium">{t("results.loadingText")}</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="max-w-md mx-auto px-4 py-20 text-center">
        <Card className="space-y-5 p-8 border border-slate-800 shadow-sm bg-[#0A1A28]">
          <div className="w-14 h-14 bg-amber-500/10 text-amber-300 border border-amber-500/20 rounded-2xl flex items-center justify-center mx-auto text-2xl">
            📋
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">{t("results.empty.title")}</h2>
            <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
              {t("results.empty.desc")}
            </p>
          </div>
          <Link href="/onboarding" className="block pt-2">
            <Button className="w-full font-bold py-2.5 rounded-xl shadow-xs">
              {t("results.empty.cta")}
            </Button>
          </Link>
        </Card>
      </div>
    );
  }

  return (
    <ReportWorkspace
      result={result}
      financialAssumptions={financialAssumptions}
      resultTimestamp={resultTimestamp}
      isHistorical={false}
    />
  );
}
