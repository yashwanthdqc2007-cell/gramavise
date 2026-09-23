"use client";

import React from "react";
import { SWOTItem, EvidenceItem } from "@/lib/types";
import { SWOTItemCard } from "./SWOTItemCard";
import { useTranslation } from "@/lib/i18n";
import {
  TrendingUp,
  AlertTriangle,
  Sparkles,
  ShieldAlert,
  Inbox,
} from "lucide-react";

export type QuadrantType = "STRENGTH" | "WEAKNESS" | "OPPORTUNITY" | "THREAT";

interface SWOTQuadrantProps {
  type: QuadrantType;
  title: string;
  subtitle: string;
  items: SWOTItem[];
  evidenceLedger?: EvidenceItem[];
  onNavigateToEvidenceTab?: () => void;
}

export const SWOTQuadrant: React.FC<SWOTQuadrantProps> = ({
  type,
  title,
  subtitle,
  items = [],
  evidenceLedger = [],
  onNavigateToEvidenceTab,
}) => {
  const { t } = useTranslation();

  const getQuadrantConfig = () => {
    switch (type) {
      case "STRENGTH":
        return {
          icon: <TrendingUp className="w-4 h-4 text-emerald-400" aria-hidden="true" />,
          badgeBg: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
          cardBorder: "border-emerald-500/20",
          accentColor: "text-emerald-400",
          glow: "from-emerald-950/20 via-transparent to-transparent",
        };
      case "WEAKNESS":
        return {
          icon: <AlertTriangle className="w-4 h-4 text-amber-400" aria-hidden="true" />,
          badgeBg: "bg-amber-500/15 text-amber-300 border-amber-500/30",
          cardBorder: "border-amber-500/20",
          accentColor: "text-amber-400",
          glow: "from-amber-950/20 via-transparent to-transparent",
        };
      case "OPPORTUNITY":
        return {
          icon: <Sparkles className="w-4 h-4 text-cyan-400" aria-hidden="true" />,
          badgeBg: "bg-cyan-500/15 text-cyan-300 border-cyan-500/30",
          cardBorder: "border-cyan-500/20",
          accentColor: "text-cyan-400",
          glow: "from-cyan-950/20 via-transparent to-transparent",
        };
      case "THREAT":
        return {
          icon: <ShieldAlert className="w-4 h-4 text-rose-400" aria-hidden="true" />,
          badgeBg: "bg-rose-500/15 text-rose-300 border-rose-500/30",
          cardBorder: "border-rose-500/20",
          accentColor: "text-rose-400",
          glow: "from-rose-950/20 via-transparent to-transparent",
        };
    }
  };

  const config = getQuadrantConfig();

  return (
    <div
      className={`rounded-xl border ${config.cardBorder} bg-[#0A1D2B]/90 p-4 sm:p-5 flex flex-col justify-between space-y-4 shadow-sm relative overflow-hidden`}
      data-testid={`swot-quadrant-${type.toLowerCase()}`}
    >
      {/* Subtle quadrant ambient glow */}
      <div
        className={`absolute inset-0 bg-gradient-to-br ${config.glow} pointer-events-none opacity-40`}
        aria-hidden="true"
      />

      <div className="relative space-y-3">
        {/* Quadrant Header */}
        <div className="flex items-start justify-between gap-2 border-b border-slate-800/80 pb-3">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-[#0E2635] border border-slate-700/80 flex items-center justify-center shrink-0">
              {config.icon}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-white tracking-tight">
                  {title}
                </h3>
                <span
                  className={`text-[10px] font-mono font-bold px-1.5 py-0.2 rounded border ${config.badgeBg}`}
                >
                  {items.length}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-0.5">
                {subtitle}
              </p>
            </div>
          </div>
        </div>

        {/* Quadrant Items List */}
        {items.length === 0 ? (
          <div className="p-4 rounded-xl border border-dashed border-slate-800/90 bg-[#081722]/50 text-center space-y-1 my-2">
            <Inbox className="w-4 h-4 text-slate-600 mx-auto" aria-hidden="true" />
            <p className="text-xs text-slate-400 font-medium">
              {t("results.swot.emptyQuadrant")}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {items.map((item) => (
              <SWOTItemCard
                key={item.id}
                item={item}
                quadrantType={type}
                evidenceLedger={evidenceLedger}
                onNavigateToEvidenceTab={onNavigateToEvidenceTab}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
