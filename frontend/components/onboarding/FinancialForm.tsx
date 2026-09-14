"use client";

import React, { useMemo } from "react";
import { Input } from "@/components/ui/Input";
import { FinancialAssumptions } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";
import { VoiceFieldType } from "@/lib/voice/types";
import { useVoiceInput } from "@/lib/voice/useVoiceInput";
import { VoiceInputButton } from "@/components/voice/VoiceInputButton";
import { VoiceConfirmationModal } from "@/components/voice/VoiceConfirmationModal";

interface FinancialFormProps {
  financials: FinancialAssumptions;
  ownCapital: number;
  desiredLoan: number;
  errors?: Record<string, string>;
  onChangeFinancials: (financials: FinancialAssumptions) => void;
  onChangeCapital: (fields: { own_capital?: number; desired_loan?: number }) => void;
}

export const FinancialForm: React.FC<FinancialFormProps> = ({
  financials,
  ownCapital,
  desiredLoan,
  errors = {},
  onChangeFinancials,
  onChangeCapital,
}) => {
  const { t } = useTranslation();

  // Voice Input Hook
  const handleVoiceConfirmed = (fieldType: VoiceFieldType, value: number) => {
    if (fieldType === "own_capital") {
      onChangeCapital({ own_capital: value });
    } else if (fieldType === "desired_loan") {
      onChangeCapital({ desired_loan: value });
    } else {
      onChangeFinancials({
        ...financials,
        [fieldType]: value,
      });
    }
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

  // Live Capex calculation (pure frontend preview)
  const totalCapex = useMemo(() => {
    const startup = Number(financials.startup_cost) || 0;
    const equipment = Number(financials.equipment_cost) || 0;
    const inventory = Number(financials.inventory_cost) || 0;
    return startup + equipment + inventory;
  }, [financials.startup_cost, financials.equipment_cost, financials.inventory_cost]);

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
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-white">{t("onboarding.financial.title")}</h3>
        <p className="text-xs text-slate-400 mt-0.5">
          {t("onboarding.step4Sub")}
        </p>
      </div>

      {/* Live CapEx & Capital Overview Card */}
      <div className="p-4 bg-gradient-to-r from-emerald-950/60 via-[#0B1C29] to-cyan-950/40 rounded-xl border border-emerald-500/30 shadow-sm space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 border-b border-emerald-500/25 pb-2">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-300">
              {t("onboarding.financial.liveSummaryTitle")}
            </span>
            <span className="text-[11px] text-slate-400 block">
              {t("onboarding.financial.liveSummaryNote")}
            </span>
          </div>
          <div className="text-right">
            <span className="text-xs text-slate-400">{t("onboarding.financial.liveSummaryTotal")}: </span>
            <span className="text-base font-black text-emerald-300">
              ₹{totalCapex.toLocaleString("en-IN")}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div className="bg-slate-950/50 p-2.5 rounded-lg border border-slate-700/70">
            <span className="text-slate-400 block">{t("results.financial.totalCapex")}</span>
            <span className="font-bold text-white text-sm">
              ₹{totalCapex.toLocaleString("en-IN")}
            </span>
            <span className="text-[10px] text-slate-500 block mt-0.5">Setup + Machinery + Stock</span>
          </div>
          <div className="bg-slate-950/50 p-2.5 rounded-lg border border-slate-700/70">
            <span className="text-slate-400 block">{t("onboarding.profile.ownCapital")}</span>
            <span className="font-bold text-emerald-300 text-sm">
              ₹{(Number(ownCapital) || 0).toLocaleString("en-IN")}
            </span>
            <span className="text-[10px] text-slate-500 block mt-0.5">Your savings / equity</span>
          </div>
          <div className="bg-slate-950/50 p-2.5 rounded-lg border border-slate-700/70">
            <span className="text-slate-400 block">{t("onboarding.profile.desiredLoan")}</span>
            <span className="font-bold text-emerald-300 text-sm">
              ₹{(Number(desiredLoan) || 0).toLocaleString("en-IN")}
            </span>
            <span className="text-[10px] text-slate-500 block mt-0.5">Loan amount requested</span>
          </div>
        </div>
      </div>

      {/* 1. Entrepreneur Capital & Loan Request */}
      <div>
        <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
          {t("onboarding.financial.sectionEquityLoan")}
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label={`${t("onboarding.profile.ownCapital")} *`}
            type="number"
            min={0}
            placeholder={t("onboarding.profile.ownCapitalPlaceholder")}
            value={ownCapital === 0 ? "" : ownCapital}
            error={errors.own_capital}
            helperText="Amount you can invest from your own savings."
            onChange={(e) =>
              handleNumberInput(e.target.value, (val) => onChangeCapital({ own_capital: val }))
            }
            rightElement={
              <VoiceInputButton
                fieldType="own_capital"
                onStartVoice={startListening}
                isListening={voiceActiveField === "own_capital" && voiceState === "LISTENING"}
              />
            }
          />
          <Input
            label={`${t("onboarding.profile.desiredLoan")} *`}
            type="number"
            min={0}
            placeholder={t("onboarding.profile.desiredLoanPlaceholder")}
            value={desiredLoan === 0 ? "" : desiredLoan}
            error={errors.desired_loan}
            helperText="Loan amount you plan to apply for from a bank or scheme."
            onChange={(e) =>
              handleNumberInput(e.target.value, (val) => onChangeCapital({ desired_loan: val }))
            }
            rightElement={
              <VoiceInputButton
                fieldType="desired_loan"
                onStartVoice={startListening}
                isListening={voiceActiveField === "desired_loan" && voiceState === "LISTENING"}
              />
            }
          />
        </div>
      </div>

      {/* 2. Initial Setup Outlay (Capex) */}
      <div>
        <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
          {t("onboarding.financial.sectionInitialCapex")}
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input
            label={`${t("onboarding.financial.startupCost")} *`}
            type="number"
            min={0}
            placeholder="0"
            value={financials.startup_cost === 0 ? "" : financials.startup_cost}
            error={errors.startup_cost}
            helperText={t("onboarding.financial.startupCostHelp")}
            onChange={(e) =>
              handleNumberInput(e.target.value, (val) =>
                onChangeFinancials({ ...financials, startup_cost: val })
              )
            }
            rightElement={
              <VoiceInputButton
                fieldType="startup_cost"
                onStartVoice={startListening}
                isListening={voiceActiveField === "startup_cost" && voiceState === "LISTENING"}
              />
            }
          />
          <Input
            label={`${t("onboarding.financial.equipmentCost")} *`}
            type="number"
            min={0}
            placeholder="0"
            value={financials.equipment_cost === 0 ? "" : financials.equipment_cost}
            error={errors.equipment_cost}
            helperText={t("onboarding.financial.equipmentCostHelp")}
            onChange={(e) =>
              handleNumberInput(e.target.value, (val) =>
                onChangeFinancials({ ...financials, equipment_cost: val })
              )
            }
            rightElement={
              <VoiceInputButton
                fieldType="equipment_cost"
                onStartVoice={startListening}
                isListening={voiceActiveField === "equipment_cost" && voiceState === "LISTENING"}
              />
            }
          />
          <Input
            label={`${t("onboarding.financial.inventoryCost")} *`}
            type="number"
            min={0}
            placeholder="0"
            value={financials.inventory_cost === 0 ? "" : financials.inventory_cost}
            error={errors.inventory_cost}
            helperText={t("onboarding.financial.inventoryCostHelp")}
            onChange={(e) =>
              handleNumberInput(e.target.value, (val) =>
                onChangeFinancials({ ...financials, inventory_cost: val })
              )
            }
            rightElement={
              <VoiceInputButton
                fieldType="inventory_cost"
                onStartVoice={startListening}
                isListening={voiceActiveField === "inventory_cost" && voiceState === "LISTENING"}
              />
            }
          />
        </div>
      </div>

      {/* 3. Daily Sales & Unit Economics */}
      <div>
        <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
          {t("onboarding.financial.sectionDailySales")}
        </h4>
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
            helperText="Days shop is open (1–31)."
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

      {/* 4. Monthly Fixed Overheads & Loan Terms */}
      <div>
        <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
          {t("onboarding.financial.sectionMonthlyOverheads")}
        </h4>
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

