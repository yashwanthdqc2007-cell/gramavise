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
  // Default to Simple View as mandated
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
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-stone-100 pb-3">
          <div>
            <h3 className="text-xl font-black text-slate-900 tracking-tight">{t("results.financialPicture.title")}</h3>
            <p className="text-xs md:text-sm text-slate-600 mt-0.5">
              {t("results.financialPicture.subtitle")}
            </p>
          </div>

          {/* View Mode Toggle: [ Simple View ] [ Detailed View ] */}
          <div
            role="tablist"
            aria-label={t("results.financial.viewToggleLabel")}
            className="inline-flex items-center p-1 bg-gray-100 rounded-lg self-start sm:self-auto border border-gray-200"
          >
            <button
              type="button"
              role="tab"
              aria-selected={viewMode === "SIMPLE"}
              onClick={() => setViewMode("SIMPLE")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1 ${
                viewMode === "SIMPLE"
                  ? "bg-white text-indigo-700 shadow-sm font-bold"
                  : "text-gray-600 hover:text-gray-900"
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
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1 ${
                viewMode === "DETAILED"
                  ? "bg-white text-indigo-700 shadow-sm font-bold"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
              <span>{t("results.financial.detailedView")}</span>
            </button>
          </div>
        </div>

        {/* Mode 1: Simple View (Low-Literacy Plain-Language Summaries & Visual Break-Even) */}
        {viewMode === "SIMPLE" ? (
          <PlainLanguageSummary
            financials={financials}
            assumptions={assumptions}
            recommendationStatus={recommendationStatus}
            onExplainMetric={handleExplain}
          />
        ) : (
          /* Mode 2: Detailed View (Technical Financial Metrics & Breakdown Table) */
          <div className="space-y-6" data-testid="detailed-financial-view">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                {t("results.financial.detailedView")}
              </span>
              <span
                className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
                  financials.is_financially_viable
                    ? "bg-emerald-100 text-emerald-800"
                    : "bg-rose-100 text-rose-800"
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
            <div className="bg-gray-50/70 rounded-xl p-4 border border-gray-100 space-y-3">
              <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                {t("results.financial.breakdownTitle")}
              </h4>

              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 text-xs">
                <div className="space-y-1.5 p-2 bg-white rounded-lg border border-gray-100">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">{t("results.financial.requiredLoan")}:</span>
                    {financials.explanations?.required_loan_amount && (
                      <button
                        type="button"
                        onClick={() => handleExplain("required_loan_amount")}
                        className="text-gray-400 hover:text-indigo-600 p-0.5 rounded transition-colors"
                        title={t("results.explainNumber.explainButtonLabel")}
                        aria-label={`${t("results.explainNumber.explainButtonLabel")}: ${t("results.financial.requiredLoan")}`}
                      >
                        <HelpCircle className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                  <span className="font-semibold text-gray-900 text-sm block">
                    {formatCurrencyINR(financials.required_loan_amount)}
                  </span>
                </div>

                <div className="space-y-1.5 p-2 bg-white rounded-lg border border-gray-100">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">{t("results.financial.variableCosts")}:</span>
                    {financials.explanations?.monthly_variable_cost && (
                      <button
                        type="button"
                        onClick={() => handleExplain("monthly_variable_cost")}
                        className="text-gray-400 hover:text-indigo-600 p-0.5 rounded transition-colors"
                        title={t("results.explainNumber.explainButtonLabel")}
                        aria-label={`${t("results.explainNumber.explainButtonLabel")}: ${t("results.financial.variableCosts")}`}
                      >
                        <HelpCircle className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                  <span className="font-semibold text-gray-900 text-sm block">
                    {formatCurrencyINR(financials.monthly_variable_cost)}
                  </span>
                </div>

                <div className="space-y-1.5 p-2 bg-white rounded-lg border border-gray-100">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">{t("results.financial.grossProfit")}:</span>
                    {financials.explanations?.monthly_gross_profit && (
                      <button
                        type="button"
                        onClick={() => handleExplain("monthly_gross_profit")}
                        className="text-gray-400 hover:text-indigo-600 p-0.5 rounded transition-colors"
                        title={t("results.explainNumber.explainButtonLabel")}
                        aria-label={`${t("results.explainNumber.explainButtonLabel")}: ${t("results.financial.grossProfit")}`}
                      >
                        <HelpCircle className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                  <span className="font-semibold text-emerald-700 text-sm block">
                    {formatCurrencyINR(financials.monthly_gross_profit)}
                  </span>
                </div>

                <div className="space-y-1.5 p-2 bg-white rounded-lg border border-gray-100">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">{t("results.financial.fixedCosts")}:</span>
                    {financials.explanations?.monthly_fixed_cost && (
                      <button
                        type="button"
                        onClick={() => handleExplain("monthly_fixed_cost")}
                        className="text-gray-400 hover:text-indigo-600 p-0.5 rounded transition-colors"
                        title={t("results.explainNumber.explainButtonLabel")}
                        aria-label={`${t("results.explainNumber.explainButtonLabel")}: ${t("results.financial.fixedCosts")}`}
                      >
                        <HelpCircle className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                  <span className="font-semibold text-gray-900 text-sm block">
                    {formatCurrencyINR(financials.monthly_fixed_cost)}
                  </span>
                </div>

                <div className="space-y-1.5 p-2 bg-white rounded-lg border border-gray-100">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">{t("results.financial.monthlyEmi")}:</span>
                    {financials.explanations?.monthly_emi && (
                      <button
                        type="button"
                        onClick={() => handleExplain("monthly_emi")}
                        className="text-gray-400 hover:text-indigo-600 p-0.5 rounded transition-colors"
                        title={t("results.explainNumber.explainButtonLabel")}
                        aria-label={`${t("results.explainNumber.explainButtonLabel")}: ${t("results.financial.monthlyEmi")}`}
                      >
                        <HelpCircle className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                  <span className="font-semibold text-gray-900 text-sm block">
                    {formatCurrencyINR(financials.monthly_emi)}
                  </span>
                </div>

                <div className="space-y-1.5 p-2 bg-white rounded-lg border border-gray-100">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">{t("results.financial.breakEvenMonthly")}:</span>
                    {financials.explanations?.break_even_revenue_monthly && (
                      <button
                        type="button"
                        onClick={() => handleExplain("break_even_revenue_monthly")}
                        className="text-gray-400 hover:text-indigo-600 p-0.5 rounded transition-colors"
                        title={t("results.explainNumber.explainButtonLabel")}
                        aria-label={`${t("results.explainNumber.explainButtonLabel")}: ${t("results.financial.breakEvenMonthly")}`}
                      >
                        <HelpCircle className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                  <span className="font-semibold text-gray-900 text-sm block">
                    {formatCurrencyINR(financials.break_even_revenue_monthly)}
                  </span>
                </div>
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

