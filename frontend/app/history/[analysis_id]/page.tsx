"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { DecisionHero } from "@/components/dashboard/DecisionHero";
import { WhyThisDecision } from "@/components/dashboard/WhyThisDecision";
import { NumbersAtAGlance } from "@/components/dashboard/NumbersAtAGlance";
import { BeforeYouBorrow } from "@/components/dashboard/BeforeYouBorrow";
import { LocalMarketSays } from "@/components/dashboard/LocalMarketSays";
import { FinancialSummary } from "@/components/dashboard/FinancialSummary";
import { BreakEvenChart } from "@/components/financial/BreakEvenChart";
import { ExplainNumberModal } from "@/components/financial/ExplainNumberModal";
import { ScenarioLabSection } from "@/components/dashboard/ScenarioLabSection";
import { SchemeSection } from "@/components/dashboard/SchemeSection";
import { PreLoanActionPlanSection } from "@/components/dashboard/PreLoanActionPlanSection";
import { RecommendationCard } from "@/components/dashboard/RecommendationCard";
import { EvidenceDrawer } from "@/components/evidence/EvidenceDrawer";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { LoadingState } from "@/components/common/LoadingState";
import { ErrorState } from "@/components/common/ErrorState";
import { AnalysisResult, FinancialAssumptions, BusinessProfile, NumberExplanation } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";
import { getHistoricalAnalysis } from "@/services/api/analysis";
import { updateHistoryEntryOpened, removeHistoryEntry } from "@/lib/storage/historyStorage";
import { ArrowLeft, Play, Copy, Printer, Clock } from "lucide-react";

