"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { fetchSchemes, SchemeInfo } from "@/services/api/schemes";
import { formatCurrencyINR } from "@/lib/utils";
import { useTranslation } from "@/lib/i18n";

/**
 * Static fallback shown before API responds.
 * max_loan_amount / subsidy fields use null where a scheme does not have
 * a simple single value (e.g. PMMY has tiered loans; PMFME has no loan cap).
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

export default function SchemesDirectoryPage() {
  const { t } = useTranslation();
  const naLabel = t("common.notApplicable");
  const [schemes, setSchemes] = useState<SchemeInfo[]>(sampleSchemes);
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

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-300 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/30 inline-block mb-2">
            Government Financing
          </span>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            {t("schemesDirectory.title")}
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            {t("schemesDirectory.subtitle")}
          </p>
        </div>
        <Link href="/onboarding">
          <Button size="sm" className="font-bold min-h-[44px] sm:min-h-[36px]">
            {t("schemesDirectory.checkEligibility")} →
          </Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {schemes.map((scheme) => (
          <Card
            key={scheme.scheme_code}
            className="flex flex-col justify-between p-6 rounded-2xl border border-slate-800 shadow-sm hover:border-emerald-500/50 transition-all space-y-4"
          >
            <div>
              <div className="flex justify-between items-start mb-2.5">
                <Badge variant="info">{scheme.scheme_code}</Badge>
                <span className="text-xs text-slate-400 font-medium">{scheme.ministry_or_dept}</span>
              </div>
              <h2 className="font-bold text-base text-white mb-2 leading-snug">
                {scheme.scheme_name}
              </h2>
              <div className="space-y-1.5 text-xs text-slate-300 mb-4 bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                <div>
                  <strong className="text-slate-100">{t("schemesDirectory.maxLoan")}:</strong>{" "}
                  <span className="font-mono font-semibold">{formatLoan(scheme.max_loan_amount, naLabel)}</span>
                </div>
                <div>
                  <strong className="text-slate-100">{t("schemesDirectory.subsidy")}:</strong>{" "}
                  <span className="font-semibold text-emerald-300">{formatSubsidy(scheme.subsidy_percentage_general, naLabel)}</span> /{" "}
                  <span className="font-semibold text-emerald-300">{formatSubsidy(scheme.subsidy_percentage_special, naLabel)}</span>
                </div>
              </div>
            </div>
            {scheme.official_portal_url && (
              <a
                href={scheme.official_portal_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-emerald-300 hover:text-emerald-200 font-semibold underline pt-2.5 border-t border-slate-800 block transition-colors"
              >
                {t("schemesDirectory.visitPortal")} &rarr;
              </a>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
