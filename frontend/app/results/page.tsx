"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
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
import { AnalysisResult, FinancialAssumptions, NumberExplanation } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";
import { useNetworkStatus } from "@/hooks/useNetworkStatus";
import { Printer, RotateCcw, AlertCircle } from "lucide-react";

export default function ResultsPage() {
  const { t } = useTranslation();
  const { isOnline } = useNetworkStatus();
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [financialAssumptions, setFinancialAssumptions] = useState<FinancialAssumptions | null>(null);
  const [resultTimestamp, setResultTimestamp] = useState<string | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [activeExplanation, setActiveExplanation] = useState<NumberExplanation | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      try {
        const storedResult = sessionStorage.getItem("gramavise_latest_result");
        const storedFinancials = sessionStorage.getItem("gramavise_financials");
        const storedTime = sessionStorage.getItem("gramavise_result_timestamp");

        if (storedResult) {
          const parsed: AnalysisResult = JSON.parse(storedResult);
          if (parsed && parsed.analysis_id && parsed.financial_result && parsed.recommendation_status) {
            setResult(parsed);
          }
        }

        if (storedFinancials) {
          setFinancialAssumptions(JSON.parse(storedFinancials));
        }

        if (storedTime) {
          setResultTimestamp(storedTime);
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
        <Card className="space-y-5 p-8 border border-slate-800 shadow-sm">
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

  const expectedDailyCustomers = financialAssumptions?.customers_per_day;
  const formattedDate = resultTimestamp
    ? new Date(resultTimestamp).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" })
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
      {/* Historical / Offline Snapshot Notice */}
      {(!isOnline || resultTimestamp) && (
        <div
          role="status"
          className="bg-slate-900/70 border border-slate-800 rounded-xl p-3.5 sm:p-4 flex items-start gap-3 text-xs sm:text-sm text-slate-300 shadow-2xs"
        >
          <span className="text-base sm:text-lg shrink-0">🕒</span>
          <div>
            <span className="font-bold text-white mr-1.5">
              [{t("results.header.historicalBadge")}]
            </span>
            <span>
              {t("results.header.historicalNotice")}
              {formattedDate && ` (${formattedDate})`}
            </span>
          </div>
        </div>
      )}

      {/* 1. Page Header & Actions */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-5">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-300 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/30 inline-block mb-2">
            Decision Briefing
          </span>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            {businessTitle}
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            {t("results.header.analysisId")}: {result.analysis_id}
          </p>
        </div>

        <div className="flex items-center gap-2.5 self-stretch sm:self-auto">
          <Link href="/onboarding" className="flex-1 sm:flex-none">
            <Button variant="secondary" size="sm" className="w-full flex items-center justify-center gap-1.5">
              <RotateCcw className="w-3.5 h-3.5" />
              <span>{t("results.header.newAssessment")}</span>
            </Button>
          </Link>
          <Button
            size="sm"
            onClick={() => window.print()}
            className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold"
          >
            <Printer className="w-3.5 h-3.5" />
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
        assessmentDate={formattedDate}
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
