"use client";

import React, { useState } from "react";
import { SUPPORTED_LANGUAGES } from "@/lib/constants";

export const LanguageToggle: React.FC = () => {
  const [selectedLang, setSelectedLang] = useState("en");

  // TODO [Frontend Lead]: Connect language selection to i18n context state
  return (
    <select
      value={selectedLang}
      onChange={(e) => setSelectedLang(e.target.value)}
      className="text-xs bg-gray-50 border border-gray-200 rounded-lg px-2.5 py-1.5 font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-brand-500 cursor-pointer"
    >
      {SUPPORTED_LANGUAGES.map((lang) => (
        <option key={lang.code} value={lang.code}>
          {lang.label}
        </option>
      ))}
    </select>
  );
};
