import React from "react";
import { EvidenceType } from "@/lib/types";
import { EVIDENCE_BADGE_COLORS } from "@/lib/constants";
import { cn } from "@/lib/utils";

interface EvidenceBadgeProps {
  type: EvidenceType;
  confidence?: number;
}

export const EvidenceBadge: React.FC<EvidenceBadgeProps> = ({ type, confidence }) => {
  const colorClass = EVIDENCE_BADGE_COLORS[type] || "bg-gray-100 text-gray-800 border-gray-200";

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold border",
        colorClass
      )}
      title={`Evidence Type: ${type}`}
    >
      <span>{type}</span>
      {confidence !== undefined && (
        <span className="opacity-75 font-normal">({(confidence * 100).toFixed(0)}%)</span>
      )}
    </span>
  );
};
