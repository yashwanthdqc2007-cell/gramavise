"use client";

import React from "react";
import Link from "next/link";
import {
  Compass,
  Calculator,
  Landmark,
  ArrowRight,
  TrendingUp,
  ShieldCheck,
  Sparkles,
  SlidersHorizontal,
  CheckCircle2,
  Store,
  Layers,
  Sprout,
  Activity,
  BarChart3,
  Scale,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { useTranslation } from "@/lib/i18n";

export default function HomePage() {
  const { t } = useTranslation();

  return (
    <div className="bg-[#06131F] text-slate-100 min-h-screen relative selection:bg-emerald-500 selection:text-slate-950 overflow-x-hidden space-y-20 pb-24">
      {/* Ambient background depth glows */}
      <div
        className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-[600px] pointer-events-none -z-0"
        style={{
          background:
            "radial-gradient(ellipse 70% 40% at 50% -10%, rgba(25, 217, 139, 0.09), transparent 70%), radial-gradient(ellipse 40% 30% at 85% 15%, rgba(56, 189, 248, 0.06), transparent 70%)",
        }}
        aria-hidden="true"
      />

      {/* 1. HERO SECTION */}
      <section className="pt-10 sm:pt-16 lg:pt-20 pb-4 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
          {/* Left: Decision-Focused Headline & Value Proposition */}
          <div className="lg:col-span-7 space-y-6 text-left">
            {/* Eyebrow badge */}
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-900/90 border border-emerald-500/30 text-emerald-400 text-xs font-semibold tracking-wide shadow-xs backdrop-blur-md">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" aria-hidden="true" />
              <span>{t("landing.eyebrow")}</span>
            </div>

            {/* Main Title */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-white tracking-tight leading-[1.12]">
              {t("landing.mainHeading")}
            </h1>

            {/* Supporting Copy */}
            <p className="text-base sm:text-lg text-slate-300 leading-relaxed max-w-xl font-normal">
              {t("landing.heroSubtitle")}
            </p>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 pt-2">
              <Link href="/onboarding" className="w-full sm:w-auto">
                <Button
                  size="lg"
                  className="w-full sm:w-auto bg-[#19D98B] hover:bg-[#16C784] text-slate-950 font-bold px-8 py-4 rounded-xl shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/30 transition-all text-base inline-flex items-center justify-center gap-2 border-0"
                >
                  <span>{t("landing.startAssessment")}</span>
                </Button>
              </Link>
              <Link href="/schemes" className="w-full sm:w-auto">
                <Button
                  variant="outline"
                  size="lg"
                  className="w-full sm:w-auto border-slate-700 hover:border-slate-500 text-slate-200 hover:text-white bg-slate-900/60 hover:bg-slate-800/80 font-semibold px-6 py-4 rounded-xl transition-all text-base inline-flex items-center justify-center gap-2 backdrop-blur-sm"
                >
                  <span>{t("landing.exploreSchemes")}</span>
                </Button>
              </Link>
            </div>
          </div>

          {/* Right: Product Visualization (Advisory Architecture Blueprint) */}
          <div className="lg:col-span-5 flex justify-center lg:justify-end">
            <div className="relative w-full max-w-md">
              {/* Layered background blur glow */}
              <div className="absolute inset-0 bg-gradient-to-tr from-emerald-500/10 via-cyan-500/5 to-slate-800/40 rounded-3xl blur-2xl -z-10 transform scale-95" />

              {/* Central Advisory Preview Card */}
              <div className="bg-[#071827]/95 rounded-3xl border border-slate-800/90 shadow-2xl p-6 sm:p-7 space-y-4 relative overflow-hidden backdrop-blur-xl before:absolute before:inset-x-0 before:top-0 before:h-[1px] before:bg-gradient-to-r before:from-transparent before:via-emerald-400/60 before:to-transparent">
                {/* Window Header */}
                <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 text-[11px] text-slate-400">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-slate-700" />
                    <span className="w-2.5 h-2.5 rounded-full bg-slate-700" />
                    <span className="w-2.5 h-2.5 rounded-full bg-slate-700" />
                    <span className="ml-2 font-mono text-[10px] text-slate-500 uppercase tracking-wider">
                      Advisory Blueprint
                    </span>
                  </div>
                  <span className="inline-flex items-center gap-1 text-[10px] text-emerald-400 font-semibold bg-emerald-950/60 border border-emerald-800/60 px-2 py-0.5 rounded-full">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                    Deterministic Engine
                  </span>
                </div>

                {/* Stage 1: Business Concept Input */}
                <div className="p-3.5 bg-[#092237] rounded-2xl border border-slate-700/60 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                      <Store className="w-4 h-4" aria-hidden="true" />
                    </div>
                    <div>
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                        Input Stage
                      </span>
                      <span className="text-xs sm:text-sm font-bold text-white">
                        {t("landing.visualIdea")}
                      </span>
                    </div>
                  </div>
                  <span className="text-[10px] bg-slate-800/90 px-2 py-0.5 rounded-md border border-slate-700 text-slate-300 font-medium">
                    Ground Reality
                  </span>
                </div>

                {/* Flow Connector */}
                <div className="flex justify-center -my-1.5" aria-hidden="true">
                  <div className="w-5 h-5 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400 text-[10px]">
                    ↓
                  </div>
                </div>

                {/* Stage 2: 4-Pillar Evaluation Matrix */}
                <div className="grid grid-cols-2 gap-2 text-left">
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-cyan-800/40 space-y-1">
                    <div className="flex items-center justify-between">
                      <Compass className="w-3.5 h-3.5 text-cyan-400" aria-hidden="true" />
                      <span className="text-[9px] font-semibold text-cyan-400 bg-cyan-950/80 px-1.5 py-0.2 rounded border border-cyan-800/50 uppercase">
                        Evidence
                      </span>
                    </div>
                    <span className="text-xs font-bold text-white block">
                      {t("landing.visualMarket")}
                    </span>
                    <span className="text-[10px] text-slate-400 block truncate">
                      {t("landing.visualCard1Title")}
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-900/80 border border-emerald-800/40 space-y-1">
                    <div className="flex items-center justify-between">
                      <Calculator className="w-3.5 h-3.5 text-emerald-400" aria-hidden="true" />
                      <span className="text-[9px] font-semibold text-emerald-400 bg-emerald-950/80 px-1.5 py-0.2 rounded border border-emerald-800/50 uppercase">
                        Formulas
                      </span>
                    </div>
                    <span className="text-xs font-bold text-white block">
                      {t("landing.visualMoney")}
                    </span>
                    <span className="text-[10px] text-slate-400 block truncate">
                      {t("landing.visualCard2Title")}
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-900/80 border border-amber-800/40 space-y-1">
                    <div className="flex items-center justify-between">
                      <Landmark className="w-3.5 h-3.5 text-amber-400" aria-hidden="true" />
                      <span className="text-[9px] font-semibold text-amber-400 bg-amber-950/80 px-1.5 py-0.2 rounded border border-amber-800/50 uppercase">
                        Subsidies
                      </span>
                    </div>
                    <span className="text-xs font-bold text-white block">
                      Schemes
                    </span>
                    <span className="text-[10px] text-slate-400 block truncate">
                      Margin Outlay
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-900/80 border border-purple-800/40 space-y-1">
                    <div className="flex items-center justify-between">
                      <ShieldCheck className="w-3.5 h-3.5 text-purple-400" aria-hidden="true" />
                      <span className="text-[9px] font-semibold text-purple-400 bg-purple-950/80 px-1.5 py-0.2 rounded border border-purple-800/50 uppercase">
                        Stress-Test
                      </span>
                    </div>
                    <span className="text-xs font-bold text-white block">
                      {t("landing.visualRisk")}
                    </span>
                    <span className="text-[10px] text-slate-400 block truncate">
                      {t("landing.visualCard3Title")}
                    </span>
                  </div>
                </div>

                {/* Flow Connector */}
                <div className="flex justify-center -my-1.5" aria-hidden="true">
                  <div className="w-5 h-5 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400 text-[10px]">
                    ↓
                  </div>
                </div>

                {/* Stage 3: Informed Verdict Output */}
                <div className="p-4 bg-gradient-to-r from-emerald-950/90 via-emerald-900/80 to-teal-950/90 border border-emerald-500/50 rounded-2xl flex items-center justify-between shadow-lg shadow-emerald-950/50">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center text-emerald-400">
                      <CheckCircle2 className="w-5 h-5" aria-hidden="true" />
                    </div>
                    <div>
                      <span className="text-[10px] text-emerald-300 uppercase tracking-wider font-bold block">
                        Output Decision
                      </span>
                      <span className="text-xs sm:text-sm font-black text-white">
                        {t("landing.visualDecision")}
                      </span>
                    </div>
                  </div>
                  <span className="text-[10px] bg-emerald-500 text-slate-950 font-extrabold px-2.5 py-1 rounded-md shadow-2xs">
                    Evidence-Backed
                  </span>
                </div>

                {/* Micro-metrics summary footer */}
                <div className="pt-2 border-t border-slate-800/80 grid grid-cols-3 gap-1 text-[10px] text-center text-slate-400">
                  <span className="truncate">✓ Local Demand</span>
                  <span className="truncate">✓ Cash Flow Math</span>
                  <span className="truncate">✓ Debt Safety</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. COMPACT TRUST STRIP */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="bg-[#07192A]/85 border border-slate-800/90 rounded-2xl py-4 px-6 shadow-xl backdrop-blur-md">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 divide-y md:divide-y-0 md:divide-x divide-slate-800">
            <div className="flex items-center justify-center md:justify-start gap-3 py-2 md:py-0 md:px-4">
              <div className="w-9 h-9 rounded-xl bg-cyan-950/80 text-cyan-400 border border-cyan-800/50 flex items-center justify-center shrink-0">
                <Compass className="w-4 h-4" aria-hidden="true" />
              </div>
              <div>
                <span className="text-xs text-slate-400 block font-medium">Hyper-Local</span>
                <span className="text-sm font-bold text-white">
                  {t("landing.trust1")}
                </span>
              </div>
            </div>

            <div className="flex items-center justify-center md:justify-start gap-3 py-2 md:py-0 md:px-6">
              <div className="w-9 h-9 rounded-xl bg-emerald-950/80 text-emerald-400 border border-emerald-800/50 flex items-center justify-center shrink-0">
                <Calculator className="w-4 h-4" aria-hidden="true" />
              </div>
              <div>
                <span className="text-xs text-slate-400 block font-medium">Transparent</span>
                <span className="text-sm font-bold text-white">
                  {t("landing.trust2")}
                </span>
              </div>
            </div>

            <div className="flex items-center justify-center md:justify-start gap-3 py-2 md:py-0 md:px-6">
              <div className="w-9 h-9 rounded-xl bg-amber-950/80 text-amber-400 border border-amber-800/50 flex items-center justify-center shrink-0">
                <Landmark className="w-4 h-4" aria-hidden="true" />
              </div>
              <div>
                <span className="text-xs text-slate-400 block font-medium">Official Subsidies</span>
                <span className="text-sm font-bold text-white">
                  {t("landing.trust3")}
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3. CORE THREE VALUE CARDS ("Everything you need before you borrow") */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8 relative z-10">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <span className="text-xs font-bold uppercase tracking-widest text-emerald-400">
            Advisory Pillars
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            {t("landing.valueSectionTitle")}
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          {/* Card 1: Know your market */}
          <div className="p-7 bg-[#071827]/90 rounded-3xl border border-slate-800/80 hover:border-emerald-500/40 hover:bg-[#081F33] transition-all group relative overflow-hidden shadow-lg space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-cyan-950/80 text-cyan-400 border border-cyan-800/50 flex items-center justify-center shadow-inner">
              <Compass className="w-6 h-6" aria-hidden="true" />
            </div>
            <h3 className="text-xl font-bold text-white">
              {t("landing.valueCard1Title")}
            </h3>
            <p className="text-sm text-slate-400 leading-relaxed font-normal">
              {t("landing.valueCard1Desc")}
            </p>
            <div className="pt-1">
              <span className="text-xs font-semibold text-emerald-400 group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">
                Explore local ground evidence →
              </span>
            </div>
          </div>

          {/* Card 2: Know your numbers */}
          <div className="p-7 bg-[#071827]/90 rounded-3xl border border-slate-800/80 hover:border-emerald-500/40 hover:bg-[#081F33] transition-all group relative overflow-hidden shadow-lg space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-emerald-950/80 text-emerald-400 border border-emerald-800/50 flex items-center justify-center shadow-inner">
              <Calculator className="w-6 h-6" aria-hidden="true" />
            </div>
            <h3 className="text-xl font-bold text-white">
              {t("landing.valueCard2Title")}
            </h3>
            <p className="text-sm text-slate-400 leading-relaxed font-normal">
              {t("landing.valueCard2Desc")}
            </p>
            <div className="pt-1">
              <span className="text-xs font-semibold text-emerald-400 group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">
                Calculate break-even units →
              </span>
            </div>
          </div>

          {/* Card 3: Know your options */}
          <div className="p-7 bg-[#071827]/90 rounded-3xl border border-slate-800/80 hover:border-emerald-500/40 hover:bg-[#081F33] transition-all group relative overflow-hidden shadow-lg space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-amber-950/80 text-amber-400 border border-amber-800/50 flex items-center justify-center shadow-inner">
              <Landmark className="w-6 h-6" aria-hidden="true" />
            </div>
            <h3 className="text-xl font-bold text-white">
              {t("landing.valueCard3Title")}
            </h3>
            <p className="text-sm text-slate-400 leading-relaxed font-normal">
              {t("landing.valueCard3Desc")}
            </p>
            <div className="pt-1">
              <span className="text-xs font-semibold text-emerald-400 group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">
                View statutory subsidies →
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* 4. DECISION JOURNEY (5 Steps) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10 relative z-10">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <span className="text-xs font-bold uppercase tracking-widest text-emerald-400">
            Advisory Sequence
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            {t("landing.journeyTitle")}
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 relative">
          {/* Step 1 */}
          <div className="p-5 bg-[#071827]/90 rounded-2xl border border-slate-800/80 shadow-md space-y-3 hover:border-slate-700 transition-all">
            <div className="w-8 h-8 rounded-xl bg-amber-950/80 text-amber-400 border border-amber-800/50 flex items-center justify-center text-xs font-mono font-black">
              01
            </div>
            <h3 className="font-bold text-white text-sm">{t("landing.journeyStep1")}</h3>
            <p className="text-xs text-slate-400 font-normal leading-relaxed">
              {t("landing.journeyStep1Desc")}
            </p>
          </div>

          {/* Step 2 */}
          <div className="p-5 bg-[#071827]/90 rounded-2xl border border-slate-800/80 shadow-md space-y-3 hover:border-slate-700 transition-all">
            <div className="w-8 h-8 rounded-xl bg-cyan-950/80 text-cyan-400 border border-cyan-800/50 flex items-center justify-center text-xs font-mono font-black">
              02
            </div>
            <h3 className="font-bold text-white text-sm">{t("landing.journeyStep2")}</h3>
            <p className="text-xs text-slate-400 font-normal leading-relaxed">
              {t("landing.journeyStep2Desc")}
            </p>
          </div>

          {/* Step 3 */}
          <div className="p-5 bg-[#071827]/90 rounded-2xl border border-slate-800/80 shadow-md space-y-3 hover:border-slate-700 transition-all">
            <div className="w-8 h-8 rounded-xl bg-emerald-950/80 text-emerald-400 border border-emerald-800/50 flex items-center justify-center text-xs font-mono font-black">
              03
            </div>
            <h3 className="font-bold text-white text-sm">{t("landing.journeyStep3")}</h3>
            <p className="text-xs text-slate-400 font-normal leading-relaxed">
              {t("landing.journeyStep3Desc")}
            </p>
          </div>

          {/* Step 4 */}
          <div className="p-5 bg-[#071827]/90 rounded-2xl border border-slate-800/80 shadow-md space-y-3 hover:border-slate-700 transition-all">
            <div className="w-8 h-8 rounded-xl bg-purple-950/80 text-purple-400 border border-purple-800/50 flex items-center justify-center text-xs font-mono font-black">
              04
            </div>
            <h3 className="font-bold text-white text-sm">{t("landing.journeyStep4")}</h3>
            <p className="text-xs text-slate-400 font-normal leading-relaxed">
              {t("landing.journeyStep4Desc")}
            </p>
          </div>

          {/* Step 5 */}
          <div className="p-5 bg-gradient-to-br from-emerald-950 via-emerald-900 to-teal-950 rounded-2xl border border-emerald-500/50 shadow-lg shadow-emerald-950/50 space-y-3">
            <div className="w-8 h-8 rounded-xl bg-emerald-400 text-slate-950 flex items-center justify-center text-xs font-mono font-black">
              05
            </div>
            <h3 className="font-bold text-white text-sm">{t("landing.journeyStep5")}</h3>
            <p className="text-xs text-emerald-200 font-normal leading-relaxed">
              {t("landing.journeyStep5Desc")}
            </p>
          </div>
        </div>
      </section>

      {/* 5. SCENARIO LAB SIGNATURE TEASER */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="rounded-3xl bg-gradient-to-br from-[#081F33] via-[#071A29] to-[#040D16] border border-slate-700/80 shadow-2xl p-8 sm:p-10 lg:p-12 relative overflow-hidden">
          {/* Subtle radial glow in corner */}
          <div
            className="absolute top-0 right-0 w-96 h-96 pointer-events-none -z-0"
            style={{
              background: "radial-gradient(circle, rgba(25, 217, 139, 0.12) 0%, transparent 70%)",
            }}
            aria-hidden="true"
          />

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center relative z-10">
            {/* Left Copy & CTA */}
            <div className="lg:col-span-7 space-y-4 text-left">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-950/80 border border-emerald-500/30 text-emerald-400 text-xs font-bold uppercase tracking-wider">
                <SlidersHorizontal className="w-3.5 h-3.5 text-emerald-400" aria-hidden="true" />
                <span>Scenario Lab &bull; Downside Stress-Testing</span>
              </div>
              <h2 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-white tracking-tight">
                {t("landing.scenarioTitle")}
              </h2>
              <p className="text-base text-slate-300 max-w-2xl leading-relaxed">
                {t("landing.scenarioDesc")}
              </p>
              <div className="pt-2">
                <Link href="/onboarding">
                  <Button className="bg-[#19D98B] hover:bg-[#16C784] text-slate-950 font-bold px-7 py-3.5 rounded-xl transition-all inline-flex items-center gap-2 border-0 shadow-lg shadow-emerald-500/20">
                    <span>{t("landing.scenarioCta")}</span>
                  </Button>
                </Link>
              </div>
            </div>

            {/* Right Abstract Simulation Preview Panel */}
            <div className="lg:col-span-5">
              <div className="bg-[#05111B]/95 border border-slate-800 rounded-2xl p-5 space-y-3.5 shadow-xl">
                <div className="flex items-center justify-between pb-2 border-b border-slate-800 text-[11px]">
                  <span className="font-bold text-white flex items-center gap-1.5">
                    <Activity className="w-3.5 h-3.5 text-emerald-400" />
                    Unit Economic Simulation
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono uppercase">
                    Non-Destructive
                  </span>
                </div>

                {/* Simulation 1: Demand Drop */}
                <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs space-y-1">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-slate-300">Stress: Customer Footfall Drop (-20%)</span>
                    <span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/80 px-1.5 py-0.2 rounded border border-emerald-800/50">
                      SAFE (1.9x DSCR)
                    </span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-emerald-400 h-full rounded-full w-3/4" />
                  </div>
                </div>

                {/* Simulation 2: Input Cost Spikes */}
                <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs space-y-1">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-slate-300">Stress: Wholesale Price Spike (+15%)</span>
                    <span className="text-[10px] font-bold text-cyan-400 bg-cyan-950/80 px-1.5 py-0.2 rounded border border-cyan-800/50">
                      MARGIN STABLE
                    </span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-cyan-400 h-full rounded-full w-2/3" />
                  </div>
                </div>

                {/* Simulation 3: Extended Tenure */}
                <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs space-y-1">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-slate-300">Adjustment: Loan Tenure Extension (36m)</span>
                    <span className="text-[10px] font-bold text-amber-400 bg-amber-950/80 px-1.5 py-0.2 rounded border border-amber-800/50">
                      LOWER EMI
                    </span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-amber-400 h-full rounded-full w-1/2" />
                  </div>
                </div>

                <div className="text-[10px] text-slate-500 italic pt-1">
                  * Exploratory sensitivity methodology for grassroots enterprise risk analysis.
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 6. FINAL DECISION CALL TO ACTION */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="bg-gradient-to-b from-[#081F33] to-[#06131F] border border-emerald-500/30 rounded-3xl p-8 sm:p-12 text-center space-y-6 shadow-2xl relative overflow-hidden">
          {/* Subtle radial emerald background glow */}
          <div
            className="absolute inset-0 pointer-events-none -z-0"
            style={{
              background: "radial-gradient(circle at 50% 50%, rgba(25, 217, 139, 0.12), transparent 70%)",
            }}
            aria-hidden="true"
          />

          <div className="max-w-2xl mx-auto space-y-4 relative z-10">
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-black text-white tracking-tight">
              {t("landing.finalCtaTitle")}
            </h2>
            <p className="text-slate-300 max-w-xl mx-auto text-base leading-relaxed">
              {t("landing.finalCtaDesc")}
            </p>
            <div className="pt-2">
              <Link href="/onboarding">
                <Button
                  size="lg"
                  className="bg-[#19D98B] hover:bg-[#16C784] text-slate-950 font-bold px-10 py-4 rounded-xl shadow-xl shadow-emerald-500/20 hover:shadow-emerald-500/30 transition-all text-base inline-flex items-center justify-center gap-2 border-0"
                >
                  <span>{t("landing.finalCtaButton")}</span>
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