export default function HistoricalAnalysisPage() {
  const params = useParams();
  const router = useRouter();
  const { t } = useTranslation();
  const analysisId = Array.isArray(params.analysis_id) ? params.analysis_id[0] : (params.analysis_id as string);

  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorStatus, setErrorStatus] = useState<number | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activeExplanation, setActiveExplanation] = useState<NumberExplanation | null>(null);

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
        <Card className="p-8 space-y-4 border border-slate-800 shadow-sm">
          <div className="w-14 h-14 bg-amber-500/10 text-amber-300 rounded-2xl flex items-center justify-center mx-auto text-2xl font-bold border border-amber-500/30">
            🔍
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900">{t("history.notFoundTitle")}</h2>
            <p className="text-xs text-stone-500 mt-1 leading-relaxed">
              {t("history.notFoundDesc")}
            </p>
          </div>
          <div className="space-y-2 pt-2">
            <Button
              variant="outline"
              onClick={handleRemoveStale}
              className="w-full min-h-[44px] text-xs text-rose-600 border-rose-200 hover:bg-rose-50"
            >
              {t("history.removeStaleEntry")}
            </Button>
            <Link href="/history" className="block">
              <Button variant="secondary" className="w-full min-h-[44px] border-slate-700 text-slate-200">
                ← {t("nav.history")}
              </Button>
            </Link>
            <Link href="/onboarding" className="block">
              <Button className="w-full min-h-[44px] bg-emerald-700 hover:bg-emerald-800 text-white font-bold">
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

  const financialAssumptions = result.financial_input_snapshot;
  const expectedDailyCustomers = financialAssumptions?.customers_per_day;
  const createdDate = result.evaluation_metadata?.evaluated_at
    ? new Date(result.evaluation_metadata.evaluated_at).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" })
    : "";

  const handleExplainNumber = (metricId: string) => {
    const exp = result?.financial_result?.explanations?.[metricId] || null;
    setActiveExplanation(exp);
  };

  const businessTitle = result.business_input_snapshot?.category || result.business_input_snapshot?.business_name
    ? `${result.business_input_snapshot.business_name || result.business_input_snapshot.category} Evaluation`
    : "Enterprise Evaluation";

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 sm:py-10 space-y-10">
      {/* Historical Point-in-Time Banner */}
      <div
        role="status"
        className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-4 flex items-start gap-3.5 text-xs sm:text-sm text-amber-200 shadow-2xs"
      >
        <Clock className="w-5 h-5 text-amber-300 shrink-0 mt-0.5" aria-hidden="true" />
        <div className="space-y-0.5">
          <span className="font-bold mr-1.5">
            [{t("history.historicalNoticeTitle")}]
          </span>
          <span>
            {t("history.historicalNoticeDesc")}
            {createdDate && ` (Saved on ${createdDate})`}
          </span>
        </div>
      </div>

      {/* 1. Page Header & Actions */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Link href="/history" className="text-slate-400 hover:text-emerald-300 text-xs flex items-center gap-1 font-semibold transition-colors">
              <ArrowLeft className="w-3.5 h-3.5" aria-hidden="true" />
              {t("nav.history")}
            </Link>
            <span className="text-slate-600">•</span>
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
              Historical Snapshot
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            {businessTitle}
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            {t("results.header.analysisId")}: {result.analysis_id}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2 self-stretch sm:self-auto">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleUseAsStartingPoint}
            className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 font-medium"
          >
            <Copy className="w-3.5 h-3.5" aria-hidden="true" />
            <span>{t("history.useAsStartingPoint")}</span>
          </Button>

          <Link href="/onboarding" className="flex-1 sm:flex-none">
            <Button size="sm" className="w-full flex items-center justify-center gap-1.5 font-bold">
              <Play className="w-3.5 h-3.5" aria-hidden="true" />
              <span>{t("results.header.newAssessment")}</span>
            </Button>
          </Link>

          <Button
            variant="secondary"
            size="sm"
            onClick={() => window.print()}
            className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 font-medium"
          >
            <Printer className="w-3.5 h-3.5" aria-hidden="true" />
            <span>{t("results.header.printReport")}</span>
          </Button>
        </div>
      </div>

      {/* 2. Decision Hero (Primary Visual Anchor - Viewport 1) */}
      <DecisionHero
        status={result.recommendation_status}
        confidence={result.confidence_score}
        businessName={result.business_input_snapshot?.business_name || "Rural Enterprise"}
        businessCategory={result.business_input_snapshot?.category}
        locationSummary={result.market_result?.location_summary || "Local Rural Catchment"}
        summary={result.ai_explanation?.summary || result.decision_trace?.summary}
        evidenceList={result.evidence_ledger || result.evidence_list || []}
        assessmentDate={createdDate}
      />

      {/* 3. Why This Decision? (Deterministic Rule Evidence) */}
      <WhyThisDecision
        decisionTrace={result.decision_trace}
      />

      {/* 4. Numbers At A Glance (Key Financial Metrics with Micro-Context) */}
      <NumbersAtAGlance
        financials={result.financial_result}
        onExplainNumber={handleExplainNumber}
      />

      {/* 5. Before You Borrow (High Priority Verification Checklist) */}
      <BeforeYouBorrow
        checklist={result.verification_checklist || []}
      />

      {/* 6. What The Local Market Says (Demand, Competition, Pricing) */}
      <LocalMarketSays
        market={result.market_result}
        evidenceList={result.evidence_ledger || result.evidence_list || []}
      />

      {/* 7. Financial Picture & Break-Even Chart */}
      <div className="space-y-6">
        <FinancialSummary
          financials={result.financial_result}
          assumptions={financialAssumptions}
          recommendationStatus={result.recommendation_status}
        />

        <BreakEvenChart
          breakEvenUnitsDaily={result.financial_result.break_even_units_daily}
          expectedDailyUnits={expectedDailyCustomers}
        />
      </div>

      {/* 8. What If Things Don't Go As Planned? (Scenario Lab) */}
      <ScenarioLabSection
        result={result}
        baselineFinancials={financialAssumptions}
      />

      {/* 9. Government Scheme Options */}
      <SchemeSection schemeResult={result.scheme_result} />

      {/* 10. Your Next Steps (Roadmap & Bank Readiness) */}
      <PreLoanActionPlanSection
        actionPlan={result.action_plan}
        documentReadiness={result.document_readiness}
        bankReadiness={result.bank_readiness}
      />

      {/* 11. Plain-Language Explanation (AI-Assisted Editorial) */}
      <RecommendationCard explanation={result.ai_explanation} />

      {/* 12. Evidence & Audit Trail (Collapsed for Evaluators/Judges) */}
      <EvidenceDrawer evidenceList={result.evidence_ledger || result.evidence_list || []} />

      {/* Number Inspector Modal */}
      <ExplainNumberModal
        explanation={activeExplanation}
        isOpen={activeExplanation !== null}
        onClose={() => setActiveExplanation(null)}
      />
    </div>
  );
}
