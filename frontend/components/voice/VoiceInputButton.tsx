"use client";

import React from "react";
import { VoiceFieldType } from "@/lib/voice/types";
import { VOICE_FIELD_CONFIGS } from "@/lib/voice/numericParser";
import { useTranslation } from "@/lib/i18n";
import { Mic } from "lucide-react";

interface VoiceInputButtonProps {
  fieldType: VoiceFieldType;
  onStartVoice: (fieldType: VoiceFieldType) => void;
  isListening?: boolean;
  disabled?: boolean;
}

export const VoiceInputButton: React.FC<VoiceInputButtonProps> = ({
  fieldType,
  onStartVoice,
  isListening = false,
  disabled = false,
}) => {
  const { t } = useTranslation();
  const config = VOICE_FIELD_CONFIGS[fieldType];

  // Only render if field is in active rollout scope
  if (!config || !config.isRolloutActive) {
    return null;
  }

  const label = t("voice.startListening");

  return (
    <button
      type="button"
      onClick={(e) => {
        e.preventDefault();
        e.stopPropagation();
        onStartVoice(fieldType);
      }}
      disabled={disabled}
      title={`${label} (${t(config.labelKey)})`}
      aria-label={`${label}: ${t(config.labelKey)}`}
      data-testid={`voice-btn-${fieldType}`}
      className={`inline-flex items-center justify-center p-2 rounded-lg border transition-all focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-1 focus:ring-offset-[#102B3A] ${
        isListening
          ? "bg-rose-500 text-white border-rose-600 animate-pulse shadow-md"
          : "bg-[#0B1F2D] hover:bg-[#0E2635] text-slate-400 hover:text-emerald-300 border-slate-700 hover:border-emerald-500/50 shadow-sm"
      } ${disabled ? "opacity-40 cursor-not-allowed" : "cursor-pointer"}`}
    >
      <Mic className={`w-4 h-4 ${isListening ? "animate-bounce" : ""}`} />
    </button>
  );
};
