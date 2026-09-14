import React from "react";
import { EvidenceType } from "@/lib/types";
import { EVIDENCE_BADGE_COLORS } from "@/lib/constants";
import { cn } from "@/lib/utils";

interface EvidenceBadgeProps {
  type: EvidenceType;
  confidence?: number | string;
  confidenceLevel?: string;
}

export const EvidenceBadge: React.FC<EvidenceBadgeProps> = ({ type, confidence, confidenceLevel }) => {
  const colorClass = EVIDENCE_BADGE_COLORS[type] || "bg-gray-100 text-gray-800 border-gray-200";

  const getFriendlyLabel = (t: EvidenceType) => {
    switch (t) {
      case "CALCULATED":
        return "Calculated";
      case "OBSERVED":
        return "Observed";
      case "ASSUMED":
        return "Assumed";
      case "MODELLED":
        return "Modelled";
      case "NEEDS_VERIFICATION":
        return "Needs Verification";
      default:
        return t;
    }
  };

  const getConfLevel = () => {
    if (confidenceLevel) return confidenceLevel;
    if (typeof confidence === "string") return confidence;
    if (typeof confidence === "number") {
      if (confidence >= 0.9) return "HIGH";
      if (confidence >= 0.6) return "MEDIUM";
      if (confidence > 0.0) return "LOW";
      return "UNKNOWN";
    }
    return null;
  };

  const confLabel = getConfLevel();

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-semibold border",
        colorClass
      )}
      title={`Evidence Classification: ${type}`}
    >
      <span>{getFriendlyLabel(type)}</span>
      {confLabel && (
        <span className="opacity-80 font-mono text-[9px] uppercase px-1 py-0.2 bg-black/5 rounded">
          {confLabel}
        </span>
      )}
    </span>
  );
};
