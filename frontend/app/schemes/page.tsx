"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { fetchSchemes, SchemeInfo } from "@/services/api/schemes";
import { formatCurrencyINR } from "@/lib/utils";
import { useTranslation } from "@/lib/i18n";
import { Landmark, Sparkles, ExternalLink, Filter, CheckCircle2 } from "lucide-react";

/**
 * Static fallback shown before API responds.
 */
const sampleSchemes: SchemeInfo[] = [
  {
    scheme_code: "PMEGP",
    scheme_name: "Prime Minister's Employment Generation Programme",
    ministry_or_dept: "Ministry of MSME",
    max_loan_amount: 5000000,
    subsidy_percentage_general: 15,
    subsidy_percentage_special: 25,
    official_portal_url: "https://www.kviconline.gov.in/pmegpeportal",
  },
  {
    scheme_code: "PMMY",
    scheme_name: "Pradhan Mantri MUDRA Yojana (PMMY)",
    ministry_or_dept: "Ministry of Finance",
    max_loan_amount: 2000000,
    subsidy_percentage_general: 0,
    subsidy_percentage_special: 0,
    official_portal_url: "https://www.mudra.org.in",
  },
  {
    scheme_code: "PMFME",
    scheme_name: "PM Formalisation of Micro Food Processing Enterprises",
    ministry_or_dept: "Ministry of Food Processing Industries",
    max_loan_amount: null,
    subsidy_percentage_general: 35,
    subsidy_percentage_special: 35,
    official_portal_url: "https://pmfme.mofpi.gov.in",
  },
];

/** Format currency or return "N/A" for null/undefined/NaN. */
function formatLoan(amount: number | null | undefined, naLabel: string): string {
  if (amount === null || amount === undefined || (typeof amount === "number" && isNaN(amount))) {
    return naLabel;
  }
  return formatCurrencyINR(amount);
}

/** Format a subsidy percentage or return "N/A" for null/undefined/NaN. */
function formatSubsidy(pct: number | null | undefined, naLabel: string): string {
  if (pct === null || pct === undefined || (typeof pct === "number" && isNaN(pct))) {
    return naLabel;
  }
  return `${pct}%`;
}

type FilterType = "ALL" | "SUBSIDY" | "CREDIT";

export default function SchemesDirectoryPage() {
  const { t } = useTranslation();
  const naLabel = t("common.notApplicable");
  const [schemes, setSchemes] = useState<SchemeInfo[]>(sampleSchemes);
  const [activeFilter, setActiveFilter] = useState<FilterType>("ALL");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetchSchemes()
      .then((data) => {
        if (data && data.length > 0) setSchemes(data);
      })
      .catch((err) => console.log("Using static scheme list preview", err))
      .finally(() => setLoading(false));
  }, []);

  const filteredSchemes = schemes.filter((s) => {
    if (activeFilter === "SUBSIDY") {
      return (
        (s.subsidy_percentage_general && s.subsidy_percentage_general > 0) ||
        (s.subsidy_percentage_special && s.subsidy_percentage_special > 0)
      );
    }
    if (activeFilter === "CREDIT") {
      return (
        !s.subsidy_percentage_general ||
        s.subsidy_percentage_general === 0
      );
    }
    return true;
  });

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-cyan-950/80 border border-cyan-500/30 text-cyan-400 text-[11px] font-bold uppercase tracking-wider mb-2">
            <Landmark className="w-3.5 h-3.5" />
            <span>Government Financing</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            {t("schemesDirectory.title")}
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            {t("schemesDirectory.subtitle")}
          </p>
        </div>

        <Link href="/onboarding" className="shrink-0">
          <Button
            size="sm"
            className="bg-[#19D98B] hover:bg-[#16C784] text-[#06131F] font-bold flex items-center gap-1.5 min-h-[40px] px-4 rounded-xl shadow-xs"
          >
            <Sparkles className="w-4 h-4" />
            <span>{t("schemesDirectory.checkEligibility")}</span>
          </Button>
        </Link>
      </div>

      {/* Filter Tabs / Pills */}
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-xs font-semibold text-slate-400 flex items-center gap-1 mr-1">
          <Filter className="w-3.5 h-3.5 text-slate-500" /> Filter:
        </span>
        <button
          type="button"
          onClick={() => setActiveFilter("ALL")}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeFilter === "ALL"
              ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
              : "bg-slate-900/60 text-slate-400 hover:text-white border border-slate-800"
          }`}
        >
          All Schemes ({schemes.length})
        </button>
        <button
          type="button"
          onClick={() => setActiveFilter("SUBSIDY")}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeFilter === "SUBSIDY"
              ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
              : "bg-slate-900/60 text-slate-400 hover:text-white border border-slate-800"
          }`}
        >
          Subsidy Programs (PMEGP / PMFME)
        </button>
        <button
          type="button"
          onClick={() => setActiveFilter("CREDIT")}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeFilter === "CREDIT"
              ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/40"
              : "bg-slate-900/60 text-slate-400 hover:text-white border border-slate-800"
          }`}
        >
          Credit / Working Capital (MUDRA)
        </button>
      </div>

      {/* Schemes Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredSchemes.map((scheme) => (
          <Card
            key={scheme.scheme_code}
            className="flex flex-col justify-between p-6 rounded-2xl bg-[#071827] border border-slate-800 shadow-md hover:border-emerald-500/50 transition-all space-y-4"
          >
            <div className="space-y-3">
              <div className="flex justify-between items-start gap-2">
                <Badge variant="info">{scheme.scheme_code}</Badge>
                <details className="max-w-[62%] text-right text-[11px] text-slate-400 font-medium">
                  <summary className="cursor-pointer list-none truncate underline decoration-dotted underline-offset-2">
                    {scheme.ministry_or_dept}
                  </summary>
                  <p className="mt-1 text-left text-xs leading-relaxed text-slate-300 break-words">
                    {scheme.ministry_or_dept}
                  </p>
                </details>
              </div>
              <h2 className="font-bold text-base text-white leading-snug">
                {scheme.scheme_name}
              </h2>
              <div className="space-y-2 text-xs text-slate-300 bg-slate-950/70 p-3.5 rounded-xl border border-slate-800/80">
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">{t("schemesDirectory.maxLoan")}:</span>
                  <span className="font-mono font-bold text-white">
                    {formatLoan(scheme.max_loan_amount, naLabel)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">{t("schemesDirectory.subsidy")}:</span>
                  <span className="font-semibold text-emerald-300">
                    {formatSubsidy(scheme.subsidy_percentage_general, naLabel)}
                    {scheme.subsidy_percentage_special && scheme.subsidy_percentage_special !== scheme.subsidy_percentage_general
                      ? ` - ${formatSubsidy(scheme.subsidy_percentage_special, naLabel)}`
                      : ""}
                  </span>
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-800 flex items-center justify-between gap-2">
              {scheme.official_portal_url ? (
                <a
                  href={scheme.official_portal_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold inline-flex items-center gap-1 transition-colors"
                >
                  <span>{t("schemesDirectory.visitPortal")}</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              ) : (
                <span />
              )}
              <Link href="/onboarding">
                <button
                  type="button"
                  className="text-xs text-slate-300 hover:text-white font-semibold underline"
                >
                  Apply via GramaVise →
                </button>
              </Link>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
