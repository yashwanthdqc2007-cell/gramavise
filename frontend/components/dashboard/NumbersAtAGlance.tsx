"use client";

import React from "react";
import { FinancialResult } from "@/lib/types";
import { formatCurrencyINR } from "@/lib/utils";
import { useTranslation } from "@/lib/i18n";
import { HelpCircle, TrendingUp, DollarSign, CreditCard, Scale, ShieldAlert, Coins } from "lucide-react";

interface NumbersAtAGlanceProps {
  financials: FinancialResult;
  onExplainNumber?: (metricId: string) => void;
}

export const NumbersAtAGlance: React.FC<NumbersAtAGlanceProps> = ({
  financials,
  onExplainNumber,
}) => {
  const { t } = useTranslation();

  const isDebtFree = financials.monthly_emi === 0 || financials.dscr === 0;

  const metrics = [
    {
      id: "monthly_revenue",
      icon: <TrendingUp className="w-4 h-4 text-emerald-400" aria-hidden="true" />,
      label: t("results.numbersAtAGlance.monthlyRevenue"),
      value: formatCurrencyINR(financials.monthly_revenue),
      subtext: t("results.numbersAtAGlance.monthlyRevenueSub"),
      color: "border-slate-700/60 bg-[#0E2635]",
      valueColor: "text-white",
    },
    {
      id: "monthly_net_profit",
      icon: <DollarSign className="w-4 h-4 text-emerald-400" aria-hidden="true" />,
      label: t("results.numbersAtAGlance.monthlyNetProfit"),
      value: formatCurrencyINR(financials.monthly_net_profit),
      subtext: `${t("results.numbersAtAGlance.monthlyNetProfitSub")} (${financials.net_profit_margin_pct.toFixed(1)}%)`,
      color: financials.monthly_net_profit > 0
        ? "border-emerald-500/25 bg-emerald-500/8"
        : "border-rose-500/25 bg-rose-500/8",
      valueColor: financials.monthly_net_profit > 0 ? "text-emerald-300" : "text-rose-300",
    },
    {
      id: "monthly_emi",
      icon: <CreditCard className="w-4 h-4 text-cyan-400" aria-hidden="true" />,
      label: t("results.numbersAtAGlance.monthlyEmi"),
      value: isDebtFree ? t("results.financial.dscrDebtFree") : formatCurrencyINR(financials.monthly_emi),
      subtext: isDebtFree ? t("results.financial.dscrSubtitleDebtFree") : t("results.numbersAtAGlance.monthlyEmiSub"),
      color: "border-slate-700/60 bg-[#0E2635]",
      valueColor: "text-white",
    },
    {
      id: "break_even_revenue_monthly",
      icon: <Scale className="w-4 h-4 text-amber-400" aria-hidden="true" />,
      label: t("results.numbersAtAGlance.breakEvenRevenue"),
      value: formatCurrencyINR(financials.break_even_revenue_monthly),
      subtext: t("results.numbersAtAGlance.breakEvenRevenueSub"),
      color: "border-amber-500/20 bg-amber-500/5",
      valueColor: "text-amber-300",
    },
    {
      id: "dscr",
      icon: <ShieldAlert className="w-4 h-4 text-cyan-400" aria-hidden="true" />,
      label: t("results.numbersAtAGlance.dscr"),
      value: isDebtFree ? t("results.financial.dscrDebtFree") : `${financials.dscr.toFixed(2)}x`,
      subtext: isDebtFree
        ? t("results.financial.dscrSubtitleDebtFree")
        : `${t("results.numbersAtAGlance.dscrSub")} (${financials.dscr >= 1.5 ? "Safe" : "Tight"})`,
      color: isDebtFree || financials.dscr >= 1.5
        ? "border-emerald-500/25 bg-emerald-500/8"
        : "border-amber-500/25 bg-amber-500/8",
      valueColor: isDebtFree || financials.dscr >= 1.5 ? "text-emerald-300" : "text-amber-300",
    },
    {
      id: "required_loan_amount",
      icon: <Coins className="w-4 h-4 text-slate-400" aria-hidden="true" />,
      label: t("results.numbersAtAGlance.loanRequirement"),
      value: formatCurrencyINR(financials.required_loan_amount),
      subtext: t("results.numbersAtAGlance.loanRequirementSub"),
      color: "border-slate-700/60 bg-[#0E2635]",
      valueColor: "text-white",
    },
  ];

  return (
    <section className="bg-[#0B1F2D] rounded-2xl border border-slate-800/80 p-6 md:p-7 shadow-xl shadow-slate-950/20 space-y-5" id="numbers-at-a-glance">
      {/* Header */}
      <div className="border-b border-slate-800 pb-3">
        <h2 className="text-xl font-black text-white tracking-tight">
          {t("results.numbersAtAGlance.title")}
        </h2>
        <p className="text-xs md:text-sm text-slate-400 mt-1">
          {t("results.numbersAtAGlance.subtitle")}
        </p>
      </div>

      {/* 6 Key Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3.5">
        {metrics.map((m) => (
          <div
            key={m.id}
            className={`p-4 rounded-xl border ${m.color} space-y-1.5 transition-all hover:shadow-sm`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5 min-w-0">
                {m.icon}
                <span className="text-xs font-semibold text-slate-300 truncate">
                  {m.label}
                </span>
              </div>
              {onExplainNumber && financials.explanations?.[m.id] && (
                <button
                  type="button"
                  onClick={() => onExplainNumber(m.id)}
                  aria-label={`Explain ${m.label}`}
                  className="text-slate-600 hover:text-emerald-400 transition-colors p-0.5 shrink-0"
                >
                  <HelpCircle className="w-3.5 h-3.5" aria-hidden="true" />
                </button>
              )}
            </div>

            <div className={`text-lg md:text-xl font-black ${m.valueColor}`}>
              {m.value}
            </div>

            <p className="text-[11px] text-slate-500 leading-tight">
              {m.subtext}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
};
