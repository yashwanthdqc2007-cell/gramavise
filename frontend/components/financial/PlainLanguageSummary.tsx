"use client";

import React from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { FinancialResult, FinancialAssumptions, RecommendationStatus } from "@/lib/types";
import { formatCurrencyINR } from "@/lib/utils";
import { useTranslation } from "@/lib/i18n";
import { CheckCircle2, AlertTriangle, TrendingUp, Wallet, ShieldCheck, ShoppingBag, HelpCircle } from "lucide-react";

interface PlainLanguageSummaryProps {
  financials: FinancialResult;
  assumptions?: FinancialAssumptions | null;
  recommendationStatus?: RecommendationStatus;
  onExplainMetric?: (metricId: string) => void;
}

export const PlainLanguageSummary: React.FC<PlainLanguageSummaryProps> = ({
  financials,
  assumptions,
  recommendationStatus,
  onExplainMetric,
}) => {
  const { t } = useTranslation();

  const isDebtFree = financials.monthly_emi === 0 || financials.dscr === 0;
  const expectedCustomers = assumptions?.customers_per_day;
  const breakEvenCustomers = financials.break_even_units_daily;

  // Maximum scale for accessible CSS visual bar representation
  const maxCustomerRef = Math.max(
    expectedCustomers || 0,
    breakEvenCustomers,
    1
  );
  const expectedBarPct = expectedCustomers
    ? Math.min(100, Math.max(10, Math.round((expectedCustomers / maxCustomerRef) * 100)))
    : 0;
  const breakEvenBarPct = Math.min(
    100,
    Math.max(10, Math.round((breakEvenCustomers / maxCustomerRef) * 100))
  );

  return (
    <div className="space-y-6" data-testid="plain-language-summary">
      {/* Header & Viability State */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-100 pb-4">
        <div>
          <h3 className="text-lg font-bold text-gray-900">
            {t("results.financial.plainSummaryTitle")}
          </h3>
          <p className="text-xs text-gray-500 mt-0.5">
            {t("results.financial.plainSummarySubtitle")}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {recommendationStatus && (
            <Badge
              variant={
                recommendationStatus === "PROCEED"
                  ? "success"
                  : recommendationStatus === "VALIDATE_FIRST"
                  ? "warning"
                  : "danger"
              }
              className="text-xs font-semibold"
            >
              {recommendationStatus}
            </Badge>
          )}
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
      </div>

      {/* Break-Even Daily Customer Visual Comparison */}
      <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-bold text-gray-900">
              {t("results.financial.breakEvenComparisonTitle")}
            </h4>
            <p className="text-xs text-gray-500 mt-0.5">
              {t("results.financial.breakEvenComparisonSubtitle")}
            </p>
          </div>
          {onExplainMetric && (
            <button
              type="button"
              onClick={() => onExplainMetric("break_even_units_daily")}
              className="inline-flex items-center gap-1 text-xs text-indigo-700 hover:text-indigo-900 bg-white border border-indigo-200 px-2.5 py-1 rounded-lg font-medium shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500"
              title={t("results.explainNumber.explainButtonLabel")}
            >
              <HelpCircle className="w-3.5 h-3.5" />
              <span>{t("results.explainNumber.explainButtonLabel")}</span>
            </button>
          )}
        </div>

        {/* Visual Guidance Bars */}
        <div className="space-y-3 pt-1">
          {/* Expected Customers Bar */}
          {expectedCustomers !== undefined && (
            <div className="space-y-1">
              <div className="flex justify-between text-xs font-medium">
                <span className="text-gray-700 flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-indigo-600 inline-block" />
                  {t("results.financial.expectedCustomersLabel")}:
                </span>
                <span className="font-bold text-gray-900">
                  {expectedCustomers} / day
                </span>
              </div>
              <div
                className="w-full bg-gray-200 h-3 rounded-full overflow-hidden"
                role="progressbar"
                aria-valuenow={expectedCustomers}
                aria-valuemin={0}
                aria-valuemax={maxCustomerRef}
                aria-label={t("results.financial.expectedCustomersLabel")}
              >
                <div
                  className="bg-indigo-600 h-full rounded-full transition-all duration-500"
                  style={{ width: `${expectedBarPct}%` }}
                />
              </div>
            </div>
          )}

          {/* Break-Even Customers Bar */}
          <div className="space-y-1">
            <div className="flex justify-between text-xs font-medium">
              <span className="text-gray-700 flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block" />
                {t("results.financial.breakEvenCustomersLabel")}:
              </span>
              <span className="font-bold text-gray-900">
                {breakEvenCustomers} / day
              </span>
            </div>
            <div
              className="w-full bg-gray-200 h-3 rounded-full overflow-hidden"
              role="progressbar"
              aria-valuenow={breakEvenCustomers}
              aria-valuemin={0}
              aria-valuemax={maxCustomerRef}
              aria-label={t("results.financial.breakEvenCustomersLabel")}
            >
              <div
                className="bg-amber-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${breakEvenBarPct}%` }}
              />
            </div>
          </div>
        </div>

        {/* Interpretive Banner */}
        <div
          className={`p-3 rounded-lg flex items-start gap-2.5 text-xs font-medium ${
            expectedCustomers !== undefined && expectedCustomers >= breakEvenCustomers
              ? "bg-emerald-50 text-emerald-900 border border-emerald-200"
              : "bg-amber-50 text-amber-900 border border-amber-200"
          }`}
        >
          {expectedCustomers !== undefined && expectedCustomers >= breakEvenCustomers ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
          ) : (
            <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5 shrink-0" />
          )}
          <div>
            {expectedCustomers !== undefined && expectedCustomers > breakEvenCustomers && (
              <span>{t("results.financial.breakEvenAbove")}</span>
            )}
            {expectedCustomers !== undefined && expectedCustomers < breakEvenCustomers && (
              <span>{t("results.financial.breakEvenBelow")}</span>
            )}
            {expectedCustomers !== undefined && expectedCustomers === breakEvenCustomers && (
              <span>{t("results.financial.breakEvenEqual")}</span>
            )}
          </div>
        </div>
      </div>

      {/* Everyday Plain-Language Concept Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* A. Monthly Revenue */}
        <div className="p-4 bg-white border border-gray-200 rounded-xl space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-indigo-700">
              <TrendingUp className="w-4 h-4" />
              <h4 className="text-xs font-bold uppercase tracking-wider">
                {t("results.financial.monthlyMoneyInTitle")}
              </h4>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] font-mono px-1.5 py-0.5 bg-blue-50 text-blue-700 rounded font-semibold">
                CALCULATED
              </span>
              {onExplainMetric && (
                <button
                  type="button"
                  onClick={() => onExplainMetric("monthly_revenue")}
                  className="text-gray-400 hover:text-indigo-600 p-0.5 rounded transition-colors"
                  title={t("results.explainNumber.explainButtonLabel")}
                >
                  <HelpCircle className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>
          <div className="text-2xl font-black text-gray-900">
            {formatCurrencyINR(financials.monthly_revenue)}
          </div>
          <p className="text-xs text-gray-600 leading-relaxed">
            {t("results.financial.monthlyMoneyInDesc", {
              amount: formatCurrencyINR(financials.monthly_revenue),
            })}
          </p>
        </div>

        {/* B. Net Profit */}
        <div className="p-4 bg-white border border-gray-200 rounded-xl space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-emerald-700">
              <Wallet className="w-4 h-4" />
              <h4 className="text-xs font-bold uppercase tracking-wider">
                {t("results.financial.monthlyProfitTitle")}
              </h4>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] font-mono px-1.5 py-0.5 bg-blue-50 text-blue-700 rounded font-semibold">
                CALCULATED
              </span>
              {onExplainMetric && (
                <button
                  type="button"
                  onClick={() => onExplainMetric("monthly_net_profit")}
                  className="text-gray-400 hover:text-indigo-600 p-0.5 rounded transition-colors"
                  title={t("results.explainNumber.explainButtonLabel")}
                >
                  <HelpCircle className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>
          <div
            className={`text-2xl font-black ${
              financials.monthly_net_profit >= 0
                ? "text-emerald-700"
                : "text-rose-600"
            }`}
          >
            {formatCurrencyINR(financials.monthly_net_profit)}
          </div>
          <p className="text-xs text-gray-600 leading-relaxed">
            {t("results.financial.monthlyProfitDesc", {
              amount: formatCurrencyINR(financials.monthly_net_profit),
            })}
          </p>
        </div>

        {/* C. Loan Repayment Cushion (DSCR) */}
        <div className="p-4 bg-white border border-gray-200 rounded-xl space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-blue-700">
              <ShieldCheck className="w-4 h-4" />
              <h4 className="text-xs font-bold uppercase tracking-wider">
                {t("results.financial.loanCushionTitle")}
              </h4>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] font-mono px-1.5 py-0.5 bg-blue-50 text-blue-700 rounded font-semibold">
                CALCULATED
              </span>
              {onExplainMetric && (
                <button
                  type="button"
                  onClick={() => onExplainMetric("dscr")}
                  className="text-gray-400 hover:text-indigo-600 p-0.5 rounded transition-colors"
                  title={t("results.explainNumber.explainButtonLabel")}
                >
                  <HelpCircle className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>
          <div className="text-2xl font-black text-gray-900">
            {isDebtFree
              ? t("results.financial.loanCushionDebtFree")
              : `${financials.dscr.toFixed(2)}x`}
          </div>
          <p className="text-xs text-gray-600 leading-relaxed">
            {isDebtFree
              ? t("results.financial.loanCushionDebtFreeDesc")
              : t("results.financial.loanCushionDesc", {
                  dscr: financials.dscr.toFixed(2),
                })}
          </p>
        </div>

        {/* D. Variable Cost (COGS) */}
        <div className="p-4 bg-white border border-gray-200 rounded-xl space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-amber-700">
              <ShoppingBag className="w-4 h-4" />
              <h4 className="text-xs font-bold uppercase tracking-wider">
                {t("results.financial.variableCostTitle")}
              </h4>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] font-mono px-1.5 py-0.5 bg-gray-100 text-gray-700 rounded font-semibold">
                {assumptions?.variable_cost_pct !== undefined ? "ASSUMED" : "CALCULATED"}
              </span>
              {onExplainMetric && (
                <button
                  type="button"
                  onClick={() => onExplainMetric("variable_cost_pct")}
                  className="text-gray-400 hover:text-indigo-600 p-0.5 rounded transition-colors"
                  title={t("results.explainNumber.explainButtonLabel")}
                >
                  <HelpCircle className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>
          <div className="text-2xl font-black text-gray-900">
            {assumptions?.variable_cost_pct !== undefined
              ? `${assumptions.variable_cost_pct}%`
              : formatCurrencyINR(financials.monthly_variable_cost)}
          </div>
          <p className="text-xs text-gray-600 leading-relaxed">
            {assumptions?.variable_cost_pct !== undefined
              ? t("results.financial.variableCostDesc", {
                  pct: assumptions.variable_cost_pct,
                })
              : t("results.financial.variableCosts")}
          </p>
        </div>
      </div>

      {/* Mathematical Interpretation Disclaimer */}
      <p className="text-[11px] text-gray-500 italic text-center">
        {t("results.financial.disclaimerNote")}
      </p>
    </div>
  );
};
