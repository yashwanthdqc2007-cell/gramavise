"use client";

import React from "react";
import { useNetworkStatus, NetworkConnectionState } from "@/hooks/useNetworkStatus";
import { useTranslation } from "@/lib/i18n";
import { WifiOff, AlertTriangle, Clock } from "lucide-react";

interface NetworkStatusBarProps {
  overrideState?: NetworkConnectionState;
  onRetry?: () => void;
}

export const NetworkStatusBar: React.FC<NetworkStatusBarProps> = ({
  overrideState,
  onRetry,
}) => {
  const { isOnline, connectionState } = useNetworkStatus();
  const { t } = useTranslation();

  const activeState = overrideState || connectionState;

  if (activeState === "ONLINE" && isOnline) {
    return null;
  }

  return (
    <div
      role="status"
      aria-live="polite"
      className="w-full bg-amber-600 text-white px-4 py-2 text-xs sm:text-sm font-medium transition-all duration-200 shadow-sm"
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          {!isOnline || activeState === "OFFLINE" ? (
            <>
              <WifiOff className="w-4 h-4 flex-shrink-0 animate-pulse text-amber-200" aria-hidden="true" />
              <span>
                <strong className="font-bold mr-1">[{t("network.offlineBadge")}]</strong>
                {t("network.offlineDesc")}
              </span>
            </>
          ) : activeState === "TIMEOUT" ? (
            <>
              <Clock className="w-4 h-4 flex-shrink-0 text-amber-200" aria-hidden="true" />
              <span>{t("network.timeout")}</span>
            </>
          ) : (
            <>
              <AlertTriangle className="w-4 h-4 flex-shrink-0 text-amber-200" aria-hidden="true" />
              <span>{t("network.serverUnavailable")}</span>
            </>
          )}
        </div>

        {onRetry && (
          <button
            onClick={onRetry}
            className="px-2.5 py-1 bg-white text-amber-800 rounded font-semibold text-xs hover:bg-amber-50 focus:ring-2 focus:ring-white focus:outline-none flex-shrink-0"
          >
            {t("common.retry")}
          </button>
        )}
      </div>
    </div>
  );
};
