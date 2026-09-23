"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { ReportWorkspace } from "@/components/dashboard/ReportWorkspace";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { LoadingState } from "@/components/common/LoadingState";
import { ErrorState } from "@/components/common/ErrorState";
import { AnalysisResult, BusinessProfile } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";
import { getHistoricalAnalysis } from "@/services/api/analysis";
import { updateHistoryEntryOpened, removeHistoryEntry } from "@/lib/storage/historyStorage";

export default function HistoricalAnalysisPage() {
  const params = useParams();
  const router = useRouter();
  const { t } = useTranslation();
  const analysisId = Array.isArray(params.analysis_id) ? params.analysis_id[0] : (params.analysis_id as string);

  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorStatus, setErrorStatus] = useState<number | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!analysisId) return;

    let isMounted = true;
    setLoading(true);
    setErrorStatus(null);
    setErrorMessage(null);

    getHistoricalAnalysis(analysisId)
      .then((data) => {
        if (!isMounted) return;
        setResult(data);
        updateHistoryEntryOpened(analysisId);
      })
      .catch((err: any) => {
        if (!isMounted) return;
        console.error("Failed to load historical analysis:", err);
        setErrorStatus(err?.statusCode || (err?.code === "NOT_FOUND" ? 404 : 500));
        setErrorMessage(err?.message || "Failed to retrieve historical analysis.");
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [analysisId]);

  const handleUseAsStartingPoint = () => {
    if (!result) return;

    if (typeof window !== "undefined") {
      try {
        if (result.business_input_snapshot) {
          sessionStorage.setItem("gramavise_profile", JSON.stringify(result.business_input_snapshot));
        } else if (result.market_result?.geography) {
          const profile: Partial<BusinessProfile> = {
            location: {
              state: result.market_result.geography.state_name || "",
              district: result.market_result.geography.district_name || "",
              village: result.market_result.geography.village_name || "",
            },
          };
          sessionStorage.setItem("gramavise_profile", JSON.stringify(profile));
        }

        if (result.financial_input_snapshot) {
          sessionStorage.setItem("gramavise_financials", JSON.stringify(result.financial_input_snapshot));
        }
      } catch (err) {
        console.error("Failed to stage starting point assumptions:", err);
      }
    }

    router.push("/onboarding");
  };

  const handleRemoveStale = () => {
    if (analysisId) {
      removeHistoryEntry(analysisId);
      router.push("/history");
    }
  };

  if (loading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center px-4 py-12">
        <LoadingState message={t("results.loadingText")} />
      </div>
    );
  }

  if (errorStatus === 404 || (!result && !loading)) {
    return (
      <div className="max-w-md mx-auto px-4 py-16 text-center space-y-4">
        <Card className="p-8 space-y-4 border border-slate-800 shadow-sm bg-[#0A1A28]">
          <div className="w-14 h-14 bg-amber-500/10 text-amber-300 rounded-2xl flex items-center justify-center mx-auto text-2xl font-bold border border-amber-500/30">
            🔍
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">{t("history.notFoundTitle")}</h2>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              {t("history.notFoundDesc")}
            </p>
          </div>
          <div className="space-y-2 pt-2">
            <Button
              variant="outline"
              onClick={handleRemoveStale}
              className="w-full min-h-[44px] text-xs text-rose-400 border-rose-500/30 hover:bg-rose-500/10"
            >
              {t("history.removeStaleEntry")}
            </Button>
            <Link href="/history" className="block">
              <Button variant="secondary" className="w-full min-h-[44px] border-slate-700 text-slate-200">
                ← {t("nav.history")}
              </Button>
            </Link>
            <Link href="/onboarding" className="block">
              <Button className="w-full min-h-[44px] bg-emerald-600 hover:bg-emerald-700 text-white font-bold">
                {t("history.startNewAnalysis")} →
              </Button>
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  if (errorMessage && !result) {
    return (
      <div className="max-w-md mx-auto px-4 py-16">
        <ErrorState
          title={t("common.errorTitle")}
          message={errorMessage}
          onRetry={() => window.location.reload()}
          secondaryAction={{
            label: t("nav.history"),
            onClick: () => router.push("/history"),
          }}
        />
      </div>
    );
  }

  if (!result) return null;

  return (
    <ReportWorkspace
      result={result}
      financialAssumptions={result.financial_input_snapshot}
      resultTimestamp={result.evaluation_metadata?.evaluated_at}
      isHistorical={true}
      onUseAsStartingPoint={handleUseAsStartingPoint}
    />
  );
}
