"use client";

import React from "react";
import { Input } from "@/components/ui/Input";
import { FinancialAssumptions } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";
import { VoiceFieldType } from "@/lib/voice/types";
import { useVoiceInput } from "@/lib/voice/useVoiceInput";
import { VoiceInputButton } from "@/components/voice/VoiceInputButton";
import { VoiceConfirmationModal } from "@/components/voice/VoiceConfirmationModal";
import { TrendingUp, DollarSign, Calendar, HelpCircle, ShieldCheck } from "lucide-react";

interface SalesAssumptionsFormProps {
  financials: FinancialAssumptions;
  errors?: Record<string, string>;
  onChangeFinancials: (financials: FinancialAssumptions) => void;
}

export const SalesAssumptionsForm: React.FC<SalesAssumptionsFormProps> = ({
  financials,
  errors = {},
  onChangeFinancials,
}) => {
  const { t } = useTranslation();

  // Voice Input Hook
  const handleVoiceConfirmed = (fieldType: VoiceFieldType, value: number) => {
    onChangeFinancials({
      ...financials,
      [fieldType]: value,
    });
  };

  const {
    state: voiceState,
    activeField: voiceActiveField,
    rawTranscript: voiceRawTranscript,
    parseResult: voiceParseResult,
    errorMessage: voiceErrorMessage,
    startListening,
    confirmValue,
    retry: retryVoice,
    cancel: cancelVoice,
  } = useVoiceInput(handleVoiceConfirmed);

  const handleNumberInput = (
    value: string,
    callback: (num: number) => void,
    isFloat = true
  ) => {
    if (value === "") {
      callback(0);
      return;
    }
    const parsed = isFloat ? parseFloat(value) : parseInt(value, 10);
    callback(isNaN(parsed) ? 0 : parsed);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <span className="w-6 h-6 rounded-full bg-emerald-500/15 text-emerald-300 flex items-center justify-center text-xs font-bold border border-emerald-500/30">
            4
          </span>
          <h2 className="text-xl font-bold text-white tracking-tight">
            {t("onboarding.step4Title")}
          </h2>
        </div>
        <p className="text-xs sm:text-sm text-slate-400">
          {t("onboarding.step4Sub")}
        </p>
      </div>

      {/* Why do we ask this Callout */}
      <div className="p-4 bg-[#0E2635] border border-cyan-500/30 rounded-xl flex items-start gap-3 text-xs sm:text-sm text-slate-300 shadow-xs">
        <div className="w-7 h-7 rounded-lg bg-cyan-500/15 text-cyan-300 flex items-center justify-center flex-shrink-0 mt-0.5 border border-cyan-500/30">
          <HelpCircle className="w-4 h-4" aria-hidden="true" />
        </div>
        <div>
          <span className="font-semibold text-cyan-200 block mb-0.5">Why do we ask this?</span>
          <p className="text-slate-300 text-xs sm:text-sm leading-relaxed">
            {t("onboarding.financial.whyAskSales")}
          </p>
        </div>
      </div>

      {/* 1. Daily Sales & Customer Footfall */}
      <div className="bg-[#0B1F2D] p-4 sm:p-5 rounded-xl border border-slate-800 space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-800/80 pb-3">
          <TrendingUp className="w-4 h-4 text-emerald-400" aria-hidden="true" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
            {t("onboarding.financial.sectionDailySales")}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          <Input
            label={`${t("onboarding.financial.customersPerDay")} *`}
            type="number"
            min={0}
            placeholder="25"
            value={financials.customers_per_day === 0 ? "" : financials.customers_per_day}
            error={errors.customers_per_day}
            helperText={t("onboarding.financial.customersPerDayHelp")}
            onChange={(e) =>
              handleNumberInput(
                e.target.value,
                (val) => onChangeFinancials({ ...financials, customers_per_day: val }),
                false
              )
            }
            rightElement={
              <VoiceInputButton
                fieldType="customers_per_day"
                onStartVoice={startListening}
                isListening={voiceActiveField === "customers_per_day" && voiceState === "LISTENING"}
              />
            }
          />
          <Input
            label={`${t("onboarding.financial.avgTicketPrice")} *`}
            type="number"
            min={0}
            placeholder="60"
            value={financials.avg_ticket_price === 0 ? "" : financials.avg_ticket_price}
            error={errors.avg_ticket_price}
            helperText={t("onboarding.financial.avgTicketPriceHelp")}
            onChange={(e) =>
              handleNumberInput(e.target.value, (val) =>
                onChangeFinancials({ ...financials, avg_ticket_price: val })
              )
            }
            rightElement={
              <VoiceInputButton
                fieldType="avg_ticket_price"
                onStartVoice={startListening}
                isListening={voiceActiveField === "avg_ticket_price" && voiceState === "LISTENING"}
              />
            }
          />
          <Input
            label={`${t("onboarding.financial.workingDaysPerMonth")} *`}
            type="number"
            min={1}
            max={31}
            placeholder="26"
            value={financials.working_days_per_month === 0 ? "" : financials.working_days_per_month}
            error={errors.working_days_per_month}
            helperText={t("onboarding.financial.workingDaysHelp")}
            onChange={(e) =>
              handleNumberInput(
                e.target.value,
                (val) => onChangeFinancials({ ...financials, working_days_per_month: val }),
                false
              )
            }
          />
          <Input
            label={`${t("onboarding.financial.variableCostPct")} *`}
            type="number"
            min={0}
            max={99.9}
            step="0.5"
            placeholder="35"
            value={financials.variable_cost_pct === 0 ? "" : financials.variable_cost_pct}
            error={errors.variable_cost_pct}
            helperText={t("onboarding.financial.variableCostPctHelp")}
            onChange={(e) =>
              handleNumberInput(e.target.value, (val) =>
                onChangeFinancials({ ...financials, variable_cost_pct: val })
              )
            }
          />
        </div>
      </div>

      {/* 2. Monthly Running Costs & Loan Conditions */}
      <div className="bg-[#0B1F2D] p-4 sm:p-5 rounded-xl border border-slate-800 space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-800/80 pb-3">
          <DollarSign className="w-4 h-4 text-emerald-400" aria-hidden="true" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
            {t("onboarding.financial.sectionMonthlyOverheads")}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Input
            label={`${t("onboarding.financial.monthlyFixedCost")} *`}
            type="number"
            min={0}
            placeholder="6000"
            value={financials.monthly_fixed_cost === 0 ? "" : financials.monthly_fixed_cost}
            error={errors.monthly_fixed_cost}
            helperText={t("onboarding.financial.monthlyFixedCostHelp")}
            onChange={(e) =>
              handleNumberInput(e.target.value, (val) =>
                onChangeFinancials({ ...financials, monthly_fixed_cost: val })
              )
            }
            rightElement={
              <VoiceInputButton
                fieldType="monthly_fixed_cost"
                onStartVoice={startListening}
                isListening={voiceActiveField === "monthly_fixed_cost" && voiceState === "LISTENING"}
              />
            }
          />
          <Input
            label={`${t("onboarding.financial.interestRatePct")} *`}
            type="number"
            min={0}
            max={40}
            step="0.1"
            placeholder="10.5"
            value={financials.interest_rate_pct === 0 ? "" : financials.interest_rate_pct}
            error={errors.interest_rate_pct}
            helperText={t("onboarding.financial.interestRatePctHelp")}
            onChange={(e) =>
              handleNumberInput(e.target.value, (val) =>
                onChangeFinancials({ ...financials, interest_rate_pct: val })
              )
            }
          />
          <Input
            label={`${t("onboarding.financial.loanTenureMonths")} *`}
            type="number"
            min={1}
            max={120}
            placeholder="36"
            value={financials.loan_tenure_months === 0 ? "" : financials.loan_tenure_months}
            error={errors.loan_tenure_months}
            helperText={t("onboarding.financial.loanTenureMonthsHelp")}
            onChange={(e) =>
              handleNumberInput(
                e.target.value,
                (val) => onChangeFinancials({ ...financials, loan_tenure_months: val }),
                false
              )
            }
          />
        </div>
      </div>

      {/* Transparent Technical Cushion Micro-Panel */}
      <div className="p-3.5 bg-[#0E2635] border border-slate-700/80 rounded-xl flex items-start gap-3 text-xs text-slate-300">
        <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" aria-hidden="true" />
        <div>
          <span className="font-semibold text-white block">
            {t("onboarding.financial.dscrNote")}
          </span>
          <p className="text-slate-400 mt-0.5">
            {t("onboarding.financial.dscrExplain")}
          </p>
        </div>
      </div>

      {/* Voice Confirmation Modal */}
      <VoiceConfirmationModal
        state={voiceState}
        activeField={voiceActiveField}
        rawTranscript={voiceRawTranscript}
        parseResult={voiceParseResult}
        errorMessage={voiceErrorMessage}
        onConfirm={confirmValue}
        onRetry={retryVoice}
        onCancel={cancelVoice}
      />
    </div>
  );
};
