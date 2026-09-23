"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import {
  AnalysisResult,
  FinancialAssumptions,
  NumberExplanation,
  RecommendationStatus,
} from "@/lib/types";
import { useTranslation } from "@/lib/i18n";
import { useNetworkStatus } from "@/hooks/useNetworkStatus";

// Component imports
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
import { DecisionTraceSection } from "@/components/dashboard/DecisionTraceSection";
import { SWOTSection } from "@/components/dashboard/swot";
import { EvidenceDrawer } from "@/components/evidence/EvidenceDrawer";
import { Button } from "@/components/ui/Button";

// Icons
import {
  LayoutDashboard,
  Coins,
  Store,
  ShieldAlert,
  Landmark,
  CheckSquare,
  Sliders,
  RotateCcw,
  Copy,
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  MapPin,
  Calendar,
  Building2,
  Clock,
} from "lucide-react";

export type ReportTabId =
  | "overview"
  | "financials"
  | "market"
  | "risks"
  | "schemes"
  | "action_plan"
  | "scenario_lab";

interface ReportWorkspaceProps {
  result: AnalysisResult;
  financialAssumptions?: FinancialAssumptions | null;
  resultTimestamp?: string | null;
  isHistorical?: boolean;
  onUseAsStartingPoint?: () => void;
}

