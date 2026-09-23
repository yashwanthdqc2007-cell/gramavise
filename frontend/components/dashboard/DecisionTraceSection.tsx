"use client";

import React, { useState } from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { DecisionTrace, EvidenceItem, VerificationCheckItem, RecommendationStatus } from "@/lib/types";
import { EvidenceBadge } from "@/components/evidence/EvidenceBadge";
import { useTranslation } from "@/lib/i18n";

interface DecisionTraceSectionProps {
  decisionTrace?: DecisionTrace;
  evidenceLedger?: EvidenceItem[];
  verificationChecklist?: VerificationCheckItem[];
  status: RecommendationStatus;
}

export const DecisionTraceSection: React.FC<DecisionTraceSectionProps> = ({
  decisionTrace,
  evidenceLedger = [],
  verificationChecklist = [],
  status
}) => {
  const { t } = useTranslation();
  const [completedTasks, setCompletedTasks] = useState<Record<string, boolean>>({});
  const [activeEvidenceFilter, setActiveEvidenceFilter] = useState<string>("ALL");

  const toggleTask = (id: string) => {
    setCompletedTasks(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const filteredEvidence = evidenceLedger.filter(item => {
    if (activeEvidenceFilter === "ALL") return true;
    return item.evidence_type === activeEvidenceFilter;
  });

  const getVerdictBadge = (st: RecommendationStatus) => {
    switch (st) {
      case "PROCEED":
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">PROCEED · RECOMMENDED</span>;
      case "VALIDATE_FIRST":
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30">VALIDATE FIRST · GROUND CHECKS NEEDED</span>;
      case "RECONSIDER":
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-rose-500/15 text-rose-300 border border-rose-500/30">RECONSIDER · HIGH FINANCIAL RISK</span>;
      default:
        return <Badge variant="neutral">{st}</Badge>;
    }
  };

  return (
    <Card className="space-y-6 border-slate-700 bg-slate-900/80">
      {/* 1. Section Header & Core Philosophy */}
      <div className="border-b border-slate-700 pb-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg">🔍</span>
              <h3 className="text-xl font-black text-white">{t("results.decisionTrace.title")}</h3>
              <span className="text-[10px] uppercase font-mono font-bold bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 px-2 py-0.5 rounded">
                Decision Trace & Evidence Ledger
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Transparent, deterministic evaluation chain: <strong>Evidence → Calculate → Explain → Decide</strong>.
            </p>
          </div>
          <div>{getVerdictBadge(status)}</div>
        </div>

        {decisionTrace?.summary && (
          <div className="mt-3 p-3 bg-cyan-500/10 border border-cyan-500/30 rounded-lg text-xs text-slate-200 leading-relaxed font-medium">
            <strong>Advisory Verdict Rationale:</strong> {decisionTrace.summary}
          </div>
        )}
      </div>

      {/* 2. Deterministic Rule Evaluations */}
      {decisionTrace?.rule_evaluations && decisionTrace.rule_evaluations.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
              <span>⚖️</span> Evaluated Decision Rules (FeasibilityRules)
            </h4>
            <span className="text-[10px] text-gray-400 font-mono">Authority: FeasibilityRules</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            {decisionTrace.rule_evaluations.map((rule, idx) => (
              <div
                key={rule.rule_id || idx}
                className={`p-3 rounded-lg border text-xs space-y-1.5 transition-all ${
                  rule.result === "PASS"
                    ? "bg-emerald-500/8 border-emerald-500/25 text-emerald-200"
                    : rule.result === "FAIL"
                    ? "bg-rose-500/8 border-rose-500/25 text-rose-200"
                    : "bg-amber-500/8 border-amber-500/25 text-amber-200"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold flex items-center gap-1 text-white">
                    {rule.result === "PASS" ? "✓" : rule.result === "FAIL" ? "✕" : "⚠"}{" "}
                    {rule.rule_name}
                  </span>
                  <span
                    className={`text-[9px] font-bold font-mono px-1.5 py-0.2 rounded uppercase ${
                      rule.result === "PASS"
                        ? "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30"
                        : rule.result === "FAIL"
                        ? "bg-rose-500/15 text-rose-300 border border-rose-500/30"
                        : "bg-amber-500/15 text-amber-300 border border-amber-500/30"
                    }`}
                  >
                    {rule.result}
                  </span>
                </div>
                <div className="text-[10px] text-slate-500 font-mono">
                Condition: <code className="bg-slate-900 px-1 py-0.2 rounded text-slate-300">{rule.condition}</code>
                </div>
                <p className="text-[11px] leading-relaxed text-slate-400">{rule.explanation}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 3. Actionable Pre-Borrowing Verification Checklist */}
      {verificationChecklist.length > 0 && (
        <div className="pt-3 border-t border-slate-700 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
              <span>📋</span> Pre-Borrowing Verification Checklist ({verificationChecklist.length} tasks)
            </h4>
            <span className="text-[10px] text-amber-300 font-semibold bg-amber-500/15 px-2 py-0.5 rounded border border-amber-500/30">
              Derived from Unresolved Evidence
            </span>
          </div>

          <p className="text-[11px] text-slate-400">
            Complete these on-ground verifications before taking loans or signing shop leases:
          </p>

          <div className="space-y-2">
            {verificationChecklist.map((task) => {
              const isChecked = !!completedTasks[task.item_id];
              return (
                <div
                  key={task.item_id}
                  onClick={() => toggleTask(task.item_id)}
                  className={`p-3 rounded-lg border text-xs cursor-pointer select-none transition-all flex items-start gap-3 ${
                    isChecked
                      ? "bg-slate-800/50 border-slate-700 text-slate-500"
                      : "bg-slate-800/60 border-amber-500/30 hover:border-amber-400/60 shadow-sm"
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={isChecked}
                    onChange={() => {}}
                    className="mt-0.5 h-4 w-4 rounded border-slate-600 bg-slate-800 text-emerald-500 focus:ring-emerald-500 cursor-pointer"
                  />
                  <div className="space-y-0.5 flex-1">
                    <div className="flex items-center justify-between">
                      <span className={`font-semibold ${isChecked ? "line-through text-slate-500" : "text-slate-100"}`}>
                        {task.title}
                      </span>
                      <span className="text-[9px] font-bold uppercase bg-slate-700 text-slate-300 px-1.5 py-0.2 rounded">
                        {task.category}
                      </span>
                    </div>
                    <p className={`text-[11px] ${isChecked ? "line-through text-slate-500" : "text-slate-400"}`}>
                      {task.description}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 4. Structured Evidence Ledger */}
      <div className="pt-3 border-t border-slate-800 space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <span>📚</span> Structured Evidence Ledger ({evidenceLedger.length} items)
          </h4>
          
          {/* Filter Pills */}
          <div className="flex items-center gap-1 flex-wrap text-[10px]">
            {["ALL", "CALCULATED", "OBSERVED", "ASSUMED", "MODELLED", "NEEDS_VERIFICATION"].map((f) => (
              <button
                key={f}
                onClick={() => setActiveEvidenceFilter(f)}
                className={`px-2 py-0.5 rounded font-medium transition-colors ${
                  activeEvidenceFilter === f
                    ? "bg-emerald-600 text-white font-bold"
                    : "bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-slate-200"
                }`}
              >
                {f.replace(/_/g, " ")}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          {filteredEvidence.map((item, idx) => (
            <div
              key={item.evidence_id || idx}
              className="p-3 bg-[#0E2635] rounded-lg border border-slate-700/60 text-xs space-y-2 hover:border-emerald-500/30 transition-colors"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5">
                <div>
                  <span className="font-bold text-white text-sm">{item.claim || item.indicator}</span>
                  {item.evidence_id && (
                    <span className="text-[10px] text-slate-500 font-mono ml-2">[{item.evidence_id}]</span>
                  )}
                </div>
                <EvidenceBadge
                  type={item.evidence_type}
                  confidence={item.confidence}
                  confidenceLevel={item.confidence_level}
                />
              </div>

              <div className="flex items-center gap-2 text-slate-400 font-medium">
                <span>Value:</span>
                <strong className="text-white font-bold bg-slate-900/70 px-2 py-0.5 rounded border border-slate-700">
                  {item.value}
                </strong>
                {item.unit && <span className="text-slate-600 font-normal text-[11px]">({item.unit})</span>}
              </div>

              {item.confidence_explanation && (
                <div className="text-[11px] text-slate-400 bg-[#06131F] p-2 rounded border border-slate-800">
                  <strong className="text-slate-300">Confidence Basis:</strong> {item.confidence_explanation}
                </div>
              )}

              {item.limitations && (
                <p className="text-[10px] text-amber-300 bg-amber-500/10 p-1.5 rounded border border-amber-500/25 italic">
                  * Limitation: {item.limitations}
                </p>
              )}

              <div className="flex flex-wrap items-center justify-between gap-2 text-[10px] text-slate-600 pt-1.5 border-t border-slate-800">
                {item.source && (
                  <span>
                    Source: <strong className="text-slate-400">{item.source_title || item.source}</strong>
                  </span>
                )}
                {item.source_url ? (
                  <a
                    href={item.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-emerald-400 hover:text-emerald-300 underline font-medium"
                  >
                    View Official Source ↗
                  </a>
                ) : (
                  <span>Source URL: None</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
};
