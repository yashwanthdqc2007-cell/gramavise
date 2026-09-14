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
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "ASSUMED":
        return "bg-amber-100 text-amber-800 border-amber-200";
      case "OBSERVED":
        return "bg-emerald-100 text-emerald-800 border-emerald-200";
      case "MODELLED":
        return "bg-purple-100 text-purple-800 border-purple-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm animate-in fade-in duration-200"
      role="dialog"
      aria-modal="true"
      aria-labelledby="explain-number-title"
      aria-describedby="explain-number-desc"
      data-testid="explain-number-modal"
    >
      <div
        ref={modalRef}
        className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col focus:outline-none"
        tabIndex={-1}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 bg-white/95 backdrop-blur-md px-6 py-4 border-b border-gray-100 flex items-center justify-between z-10">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-50 text-indigo-700 rounded-xl" aria-hidden="true">
              <Calculator className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 id="explain-number-title" className="text-base font-bold text-gray-900">
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
              <p id="explain-number-desc" className="text-xs text-gray-600">
                {t("results.explainNumber.modalSubtitle")}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
            aria-label={t("results.explainNumber.closeBtn")}
          >
            <X className="w-5 h-5" aria-hidden="true" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6 text-sm">
          {/* Main Displayed Metric Highlight */}
          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-slate-600 uppercase tracking-wider block">
                {explanation.metric_name}
              </span>
              <span className="text-2xl font-black text-slate-900 mt-0.5 block" data-testid="explained-displayed-value">
                {explanation.displayed_value}
              </span>
            </div>
            {explanation.is_debt_free && (
              <div className="px-3 py-1.5 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs font-semibold">
                Debt-Free Enterprise
              </div>
            )}
          </div>

          {/* Debt-free Special Notice */}
          {explanation.is_debt_free && (
            <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl flex items-start gap-2.5 text-xs text-emerald-900">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" aria-hidden="true" />
              <span>{t("results.explainNumber.debtFreeNotice")}</span>
            </div>
          )}

          {/* 1. Plain Meaning */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider flex items-center gap-1.5">
              <HelpCircle className="w-3.5 h-3.5 text-indigo-600" aria-hidden="true" />
              {t("results.explainNumber.plainMeaningTitle")}
            </h4>
            <p className="text-gray-800 bg-indigo-50/50 p-3.5 rounded-xl border border-indigo-100/80 leading-relaxed">
              {explanation.plain_meaning}
            </p>
          </div>

          {/* 2. Formula & Substituted Calculation */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider flex items-center gap-1.5">
              <Calculator className="w-3.5 h-3.5 text-indigo-600" aria-hidden="true" />
              {t("results.explainNumber.formulaTitle")}
            </h4>
            <div className="bg-slate-900 text-slate-100 p-4 rounded-xl space-y-2 font-mono text-xs shadow-inner">
              <div className="text-slate-300 text-[11px] font-sans">
                {explanation.formula_label}:
              </div>
              <div className="text-amber-300 font-bold tracking-wide">
                {explanation.formula_expression}
              </div>
              <div className="pt-2 border-t border-slate-800 text-emerald-300">
                <span className="text-slate-400 mr-2">=</span>
                {explanation.substituted_expression}
              </div>
            </div>
          </div>

          {/* 3. Step-by-Step Calculation Trace */}
          {explanation.calculation_steps.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-indigo-600" aria-hidden="true" />
                {t("results.explainNumber.stepsTitle")}
              </h4>
              <ul className="space-y-1.5 bg-gray-50 p-3.5 rounded-xl border border-gray-200">
                {explanation.calculation_steps.map((step, idx) => (
                  <li key={idx} className="text-xs text-gray-700 flex items-start gap-2">
                    <span className="font-mono text-gray-500 font-semibold shrink-0">
                      {idx + 1}.
                    </span>
                    <span className="font-mono text-gray-900">{step}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* 4. Input Variables & Data Provenance */}
          {explanation.inputs.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                {t("results.explainNumber.inputsTitle")}
              </h4>
              <div className="border border-gray-200 rounded-xl overflow-hidden">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-gray-50 border-b border-gray-200 text-gray-700 font-semibold">
                      <th scope="col" className="py-2 px-3">{t("results.explainNumber.inputNameHeader")}</th>
                      <th scope="col" className="py-2 px-3">{t("results.explainNumber.inputValueHeader")}</th>
                      <th scope="col" className="py-2 px-3">{t("results.explainNumber.inputProvenanceHeader")}</th>
                      <th scope="col" className="py-2 px-3">{t("results.explainNumber.inputSourceHeader")}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {explanation.inputs.map((inp, idx) => (
                      <tr key={idx} className="hover:bg-gray-50/50">
                        <td className="py-2 px-3 font-medium text-gray-800">{inp.label || inp.name}</td>
                        <td className="py-2 px-3 font-mono font-semibold text-gray-900">{inp.formatted_value}</td>
                        <td className="py-2 px-3">
                          <span
                            className={`text-[9px] font-mono px-1.5 py-0.5 rounded border font-semibold ${getProvenanceBadge(
                              inp.provenance
                            )}`}
                          >
                            {inp.provenance}
                          </span>
                        </td>
                        <td className="py-2 px-3 text-gray-600 text-[11px]">{inp.source_description}</td>
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
              <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
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
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg text-xs font-mono font-medium border border-slate-300 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
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
              <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider flex items-center gap-1.5">
                <ShieldAlert className="w-3.5 h-3.5 text-amber-600" aria-hidden="true" />
                {t("results.explainNumber.limitationsTitle")}
              </h4>
              <ul className="space-y-1 bg-amber-50/60 p-3.5 rounded-xl border border-amber-200/80 text-xs text-amber-900">
                {explanation.limitations.map((lim, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-amber-600 font-bold shrink-0" aria-hidden="true">&bull;</span>
                    <span>{lim}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 px-6 py-3 border-t border-gray-100 flex items-center justify-end rounded-b-2xl">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 bg-gray-900 text-white hover:bg-black rounded-xl text-xs font-bold transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-gray-900"
          >
            {t("results.explainNumber.closeBtn")}
          </button>
        </div>
      </div>
    </div>
  );
};

