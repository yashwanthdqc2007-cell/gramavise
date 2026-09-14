"use client";

import React from "react";
import { Button } from "@/components/ui/Button";
import { useTranslation } from "@/lib/i18n";

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title,
  message,
  onRetry,
  secondaryAction,
}) => {
  const { t } = useTranslation();
  const displayTitle = title || t("common.errorTitle");

  return (
    <div className="p-6 bg-red-50 border border-red-200 rounded-xl text-center space-y-4 max-w-lg mx-auto">
      <div className="w-12 h-12 bg-red-100 text-red-600 rounded-full flex items-center justify-center mx-auto text-xl font-bold">
        ⚠️
      </div>
      <div>
        <h3 className="text-base font-bold text-red-800">{displayTitle}</h3>
        <p className="text-sm text-red-600 mt-1">{message}</p>
      </div>
      {(onRetry || secondaryAction) && (
        <div className="flex flex-wrap justify-center gap-3 pt-2">
          {onRetry && (
            <Button variant="danger" size="sm" onClick={onRetry}>
              {t("common.retry")}
            </Button>
          )}
          {secondaryAction && (
            <Button variant="outline" size="sm" onClick={secondaryAction.onClick}>
              {secondaryAction.label}
            </Button>
          )}
        </div>
      )}
    </div>
  );
};

