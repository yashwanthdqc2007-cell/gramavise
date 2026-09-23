"use client";

import React from "react";
import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { useTranslation } from "@/lib/i18n";
import {
  HelpCircle,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Scale,
  FileCheck,
  Layers,
  ArrowRight,
  Sparkles,
} from "lucide-react";

export default function HelpPage() {
  const { t } = useTranslation();

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 sm:py-10 space-y-8">
      {/* Header */}
      <div className="border-b border-slate-800 pb-5">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-300 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/30 inline-flex items-center gap-1.5">
            <HelpCircle className="w-3.5 h-3.5" />
            Knowledge Base
          </span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          {t("help.title")}
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl leading-relaxed">
          {t("help.subtitle")}
        </p>
      </div>

      {/* 1. Advisory Decision Status Explanations */}
      <Card className="p-6 md:p-8 space-y-6 border-slate-800 bg-[#0A1A28]">
        <div className="flex items-center gap-2.5 border-b border-slate-800/80 pb-3">
          <ShieldCheck className="w-5 h-5 text-emerald-400" />
          <h2 className="text-lg font-black text-white">{t("help.decisionGuideTitle")}</h2>
        </div>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          {t("help.decisionGuideDesc")}
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Proceed */}
          <div className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-950/40 space-y-2.5">
            <div className="flex items-center gap-2 text-emerald-300 font-bold text-sm">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>PROCEED</span>
            </div>
            <p className="text-xs text-emerald-100/80 leading-relaxed">
              {t("help.proceedDesc")}
            </p>
          </div>

          {/* Validate First */}
          <div className="p-4 rounded-xl border border-amber-500/30 bg-amber-950/40 space-y-2.5">
            <div className="flex items-center gap-2 text-amber-300 font-bold text-sm">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <span>VALIDATE FIRST</span>
            </div>
            <p className="text-xs text-amber-100/80 leading-relaxed">
              {t("help.validateDesc")}
            </p>
          </div>

          {/* Reconsider */}
          <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-950/40 space-y-2.5">
            <div className="flex items-center gap-2 text-rose-300 font-bold text-sm">
              <XCircle className="w-4 h-4 text-rose-400" />
              <span>RECONSIDER</span>
            </div>
            <p className="text-xs text-rose-100/80 leading-relaxed">
              {t("help.reconsiderDesc")}
            </p>
          </div>
        </div>
      </Card>

      {/* 2. DSCR & Debt Safety */}
      <Card className="p-6 md:p-8 space-y-4 border-slate-800 bg-[#0A1A28]">
        <div className="flex items-center gap-2.5 border-b border-slate-800/80 pb-3">
          <Scale className="w-5 h-5 text-cyan-400" />
          <h2 className="text-lg font-black text-white">{t("help.dscrTitle")}</h2>
        </div>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          {t("help.dscrDesc")}
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
          <div className="p-4 rounded-xl bg-[#06131F] border border-slate-800 space-y-1.5">
            <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider">
              DSCR ≥ 1.50x (Healthy Cushion)
            </span>
            <p className="text-xs text-slate-400 leading-relaxed">
              Your business earns at least 50% more operating cash flow than required for monthly bank EMI payments.
            </p>
          </div>
          <div className="p-4 rounded-xl bg-[#06131F] border border-slate-800 space-y-1.5">
            <span className="text-[11px] font-bold text-amber-400 uppercase tracking-wider">
              DSCR &lt; 1.50x (High Sensitivity)
            </span>
            <p className="text-xs text-slate-400 leading-relaxed">
              A slight drop in daily customers or raw material price spike could leave insufficient funds for loan repayments.
            </p>
          </div>
        </div>
      </Card>

      {/* 3. Evidence Labels & Provenance */}
      <Card className="p-6 md:p-8 space-y-4 border-slate-800 bg-[#0A1A28]">
        <div className="flex items-center gap-2.5 border-b border-slate-800/80 pb-3">
          <Layers className="w-5 h-5 text-emerald-400" />
          <h2 className="text-lg font-black text-white">{t("help.evidenceTitle")}</h2>
        </div>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          {t("help.evidenceDesc")}
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-2 text-xs">
          <div className="p-3 bg-[#06131F] rounded-xl border border-emerald-500/30 space-y-1">
            <span className="font-bold text-emerald-300 block">OBSERVED</span>
            <p className="text-[11px] text-slate-400 leading-snug">Official public data from Census 2011, Agmarknet Mandis, or LGD registry.</p>
          </div>
          <div className="p-3 bg-[#06131F] rounded-xl border border-cyan-500/30 space-y-1">
            <span className="font-bold text-cyan-300 block">CALCULATED</span>
            <p className="text-[11px] text-slate-400 leading-snug">Exact deterministic financial arithmetic based on your inputs.</p>
          </div>
          <div className="p-3 bg-[#06131F] rounded-xl border border-blue-500/30 space-y-1">
            <span className="font-bold text-blue-300 block">MODELLED</span>
            <p className="text-[11px] text-slate-400 leading-snug">Catchment estimation formulas based on standard 5 km radius models.</p>
          </div>
          <div className="p-3 bg-[#06131F] rounded-xl border border-amber-500/30 space-y-1">
            <span className="font-bold text-amber-300 block">NEEDS VERIFICATION</span>
            <p className="text-[11px] text-slate-400 leading-snug">Requires personal on-ground inquiry before signing financial contracts.</p>
          </div>
        </div>
      </Card>

      {/* 4. How to Read the Feasibility Report */}
      <Card className="p-6 md:p-8 space-y-4 border-slate-800 bg-[#0A1A28]">
        <div className="flex items-center gap-2.5 border-b border-slate-800/80 pb-3">
          <FileCheck className="w-5 h-5 text-purple-400" />
          <h2 className="text-lg font-black text-white">{t("help.howToReadTitle")}</h2>
        </div>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          {t("help.howToReadDesc")}
        </p>

        <div className="space-y-2 pt-2 text-xs">
          <div className="flex items-start gap-3 p-3 bg-[#06131F] rounded-xl border border-slate-800">
            <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-300 flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">1</span>
            <div>
              <strong className="text-white">Overview:</strong> Check the decision summary, 6 core numbers, and high-priority flags in 30 seconds.
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-[#06131F] rounded-xl border border-slate-800">
            <span className="w-5 h-5 rounded-full bg-cyan-500/20 text-cyan-300 flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">2</span>
            <div>
              <strong className="text-white">Financials & Market:</strong> Inspect monthly cash flow, break-even customer volume, and local catchment competitors.
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-[#06131F] rounded-xl border border-slate-800">
            <span className="w-5 h-5 rounded-full bg-blue-500/20 text-blue-300 flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">3</span>
            <div>
              <strong className="text-white">Action Plan & Schemes:</strong> Complete document readiness steps and check matching government credit subsidies.
            </div>
          </div>
        </div>
      </Card>

      {/* Call to action */}
      <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4 bg-gradient-to-r from-emerald-950/60 to-slate-900 p-6 rounded-2xl border border-emerald-500/30">
        <div>
          <h3 className="text-base font-bold text-white">Ready to test your business idea?</h3>
          <p className="text-xs text-slate-400 mt-0.5">Start an advisory assessment to evaluate your setup, costs, and loan needs.</p>
        </div>
        <Link href="/onboarding" className="shrink-0">
          <Button className="font-bold flex items-center gap-2">
            <Sparkles className="w-4 h-4" />
            <span>{t("nav.newAdvisory")}</span>
            <ArrowRight className="w-4 h-4" />
          </Button>
        </Link>
      </div>
    </div>
  );
}
