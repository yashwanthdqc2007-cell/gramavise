"use client";

import React, { useMemo } from "react";
import { Input } from "@/components/ui/Input";
import { FinancialAssumptions } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";
import { VoiceFieldType } from "@/lib/voice/types";
import { useVoiceInput } from "@/lib/voice/useVoiceInput";
import { VoiceInputButton } from "@/components/voice/VoiceInputButton";
import { VoiceConfirmationModal } from "@/components/voice/VoiceConfirmationModal";
import { Coins, HelpCircle, Wrench, Package, Building, ShieldCheck } from "lucide-react";

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
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <span className="w-6 h-6 rounded-full bg-emerald-500/15 text-emerald-300 flex items-center justify-center text-xs font-bold border border-emerald-500/30">
            3
          </span>
          <h2 className="text-xl font-bold text-white tracking-tight">
            {t("onboarding.step3Title")}
          </h2>
        </div>
        <p className="text-xs sm:text-sm text-slate-400">
          {t("onboarding.step3Sub")}
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
            {t("onboarding.financial.whyAskMoney")}
          </p>
        </div>
      </div>

      {/* Live CapEx & Capital Overview Card */}
      <div className="p-4 sm:p-5 bg-gradient-to-r from-emerald-950/60 via-[#0B1F2D] to-cyan-950/40 rounded-xl border border-emerald-500/30 shadow-sm space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 border-b border-emerald-500/25 pb-2.5">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-300">
              {t("onboarding.financial.liveSummaryTitle")}
            </span>
            <span className="text-[11px] text-slate-400 block">
              {t("onboarding.financial.liveSummaryNote")}
            </span>
          </div>
          <div className="text-left sm:text-right">
            <span className="text-xs text-slate-400">{t("onboarding.financial.liveSummaryTotal")}: </span>
            <span className="text-base font-black text-emerald-300">
              ₹{totalCapex.toLocaleString("en-IN")}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div className="bg-[#06131F] p-3 rounded-lg border border-slate-700/70">
            <span className="text-slate-400 block text-[11px] font-medium">{t("onboarding.review.totalCapex")}</span>
            <span className="font-bold text-white text-sm sm:text-base">
              ₹{totalCapex.toLocaleString("en-IN")}
            </span>
            <span className="text-[10px] text-slate-400 block mt-0.5">Setup + Machinery + Stock</span>
          </div>
          <div className="bg-[#06131F] p-3 rounded-lg border border-slate-700/70">
            <span className="text-slate-400 block text-[11px] font-medium">{t("onboarding.profile.ownCapital")}</span>
            <span className="font-bold text-emerald-300 text-sm sm:text-base">
              ₹{(Number(ownCapital) || 0).toLocaleString("en-IN")}
            </span>
            <span className="text-[10px] text-emerald-400/80 block mt-0.5">Your savings contribution</span>
          </div>
          <div className="bg-[#06131F] p-3 rounded-lg border border-slate-700/70">
            <span className="text-slate-400 block text-[11px] font-medium">{t("onboarding.profile.desiredLoan")}</span>
            <span className="font-bold text-cyan-300 text-sm sm:text-base">
              ₹{(Number(desiredLoan) || 0).toLocaleString("en-IN")}
            </span>
            <span className="text-[10px] text-cyan-400/80 block mt-0.5">Loan amount requested</span>
          </div>
        </div>
      </div>

      {/* 1. Entrepreneur Capital & Loan Request */}
      <div className="bg-[#0B1F2D] p-4 sm:p-5 rounded-xl border border-slate-800 space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-800/80 pb-3">
          <Coins className="w-4 h-4 text-emerald-400" aria-hidden="true" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
            {t("onboarding.financial.sectionEquityLoan")}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label={`${t("onboarding.profile.ownCapital")} *`}
            type="number"
            min={0}
            placeholder={t("onboarding.profile.ownCapitalPlaceholder")}
            value={ownCapital === 0 ? "" : ownCapital}
            error={errors.own_capital}
            helperText={t("onboarding.profile.ownCapitalHelp")}
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
            helperText={t("onboarding.profile.desiredLoanHelp")}
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
      <div className="bg-[#0B1F2D] p-4 sm:p-5 rounded-xl border border-slate-800 space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-800/80 pb-3">
          <Building className="w-4 h-4 text-emerald-400" aria-hidden="true" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
            {t("onboarding.financial.sectionInitialCapex")}
          </span>
        </div>

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
