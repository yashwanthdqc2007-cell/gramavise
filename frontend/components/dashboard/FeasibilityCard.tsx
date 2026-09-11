"use client";

import React from "react";
import { Card } from "@/components/ui/Card";
import { AnalysisStatus } from "@/components/analysis/AnalysisStatus";
import { RecommendationStatus } from "@/lib/types";

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
  // TODO [Frontend Lead]: Add visual gauge meter and verdict highlights
  return (
    <Card className="border-l-4 border-l-brand-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
            Overall Feasibility Verdict
          </span>
          <div className="mt-1">
            <AnalysisStatus status={status} confidence={confidence} />
          </div>
          {summary && <p className="mt-2 text-sm text-gray-700">{summary}</p>}
        </div>
      </div>
    </Card>
  );
};