export const ReportWorkspace: React.FC<ReportWorkspaceProps> = ({
  result,
  financialAssumptions,
  resultTimestamp,
  isHistorical = false,
  onUseAsStartingPoint,
}) => {
  const { t } = useTranslation();
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();
  const { isOnline } = useNetworkStatus();

  // Tab state: default to "overview" or search param
  const validTabs: ReportTabId[] = [
    "overview",
    "financials",
    "market",
    "risks",
    "schemes",
    "action_plan",
    "scenario_lab",
  ];

  const initialTab = (searchParams?.get("tab") as ReportTabId) || "overview";
  const [activeTab, setActiveTab] = useState<ReportTabId>(
    validTabs.includes(initialTab) ? initialTab : "overview"
  );

  const [activeExplanation, setActiveExplanation] = useState<NumberExplanation | null>(null);
  const tabListRef = useRef<HTMLDivElement>(null);

  // Sync tab with URL without triggering re-fetch
  const handleTabChange = (tabId: ReportTabId) => {
    setActiveTab(tabId);
    if (typeof window !== "undefined") {
      const url = new URL(window.location.href);
      if (tabId === "overview") {
        url.searchParams.delete("tab");
      } else {
        url.searchParams.set("tab", tabId);
      }
      window.history.replaceState(null, "", url.toString());
    }
  };

  const coreReportTabIds: ReportTabId[] = [
    "overview",
    "financials",
    "market",
    "risks",
    "schemes",
    "action_plan",
  ];

  // Keyboard accessibility for tabs
  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    if (e.key === "ArrowRight") {
      e.preventDefault();
      const nextIndex = (index + 1) % coreReportTabIds.length;
      handleTabChange(coreReportTabIds[nextIndex]);
      const nextButton = tabListRef.current?.querySelectorAll<HTMLButtonElement>('[role="tab"]')[nextIndex];
      nextButton?.focus();
    } else if (e.key === "ArrowLeft") {
      e.preventDefault();
      const prevIndex = (index - 1 + coreReportTabIds.length) % coreReportTabIds.length;
      handleTabChange(coreReportTabIds[prevIndex]);
      const prevButton = tabListRef.current?.querySelectorAll<HTMLButtonElement>('[role="tab"]')[prevIndex];
      prevButton?.focus();
    } else if (e.key === "Home") {
      e.preventDefault();
      handleTabChange(coreReportTabIds[0]);
      const firstButton = tabListRef.current?.querySelectorAll<HTMLButtonElement>('[role="tab"]')[0];
      firstButton?.focus();
    } else if (e.key === "End") {
      e.preventDefault();
      handleTabChange(coreReportTabIds[coreReportTabIds.length - 1]);
      const lastButton = tabListRef.current?.querySelectorAll<HTMLButtonElement>('[role="tab"]')[coreReportTabIds.length - 1];
      lastButton?.focus();
    }
  };

  const handleExplainNumber = (metricId: string) => {
    const exp = result?.financial_result?.explanations?.[metricId] || null;
    setActiveExplanation(exp);
  };

  const assumptions = financialAssumptions || result.financial_input_snapshot;
  const expectedDailyCustomers = assumptions?.customers_per_day;

  const dateToFormat = resultTimestamp || result.evaluation_metadata?.evaluated_at;
  const formattedDate = dateToFormat
    ? new Date(dateToFormat).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" })
    : "";

  const businessName =
    result.business_input_snapshot?.business_name ||
    result.business_input_snapshot?.category ||
    result.market_result?.geography?.village_name ||
    "Kisan Rural Enterprise";
  const businessCategory =
    result.business_input_snapshot?.category ||
    result.market_result?.price_benchmark?.category ||
    "Micro-Enterprise Evaluation";
  const locationSummary = result.market_result?.location_summary || "Local Rural Catchment";

  // Decision Status Theme
  const statusTheme = {
    PROCEED: {
      cardBg: "bg-gradient-to-br from-emerald-950/80 via-[#0B241C] to-[#041410] border-emerald-500/40",
      badge: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
      icon: <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />,
      title: t("results.decisionHero.proceed"),
      barColor: "bg-emerald-400",
    },
    VALIDATE_FIRST: {
      cardBg: "bg-gradient-to-br from-amber-950/80 via-[#261B0B] to-[#140F04] border-amber-500/40",
      badge: "bg-amber-500/20 text-amber-300 border-amber-500/40",
      icon: <AlertTriangle className="w-6 h-6 text-amber-400 shrink-0" />,
      title: t("results.decisionHero.validateFirst"),
      barColor: "bg-amber-400",
    },
    RECONSIDER: {
      cardBg: "bg-gradient-to-br from-rose-950/80 via-[#280E14] to-[#140508] border-rose-500/40",
      badge: "bg-rose-500/20 text-rose-300 border-rose-500/40",
      icon: <XCircle className="w-6 h-6 text-rose-400 shrink-0" />,
      title: t("results.decisionHero.reconsider"),
      barColor: "bg-rose-400",
    },
  };

  const theme = statusTheme[result.recommendation_status] || statusTheme.VALIDATE_FIRST;
  const confidence = result.confidence_score || 0.7;

  // 6 Core Report Tabs
  const reportTabs = [
    {
      id: "overview" as ReportTabId,
      label: t("results.tabs.overview") || "Overview",
      icon: LayoutDashboard,
    },
    {
      id: "financials" as ReportTabId,
      label: t("results.tabs.financials") || "Financials",
      icon: Coins,
    },
    {
      id: "market" as ReportTabId,
      label: t("results.tabs.market") || "Local Market",
      icon: Store,
    },
    {
      id: "risks" as ReportTabId,
      label: t("results.tabs.risks") || "Risks & Evidence",
      icon: ShieldAlert,
    },
    {
      id: "schemes" as ReportTabId,
      label: t("results.tabs.schemes") || "Schemes & Funding",
      icon: Landmark,
    },
    {
      id: "action_plan" as ReportTabId,
      label: t("results.tabs.actionPlan") || "Action Plan",
      icon: CheckSquare,
    },
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6">
      {/* Top Notice: Historical Snapshot Banner if applicable */}
      {isHistorical && (
        <div
          role="status"
          className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-3.5 flex items-start gap-3 text-xs sm:text-sm text-amber-200 shadow-2xs"
        >
          <Clock className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" aria-hidden="true" />
          <div className="space-y-0.5">
            <span className="font-bold mr-1.5">
              [{t("history.historicalNoticeTitle")}]
            </span>
            <span>
              {t("history.historicalNoticeDesc")}
              {formattedDate && ` (Saved: ${formattedDate})`}
            </span>
          </div>
        </div>
      )}

      {/* Offline Alert if offline */}
      {!isOnline && !isHistorical && (
        <div
          role="status"
          className="bg-slate-900 border border-slate-800 rounded-xl p-3.5 flex items-center gap-3 text-xs text-slate-300"
        >
          <span className="text-base shrink-0">📡</span>
          <span>Offline mode. Viewing cached evaluation result.</span>
        </div>
      )}

      {/* ============================================================ */}
      {/* 1. PERSISTENT COMPACT DECISION AREA (NON-STICKY)              */}
      {/* ============================================================ */}
      <div
        className={`rounded-2xl border p-5 sm:p-6 shadow-xl ${theme.cardBg} transition-all`}
        data-testid="decision-summary-hero"
      >
        {/* Top bar: Breadcrumb / Meta + Quick Actions */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/10 pb-4">
          <div className="flex flex-wrap items-center gap-2 text-xs text-white/70">
            <Link
              href="/history"
              className="hover:text-emerald-300 flex items-center gap-1 font-semibold transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>{t("nav.history")}</span>
            </Link>
            <span className="text-white/30">•</span>
            <span className="font-mono text-[11px] text-white/60">
              ID: {result.analysis_id.slice(0, 8)}...
            </span>
            {formattedDate && (
              <>
                <span className="text-white/30">•</span>
                <span className="flex items-center gap-1 text-white/60">
                  <Calendar className="w-3 h-3 text-white/40" />
                  {formattedDate}
                </span>
              </>
            )}
          </div>

          {/* Action buttons */}
          <div className="flex flex-wrap items-center gap-2">
            {onUseAsStartingPoint && (
              <Button
                variant="secondary"
                size="sm"
                onClick={onUseAsStartingPoint}
                className="text-xs flex items-center gap-1.5 font-medium border-white/20 bg-black/30 hover:bg-black/50 text-white"
              >
                <Copy className="w-3.5 h-3.5" />
                <span>{t("history.useAsStartingPoint")}</span>
              </Button>
            )}

            <Link href="/onboarding">
              <Button
                variant="secondary"
                size="sm"
                className="text-xs flex items-center gap-1.5 font-medium border-white/20 bg-black/30 hover:bg-black/50 text-white"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>{t("results.header.newAssessment")}</span>
              </Button>
            </Link>

            <button
              type="button"
              onClick={() => handleTabChange(activeTab === "scenario_lab" ? "overview" : "scenario_lab")}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 shadow-sm transition-all duration-150 ease-out select-none active:scale-[0.99] focus:outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#19D98B]/60 focus-visible:outline-offset-2 motion-reduce:transition-none motion-reduce:transform-none ${
                activeTab === "scenario_lab"
                  ? "bg-amber-400 text-slate-950 font-black shadow-amber-500/20 active:bg-amber-300"
                  : "bg-[#19D98B] hover:bg-[#16C784] text-[#040F19] shadow-emerald-500/20 active:bg-[#14B870]"
              }`}
            >
              <Sliders className="w-3.5 h-3.5" />
              <span>{activeTab === "scenario_lab" ? "Exit Scenario Lab" : "Scenario Lab"}</span>
            </button>
          </div>
        </div>

        {/* Main Verdict Row: Business Title + Decision Verdict + Confidence */}
        <div className="pt-4 flex flex-col lg:flex-row lg:items-center justify-between gap-5">
          {/* Left: Identity & Summary */}
          <div className="space-y-2 max-w-2xl">
            <div className="flex flex-wrap items-center gap-2">
              <Building2 className="w-4 h-4 text-emerald-400" />
              <h1 className="text-xl sm:text-2xl font-black text-white tracking-tight">
                {businessName}
              </h1>
              {businessCategory && (
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-white/10 text-white/90 border border-white/15">
                  {businessCategory}
                </span>
              )}
            </div>

            {locationSummary && (
              <div className="flex items-center gap-1.5 text-xs text-white/70">
                <MapPin className="w-3.5 h-3.5 text-emerald-400/80 shrink-0" />
                <span>{locationSummary}</span>
              </div>
            )}

            <p className="text-xs sm:text-sm text-white/90 leading-relaxed font-medium pt-1">
              {result.ai_explanation?.summary || result.decision_trace?.summary}
            </p>
          </div>

          {/* Right: Decision Pill & Confidence Meter */}
          <div className="shrink-0 flex items-center gap-4 bg-black/30 p-3.5 rounded-xl border border-white/10">
            {theme.icon}
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-base sm:text-lg font-black text-white tracking-tight">
                  {theme.title}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] uppercase font-bold text-white/60 tracking-wider">
                  Confidence:
                </span>
                <span className="text-xs font-bold text-white">
                  {(confidence * 100).toFixed(0)}%
                </span>
                <div className="w-16 h-1.5 bg-white/20 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${theme.barColor}`}
                    style={{ width: `${Math.min(100, Math.max(10, confidence * 100))}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ============================================================ */}
      {/* 2. ACCESSIBLE TAB NAVIGATION BAR (6 CORE REPORT TABS)        */}
      {/* ============================================================ */}
      <div className="border-b border-slate-800/90 sticky top-16 z-20 bg-[#050E17]/95 backdrop-blur-md pt-2 pb-0">
        <div
          ref={tabListRef}
          role="tablist"
          aria-label="6 Core Feasibility Report Tabs"
          className="flex items-center gap-1.5 overflow-x-auto no-scrollbar scroll-smooth pb-2 -mb-px"
        >
          {reportTabs.map((tab, idx) => {
            const Icon = tab.icon;
            const isSelected = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                role="tab"
                id={`tab-${tab.id}`}
                aria-controls={`tabpanel-${tab.id}`}
                aria-selected={isSelected}
                tabIndex={isSelected ? 0 : -1}
                onClick={() => handleTabChange(tab.id)}
                onKeyDown={(e) => handleKeyDown(e, idx)}
                className={`group flex items-center gap-2 px-3.5 py-2.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all duration-150 ease-out shrink-0 min-h-[42px] select-none motion-reduce:transition-none motion-reduce:transform-none active:scale-[0.99] focus:outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#19D98B]/60 focus-visible:outline-offset-2 ${
                  isSelected
                    ? "bg-[#19D98B]/10 text-[#19D98B] border border-[#19D98B]/40 shadow-xs active:bg-[#19D98B]/15"
                    : "text-slate-400 hover:text-slate-100 hover:bg-[#19D98B]/[0.06] border border-transparent active:bg-[#0E2635]"
                }`}
              >
                <Icon
                  className={`w-4 h-4 shrink-0 transition-colors duration-150 ease-out motion-reduce:transition-none ${
                    isSelected ? "text-[#19D98B]" : "text-slate-400 group-hover:text-slate-200"
                  }`}
                  aria-hidden="true"
                />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* ============================================================ */}
      {/* 3. TAB PANELS                                                */}
      {/* ============================================================ */}

      {/* TAB 1: OVERVIEW (DEFAULT) */}
      <div
        role="tabpanel"
        id="tabpanel-overview"
        aria-labelledby="tab-overview"
        hidden={activeTab !== "overview"}
        className="space-y-8 animate-in fade-in duration-150"
      >
        {/* Why This Decision (Deterministic Rule Trace) */}
        <WhyThisDecision decisionTrace={result.decision_trace} />

        {/* SWOT / Business Factors (Evidence-Backed Decision Support) */}
        <SWOTSection
          swot={result.market_result?.swot}
          evidenceLedger={result.evidence_ledger || result.evidence_list || []}
          onNavigateToEvidenceTab={() => handleTabChange("risks")}
        />

        {/* 4–6 Key Numbers At A Glance */}
        <NumbersAtAGlance
          financials={result.financial_result}
          onExplainNumber={handleExplainNumber}
        />

        {/* High-Priority Before You Borrow Checklist */}
        <BeforeYouBorrow checklist={result.verification_checklist || []} />

        {/* Plain-Language Business Advisory & Immediate Next Steps */}
        <RecommendationCard explanation={result.ai_explanation} />

        {/* Bottom tab switcher CTA */}
        <div className="p-4 bg-[#0A1A28] rounded-xl border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
          <span className="text-slate-400">
            Want to inspect deep cash flow breakdowns, local competitors, or loan subsidies?
          </span>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => handleTabChange("financials")}
              className="text-emerald-400 hover:text-emerald-300 font-bold underline"
            >
              View Financials →
            </button>
            <span className="text-slate-600">|</span>
            <button
              type="button"
              onClick={() => handleTabChange("market")}
              className="text-cyan-400 hover:text-cyan-300 font-bold underline"
            >
              View Local Market →
            </button>
          </div>
        </div>
      </div>

      {/* TAB 2: FINANCIALS */}
      <div
        role="tabpanel"
        id="tabpanel-financials"
        aria-labelledby="tab-financials"
        hidden={activeTab !== "financials"}
        className="space-y-8 animate-in fade-in duration-150"
      >
        {/* Financial Summary (Revenue, Costs, Margin, EMI, DSCR) */}
        <FinancialSummary
          financials={result.financial_result}
          assumptions={assumptions}
          recommendationStatus={result.recommendation_status}
        />

        {/* Break-Even Volume Chart */}
        <BreakEvenChart
          breakEvenUnitsDaily={result.financial_result.break_even_units_daily}
          expectedDailyUnits={expectedDailyCustomers}
        />
      </div>

      {/* TAB 3: LOCAL MARKET */}
      <div
        role="tabpanel"
        id="tabpanel-market"
        aria-labelledby="tab-market"
        hidden={activeTab !== "market"}
        className="space-y-8 animate-in fade-in duration-150"
      >
        {/* Local Market Demand, Competition & Mandi Pricing */}
        <LocalMarketSays
          market={result.market_result}
          evidenceList={result.evidence_ledger || result.evidence_list || []}
          verificationChecklist={result.verification_checklist || []}
        />
      </div>

      {/* TAB 4: RISKS & EVIDENCE */}
      <div
        role="tabpanel"
        id="tabpanel-risks"
        aria-labelledby="tab-risks"
        hidden={activeTab !== "risks"}
        className="space-y-8 animate-in fade-in duration-150"
      >
        {/* Comprehensive Decision Trace, Evaluated FeasibilityRules & Evidence Ledger */}
        <DecisionTraceSection
          decisionTrace={result.decision_trace}
          evidenceLedger={result.evidence_ledger || result.evidence_list || []}
          verificationChecklist={result.verification_checklist || []}
          status={result.recommendation_status}
        />

        {/* Evidence Drawer for complete audit trail */}
        <EvidenceDrawer
          evidenceList={result.evidence_ledger || result.evidence_list || []}
        />
      </div>

      {/* TAB 5: SCHEMES & FUNDING */}
      <div
        role="tabpanel"
        id="tabpanel-schemes"
        aria-labelledby="tab-schemes"
        hidden={activeTab !== "schemes"}
        className="space-y-8 animate-in fade-in duration-150"
      >
        {/* Matched Government Schemes & Subsidy Rules */}
        <SchemeSection schemeResult={result.scheme_result} />
      </div>

      {/* TAB 6: ACTION PLAN */}
      <div
        role="tabpanel"
        id="tabpanel-action_plan"
        aria-labelledby="tab-action_plan"
        hidden={activeTab !== "action_plan"}
        className="space-y-8 animate-in fade-in duration-150"
      >
        {/* Step-by-step Pre-Loan Roadmap, Bank Readiness & Document Checklist */}
        <PreLoanActionPlanSection
          actionPlan={result.action_plan}
          documentReadiness={result.document_readiness}
          bankReadiness={result.bank_readiness}
        />
      </div>

      {/* TAB 7: SCENARIO LAB */}
      <div
        role="tabpanel"
        id="tabpanel-scenario_lab"
        aria-labelledby="tab-scenario_lab"
        hidden={activeTab !== "scenario_lab"}
        className="space-y-8 animate-in fade-in duration-150"
      >
        {/* Scenario Lab Simulator */}
        <ScenarioLabSection
          result={result}
          baselineFinancials={assumptions}
        />
      </div>

      {/* Universal Number Inspector Modal */}
      <ExplainNumberModal
        explanation={activeExplanation}
        isOpen={activeExplanation !== null}
        onClose={() => setActiveExplanation(null)}
      />
    </div>
  );
};
