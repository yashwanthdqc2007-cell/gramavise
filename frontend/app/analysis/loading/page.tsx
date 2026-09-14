"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { LoadingState } from "@/components/common/LoadingState";
import { ErrorState } from "@/components/common/ErrorState";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { runAnalysis, AnalyzePayload } from "@/services/api/analysis";
import { BusinessProfile, FinancialAssumptions, AnalysisResult } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";
import { ApiError } from "@/lib/api";

type PageState = "loading" | "error" | "missing_data";

function sanitizeAndValidatePayload(preferred_language: string): AnalyzePayload | null {
  if (typeof window === "undefined") return null;

  try {
    const rawProfile = sessionStorage.getItem("gramavise_profile");
    const rawFinancials = sessionStorage.getItem("gramavise_financials");

    if (!rawProfile || !rawFinancials) return null;

    const parsedProfile = JSON.parse(rawProfile);
    const parsedFinancials = JSON.parse(rawFinancials);

    if (
      !parsedProfile.business_name?.trim() ||
      !parsedProfile.category?.trim() ||
      !parsedProfile.location?.state?.trim() ||
      !parsedProfile.location?.district?.trim() ||
      !parsedProfile.location?.village?.trim()
    ) {
      return null;
    }

    const profile: BusinessProfile = {
      business_name: String(parsedProfile.business_name).trim(),
      category: String(parsedProfile.category).trim(),
      description: parsedProfile.description ? String(parsedProfile.description).trim() : undefined,
      location: {
        state: String(parsedProfile.location.state).trim(),
        district: String(parsedProfile.location.district).trim(),
        village: String(parsedProfile.location.village).trim(),
        latitude: parsedProfile.location.latitude != null ? Number(parsedProfile.location.latitude) : undefined,
        longitude: parsedProfile.location.longitude != null ? Number(parsedProfile.location.longitude) : undefined,
      },
      experience_years: Math.max(0, Number(parsedProfile.experience_years) || 0),
      own_capital: Math.max(0, Number(parsedProfile.own_capital) || 0),
      desired_loan: Math.max(0, Number(parsedProfile.desired_loan) || 0),
      is_new_business: parsedProfile.is_new_business !== false,
    };

    const financials: FinancialAssumptions = {
      startup_cost: Math.max(0, Number(parsedFinancials.startup_cost) || 0),
      equipment_cost: Math.max(0, Number(parsedFinancials.equipment_cost) || 0),
      inventory_cost: Math.max(0, Number(parsedFinancials.inventory_cost) || 0),
      monthly_fixed_cost: Math.max(0, Number(parsedFinancials.monthly_fixed_cost) || 0),
      customers_per_day: Math.max(0, Math.floor(Number(parsedFinancials.customers_per_day) || 0)),
      avg_ticket_price: Math.max(0, Number(parsedFinancials.avg_ticket_price) || 0),
      working_days_per_month: Math.min(
        31,
        Math.max(1, Math.floor(Number(parsedFinancials.working_days_per_month) || 26))
      ),
      variable_cost_pct: Math.min(99.9, Math.max(0, Number(parsedFinancials.variable_cost_pct) || 0)),
      interest_rate_pct: Math.min(40, Math.max(0, Number(parsedFinancials.interest_rate_pct) || 10.5)),
      loan_tenure_months: Math.min(
        120,
        Math.max(1, Math.floor(Number(parsedFinancials.loan_tenure_months) || 36))
      ),
    };

    return { profile, financials, preferred_language };
  } catch (e) {
    console.error("Error reading stored onboarding payload:", e);
    return null;
  }
}

export default function AnalysisLoadingPage() {
  const router = useRouter();
  const { t, language } = useTranslation();
  const [pageState, setPageState] = useState<PageState>("loading");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [errorTitle, setErrorTitle] = useState<string>("");
  const isExecutingRef = useRef<boolean>(false);

  const execute = useCallback(async () => {
    if (isExecutingRef.current) return;

    const payload = sanitizeAndValidatePayload(language);
    if (!payload) {
      setPageState("missing_data");
      return;
    }

    isExecutingRef.current = true;
    setPageState("loading");
    setErrorMessage("");
    setErrorTitle("");

    try {
      const result: AnalysisResult = await runAnalysis(payload);

      if (!result || !result.analysis_id || !result.financial_result || !result.recommendation_status) {
        throw new ApiError(
          "Received an incomplete analysis response from the advisory engine.",
          "MALFORMED_RESPONSE"
        );
      }

      if (typeof window !== "undefined") {
        try {
          sessionStorage.setItem("gramavise_latest_result", JSON.stringify(result));
          sessionStorage.setItem("gramavise_result_timestamp", new Date().toISOString());
        } catch (storageErr) {
          console.error("Failed to cache latest analysis result:", storageErr);
        }
      }

      try {
        const { saveHistoryEntry } = await import("@/lib/storage/historyStorage");
        saveHistoryEntry({
          analysis_id: result.analysis_id,
          business_name: payload.profile.business_name || "Untitled Business",
          business_category: payload.profile.category || "General",
          recommendation_status: result.recommendation_status,
          created_at: new Date().toISOString(),
        });
      } catch (histErr) {
        console.error("Failed to save analysis to history:", histErr);
      }

      router.push("/results");
    } catch (err: any) {
      console.error("Analysis execution error:", err);

      let title = t("common.errorTitle");
      let friendlyMessage = err?.message || "GramaVise was unable to complete the analysis. Please try again.";

      if (err instanceof ApiError) {
        if (err.code === "TIMEOUT") {
          title = t("network.timeout");
          friendlyMessage = t("network.timeout");
        } else if (err.code === "OFFLINE") {
          title = t("network.offlineTitle");
          friendlyMessage = t("network.offlineDesc");
        } else if (err.code === "SERVER_ERROR") {
          title = t("network.serverUnavailable");
          friendlyMessage = t("network.serverUnavailable");
        }
      }

      setErrorTitle(title);
      setErrorMessage(friendlyMessage);
      setPageState("error");
    } finally {
      isExecutingRef.current = false;
    }
  }, [router, language, t]);

  useEffect(() => {
    execute();
  }, [execute]);

  const handleRetry = () => {
    execute();
  };

  const handleGoToOnboarding = () => {
    router.push("/onboarding");
  };

  return (
    <div className="min-h-[60vh] flex items-center justify-center px-4 py-12">
      {pageState === "loading" && (
        <LoadingState message={t("loading.subtitle")} />
      )}

      {pageState === "error" && (
        <ErrorState
          title={errorTitle || t("common.errorTitle")}
          message={errorMessage}
          onRetry={handleRetry}
          secondaryAction={{
            label: t("onboarding.actions.previous"),
            onClick: handleGoToOnboarding,
          }}
        />
      )}

      {pageState === "missing_data" && (
        <Card className="max-w-md mx-auto text-center space-y-4 p-8">
          <div className="w-12 h-12 bg-amber-100 text-amber-600 rounded-full flex items-center justify-center mx-auto text-xl font-bold">
            📋
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">{t("results.empty.title")}</h3>
            <p className="text-sm text-slate-400 mt-1">
              {t("results.empty.desc")}
            </p>
          </div>
          <Button className="w-full min-h-[44px]" onClick={handleGoToOnboarding}>
            {t("results.empty.cta")}
          </Button>
        </Card>
      )}
    </div>
  );
}
