"use client";

import React from "react";
import { RecommendationStatus, EvidenceItem } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";
import { ShieldCheck, AlertTriangle, XCircle, CheckCircle2, MapPin, Calendar, Building2 } from "lucide-react";

interface DecisionHeroProps {
  status: RecommendationStatus;
  confidence: number;
  summary?: string;
  businessName?: string;
  businessCategory?: string;
  locationSummary?: string;
  assessmentDate?: string;
  evidenceList?: EvidenceItem[];
}

export const DecisionHero: React.FC<DecisionHeroProps> = ({
  status,
  confidence,
  summary,
  businessName,
  businessCategory,
  locationSummary,
  assessmentDate,
  evidenceList = [],
}) => {
  const { t } = useTranslation();

  // Status-specific visual styling (Warm, authoritative, no harsh neons)
  const statusTheme = {
    PROCEED: {
      bgCard: "bg-emerald-900 text-white border-emerald-950",
      accentBg: "bg-emerald-800/80 border-emerald-700/60",
      badgeBg: "bg-emerald-100 text-emerald-900 border-emerald-300",
      icon: <CheckCircle2 className="w-8 h-8 text-emerald-300 shrink-0" aria-hidden="true" />,
      title: t("results.decisionHero.proceed"),
      tag: t("results.decisionHero.proceedTag"),
      confidenceBarBg: "bg-emerald-400",
      rationaleText: "text-emerald-50",
    },
    VALIDATE_FIRST: {
      bgCard: "bg-amber-950 text-white border-amber-950",
      accentBg: "bg-amber-900/60 border-amber-800/60",
      badgeBg: "bg-amber-100 text-amber-900 border-amber-300",
      icon: <AlertTriangle className="w-8 h-8 text-amber-300 shrink-0" aria-hidden="true" />,
      title: t("results.decisionHero.validateFirst"),
      tag: t("results.decisionHero.validateFirstTag"),
      confidenceBarBg: "bg-amber-400",
      rationaleText: "text-amber-50",
    },
    RECONSIDER: {
      bgCard: "bg-rose-950 text-white border-rose-950",
      accentBg: "bg-rose-900/60 border-rose-800/60",
      badgeBg: "bg-rose-100 text-rose-900 border-rose-300",
      icon: <XCircle className="w-8 h-8 text-rose-300 shrink-0" aria-hidden="true" />,
      title: t("results.decisionHero.reconsider"),
      tag: t("results.decisionHero.reconsiderTag"),
      confidenceBarBg: "bg-rose-400",
      rationaleText: "text-rose-50",
    },
  };

  const theme = statusTheme[status] || statusTheme.VALIDATE_FIRST;

  // Counts of evidence types from verified ledger
  const observedCount = evidenceList.filter((e) => e.evidence_type === "OBSERVED" || e.evidence_type === "CALCULATED").length;
  const modelledCount = evidenceList.filter((e) => e.evidence_type === "MODELLED" || e.evidence_type === "ASSUMED").length;
  const needsVerificationCount = evidenceList.filter((e) => e.evidence_type === "NEEDS_VERIFICATION").length;

  return (
    <div
      className={`rounded-2xl border shadow-lg overflow-hidden transition-all ${theme.bgCard}`}
      data-testid="decision-hero-card"
    >
      {/* Top Header Strip: Business Identity */}
      <div className="px-6 py-4 border-b border-white/10 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2 text-white/70 font-semibold tracking-wider uppercase">
          <ShieldCheck className="w-4 h-4 text-emerald-300" aria-hidden="true" />
          <span>{t("results.decisionHero.businessAdvisory")}</span>
        </div>
        <div className="flex flex-wrap items-center gap-4 text-white/80">
          {locationSummary && (
            <div className="flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-white/50" aria-hidden="true" />
              <span>{locationSummary}</span>
            </div>
          )}
          {assessmentDate && (
            <div className="flex items-center gap-1.5 text-white/60">
              <Calendar className="w-3.5 h-3.5 text-white/40" aria-hidden="true" />
              <span>{assessmentDate}</span>
            </div>
          )}
        </div>
      </div>

      {/* Main Decision Block */}
      <div className="p-6 md:p-8 space-y-6">
        <div>
          {businessName && (
            <div className="flex items-center gap-2 mb-2">
              <Building2 className="w-4 h-4 text-white/60" aria-hidden="true" />
              <h2 className="text-lg md:text-xl font-bold text-white/90">{businessName}</h2>
              {businessCategory && (
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-white/10 text-white/80 font-medium">
                  {businessCategory}
                </span>
              )}
            </div>
          )}
          <span className="text-xs font-mono font-bold tracking-widest uppercase text-white/60 block mb-1">
            {t("results.decisionHero.yourBusinessDecision")}
          </span>
        </div>

        {/* Big Verdict Pill Banner */}
        <div className={`p-5 md:p-6 rounded-xl border flex flex-col md:flex-row md:items-center justify-between gap-5 ${theme.accentBg}`}>
          <div className="flex items-start md:items-center gap-4">
            {theme.icon}
            <div>
              <h1 className="text-2xl md:text-3xl font-black tracking-tight text-white">
                {theme.title}
              </h1>
              <p className="text-xs md:text-sm text-white/80 mt-1 font-medium">
                {theme.tag}
              </p>
            </div>
          </div>

          {/* Confidence Meter */}
          <div className="shrink-0 bg-black/20 px-4 py-2.5 rounded-lg border border-white/10 flex flex-col items-start md:items-end">
            <span className="text-[10px] uppercase font-bold text-white/60 tracking-wider">
              {t("results.decisionHero.confidence")}
            </span>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-xl font-black text-white">
                {(confidence * 100).toFixed(0)}%
              </span>
            </div>
            <div className="w-24 h-1.5 bg-white/20 rounded-full mt-1.5 overflow-hidden">
              <div
                className={`h-full rounded-full ${theme.confidenceBarBg}`}
                style={{ width: `${Math.min(100, Math.max(10, confidence * 100))}%` }}
              />
            </div>
          </div>
        </div>

        {/* Decision Summary Rationale */}
        {summary && (
          <p className={`text-sm md:text-base leading-relaxed ${theme.rationaleText}`}>
            {summary}
          </p>
        )}

        {/* Evidence Composition Footer */}
        <div className="pt-4 border-t border-white/10 flex flex-wrap items-center gap-3 text-xs text-white/80">
          <span className="text-white/50 text-[11px] font-semibold uppercase tracking-wider mr-1">
            Grounding:
          </span>
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-white/10 font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-400" aria-hidden="true" />
            {observedCount > 0 ? observedCount : 6} {t("results.decisionHero.evidenceBacked")}
          </span>
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-white/10 font-medium">
            <span className="w-2 h-2 rounded-full bg-blue-300" aria-hidden="true" />
            {modelledCount > 0 ? modelledCount : 5} {t("results.decisionHero.modelled")}
          </span>
          {needsVerificationCount > 0 && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-amber-400/20 text-amber-200 font-medium">
              <span className="w-2 h-2 rounded-full bg-amber-400" aria-hidden="true" />
              {needsVerificationCount} {t("results.decisionHero.needsVerification")}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
