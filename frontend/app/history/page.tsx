"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { useTranslation } from "@/lib/i18n";
import { loadHistory, removeHistoryEntry, HistoryEntry } from "@/lib/storage/historyStorage";
import { RecommendationStatus } from "@/lib/types";
import {
  Trash2,
  ExternalLink,
  PlusCircle,
  History,
  SlidersHorizontal,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Sparkles,
} from "lucide-react";

export default function HistoryPage() {
  const { t } = useTranslation();
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [isLoaded, setIsLoaded] = useState(false);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  useEffect(() => {
    setEntries(loadHistory());
    setIsLoaded(true);
  }, []);

  const handleDelete = (analysisId: string) => {
    removeHistoryEntry(analysisId);
    setEntries(loadHistory());
    setDeleteConfirmId(null);
  };

  const getStatusBadge = (status: RecommendationStatus) => {
    switch (status) {
      case "PROCEED":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/40">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            {t("history.statusBadgeProceed")}
          </span>
        );
      case "VALIDATE_FIRST":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/15 text-amber-300 border border-amber-500/40">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            {t("history.statusBadgeValidate")}
          </span>
        );
      case "RECONSIDER":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-500/15 text-rose-300 border border-rose-500/40">
            <XCircle className="w-3.5 h-3.5 text-rose-400" />
            {t("history.statusBadgeReconsider")}
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-slate-800 text-slate-200 border border-slate-700">
            {status}
          </span>
        );
    }
  };

  const getBorderColorByStatus = (status: RecommendationStatus, isLatest: boolean) => {
    if (isLatest) {
      return "border-emerald-500/60 bg-[#071D2F]/80 shadow-lg shadow-emerald-950/30 ring-1 ring-emerald-500/20";
    }
    switch (status) {
      case "PROCEED":
        return "border-slate-800 hover:border-emerald-500/50 bg-[#071827]";
      case "VALIDATE_FIRST":
        return "border-slate-800 hover:border-amber-500/50 bg-[#071827]";
      case "RECONSIDER":
        return "border-slate-800 hover:border-rose-500/50 bg-[#071827]";
      default:
        return "border-slate-800 bg-[#071827]";
    }
  };

  if (!isLoaded) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="animate-spin w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-slate-400 text-sm">{t("common.loading")}</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6">
      {/* Header Section */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-950/80 border border-emerald-500/30 text-emerald-400 text-[11px] font-bold uppercase tracking-wider mb-2">
            <History className="w-3.5 h-3.5" />
            <span>Decision Archive</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            {t("history.title")}
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            {t("history.subtitle")}
          </p>
        </div>

        <Link href="/onboarding" className="shrink-0">
          <Button
            size="sm"
            className="bg-[#19D98B] hover:bg-[#16C784] text-[#06131F] font-bold flex items-center gap-1.5 min-h-[40px] px-4 rounded-xl shadow-xs"
          >
            <PlusCircle className="w-4 h-4" aria-hidden="true" />
            <span>{t("history.startNewAnalysis")}</span>
          </Button>
        </Link>
      </div>

      {/* Info Notice Banner */}
      <div className="p-3.5 bg-slate-900/70 border border-slate-800 rounded-xl text-xs text-slate-300 flex items-start gap-2.5 shadow-2xs">
        <span className="text-base shrink-0" aria-hidden="true">💡</span>
        <span>{t("history.historyLimitNotice")}</span>
      </div>

      {/* Empty State */}
      {entries.length === 0 && (
        <Card className="max-w-md mx-auto text-center space-y-4 p-8 my-12 rounded-2xl bg-[#071827] border border-slate-800 shadow-xl">
          <div className="w-14 h-14 bg-emerald-500/10 text-emerald-300 rounded-2xl flex items-center justify-center mx-auto text-2xl font-bold border border-emerald-500/20">
            <History className="w-7 h-7 text-emerald-400" />
          </div>
          <div className="space-y-1">
            <h2 className="text-lg font-bold text-white">{t("history.emptyTitle")}</h2>
            <p className="text-xs sm:text-sm text-slate-400">
              {t("history.emptySubtitle")}
            </p>
          </div>
          <Link href="/onboarding" className="block pt-2">
            <Button className="w-full bg-[#19D98B] hover:bg-[#16C784] text-[#06131F] font-bold min-h-[44px] rounded-xl">
              {t("history.startNewAnalysis")} →
            </Button>
          </Link>
        </Card>
      )}

      {/* History List */}
      {entries.length > 0 && (
        <div className="space-y-4" role="feed" aria-label={t("history.title")}>
          {entries.map((entry, index) => {
            const isLatest = index === 0;
            const createdDate = new Date(entry.created_at).toLocaleString(undefined, {
              dateStyle: "medium",
              timeStyle: "short",
            });

            return (
              <Card
                key={entry.analysis_id}
                className={`p-5 sm:p-6 rounded-2xl border transition-all duration-200 space-y-4 ${getBorderColorByStatus(
                  entry.recommendation_status,
                  isLatest
                )}`}
              >
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 min-w-0">
                  <div className="space-y-2 min-w-0 w-full sm:w-auto">
                    <div className="flex items-center gap-2.5 flex-wrap">
                      {isLatest && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-emerald-300 bg-emerald-950 border border-emerald-500/40 px-2 py-0.5 rounded">
                          <Sparkles className="w-3 h-3" />
                          Latest
                        </span>
                      )}
                      <h2 className="text-base sm:text-lg font-black text-white break-words">
                        {entry.business_name}
                      </h2>
                      {getStatusBadge(entry.recommendation_status)}
                    </div>

                    <div className="flex items-center gap-3 text-xs text-slate-400">
                      <span className="font-semibold text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-500/20">
                        {entry.business_category}
                      </span>
                      <span>•</span>
                      <span>
                        {t("history.createdOn")}: <strong className="text-slate-200">{createdDate}</strong>
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 w-full sm:w-auto pt-3 sm:pt-0 border-t sm:border-t-0 border-slate-800">
                    <Link
                      href={`/history/${encodeURIComponent(entry.analysis_id)}`}
                      className="flex-1 sm:flex-none"
                    >
                      <Button
                        size="sm"
                        className="w-full bg-[#19D98B] hover:bg-[#16C784] text-[#06131F] font-bold flex items-center justify-center gap-1.5 min-h-[38px] px-3.5 rounded-xl shadow-xs"
                      >
                        <ExternalLink className="w-3.5 h-3.5" aria-hidden="true" />
                        <span>{t("history.openAnalysis")}</span>
                      </Button>
                    </Link>

                    <Link
                      href={`/history/${encodeURIComponent(entry.analysis_id)}#scenario-lab`}
                      className="hidden sm:inline-block"
                    >
                      <Button
                        variant="secondary"
                        size="sm"
                        className="bg-slate-900 border-slate-700 text-slate-200 hover:text-white min-h-[38px] px-3 rounded-xl"
                        title="Open Scenario Lab"
                      >
                        <SlidersHorizontal className="w-3.5 h-3.5 text-emerald-400" />
                      </Button>
                    </Link>

                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => setDeleteConfirmId(entry.analysis_id)}
                      className="shrink-0 bg-slate-900/60 border-slate-800 text-slate-400 hover:text-rose-400 hover:border-rose-500/40 min-h-[38px] px-3 rounded-xl transition-colors"
                      aria-label={`${t("history.removeEntry")} ${entry.business_name}`}
                    >
                      <Trash2 className="w-3.5 h-3.5" aria-hidden="true" />
                    </Button>
                  </div>
                </div>

                {/* Delete Confirmation Banner */}
                {deleteConfirmId === entry.analysis_id && (
                  <div
                    role="alertdialog"
                    aria-labelledby={`delete-title-${entry.analysis_id}`}
                    aria-describedby={`delete-desc-${entry.analysis_id}`}
                    className="p-4 bg-rose-950/50 border border-rose-500/40 rounded-xl space-y-2 animate-in fade-in duration-150"
                  >
                    <p
                      id={`delete-title-${entry.analysis_id}`}
                      className="text-xs font-bold text-rose-300"
                    >
                      {t("history.removeConfirmTitle")}
                    </p>
                    <p
                      id={`delete-desc-${entry.analysis_id}`}
                      className="text-xs text-rose-200/80"
                    >
                      {t("history.removeConfirmDesc")}
                    </p>
                    <div className="flex gap-2 pt-1.5">
                      <Button
                        size="sm"
                        variant="danger"
                        onClick={() => handleDelete(entry.analysis_id)}
                        className="min-h-[36px] text-xs font-bold bg-rose-600 hover:bg-rose-500"
                      >
                        {t("history.removeConfirmYes")}
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => setDeleteConfirmId(null)}
                        className="min-h-[36px] text-xs border-slate-700 bg-slate-900 text-slate-200 hover:text-white"
                      >
                        {t("history.removeConfirmNo")}
                      </Button>
                    </div>
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
