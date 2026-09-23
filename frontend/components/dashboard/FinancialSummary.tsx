"use client";

import React, { useState } from "react";
import { Card } from "@/components/ui/Card";
import { MetricCard } from "@/components/financial/MetricCard";
import { FinancialResult, FinancialAssumptions, RecommendationStatus, NumberExplanation } from "@/lib/types";
import { formatCurrencyINR, formatPercentage } from "@/lib/utils";
import { useTranslation } from "@/lib/i18n";
import { PlainLanguageSummary } from "@/components/financial/PlainLanguageSummary";
import { ExplainNumberModal } from "@/components/financial/ExplainNumberModal";
import { Sparkles, SlidersHorizontal, HelpCircle } from "lucide-react";

interface FinancialSummaryProps {
  financials: FinancialResult;
  assumptions?: FinancialAssumptions | null;
  recommendationStatus?: RecommendationStatus;
  onViewEvidence?: (evidenceId: string) => void;
}

export const FinancialSummary: React.FC<FinancialSummaryProps> = ({
  financials,
  assumptions,
  recommendationStatus,
  onViewEvidence,
}) => {
  const { t } = useTranslation();
  const [viewMode, setViewMode] = useState<"SIMPLE" | "DETAILED">("SIMPLE");
  const [activeExplanation, setActiveExplanation] = useState<NumberExplanation | null>(null);

  const isDebtFree = financials.monthly_emi === 0 || financials.dscr === 0;

  const dscrDisplayValue = isDebtFree ? t("results.financial.dscrDebtFree") : financials.dscr.toFixed(2);
  const dscrIsPositive = isDebtFree ? true : financials.dscr >= 1.5;
  const dscrSubtitle = isDebtFree
    ? t("results.financial.dscrSubtitleDebtFree")
    : `${t("results.financial.dscrSubtitleCover")} ${financials.dscr.toFixed(1)}x`;

  const handleExplain = (metricId: string) => {
    if (financials.explanations && financials.explanations[metricId]) {
      setActiveExplanation(financials.explanations[metricId]);
    }
  };

  return (
    <>
      <Card className="space-y-6" data-testid="financial-summary-container">
        {/* Top View Mode Switcher Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div>
            <h3 className="text-xl font-black text-white tracking-tight">{t("results.financialPicture.title")}</h3>
            <p className="text-xs md:text-sm text-slate-400 mt-0.5">
              {t("results.financialPicture.subtitle")}
            </p>
          </div>

          {/* View Mode Toggle */}
          <div
            role="tablist"
            aria-label={t("results.financial.viewToggleLabel")}
            className="inline-flex items-center p-1 bg-[#06131F] rounded-lg self-start sm:self-auto border border-slate-800"
          >
            <button
              type="button"
              role="tab"
              aria-selected={viewMode === "SIMPLE"}
              onClick={() => setViewMode("SIMPLE")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-all duration-150 ease-out select-none active:scale-[0.99] focus:outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#19D98B]/60 focus-visible:outline-offset-1 motion-reduce:transition-none motion-reduce:transform-none ${
                viewMode === "SIMPLE"
                  ? "bg-[#19D98B]/10 text-[#19D98B] shadow-sm font-bold border border-[#19D98B]/40 active:bg-[#19D98B]/15"
                  : "text-slate-400 hover:text-slate-200 hover:bg-[#19D98B]/[0.05] border border-transparent active:bg-[#0E2635]"
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{t("results.financial.simpleView")}</span>
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={viewMode === "DETAILED"}
              onClick={() => setViewMode("DETAILED")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-all duration-150 ease-out select-none active:scale-[0.99] focus:outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#19D98B]/60 focus-visible:outline-offset-1 motion-reduce:transition-none motion-reduce:transform-none ${
                viewMode === "DETAILED"
                  ? "bg-[#19D98B]/10 text-[#19D98B] shadow-sm font-bold border border-[#19D98B]/40 active:bg-[#19D98B]/15"
                  : "text-slate-400 hover:text-slate-200 hover:bg-[#19D98B]/[0.05] border border-transparent active:bg-[#0E2635]"
              }`}
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
              <span>{t("results.financial.detailedView")}</span>
            </button>
          </div>
        </div>

        {/* Mode 1: Simple View */}
        {viewMode === "SIMPLE" ? (
          <PlainLanguageSummary
            financials={financials}
            assumptions={assumptions}
            recommendationStatus={recommendationStatus}
            onExplainMetric={handleExplain}
          />
        ) : (
          /* Mode 2: Detailed View */
          <div className="space-y-6" data-testid="detailed-financial-view">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                {t("results.financial.detailedView")}
              </span>
              <span
                className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
                  financials.is_financially_viable
                    ? "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30"
                    : "bg-rose-500/15 text-rose-300 border border-rose-500/30"
                }`}
              >
                {financials.is_financially_viable
                  ? t("results.financial.viable")
                  : t("results.financial.deficitWarning")}
              </span>
            </div>

            {/* Primary Key Metrics */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
              <MetricCard
                label={t("results.financial.totalCapex")}
                value={formatCurrencyINR(financials.total_capex)}
                subtitle={t("results.financial.totalCapexSub")}
                onExplain={financials.explanations?.total_capex ? () => handleExplain("total_capex") : undefined}
                explainLabel={t("results.explainNumber.explainButtonLabel")}
              />
              <MetricCard
                label={t("results.financial.monthlyRevenue")}
                value={formatCurrencyINR(financials.monthly_revenue)}
                subtitle={t("results.financial.monthlyRevenueSub")}
                onExplain={financials.explanations?.monthly_revenue ? () => handleExplain("monthly_revenue") : undefined}
                explainLabel={t("results.explainNumber.explainButtonLabel")}
              />
              <MetricCard
                label={t("results.financial.monthlyNetProfit")}
                value={formatCurrencyINR(financials.monthly_net_profit)}
                subtitle={`${formatPercentage(financials.net_profit_margin_pct)} ${t("results.financial.monthlyNetProfitSub")}`}
                isPositive={financials.monthly_net_profit > 0}
                onExplain={financials.explanations?.monthly_net_profit ? () => handleExplain("monthly_net_profit") : undefined}
                explainLabel={t("results.explainNumber.explainButtonLabel")}
              />
              <MetricCard
                label={t("results.financial.dscr")}
                value={dscrDisplayValue}
                subtitle={dscrSubtitle}
                isPositive={dscrIsPositive}
                onExplain={financials.explanations?.dscr ? () => handleExplain("dscr") : undefined}
                explainLabel={t("results.explainNumber.explainButtonLabel")}
              />
            </div>

            {/* Detailed Financial Breakdown Table */}
            <div className="bg-[#06131F] rounded-xl p-4 border border-slate-800 space-y-3">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                {t("results.financial.breakdownTitle")}
              </h4>

              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 text-xs">
                {[
                  { labelKey: "results.financial.requiredLoan", explainKey: "required_loan_amount", value: formatCurrencyINR(financials.required_loan_amount), color: "text-white" },
                  { labelKey: "results.financial.variableCosts", explainKey: "monthly_variable_cost", value: formatCurrencyINR(financials.monthly_variable_cost), color: "text-white" },
                  { labelKey: "results.financial.grossProfit", explainKey: "monthly_gross_profit", value: formatCurrencyINR(financials.monthly_gross_profit), color: "text-emerald-300" },
                  { labelKey: "results.financial.fixedCosts", explainKey: "monthly_fixed_cost", value: formatCurrencyINR(financials.monthly_fixed_cost), color: "text-white" },
                  { labelKey: "results.financial.monthlyEmi", explainKey: "monthly_emi", value: formatCurrencyINR(financials.monthly_emi), color: "text-white" },
                  { labelKey: "results.financial.breakEvenMonthly", explainKey: "break_even_revenue_monthly", value: formatCurrencyINR(financials.break_even_revenue_monthly), color: "text-amber-300" },
                ].map(({ labelKey, explainKey, value, color }) => (
                  <div key={explainKey} className="space-y-1.5 p-2 bg-[#0E2635] rounded-lg border border-slate-700/60">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500">{t(labelKey as Parameters<typeof t>[0])}:</span>
                      {Boolean((financials.explanations as Record<string, unknown>)?.[explainKey]) && (
                        <button
                          type="button"
                          onClick={() => handleExplain(explainKey)}
                          className="text-slate-600 hover:text-emerald-400 p-0.5 rounded transition-colors"
                          title={t("results.explainNumber.explainButtonLabel")}
                          aria-label={`${t("results.explainNumber.explainButtonLabel")}: ${t(labelKey as Parameters<typeof t>[0])}`}
                        >
                          <HelpCircle className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                    <span className={`font-semibold text-sm block ${color}`}>
                      {value}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </Card>

      {/* Explain Number Modal */}
      <ExplainNumberModal
        explanation={activeExplanation}
        isOpen={activeExplanation !== null}
        onClose={() => setActiveExplanation(null)}
        onViewEvidence={onViewEvidence}
      />
    </>
  );
};
