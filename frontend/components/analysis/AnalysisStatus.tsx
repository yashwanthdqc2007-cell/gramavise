"use client";

import React from "react";
import { RecommendationStatus } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";

interface AnalysisStatusProps {
  status: RecommendationStatus;
  confidence: number;
}

export const AnalysisStatus: React.FC<AnalysisStatusProps> = ({ status, confidence }) => {
  const statusConfig = {
    PROCEED: {
      label: "PROCEED (Viable)",
      variant: "success" as const,
      description: "Business model shows strong margins and adequate debt coverage.",
    },
    VALIDATE_FIRST: {
      label: "VALIDATE FIRST (Cautious)",
      variant: "warning" as const,
      description: "Viable under current assumptions, but local validation is recommended.",
    },
    RECONSIDER: {
      label: "RECONSIDER (High Risk)",
      variant: "danger" as const,
      description: "Projected cash flows show deficit or insufficient debt service capacity.",
    },
  };

  const current = statusConfig[status] || statusConfig.VALIDATE_FIRST;

  return (
    <div className="flex items-center space-x-3">
      <Badge variant={current.variant}>{current.label}</Badge>
      <span className="text-xs text-gray-500">Confidence: {(confidence * 100).toFixed(0)}%</span>
    </div>
  );
};
