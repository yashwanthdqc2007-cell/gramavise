"use client";

import React from "react";
import { NumberExplanation } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";
import { useFocusTrap } from "@/hooks/useFocusTrap";
import { X, HelpCircle, Calculator, FileText, CheckCircle2, ShieldAlert } from "lucide-react";

interface ExplainNumberModalProps {
  explanation: NumberExplanation | null;
  isOpen: boolean;
  onClose: () => void;
  onViewEvidence?: (evidenceId: string) => void;
}

export const ExplainNumberModal: React.FC<ExplainNumberModalProps> = ({
  explanation,
  isOpen,
  onClose,
  onViewEvidence,
}) => {
  const { t } = useTranslation();
  const modalRef = useFocusTrap<HTMLDivElement>({
    isOpen: isOpen && explanation !== null,
    onClose,
  });

  if (!isOpen || !explanation) {
    return null;
  }

  const getProvenanceBadge = (prov: string) => {
    switch (prov) {
      case "CALCULATED":
        return "bg-cyan-500/15 text-cyan-300 border-cyan-500/30";
      case "ASSUMED":
        return "bg-amber-500/15 text-amber-300 border-amber-500/30";
      case "OBSERVED":
        return "bg-emerald-500/15 text-emerald-300 border-emerald-500/30";
      case "MODELLED":
        return "bg-purple-500/15 text-purple-300 border-purple-500/30";
      default:
        return "bg-slate-700 text-slate-300 border-slate-600";
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm animate-in fade-in duration-200"
      role="dialog"
      aria-modal="true"
      aria-labelledby="explain-number-title"
      aria-describedby="explain-number-desc"
      data-testid="explain-number-modal"
    >
      <div
        ref={modalRef}
        className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-[#0B1F2D] rounded-2xl shadow-2xl border border-slate-700 flex flex-col focus:outline-none"
        tabIndex={-1}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 bg-[#06131F]/95 backdrop-blur-md px-6 py-4 border-b border-slate-800 flex items-center justify-between z-10">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-500/15 text-emerald-300 rounded-xl border border-emerald-500/25" aria-hidden="true">
              <Calculator className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 id="explain-number-title" className="text-base font-bold text-white">
                  {explanation.metric_name}
                </h3>
                <span
                  className={`text-[10px] font-mono px-2 py-0.5 rounded-full border font-bold ${getProvenanceBadge(
                    explanation.provenance
                  )}`}
                >
                  {explanation.provenance}
                </span>
              </div>
              <p id="explain-number-desc" className="text-xs text-slate-500">
                {t("results.explainNumber.modalSubtitle")}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-500 hover:text-white hover:bg-slate-700 rounded-lg transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
            aria-label={t("results.explainNumber.closeBtn")}
          >
            <X className="w-5 h-5" aria-hidden="true" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6 text-sm">
          {/* Main Displayed Metric Highlight */}
          <div className="p-4 bg-[#06131F] border border-slate-800 rounded-xl flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
                {explanation.metric_name}
              </span>
              <span className="text-2xl font-black text-white mt-0.5 block" data-testid="explained-displayed-value">
                {explanation.displayed_value}
              </span>
            </div>
            {explanation.is_debt_free && (
              <div className="px-3 py-1.5 bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 rounded-lg text-xs font-semibold">
                Debt-Free Enterprise
              </div>
            )}
          </div>

          {/* Debt-free Special Notice */}
          {explanation.is_debt_free && (
            <div className="p-3.5 bg-emerald-500/10 border border-emerald-500/25 rounded-xl flex items-start gap-2.5 text-xs text-emerald-200">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" aria-hidden="true" />
              <span>{t("results.explainNumber.debtFreeNotice")}</span>
            </div>
          )}

          {/* 1. Plain Meaning */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <HelpCircle className="w-3.5 h-3.5 text-emerald-500" aria-hidden="true" />
              {t("results.explainNumber.plainMeaningTitle")}
            </h4>
            <p className="text-slate-200 bg-[#06131F] p-3.5 rounded-xl border border-slate-800 leading-relaxed">
              {explanation.plain_meaning}
            </p>
          </div>

          {/* 2. Formula & Substituted Calculation */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Calculator className="w-3.5 h-3.5 text-emerald-500" aria-hidden="true" />
              {t("results.explainNumber.formulaTitle")}
            </h4>
            <div className="bg-[#06131F] text-slate-100 p-4 rounded-xl space-y-2 font-mono text-xs shadow-inner border border-slate-800">
              <div className="text-slate-400 text-[11px] font-sans">
                {explanation.formula_label}:
              </div>
              <div className="text-amber-300 font-bold tracking-wide">
                {explanation.formula_expression}
              </div>
              <div className="pt-2 border-t border-slate-800 text-emerald-300">
                <span className="text-slate-500 mr-2">=</span>
                {explanation.substituted_expression}
              </div>
            </div>
          </div>

          {/* 3. Step-by-Step Calculation Trace */}
          {explanation.calculation_steps.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-emerald-500" aria-hidden="true" />
                {t("results.explainNumber.stepsTitle")}
              </h4>
              <ul className="space-y-1.5 bg-[#06131F] p-3.5 rounded-xl border border-slate-800">
                {explanation.calculation_steps.map((step, idx) => (
                  <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                    <span className="font-mono text-slate-600 font-semibold shrink-0">
                      {idx + 1}.
                    </span>
                    <span className="font-mono text-slate-200">{step}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* 4. Input Variables & Data Provenance */}
          {explanation.inputs.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                {t("results.explainNumber.inputsTitle")}
              </h4>
              <div className="border border-slate-800 rounded-xl overflow-hidden">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-[#06131F] border-b border-slate-800 text-slate-400 font-semibold">
                      <th scope="col" className="py-2 px-3">{t("results.explainNumber.inputNameHeader")}</th>
                      <th scope="col" className="py-2 px-3">{t("results.explainNumber.inputValueHeader")}</th>
                      <th scope="col" className="py-2 px-3">{t("results.explainNumber.inputProvenanceHeader")}</th>
                      <th scope="col" className="py-2 px-3">{t("results.explainNumber.inputSourceHeader")}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {explanation.inputs.map((inp, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/40">
                        <td className="py-2 px-3 font-medium text-slate-300">{inp.label || inp.name}</td>
                        <td className="py-2 px-3 font-mono font-semibold text-white">{inp.formatted_value}</td>
                        <td className="py-2 px-3">
                          <span
                            className={`text-[9px] font-mono px-1.5 py-0.5 rounded border font-semibold ${getProvenanceBadge(
                              inp.provenance
                            )}`}
                          >
                            {inp.provenance}
                          </span>
                        </td>
                        <td className="py-2 px-3 text-slate-500 text-[11px]">{inp.source_description}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 5. Supporting Evidence & Market Sources */}
          {explanation.related_evidence_ids.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                {t("results.explainNumber.evidenceTitle")}
              </h4>
              <div className="flex flex-wrap gap-2">
                {explanation.related_evidence_ids.map((evId) => (
                  <button
                    key={evId}
                    type="button"
                    onClick={() => {
                      if (onViewEvidence) {
                        onClose();
                        onViewEvidence(evId);
                      }
                    }}
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-mono font-medium border border-slate-700 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
                  >
                    <span aria-hidden="true">🔗</span>
                    <span>{evId}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* 6. Practical Limitations & Caveats */}
          {explanation.limitations.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <ShieldAlert className="w-3.5 h-3.5 text-amber-400" aria-hidden="true" />
                {t("results.explainNumber.limitationsTitle")}
              </h4>
              <ul className="space-y-1 bg-amber-500/10 p-3.5 rounded-xl border border-amber-500/25 text-xs text-amber-200">
                {explanation.limitations.map((lim, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-amber-400 font-bold shrink-0" aria-hidden="true">&bull;</span>
                    <span>{lim}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-[#06131F] px-6 py-3 border-t border-slate-800 flex items-center justify-end rounded-b-2xl">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-300 border border-emerald-500/30 rounded-xl text-xs font-bold transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-[#06131F] focus-visible:ring-emerald-400"
          >
            {t("results.explainNumber.closeBtn")}
          </button>
        </div>
      </div>
    </div>
  );
};
