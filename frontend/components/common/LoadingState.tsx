"use client";

import React from "react";
import { useTranslation } from "@/lib/i18n";

interface LoadingStateProps {
  message?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({ message }) => {
  const { t } = useTranslation();
  const displayMessage = message || t("common.loading");

  return (
    <div
      role="status"
      aria-live="polite"
      className="flex flex-col items-center justify-center p-12 space-y-4"
    >
      <div
        className="w-10 h-10 border-4 border-emerald-200 border-t-emerald-600 rounded-full animate-spin"
        aria-hidden="true"
      />
      <h1 className="text-base font-semibold text-gray-800 text-center">{displayMessage}</h1>
    </div>
  );
};

