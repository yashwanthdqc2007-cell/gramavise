"use client";

import { useState, useEffect, useCallback } from "react";

export type NetworkConnectionState =
  | "ONLINE"
  | "OFFLINE"
  | "SERVER_UNAVAILABLE"
  | "ANALYSIS_PENDING"
  | "ANALYSIS_FAILED"
  | "TIMEOUT";

export function useNetworkStatus() {
  const [isOnline, setIsOnline] = useState<boolean>(() => {
    if (typeof window !== "undefined" && typeof navigator !== "undefined") {
      return navigator.onLine;
    }
    return true;
  });

  const [connectionState, setConnectionState] = useState<NetworkConnectionState>(() => {
    if (typeof window !== "undefined" && typeof navigator !== "undefined" && !navigator.onLine) {
      return "OFFLINE";
    }
    return "ONLINE";
  });

  useEffect(() => {
    if (typeof window === "undefined") return;

    const handleOnline = () => {
      setIsOnline(true);
      setConnectionState("ONLINE");
    };

    const handleOffline = () => {
      setIsOnline(false);
      setConnectionState("OFFLINE");
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  const reportApiError = useCallback((errorType: "SERVER_UNAVAILABLE" | "TIMEOUT" | "ANALYSIS_FAILED") => {
    if (typeof navigator !== "undefined" && !navigator.onLine) {
      setIsOnline(false);
      setConnectionState("OFFLINE");
      return;
    }
    setConnectionState(errorType);
  }, []);

  const resetNetworkStatus = useCallback(() => {
    if (typeof navigator !== "undefined" && !navigator.onLine) {
      setIsOnline(false);
      setConnectionState("OFFLINE");
    } else {
      setIsOnline(true);
      setConnectionState("ONLINE");
    }
  }, []);

  return {
    isOnline,
    connectionState,
    reportApiError,
    resetNetworkStatus,
  };
}
