"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  Compass,
  PlusCircle,
  Landmark,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Store,
  Layers,
  Sprout,
  BarChart3,
  Scale,
  History as HistoryIcon,
  ExternalLink,
  SlidersHorizontal,
  ChevronRight,
  TrendingUp,
  ShieldCheck,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useTranslation } from "@/lib/i18n";
import { loadHistory, HistoryEntry } from "@/lib/storage/historyStorage";
import { RecommendationStatus } from "@/lib/types";

export default function DashboardPage() {
  const { t } = useTranslation();
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const saved = loadHistory();
    setHistory(saved);
    setIsLoaded(true);
  }, []);

  const latest = history.length > 0 ? history[0] : null;

  const getStatusBadge = (status: RecommendationStatus) => {
    switch (status) {
      case "PROCEED":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/40 shadow-xs">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            {t("history.statusBadgeProceed")}
          </span>
        );
      case "VALIDATE_FIRST":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/15 text-amber-300 border border-amber-500/40 shadow-xs">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            {t("history.statusBadgeValidate")}
          </span>
        );
      case "RECONSIDER":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-500/15 text-rose-300 border border-rose-500/40 shadow-xs">
            <XCircle className="w-3.5 h-3.5 text-rose-400" />
            {t("history.statusBadgeReconsider")}
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-slate-800 text-slate-300 border border-slate-700">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="text-slate-100 min-h-screen relative selection:bg-emerald-500 selection:text-slate-950 overflow-x-hidden pb-20">
      {/* Background radial glow */}
      <div
        className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-6xl h-[450px] pointer-events-none -z-0"
        style={{
          background:
            "radial-gradient(ellipse 65% 45% at 50% -5%, rgba(25, 217, 139, 0.08), transparent 70%), radial-gradient(ellipse 40% 30% at 85% 15%, rgba(56, 189, 248, 0.05), transparent 70%)",
        }}
        aria-hidden="true"
      />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 sm:pt-8 relative z-10 space-y-8">
        {/* ============================================================ */}
        {/* STATE A: RETURNING USER WITH PRIOR ANALYSES                 */}
        {/* ============================================================ */}
        {isLoaded && latest ? (
          <div className="space-y-8 animate-in fade-in duration-300">
            {/* Workspace Welcome Bar */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-500/30 text-emerald-400 text-xs font-semibold mb-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span>{t("dashboard.welcomeBack")}</span>
                </div>
                <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                  Business Advisory Workspace
                </h1>
                <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
                  Review prior feasibility reports or evaluate a new rural enterprise concept.
                </p>
              </div>

              <Link href="/onboarding" className="shrink-0">
                <Button
                  size="lg"
                  className="bg-gradient-to-r from-[#19D98B] to-emerald-500 hover:from-[#16C784] hover:to-emerald-400 text-[#040F19] font-bold px-6 py-3 rounded-xl shadow-md shadow-emerald-500/20 text-xs sm:text-sm inline-flex items-center gap-2 border-0"
                >
                  <Sparkles className="w-4 h-4" />
                  <span>{t("dashboard.startAdvisory")}</span>
                </Button>
              </Link>
            </div>

            {/* Featured Hero: Most Recent Analysis */}
            <div className="relative rounded-2xl bg-[#071827] border border-emerald-500/30 p-6 sm:p-8 shadow-xl shadow-emerald-950/20 overflow-hidden">
              <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />
              
              <div className="relative z-10 space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-400 bg-emerald-950/90 border border-emerald-500/40 px-2.5 py-1 rounded-md">
                      {t("dashboard.latestAnalysis")}
                    </span>
                    <span className="text-xs text-slate-400">
                      {new Date(latest.created_at).toLocaleDateString(undefined, {
                        dateStyle: "medium",
                      })}
                    </span>
                  </div>
                  <div>{getStatusBadge(latest.recommendation_status)}</div>
                </div>

                <div className="space-y-2">
                  <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight">
                    {latest.business_name}
                  </h2>
                  <div className="flex items-center gap-3 text-xs sm:text-sm text-slate-300">
                    <span className="font-semibold text-emerald-400 bg-emerald-950/40 px-2.5 py-0.5 rounded border border-emerald-500/20">
                      {latest.business_category}
                    </span>
                    <span className="text-slate-500">•</span>
                    <span className="text-slate-400 font-mono text-xs">
                      ID: {latest.analysis_id.slice(0, 8)}...
                    </span>
                  </div>
                </div>

                {/* Quick Action Buttons for Latest */}
                <div className="flex flex-wrap items-center gap-3 pt-2">
                  <Link href={`/history/${encodeURIComponent(latest.analysis_id)}`}>
                    <Button
                      size="sm"
                      className="bg-[#19D98B] hover:bg-[#16C784] text-[#06131F] font-bold px-5 py-2.5 rounded-xl text-xs inline-flex items-center gap-2 shadow-sm"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                      <span>{t("dashboard.viewReport")}</span>
                    </Button>
                  </Link>
                  <Link href={`/history/${encodeURIComponent(latest.analysis_id)}#scenario-lab`}>
                    <Button
                      variant="outline"
                      size="sm"
                      className="border-slate-700 bg-slate-900/80 hover:bg-slate-800 text-slate-200 hover:text-white text-xs font-semibold px-4 py-2.5 rounded-xl inline-flex items-center gap-2"
                    >
                      <SlidersHorizontal className="w-3.5 h-3.5 text-emerald-400" />
                      <span>{t("dashboard.runScenarioLab")}</span>
                    </Button>
                  </Link>
                </div>
              </div>
            </div>

            {/* Grid: Quick Actions + Recent History List */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Quick Actions Column */}
              <div className="space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 px-1">
                  {t("dashboard.quickActions")}
                </h3>
                <div className="space-y-3">
                  <Link href="/onboarding" className="block group">
                    <div className="p-4 rounded-xl bg-[#071827] border border-slate-800 hover:border-emerald-500/40 transition-all hover:bg-[#0A2236] flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold">
                          <PlusCircle className="w-4 h-4" />
                        </div>
                        <div>
                          <div className="text-xs font-bold text-white group-hover:text-emerald-300 transition-colors">
                            {t("dashboard.startAdvisory")}
                          </div>
                          <div className="text-[11px] text-slate-400">
                            Check a new business concept
                          </div>
                        </div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-emerald-400 group-hover:translate-x-0.5 transition-all" />
                    </div>
                  </Link>

                  <Link href="/schemes" className="block group">
                    <div className="p-4 rounded-xl bg-[#071827] border border-slate-800 hover:border-emerald-500/40 transition-all hover:bg-[#0A2236] flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center font-bold">
                          <Landmark className="w-4 h-4" />
                        </div>
                        <div>
                          <div className="text-xs font-bold text-white group-hover:text-cyan-300 transition-colors">
                            {t("nav.schemesDirectory")}
                          </div>
                          <div className="text-[11px] text-slate-400">
                            PMEGP, MUDRA & PMFME
                          </div>
                        </div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-cyan-400 group-hover:translate-x-0.5 transition-all" />
                    </div>
                  </Link>

                  <Link href="/history" className="block group">
                    <div className="p-4 rounded-xl bg-[#071827] border border-slate-800 hover:border-emerald-500/40 transition-all hover:bg-[#0A2236] flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center font-bold">
                          <HistoryIcon className="w-4 h-4" />
                        </div>
                        <div>
                          <div className="text-xs font-bold text-white group-hover:text-indigo-300 transition-colors">
                            {t("dashboard.allReports")}
                          </div>
                          <div className="text-[11px] text-slate-400">
                            {history.length} saved assessments
                          </div>
                        </div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-indigo-400 group-hover:translate-x-0.5 transition-all" />
                    </div>
                  </Link>
                </div>
              </div>

              {/* Recent Analyses Column */}
              <div className="lg:col-span-2 space-y-4">
                <div className="flex items-center justify-between px-1">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    {t("dashboard.recentAnalyses")}
                  </h3>
                  <Link
                    href="/history"
                    className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 inline-flex items-center gap-1"
                  >
                    <span>View all ({history.length})</span>
                    <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>

                <div className="space-y-3">
                  {history.slice(0, 4).map((entry) => (
                    <Link
                      key={entry.analysis_id}
                      href={`/history/${encodeURIComponent(entry.analysis_id)}`}
                      className="block group"
                    >
                      <div className="p-4 rounded-xl bg-[#071827] border border-slate-800 hover:border-emerald-500/40 hover:bg-[#0A2236] transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                        <div className="space-y-1 min-w-0">
                          <div className="flex items-center gap-2.5">
                            <span className="text-sm font-bold text-white group-hover:text-emerald-300 transition-colors truncate">
                              {entry.business_name}
                            </span>
                            {getStatusBadge(entry.recommendation_status)}
                          </div>
                          <div className="flex items-center gap-2 text-xs text-slate-400">
                            <span className="text-emerald-400 font-medium">
                              {entry.business_category}
                            </span>
                            <span>•</span>
                            <span>
                              {new Date(entry.created_at).toLocaleDateString(undefined, {
                                dateStyle: "short",
                              })}
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 group-hover:text-emerald-400 shrink-0">
                          <span>Open Report</span>
                          <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* ============================================================ */
          /* STATE B: FIRST-TIME USER / INTRODUCTORY WORKSPACE           */
          /* ============================================================ */
          <div className="space-y-12 animate-in fade-in duration-300">
            {/* Hero Banner */}
            <div className="relative rounded-3xl bg-[#071827] border border-slate-800 p-8 sm:p-12 shadow-2xl overflow-hidden">
              <div className="max-w-2xl space-y-6">
                <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-950/80 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span>{t("landing.eyebrow")}</span>
                </div>

                <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-white tracking-tight leading-tight">
                  {t("landing.mainHeading")}
                </h1>

                <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-xl font-normal">
                  {t("landing.heroSubtitle")}
                </p>

                <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 pt-2">
                  <Link href="/onboarding">
                    <Button
                      size="lg"
                      className="w-full sm:w-auto bg-[#19D98B] hover:bg-[#16C784] text-[#06131F] font-bold px-8 py-3.5 rounded-xl shadow-lg shadow-emerald-500/20 text-sm inline-flex items-center justify-center gap-2 border-0"
                    >
                      <Sparkles className="w-4 h-4" />
                      <span>{t("landing.startAssessment")}</span>
                    </Button>
                  </Link>
                  <Link href="/schemes">
                    <Button
                      variant="outline"
                      size="lg"
                      className="w-full sm:w-auto border-slate-700 hover:border-slate-500 text-slate-200 hover:text-white bg-slate-900/60 font-semibold px-6 py-3.5 rounded-xl text-sm inline-flex items-center justify-center gap-2"
                    >
                      <span>{t("landing.exploreSchemes")}</span>
                    </Button>
                  </Link>
                </div>
              </div>
            </div>

            {/* 3 Core Analytical Pillars */}
            <div className="space-y-4">
              <div className="text-center sm:text-left">
                <h2 className="text-lg font-bold text-white tracking-tight">
                  How GramaVise Protects Rural Entrepreneurs
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Three deterministic layers of feasibility modeling before you borrow.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="p-6 rounded-2xl bg-[#071827] border border-slate-800 space-y-3 shadow-md hover:border-emerald-500/40 transition-colors">
                  <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold">
                    <Store className="w-5 h-5" />
                  </div>
                  <h3 className="text-sm font-bold text-white">
                    {t("landing.visualCard1Title")}
                  </h3>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Evaluates local village demographics, competitive density, and population catchments using official LGD and spatial models.
                  </p>
                </Card>

                <Card className="p-6 rounded-2xl bg-[#071827] border border-slate-800 space-y-3 shadow-md hover:border-emerald-500/40 transition-colors">
                  <div className="w-10 h-10 rounded-xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center font-bold">
                    <BarChart3 className="w-5 h-5" />
                  </div>
                  <h3 className="text-sm font-bold text-white">
                    {t("landing.visualCard2Title")}
                  </h3>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Calculates exact monthly break-even sales, net profit margins, and debt service coverage (DSCR) to prevent over-borrowing.
                  </p>
                </Card>

                <Card className="p-6 rounded-2xl bg-[#071827] border border-slate-800 space-y-3 shadow-md hover:border-emerald-500/40 transition-colors">
                  <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center font-bold">
                    <Landmark className="w-5 h-5" />
                  </div>
                  <h3 className="text-sm font-bold text-white">
                    {t("landing.visualCard3Title")}
                  </h3>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Recommends matching central and state credit schemes like PMEGP, MUDRA, and PMFME with applicable capital subsidies.
                  </p>
                </Card>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
