"use client";

import React, { useState } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { LanguageToggle } from "@/components/common/LanguageToggle";
import { useTranslation, SUPPORTED_LANGUAGE_OPTIONS, SupportedLanguage } from "@/lib/i18n";
import { clearDraft } from "@/lib/storage/draftStorage";
import { clearHistory } from "@/lib/storage/historyStorage";
import {
  Settings,
  Globe,
  Database,
  Trash2,
  CheckCircle2,
  AlertTriangle,
  Accessibility,
  Keyboard,
  Contrast,
} from "lucide-react";

export default function SettingsPage() {
  const { t, language, setLanguage } = useTranslation();
  const [showConfirmClear, setShowConfirmClear] = useState(false);
  const [clearSuccess, setClearSuccess] = useState(false);

  const handleClearData = () => {
    try {
      clearDraft();
      clearHistory();
      if (typeof window !== "undefined") {
        sessionStorage.removeItem("gramavise_latest_result");
        sessionStorage.removeItem("gramavise_financials");
        sessionStorage.removeItem("gramavise_result_timestamp");
      }
      setShowConfirmClear(false);
      setClearSuccess(true);
      setTimeout(() => setClearSuccess(false), 4000);
    } catch (err) {
      console.error("Failed to clear local data:", err);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 sm:py-10 space-y-8">
      {/* Header */}
      <div className="border-b border-slate-800 pb-5">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-300 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/30 inline-flex items-center gap-1.5">
            <Settings className="w-3.5 h-3.5" />
            Preferences
          </span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          {t("settings.title")}
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl leading-relaxed">
          {t("settings.subtitle")}
        </p>
      </div>

      {/* Success Notification */}
      {clearSuccess && (
        <div
          role="status"
          className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-4 flex items-center gap-3 text-sm text-emerald-300 animate-in fade-in duration-200"
        >
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
          <span>{t("settings.clearDataSuccess")}</span>
        </div>
      )}

      {/* 1. Language Preference */}
      <Card className="p-6 md:p-7 space-y-5 border-slate-800 bg-[#0A1A28]">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <div className="flex items-center gap-2.5">
            <Globe className="w-5 h-5 text-emerald-400" />
            <h2 className="text-base font-bold text-white">{t("settings.languageTitle")}</h2>
          </div>
          <LanguageToggle isDark />
        </div>
        <p className="text-xs text-slate-400 leading-relaxed">
          {t("settings.languageDesc")}
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 pt-1">
          {SUPPORTED_LANGUAGE_OPTIONS.map((lang) => {
            const isSelected = language === lang.code;
            return (
              <button
                key={lang.code}
                type="button"
                onClick={() => setLanguage(lang.code)}
                className={`p-3 rounded-xl border text-left transition-all ${
                  isSelected
                    ? "bg-emerald-950/60 border-emerald-500/50 text-white shadow-xs"
                    : "bg-[#06131F] border-slate-800 text-slate-300 hover:border-slate-700 hover:text-white"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm">{lang.nativeLabel}</span>
                  {isSelected && <span className="w-2 h-2 rounded-full bg-emerald-400" />}
                </div>
                <span className="text-[11px] text-slate-400 block mt-0.5">{lang.label}</span>
              </button>
            );
          })}
        </div>
      </Card>

      {/* 2. Local Data & Offline Storage */}
      <Card className="p-6 md:p-7 space-y-5 border-slate-800 bg-[#0A1A28]">
        <div className="flex items-center gap-2.5 border-b border-slate-800/80 pb-3">
          <Database className="w-5 h-5 text-cyan-400" />
          <h2 className="text-base font-bold text-white">{t("settings.dataTitle")}</h2>
        </div>
        <p className="text-xs text-slate-400 leading-relaxed">
          {t("settings.dataDesc")}
        </p>

        <div className="p-4 bg-[#06131F] rounded-xl border border-slate-800 text-xs text-slate-400 space-y-2">
          <div className="flex items-center justify-between text-slate-300">
            <span>Client storage type:</span>
            <span className="font-mono text-[11px] text-emerald-400 font-bold">Browser LocalStorage + SessionStorage</span>
          </div>
          <div className="flex items-center justify-between text-slate-300">
            <span>Recent reports limit:</span>
            <span className="font-mono text-[11px] text-slate-300">20 analyses max</span>
          </div>
          <p className="text-[11px] text-slate-400 pt-1 border-t border-slate-800">
            Permanent evaluation traces and calculation snapshots are securely preserved in the database.
          </p>
        </div>

        {/* Clear Data Section */}
        {!showConfirmClear ? (
          <div className="pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowConfirmClear(true)}
              className="text-rose-400 border-rose-500/30 hover:bg-rose-500/10 hover:text-rose-300 flex items-center gap-2"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>{t("settings.clearDataBtn")}</span>
            </Button>
          </div>
        ) : (
          <div className="p-4 rounded-xl border border-rose-500/40 bg-rose-950/30 space-y-3 animate-in fade-in duration-150">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
              <div className="space-y-1">
                <h3 className="text-xs font-bold text-white">{t("settings.clearDataConfirmTitle")}</h3>
                <p className="text-xs text-rose-200/80 leading-relaxed">
                  {t("settings.clearDataConfirmDesc")}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 pt-1">
              <Button
                size="sm"
                onClick={handleClearData}
                className="bg-rose-600 hover:bg-rose-700 text-white font-bold"
              >
                Yes, Clear Local Data
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setShowConfirmClear(false)}
                className="border-slate-700 text-slate-300"
              >
                Cancel
              </Button>
            </div>
          </div>
        )}
      </Card>

      {/* 3. Accessibility & High Contrast */}
      <Card className="p-6 md:p-7 space-y-4 border-slate-800 bg-[#0A1A28]">
        <div className="flex items-center gap-2.5 border-b border-slate-800/80 pb-3">
          <Accessibility className="w-5 h-5 text-purple-400" />
          <h2 className="text-base font-bold text-white">{t("settings.accessibilityTitle")}</h2>
        </div>
        <p className="text-xs text-slate-400 leading-relaxed">
          {t("settings.accessibilityDesc")}
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1 text-xs">
          <div className="p-3 bg-[#06131F] rounded-xl border border-slate-800 flex items-center gap-2.5 text-slate-300">
            <Contrast className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>High-Contrast Navy & Emerald Palette (WCAG AA Compliant)</span>
          </div>
          <div className="p-3 bg-[#06131F] rounded-xl border border-slate-800 flex items-center gap-2.5 text-slate-300">
            <Keyboard className="w-4 h-4 text-cyan-400 shrink-0" />
            <span>Full Keyboard & Screen Reader Navigation Support</span>
          </div>
        </div>
      </Card>
    </div>
  );
}
