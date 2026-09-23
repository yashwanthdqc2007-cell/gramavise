"use client";

import React from "react";
import { Card } from "@/components/ui/Card";
import { AnalysisStatus } from "@/components/analysis/AnalysisStatus";
import { RecommendationStatus } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";

interface FeasibilityCardProps {
  status: RecommendationStatus;
  confidence: number;
  summary?: string;
}

export const FeasibilityCard: React.FC<FeasibilityCardProps> = ({
  status,
  confidence,
  summary,
}) => {
  const { t } = useTranslation();
  const borderColors: Record<RecommendationStatus, string> = {
    PROCEED: "border-l-emerald-500 bg-emerald-500/8",
    VALIDATE_FIRST: "border-l-amber-500 bg-amber-500/8",
    RECONSIDER: "border-l-rose-500 bg-rose-500/8",
  };

  const currentStyle = borderColors[status] || "border-l-slate-600 bg-[#0B1F2D]";

  return (
    <Card className={`border-l-4 shadow-sm ${currentStyle}`}>
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            {t("results.feasibility.title")}
          </span>
          <div>
            <AnalysisStatus status={status} confidence={confidence} />
          </div>
          {summary && <p className="mt-2.5 text-sm text-slate-300 leading-relaxed">{summary}</p>}
        </div>
      </div>
    </Card>
  );
};

