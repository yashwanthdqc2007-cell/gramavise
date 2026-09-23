"use client";

import React from "react";
import { Badge } from "@/components/ui/Badge";
import { SchemeResult } from "@/lib/types";
import { formatCurrencyINR } from "@/lib/utils";
import { useTranslation } from "@/lib/i18n";
import { Landmark, ExternalLink, CheckCircle2, AlertTriangle, HelpCircle } from "lucide-react";

interface SchemeSectionProps {
  schemeResult: SchemeResult;
}

export const SchemeSection: React.FC<SchemeSectionProps> = ({ schemeResult }) => {
  const { t } = useTranslation();
  const schemes = schemeResult?.schemes || [];

  return (
    <section className="rounded-2xl border border-slate-700/80 bg-slate-900/80 p-6 md:p-8 shadow-lg shadow-slate-950/20 space-y-6">
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-700 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <Landmark className="w-5 h-5 text-emerald-700" />
            <h2 className="text-xl font-bold tracking-tight text-white">
              {t("results.governmentSchemes.title")}
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            {t("results.governmentSchemes.subtitle")}
          </p>
        </div>

        {schemeResult.total_potential_subsidy > 0 && (
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-bold self-start sm:self-auto">
            <span>{t("results.schemes.subsidyLabel")}:</span>
            <span className="text-emerald-200 font-black">
              {formatCurrencyINR(schemeResult.total_potential_subsidy)}
            </span>
          </div>
        )}
      </div>

      {schemes.length === 0 ? (
        <div className="p-8 bg-slate-800/60 rounded-xl border border-slate-700 text-center space-y-2">
          <HelpCircle className="w-8 h-8 text-stone-400 mx-auto" />
          <p className="text-sm font-semibold text-slate-200">
            {t("results.schemes.noSchemesMatched")}
          </p>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            The enterprise may still qualify for general micro-credit, Kisan Credit Card (KCC), or local Cooperative Society loans.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {schemes.map((scheme) => {
            const isEligible = scheme.eligibility_status === "ELIGIBLE";
            const isPartial = scheme.eligibility_status === "PARTIALLY_ELIGIBLE";

            return (
              <div
                key={scheme.scheme_code}
                className="rounded-xl border border-slate-700/80 bg-slate-800/60 p-5 space-y-4 hover:border-emerald-400/60 hover:bg-slate-800 transition-all flex flex-col justify-between"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h3 className="font-bold text-slate-100 text-sm leading-snug">
                        {scheme.scheme_name}
                      </h3>
                      <span className="text-[11px] text-slate-500 font-mono">
                        {scheme.scheme_code}
                      </span>
                    </div>
                    <Badge
                      variant={
                        isEligible
                          ? "success"
                          : isPartial
                          ? "warning"
                          : "neutral"
                      }
                    >
                      {scheme.eligibility_status}
                    </Badge>
                  </div>

                  {/* Financial Subsidy & Margin Matrix */}
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-xs bg-slate-900/70 p-3 rounded-lg border border-slate-700">
                    <div>
                      <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold block">
                        Subsidy
                      </span>
                      <span className="font-bold text-emerald-400 text-sm">
                        {formatCurrencyINR(scheme.subsidy_eligible_amount)}
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold block">
                        Your Margin
                      </span>
                      <span className="font-bold text-slate-200 text-sm">
                        {formatCurrencyINR(scheme.own_contribution_required)}
                      </span>
                    </div>
                    {scheme.max_bank_loan > 0 && (
                      <div className="col-span-2 sm:col-span-1">
                        <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold block">
                          Max Loan
                        </span>
                        <span className="font-bold text-cyan-300 text-sm">
                          {formatCurrencyINR(scheme.max_bank_loan)}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Why Matched */}
                  {scheme.reasons && scheme.reasons.length > 0 && (
                    <div className="space-y-1">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                        Why Matched:
                      </span>
                      <ul className="text-xs text-slate-300 space-y-1">
                        {scheme.reasons.map((reason, rIdx) => (
                          <li key={rIdx} className="flex items-start gap-1.5">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                            <span>{reason}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Conditions to Verify */}
                  {scheme.conditions_to_verify && scheme.conditions_to_verify.length > 0 && (
                    <div className="space-y-1 bg-amber-500/10 p-2.5 rounded-lg border border-amber-500/30">
                      <span className="text-[10px] font-bold text-amber-300 uppercase tracking-wider flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3 text-amber-400" />
                        To Verify Before Sanction:
                      </span>
                      <ul className="text-[11px] text-amber-200 space-y-0.5 pl-4 list-disc">
                        {scheme.conditions_to_verify.map((cond, cIdx) => (
                          <li key={cIdx}>{cond}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {scheme.portal_url && (
                  <div className="pt-2 border-t border-slate-700">
                    <a
                      href={scheme.portal_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-emerald-300 hover:text-emerald-200 font-semibold inline-flex items-center gap-1.5 transition-colors"
                    >
                      <span>Official Scheme Application Portal</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      <p className="text-[11px] text-slate-500 italic">
        * Government scheme terms and subsidies are informational benchmarks. Final sanction is subject to bank appraisal, documentary verification, and scheme quota availability.
      </p>
    </section>
  );
};
