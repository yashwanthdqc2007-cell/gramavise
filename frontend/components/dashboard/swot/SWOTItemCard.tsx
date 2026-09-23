"use client";

import React, { useState } from "react";
import { SWOTItem, EvidenceItem, EvidenceType } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";
import {
  ShieldCheck,
  AlertTriangle,
  FileText,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  HelpCircle,
  CheckCircle2,
} from "lucide-react";

interface SWOTItemCardProps {
  item: SWOTItem;
  quadrantType: "STRENGTH" | "WEAKNESS" | "OPPORTUNITY" | "THREAT";
  evidenceLedger?: EvidenceItem[];
  onNavigateToEvidenceTab?: () => void;
}

export const SWOTItemCard: React.FC<SWOTItemCardProps> = ({
  item,
  quadrantType,
  evidenceLedger = [],
  onNavigateToEvidenceTab,
}) => {
  const { t } = useTranslation();
  const [showEvidence, setShowEvidence] = useState(false);

  // Evidence badge styling matching GramaVise design system
  const getEvidenceTypeBadge = (type?: EvidenceType | string) => {
    switch (type) {
      case "OBSERVED":
        return {
          label: "OBSERVED",
          bg: "bg-blue-500/15 text-blue-300 border-blue-500/30",
        };
      case "CALCULATED":
        return {
          label: "CALCULATED",
          bg: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
        };
      case "MODELLED":
        return {
          label: "MODELLED",
          bg: "bg-purple-500/15 text-purple-300 border-purple-500/30",
        };
      case "ASSUMED":
        return {
          label: "ASSUMED",
          bg: "bg-amber-500/15 text-amber-300 border-amber-500/30",
        };
      case "NEEDS_VERIFICATION":
        return {
          label: "NEEDS VERIFICATION",
          bg: "bg-rose-500/15 text-rose-300 border-rose-500/30",
        };
      default:
        return {
          label: type || "DERIVED",
          bg: "bg-slate-700/50 text-slate-300 border-slate-600/50",
        };
    }
  };

  // Severity / Importance badge
  const getImportanceBadge = (importance?: string) => {
    switch (importance) {
      case "CRITICAL":
        return "bg-rose-500/20 text-rose-300 border-rose-500/40";
      case "HIGH":
        return "bg-amber-500/20 text-amber-300 border-amber-500/40";
      case "MEDIUM":
        return "bg-slate-700/50 text-slate-300 border-slate-600/50";
      case "LOW":
        return "bg-slate-800 text-slate-400 border-slate-700/50";
      default:
        return null;
    }
  };

  const evidenceTypeMeta = getEvidenceTypeBadge(item.evidence_type);
  const importanceClass = getImportanceBadge(item.importance);
  const isNeedsVerification = item.evidence_type === "NEEDS_VERIFICATION";

  // Match linked evidence items from the full evidence ledger
  const linkedEvidence = (item.evidence_ids || [])
    .map((id) => evidenceLedger.find((e) => e.evidence_id === id))
    .filter((e): e is EvidenceItem => e !== undefined);

  return (
    <div
      className="p-4 rounded-xl bg-[#0E2635] border border-slate-800/90 hover:border-slate-700/80 transition-all space-y-3 shadow-xs"
      data-testid={`swot-item-${item.id}`}
    >
      {/* Top Header: Title & Badges */}
      <div className="space-y-1.5">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <h4 className="text-sm font-bold text-white tracking-tight leading-snug flex-1">
            {item.title}
          </h4>
          <div className="flex items-center gap-1.5 shrink-0">
            {importanceClass && item.importance && (
              <span
                className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded border ${importanceClass}`}
                title={`Importance: ${item.importance}`}
              >
                {item.importance}
              </span>
            )}
            <span
              className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${evidenceTypeMeta.bg}`}
              title={`Evidence Classification: ${evidenceTypeMeta.label}`}
            >
              {evidenceTypeMeta.label}
            </span>
          </div>
        </div>

        {/* Item ID & Category (if provided) */}
        <div className="flex items-center gap-2 text-[10px] font-mono text-slate-400">
          <span>{item.id}</span>
          {item.category && (
            <>
              <span>•</span>
              <span className="uppercase text-slate-400">{item.category}</span>
            </>
          )}
          {typeof item.confidence === "number" && (
            <>
              <span>•</span>
              <span className="text-slate-300">
                {t("results.swot.confidence")}: {(item.confidence * 100).toFixed(0)}%
              </span>
            </>
          )}
        </div>
      </div>

      {/* Explanation Text */}
      <p className="text-xs text-slate-300 leading-relaxed font-normal">
        {item.explanation}
      </p>

      {/* Needs Verification Calm Notice Banner */}
      {isNeedsVerification && (
        <div className="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/25 flex items-start gap-2 text-[11px] text-amber-200/90">
          <HelpCircle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" aria-hidden="true" />
          <span>{t("results.swot.needsVerificationDesc")}</span>
        </div>
      )}

      {/* Evidence Interaction Footer */}
      {(item.evidence_ids && item.evidence_ids.length > 0) && (
        <div className="pt-2 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-2">
          <button
            type="button"
            onClick={() => setShowEvidence(!showEvidence)}
            className="text-[11px] font-bold text-emerald-400 hover:text-emerald-300 inline-flex items-center gap-1 transition-colors focus:outline-none focus-visible:underline"
            aria-expanded={showEvidence}
          >
            <span>{showEvidence ? "Hide evidence" : t("results.swot.viewEvidence")}</span>
            {showEvidence ? (
              <ChevronUp className="w-3 h-3" />
            ) : (
              <ChevronDown className="w-3 h-3" />
            )}
          </button>

          <span className="text-[10px] font-mono text-slate-400">
            {item.evidence_ids.length} backing indicator{item.evidence_ids.length > 1 ? "s" : ""}
          </span>
        </div>
      )}

      {/* Expandable Supporting Evidence Drawer */}
      {showEvidence && item.evidence_ids && item.evidence_ids.length > 0 && (
        <div className="mt-2.5 p-3 rounded-lg bg-[#071822] border border-slate-800 text-xs space-y-2 animate-in fade-in duration-100">
          <div className="flex items-center justify-between text-[11px] font-bold text-slate-300">
            <span className="flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-emerald-400" />
              Evidence Ledger Provenance
            </span>
            {onNavigateToEvidenceTab && (
              <button
                type="button"
                onClick={onNavigateToEvidenceTab}
                className="text-[10px] text-emerald-400 hover:text-emerald-300 flex items-center gap-1 underline font-semibold"
              >
                <span>Full Audit Trail</span>
                <ExternalLink className="w-3 h-3" />
              </button>
            )}
          </div>

          <div className="space-y-1.5 pt-1">
            {item.evidence_ids.map((id) => {
              const matched = linkedEvidence.find((e) => e.evidence_id === id);
              return (
                <div
                  key={id}
                  className="p-2 rounded bg-[#0A1F2D] border border-slate-800/80 text-[11px] flex flex-col sm:flex-row sm:items-center justify-between gap-1.5"
                >
                  <div className="space-y-0.5">
                    <span className="font-mono text-emerald-300 font-bold mr-1.5">
                      {id}
                    </span>
                    {matched && (
                      <span className="text-slate-300 font-medium">
                        {matched.indicator}
                      </span>
                    )}
                  </div>
                  {matched && (
                    <div className="flex items-center gap-2 text-[10px] text-slate-400 shrink-0">
                      <span className="px-1.5 py-0.2 rounded bg-slate-800 border border-slate-700 text-slate-300">
                        {matched.evidence_type}
                      </span>
                      {matched.source && (
                        <span className="truncate max-w-[140px]" title={matched.source}>
                          {matched.source}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
