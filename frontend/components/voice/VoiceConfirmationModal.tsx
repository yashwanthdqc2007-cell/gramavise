"use client";

import React from "react";
import { VoiceFieldType, VoiceListeningState, ParseResult } from "@/lib/voice/types";
import { VOICE_FIELD_CONFIGS } from "@/lib/voice/numericParser";
import { useTranslation } from "@/lib/i18n";
import { useFocusTrap } from "@/hooks/useFocusTrap";
import { Mic, CheckCircle2, AlertTriangle, AlertCircle, X, RotateCcw, ShieldCheck, Info } from "lucide-react";

interface VoiceConfirmationModalProps {
  state: VoiceListeningState;
  activeField: VoiceFieldType | null;
  rawTranscript: string;
  parseResult: ParseResult | null;
  errorMessage: string | null;
  onConfirm: () => void;
  onRetry: () => void;
  onCancel: () => void;
}

export const VoiceConfirmationModal: React.FC<VoiceConfirmationModalProps> = ({
  state,
  activeField,
  rawTranscript,
  parseResult,
  errorMessage,
  onConfirm,
  onRetry,
  onCancel,
}) => {
  const { t } = useTranslation();
  const isOpen = state !== "IDLE" && activeField !== null;
  const modalRef = useFocusTrap<HTMLDivElement>({
    isOpen,
    onClose: onCancel,
  });

  if (!isOpen || !activeField) {
    return null;
  }

  const fieldConfig = VOICE_FIELD_CONFIGS[activeField];
  const fieldLabel = fieldConfig ? t(fieldConfig.labelKey) : activeField;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm animate-in fade-in duration-200"
      role="dialog"
      aria-modal="true"
      aria-labelledby="voice-modal-title"
      aria-describedby="voice-modal-desc"
      data-testid="voice-confirmation-modal"
    >
      <div
        ref={modalRef}
        className="relative w-full max-w-lg bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden flex flex-col focus:outline-none"
        tabIndex={-1}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="bg-slate-900 text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className={`p-2 rounded-xl ${
                state === "LISTENING" ? "bg-rose-500 animate-pulse text-white" : "bg-indigo-600 text-white"
              }`}
              aria-hidden="true"
            >
              <Mic className="w-5 h-5" />
            </div>
            <div>
              <h3 id="voice-modal-title" className="text-base font-bold">
                {t("voice.confirmTitle")}
              </h3>
              <p id="voice-modal-desc" className="text-xs text-slate-300">
                {fieldLabel}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onCancel}
            className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
            aria-label={t("voice.cancelManual")}
          >
            <X className="w-5 h-5" aria-hidden="true" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5 text-sm" role="status" aria-live="polite">
          {/* State 1: Active Listening */}
          {state === "LISTENING" && (
            <div className="text-center py-6 space-y-4">
              <div
                className="w-16 h-16 bg-rose-50 border-4 border-rose-200 text-rose-600 rounded-full flex items-center justify-center mx-auto animate-bounce"
                aria-hidden="true"
              >
                <Mic className="w-8 h-8" />
              </div>
              <div>
                <h4 className="font-bold text-gray-900 text-base">{t("voice.listening")}</h4>
                <p className="text-xs text-gray-600 mt-1">
                  e.g., &quot;50 thousand&quot;, &quot;2.5 lakh&quot;, or &quot;₹50,000&quot;
                </p>
              </div>
            </div>
          )}

          {/* State 2: Requesting Permission / Processing */}
          {(state === "REQUESTING_PERMISSION" || state === "PARSING") && (
            <div className="text-center py-8 space-y-3">
              <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" aria-hidden="true" />
              <p className="text-xs font-semibold text-gray-700">Processing audio...</p>
            </div>
          )}

          {/* State 3: Success Confirmation */}
          {state === "AWAITING_CONFIRMATION" && parseResult && parseResult.status === "SUCCESS" && (
            <div className="space-y-4">
              <div className="p-4 bg-emerald-50/70 border border-emerald-200 rounded-xl space-y-3">
                <div className="flex items-center gap-2 text-emerald-800 font-bold text-xs uppercase tracking-wider">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" aria-hidden="true" />
                  <span>Number Recognized</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                  <div className="bg-white p-3 rounded-lg border border-emerald-100">
                    <span className="text-[11px] text-gray-600 block">{t("voice.heard")}:</span>
                    <span className="font-bold text-gray-900 text-sm block mt-0.5">
                      &ldquo;{rawTranscript}&rdquo;
                    </span>
                  </div>
                  <div className="bg-white p-3 rounded-lg border border-emerald-100">
                    <span className="text-[11px] text-gray-600 block">{t("voice.interpretedValue")}:</span>
                    <span className="font-black text-emerald-700 text-base block mt-0.5" data-testid="voice-interpreted-value">
                      {parseResult.formatted_display}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* State 4: Ambiguous result */}
          {state === "AWAITING_CONFIRMATION" && parseResult && parseResult.status === "AMBIGUOUS" && (
            <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl space-y-2 text-amber-900">
              <div className="flex items-center gap-2 font-bold text-xs uppercase tracking-wider">
                <AlertTriangle className="w-4 h-4 text-amber-600" aria-hidden="true" />
                <span>Ambiguous Spoken Value</span>
              </div>
              <p className="text-xs">{parseResult.ambiguity_reason || t("voice.couldNotUnderstand")}</p>
              <div className="text-xs font-mono bg-white p-2 rounded border border-amber-200">
                {t("voice.heard")}: &ldquo;{rawTranscript}&rdquo;
              </div>
            </div>
          )}

          {/* State 5: Out of range */}
          {state === "AWAITING_CONFIRMATION" && parseResult && parseResult.status === "OUT_OF_RANGE" && (
            <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl space-y-2 text-rose-900">
              <div className="flex items-center gap-2 font-bold text-xs uppercase tracking-wider">
                <AlertCircle className="w-4 h-4 text-rose-600" aria-hidden="true" />
                <span>Out of Allowable Range</span>
              </div>
              <p className="text-xs">{parseResult.ambiguity_reason || t("voice.outOfRange")}</p>
              <div className="text-xs font-mono bg-white p-2 rounded border border-rose-200">
                {t("voice.heard")}: &ldquo;{rawTranscript}&rdquo;
              </div>
            </div>
          )}

          {/* State 6: Invalid / Error States */}
          {(state === "PERMISSION_DENIED" ||
            state === "UNSUPPORTED" ||
            state === "NO_SPEECH" ||
            state === "RECOGNITION_ERROR" ||
            (parseResult && parseResult.status === "INVALID")) && (
            <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl space-y-2 text-rose-900">
              <div className="flex items-center gap-2 font-bold text-xs uppercase tracking-wider">
                <AlertCircle className="w-4 h-4 text-rose-600" aria-hidden="true" />
                <span>Voice Input Notice</span>
              </div>
              <p className="text-xs">
                {errorMessage ||
                  (state === "PERMISSION_DENIED"
                    ? t("voice.micDenied")
                    : state === "UNSUPPORTED"
                    ? t("voice.unsupported")
                    : state === "NO_SPEECH"
                    ? t("voice.noSpeech")
                    : t("voice.couldNotUnderstand"))}
              </p>
              {rawTranscript && (
                <div className="text-xs font-mono bg-white p-2 rounded border border-rose-200">
                  {t("voice.heard")}: &ldquo;{rawTranscript}&rdquo;
                </div>
              )}
            </div>
          )}

          {/* Mandatory Privacy & Accuracy Disclaimers */}
          <div className="pt-2 border-t border-gray-100 space-y-1.5 text-[11px] text-gray-600">
            <div className="flex items-start gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" aria-hidden="true" />
              <span>{t("voice.privacyNotice")}</span>
            </div>
            <div className="flex items-start gap-1.5">
              <Info className="w-3.5 h-3.5 text-slate-500 mt-0.5 shrink-0" aria-hidden="true" />
              <span>{t("voice.accuracyDisclaimer")}</span>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="bg-gray-50 px-6 py-3 border-t border-gray-100 flex flex-wrap items-center justify-between gap-2">
          <button
            type="button"
            onClick={onCancel}
            className="px-3.5 py-2 text-xs font-semibold text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-400"
          >
            {t("voice.cancelManual")}
          </button>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onRetry}
              className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-lg shadow-sm transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
            >
              <RotateCcw className="w-3.5 h-3.5" aria-hidden="true" />
              <span>{t("voice.tryAgain")}</span>
            </button>

            {state === "AWAITING_CONFIRMATION" && parseResult && parseResult.status === "SUCCESS" && (
              <button
                type="button"
                onClick={onConfirm}
                className="flex items-center gap-1.5 px-4 py-2 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow-sm transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-emerald-500"
                data-testid="voice-use-value-btn"
              >
                <CheckCircle2 className="w-3.5 h-3.5" aria-hidden="true" />
                <span>{t("voice.useValue")}</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

