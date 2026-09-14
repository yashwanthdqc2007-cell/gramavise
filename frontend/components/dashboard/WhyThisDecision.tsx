"use client";

import React, { useState } from "react";
import { DecisionTrace, RuleEvaluation } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";
import { CheckCircle2, AlertTriangle, XCircle, ChevronDown, ChevronUp, Code2 } from "lucide-react";

interface WhyThisDecisionProps {
  decisionTrace?: DecisionTrace;
}

export const WhyThisDecision: React.FC<WhyThisDecisionProps> = ({ decisionTrace }) => {
  const { t } = useTranslation();
  const [showTechnical, setShowTechnical] = useState(false);

  const rules: RuleEvaluation[] = decisionTrace?.rule_evaluations || [];
  if (rules.length === 0) return null;

  const getStatusIcon = (res: string) => {
    switch (res) {
      case "PASS":
        return <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" aria-hidden="true" />;
      case "FAIL":
        return <XCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" aria-hidden="true" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" aria-hidden="true" />;
    }
  };

  const getStatusBadge = (res: string) => {
    switch (res) {
      case "PASS":
        return "bg-emerald-50 text-emerald-800 border-emerald-200";
      case "FAIL":
        return "bg-rose-50 text-rose-800 border-rose-200";
      default:
        return "bg-amber-50 text-amber-800 border-amber-200";
    }
  };

  return (
    <section className="bg-white rounded-2xl border border-stone-200/80 p-6 md:p-7 shadow-sm space-y-5" id="why-this-decision">
      {/* Header */}
      <div className="border-b border-stone-100 pb-3">
        <h2 className="text-xl font-black text-slate-900 tracking-tight">
          {t("results.whyThisDecision.title")}
        </h2>
        <p className="text-xs md:text-sm text-slate-600 mt-1">
          {t("results.whyThisDecision.subtitle")}
        </p>
      </div>

      {/* 3–6 Scannable Reason Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {rules.map((rule, idx) => (
          <div
            key={rule.rule_id || idx}
            className="p-4 rounded-xl border border-stone-200/90 bg-stone-50/50 hover:bg-white hover:border-stone-300 hover:shadow-sm transition-all space-y-1.5"
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-start gap-2">
                {getStatusIcon(rule.result)}
                <h3 className="text-sm font-bold text-slate-900 leading-snug">
                  {rule.rule_name}
                </h3>
              </div>
              <span
                className={`text-[10px] font-bold font-mono px-2 py-0.5 rounded border uppercase shrink-0 ${getStatusBadge(
                  rule.result
                )}`}
              >
                {rule.result}
              </span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed pl-6">
              {rule.explanation}
            </p>
          </div>
        ))}
      </div>

      {/* Progressive Disclosure: Technical Details for Judges/Evaluators */}
      <div className="pt-2">
        <button
          type="button"
          onClick={() => setShowTechnical(!showTechnical)}
          className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-900 font-medium py-1 transition-colors"
          aria-expanded={showTechnical}
        >
          <Code2 className="w-3.5 h-3.5 text-slate-400" aria-hidden="true" />
          <span>
            {showTechnical
              ? t("results.whyThisDecision.technicalDetailsHide")
              : t("results.whyThisDecision.technicalDetails")}
          </span>
          {showTechnical ? (
            <ChevronUp className="w-3.5 h-3.5 text-slate-400" aria-hidden="true" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" aria-hidden="true" />
          )}
        </button>

        {showTechnical && (
          <div className="mt-3 p-4 rounded-xl bg-slate-900 text-slate-200 font-mono text-xs space-y-3 shadow-inner">
            <div className="flex items-center justify-between text-slate-400 text-[11px] border-b border-slate-800 pb-2">
              <span>{t("results.whyThisDecision.evaluatedRules")}</span>
              <span>{t("results.whyThisDecision.ruleAuthority")}</span>
            </div>
            <div className="space-y-2.5">
              {rules.map((rule, idx) => (
                <div key={`tech-${rule.rule_id || idx}`} className="text-[11px] space-y-0.5">
                  <div className="flex items-center justify-between text-slate-300">
                    <span className="font-semibold text-emerald-400">{rule.rule_id}</span>
                    <span className="text-slate-400">{rule.rule_name}</span>
                  </div>
                  <div className="text-slate-400 pl-2">
                    <span className="text-amber-300">{t("results.whyThisDecision.condition")}:</span>{" "}
                    <code className="text-slate-200">{rule.condition}</code>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
};
