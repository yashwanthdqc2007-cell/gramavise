"use client";

import React from "react";
import { SWOTAnalysis, EvidenceItem } from "@/lib/types";
import { SWOTQuadrant } from "./SWOTQuadrant";
import { useTranslation } from "@/lib/i18n";
import { Compass, ShieldCheck, FileCheck, Info } from "lucide-react";

interface SWOTSectionProps {
  swot?: SWOTAnalysis | null;
  evidenceLedger?: EvidenceItem[];
  onNavigateToEvidenceTab?: () => void;
}

export const SWOTSection: React.FC<SWOTSectionProps> = ({
  swot,
  evidenceLedger = [],
  onNavigateToEvidenceTab,
}) => {
  const { t } = useTranslation();

  // If SWOT data is unavailable / null
  if (!swot) {
    return (
      <section
        id="business-factors"
        className="bg-[#0B1F2D] rounded-2xl border border-slate-800/80 p-6 md:p-7 shadow-xl space-y-4"
        data-testid="swot-section-empty"
      >
        <div className="flex items-center gap-2 text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider">
          <Compass className="w-4 h-4" aria-hidden="true" />
          <span>{t("results.swot.badge")}</span>
        </div>
        <div className="border-b border-slate-800 pb-3">
          <h2 className="text-xl font-black text-white tracking-tight">
            {t("results.swot.title")}
          </h2>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            {t("results.swot.subtitle")}
          </p>
        </div>
        <div className="p-6 rounded-xl border border-dashed border-slate-800 bg-[#081722]/50 text-center space-y-2">
          <Info className="w-5 h-5 text-slate-500 mx-auto" aria-hidden="true" />
          <p className="text-xs sm:text-sm text-slate-400 font-medium">
            {t("results.swot.emptyState")}
          </p>
        </div>
      </section>
    );
  }

  const strengths = swot.strengths || [];
  const weaknesses = swot.weaknesses || [];
  const opportunities = swot.opportunities || [];
  const threats = swot.threats || [];

  const totalFactors =
    strengths.length + weaknesses.length + opportunities.length + threats.length;

  return (
    <section
      id="business-factors"
      className="bg-[#0B1F2D] rounded-2xl border border-slate-800/80 p-5 sm:p-6 md:p-7 shadow-xl shadow-slate-950/20 space-y-6"
      data-testid="swot-section"
    >
      {/* Section Header */}
      <div className="border-b border-slate-800 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/25 tracking-wider uppercase">
              {t("results.swot.badge")}
            </span>
            <span className="text-xs font-mono text-slate-400">
              {totalFactors} verified factor{totalFactors === 1 ? "" : "s"}
            </span>
          </div>
          <h2 className="text-xl font-black text-white tracking-tight">
            {t("results.swot.title")}
          </h2>
          <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl leading-relaxed">
            {t("results.swot.subtitle")}
          </p>
        </div>

        {onNavigateToEvidenceTab && (
          <button
            type="button"
            onClick={onNavigateToEvidenceTab}
            className="text-xs font-bold text-emerald-400 hover:text-emerald-300 flex items-center gap-1.5 self-start sm:self-center px-3 py-1.5 rounded-lg bg-[#0E2635] border border-emerald-500/30 transition-all hover:border-emerald-500/50 shadow-2xs"
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Audit Ledger ({evidenceLedger.length})</span>
          </button>
        )}
      </div>

      {/* Balanced 2x2 Grid (Desktop) / Vertical Stack (Mobile) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        {/* Quadrant 1: Strengths */}
        <SWOTQuadrant
          type="STRENGTH"
          title={t("results.swot.strengths")}
          subtitle={t("results.swot.strengthsSub")}
          items={strengths}
          evidenceLedger={evidenceLedger}
          onNavigateToEvidenceTab={onNavigateToEvidenceTab}
        />

        {/* Quadrant 2: Weaknesses */}
        <SWOTQuadrant
          type="WEAKNESS"
          title={t("results.swot.weaknesses")}
          subtitle={t("results.swot.weaknessesSub")}
          items={weaknesses}
          evidenceLedger={evidenceLedger}
          onNavigateToEvidenceTab={onNavigateToEvidenceTab}
        />

        {/* Quadrant 3: Opportunities */}
        <SWOTQuadrant
          type="OPPORTUNITY"
          title={t("results.swot.opportunities")}
          subtitle={t("results.swot.opportunitiesSub")}
          items={opportunities}
          evidenceLedger={evidenceLedger}
          onNavigateToEvidenceTab={onNavigateToEvidenceTab}
        />

        {/* Quadrant 4: Threats */}
        <SWOTQuadrant
          type="THREAT"
          title={t("results.swot.threats")}
          subtitle={t("results.swot.threatsSub")}
          items={threats}
          evidenceLedger={evidenceLedger}
          onNavigateToEvidenceTab={onNavigateToEvidenceTab}
        />
      </div>

      {/* Grounding & Methodology Footer */}
      <div className="p-3.5 rounded-xl bg-[#081722]/80 border border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <FileCheck className="w-4 h-4 text-emerald-400 shrink-0" aria-hidden="true" />
          <span>
            Grounding: Derived strictly from deterministic financial ratios, OpenStreetMap amenities, Agmarknet price references, and statutory schemes.
          </span>
        </div>
        {typeof swot.confidence === "number" && (
          <span className="shrink-0 font-mono text-[11px] text-slate-300">
            Engine Confidence: {(swot.confidence * 100).toFixed(0)}%
          </span>
        )}
      </div>
    </section>
  );
};
