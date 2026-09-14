"use client";

import React, { useState } from "react";
import { EvidenceItem } from "@/lib/types";
import { EvidenceBadge } from "@/components/evidence/EvidenceBadge";
import { useTranslation } from "@/lib/i18n";
import { ChevronDown, ChevronUp, FileCode2, ExternalLink, Filter } from "lucide-react";

interface EvidenceDrawerProps {
  evidenceList: EvidenceItem[];
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({ evidenceList = [] }) => {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [filterType, setFilterType] = useState<string>("ALL");

  const filteredList = evidenceList.filter((item) => {
    if (filterType === "ALL") return true;
    return item.evidence_type.toUpperCase() === filterType.toUpperCase();
  });

  return (
    <section className="rounded-2xl border border-slate-700/80 bg-slate-900/70 p-6 md:p-8 shadow-lg shadow-slate-950/20">
      <div
        className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 cursor-pointer select-none"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-start sm:items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0">
            <FileCode2 className="w-5 h-5 text-stone-600" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-white">
                {t("results.auditTrail.title")}
              </h3>
              <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                {evidenceList.length} indicators
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              {t("results.auditTrail.subtitle")}
            </p>
          </div>
        </div>

        <button
          type="button"
          className="text-xs font-semibold text-slate-300 hover:text-white inline-flex items-center gap-1.5 self-start sm:self-auto px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 shadow-2xs transition-all"
        >
          <span>{isOpen ? t("results.auditTrail.hideProvenance") : t("results.auditTrail.viewProvenance")}</span>
          {isOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>

      {isOpen && (
        <div className="mt-6 pt-5 border-t border-slate-700 space-y-4">
          {/* Provenance Filter Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-800/70 p-3 rounded-xl border border-slate-700">
            <div className="flex items-center gap-1.5 text-xs text-stone-500">
              <Filter className="w-3.5 h-3.5 text-stone-400" />
              <span className="font-semibold">Filter:</span>
            </div>
            <div className="flex flex-wrap gap-1.5 text-xs">
              {["ALL", "OBSERVED", "CALCULATED", "ASSUMED", "MOCK"].map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setFilterType(type);
                  }}
                  className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors ${
                    filterType === type
                      ? "bg-slate-900 text-white font-semibold shadow-2xs"
                      : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                  }`}
                >
                  {type === "ALL" ? t("results.auditTrail.allEvidence") : type}
                </button>
              ))}
            </div>
          </div>

          {/* Indicators List */}
          <div className="space-y-3">
            {filteredList.length === 0 ? (
              <div className="p-6 text-center border border-dashed border-stone-200 rounded-xl">
                <p className="text-xs text-stone-500">No evidence items match filter &quot;{filterType}&quot;</p>
              </div>
            ) : (
              filteredList.map((item, idx) => (
                <div
                  key={item.evidence_id || idx}
                  className="p-4 bg-slate-800/60 rounded-xl border border-slate-700 text-xs space-y-2 shadow-2xs"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-slate-100 text-sm">{item.indicator}</span>
                      {item.evidence_id && (
                        <span className="text-[10px] font-mono text-stone-400">
                          ({item.evidence_id})
                        </span>
                      )}
                    </div>
                    <EvidenceBadge type={item.evidence_type} confidence={item.confidence} />
                  </div>

                  <div className="text-slate-300 text-xs">
                    Recorded Value: <span className="font-mono font-bold text-slate-100">{String(item.value)}</span>{" "}
                    {item.unit && <span className="text-slate-500 font-normal">({item.unit})</span>}
                  </div>

                  {item.confidence_explanation && (
                    <p className="text-[11px] text-slate-300 bg-slate-900/70 p-2 rounded-lg border border-slate-700">
                      <strong>Confidence Basis:</strong> {item.confidence_explanation}
                    </p>
                  )}

                  {item.notes && (
                    <p className="text-[11px] text-slate-400 italic">
                      {item.notes}
                    </p>
                  )}

                  <div className="flex flex-wrap items-center justify-between gap-3 text-[11px] text-slate-500 pt-2 border-t border-slate-700">
                    <div className="flex items-center gap-3">
                      {item.source && (
                        <span>Source: <strong className="text-slate-300">{item.source}</strong></span>
                      )}
                      {item.observed_at && (
                        <span>Observed: <span className="text-slate-400">{new Date(item.observed_at).toLocaleDateString()}</span></span>
                      )}
                    </div>

                    {item.source_url && (
                      <a
                        href={item.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-emerald-300 hover:text-emerald-200 font-medium inline-flex items-center gap-1 transition-colors"
                      >
                        <span>Official Reference</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </section>
  );
};
