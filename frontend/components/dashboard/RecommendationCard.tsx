"use client";

import React from "react";
import { AIExplanation } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";
import { Sparkles, CheckCircle, AlertCircle, ArrowUpRight, ShieldAlert } from "lucide-react";

interface RecommendationCardProps {
  explanation?: AIExplanation;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({ explanation }) => {
  const { t } = useTranslation();

  if (!explanation) {
    return (
      <section className="rounded-2xl border border-slate-700/80 bg-slate-900/70 p-6 space-y-2">
      <h3 className="text-sm font-bold text-slate-100">
          {t("results.aiExplanationSection.title")}
        </h3>
        <p className="text-xs text-slate-400 italic">
          Plain-language narrative is currently unavailable. All financial calculations and deterministic recommendations above remain complete, binding, and authoritative.
        </p>
      </section>
    );
  }

  return (
    <section className="rounded-2xl border border-slate-700/80 bg-slate-900/80 p-6 md:p-8 shadow-lg shadow-slate-950/20 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-stone-100 pb-4">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-emerald-700" />
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold tracking-tight text-white">
                {t("results.aiExplanationSection.title")}
              </h2>
              <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-300 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/30">
                {t("results.aiExplanationSection.aiAssistedBadge")}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Advisory commentary and strategic guidance based on your inputs.
            </p>
          </div>
        </div>

        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-800/70 border border-slate-700 text-slate-300 text-[11px] self-start sm:self-auto">
          <ShieldAlert className="w-3.5 h-3.5 text-slate-400" />
          <span>{t("results.aiExplanationSection.deterministicNote")}</span>
        </div>
      </div>

      {/* Summary Narrative */}
      <div className="text-sm md:text-base text-slate-200 leading-relaxed font-normal bg-slate-800/70 p-5 rounded-xl border border-slate-700 shadow-2xs">
        {explanation.summary}
      </div>

      {/* 3-Column Editorial Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Strengths */}
        {explanation.strengths && explanation.strengths.length > 0 && (
          <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 space-y-2">
            <h3 className="text-xs font-bold text-emerald-300 uppercase tracking-wider flex items-center gap-1.5">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-700" />
              <span>{t("results.aiExplanationSection.strengthsTitle")}</span>
            </h3>
            <ul className="space-y-1.5 text-xs text-slate-300">
              {explanation.strengths.map((item, idx) => (
                <li key={idx} className="leading-snug flex items-start gap-1.5">
                  <span className="text-emerald-600 mt-0.5">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Cautions */}
        {explanation.cautions_and_risks && explanation.cautions_and_risks.length > 0 && (
          <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 space-y-2">
            <h3 className="text-xs font-bold text-amber-300 uppercase tracking-wider flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5 text-amber-700" />
              <span>{t("results.aiExplanationSection.cautionsTitle")}</span>
            </h3>
            <ul className="space-y-1.5 text-xs text-slate-300">
              {explanation.cautions_and_risks.map((item, idx) => (
                <li key={idx} className="leading-snug flex items-start gap-1.5">
                  <span className="text-amber-600 mt-0.5">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Actionable Next Steps */}
        {explanation.actionable_next_steps && explanation.actionable_next_steps.length > 0 && (
          <div className="rounded-xl border border-slate-700/80 bg-slate-800/60 p-4 space-y-2">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
              <ArrowUpRight className="w-3.5 h-3.5 text-slate-700" />
              <span>Suggested Ground Steps</span>
            </h3>
            <ul className="space-y-1.5 text-xs text-slate-300">
              {explanation.actionable_next_steps.map((step, idx) => (
                <li key={idx} className="leading-snug flex items-start gap-1.5">
                  <span className="text-slate-500 mt-0.5">•</span>
                  <span>{step}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {explanation.disclaimer && (
        <p className="text-[11px] text-slate-500 italic pt-2 border-t border-slate-700">
          * {explanation.disclaimer}
        </p>
      )}
    </section>
  );
};
