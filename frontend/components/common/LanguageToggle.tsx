"use client";

import React from "react";
import { useTranslation, SUPPORTED_LANGUAGE_OPTIONS, SupportedLanguage } from "@/lib/i18n";

interface LanguageToggleProps {
  className?: string;
  isDark?: boolean;
}

export const LanguageToggle: React.FC<LanguageToggleProps> = ({ className, isDark = false }) => {
  const { language, setLanguage, t } = useTranslation();

  const baseStyle = isDark
    ? "text-xs bg-slate-900/90 border border-slate-700 text-slate-200 rounded-xl px-3 py-1.5 font-medium focus:outline-none focus:ring-2 focus:ring-emerald-500 cursor-pointer shadow-2xs"
    : "text-xs bg-slate-900/90 border border-slate-700 text-slate-200 rounded-xl px-3 py-1.5 font-medium focus:outline-none focus:ring-2 focus:ring-emerald-500 cursor-pointer shadow-2xs";

  return (
    <select
      value={language}
      onChange={(e) => setLanguage(e.target.value as SupportedLanguage)}
      aria-label={t("nav.selectLanguage")}
      className={`${baseStyle} ${className || ""}`}
    >
      {SUPPORTED_LANGUAGE_OPTIONS.map((lang) => (
        <option key={lang.code} value={lang.code} className={isDark ? "bg-slate-900 text-slate-100" : ""}>
          {lang.nativeLabel} ({lang.label})
        </option>
      ))}
    </select>
  );
};

