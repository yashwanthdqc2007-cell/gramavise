"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  ActionPlan,
  ActionItem,
  ActionPriority,
  ActionCategory,
  ActionStatus,
  DocumentReadiness,
  BankReadiness,
  ReadinessStatus
} from "@/lib/types";
import { useTranslation } from "@/lib/i18n";
import { MapPin, CheckCircle2, ChevronDown, FileText, ArrowRight, ShieldCheck } from "lucide-react";

interface PreLoanActionPlanSectionProps {
  actionPlan?: ActionPlan;
  documentReadiness?: DocumentReadiness;
  bankReadiness?: BankReadiness;
}

export const PreLoanActionPlanSection: React.FC<PreLoanActionPlanSectionProps> = ({
  actionPlan,
  documentReadiness,
  bankReadiness
}) => {
  const { t } = useTranslation();
  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");
  const [selectedStatus, setSelectedStatus] = useState<string>("ALL");
  const [completedActionIds, setCompletedActionIds] = useState<Set<string>>(new Set());

  if (!actionPlan && !bankReadiness && !documentReadiness) {
    return null;
  }

  const toggleActionCompleted = (actionId: string) => {
    setCompletedActionIds((prev) => {
      const next = new Set(prev);
      if (next.has(actionId)) {
        next.delete(actionId);
      } else {
        next.add(actionId);
      }
      return next;
    });
  };

  const getPriorityBadge = (priority: ActionPriority) => {
    switch (priority) {
      case "CRITICAL":
        return "bg-rose-50 text-rose-800 border-rose-200";
      case "HIGH":
        return "bg-amber-50 text-amber-800 border-amber-200";
      case "MEDIUM":
        return "bg-blue-50 text-blue-800 border-blue-200";
      case "LOW":
        return "bg-stone-100 text-stone-700 border-stone-200";
      default:
        return "bg-stone-100 text-stone-700 border-stone-200";
    }
  };

  const getReadinessBadge = (status: ReadinessStatus) => {
    switch (status) {
      case "READY":
        return "bg-emerald-50 text-emerald-800 border-emerald-200";
      case "PARTIALLY_READY":
        return "bg-amber-50 text-amber-800 border-amber-200";
      case "NOT_READY":
        return "bg-rose-50 text-rose-800 border-rose-200";
      default:
        return "bg-stone-100 text-stone-700 border-stone-200";
    }
  };

  const actions = actionPlan?.actions || [];
  const filteredActions = actions.filter((action) => {
    const isCompleted = completedActionIds.has(action.action_id);
    const matchesCategory = selectedCategory === "ALL" || action.category === selectedCategory;
    const matchesStatus =
      selectedStatus === "ALL" ||
      (selectedStatus === "COMPLETED" && isCompleted) ||
      (selectedStatus === "TODO" && !isCompleted);
    return matchesCategory && matchesStatus;
  });

  return (
    <section className="rounded-2xl border border-stone-200/80 bg-white shadow-sm overflow-hidden" id="action-plan">
      {/* Section Header */}
      <div className="p-6 md:p-8 border-b border-stone-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-700" />
            <h2 className="text-xl font-bold tracking-tight text-slate-900">
              {t("results.nextSteps.title")}
            </h2>
          </div>
          <p className="text-xs text-stone-500 mt-1">
            {t("results.nextSteps.subtitle")}
          </p>
        </div>

        {bankReadiness && (
          <div className="bg-stone-50 rounded-xl p-3 border border-stone-200/70 text-right min-w-[180px] self-start sm:self-auto">
            <span className="text-[10px] uppercase tracking-wider text-stone-500 font-semibold block">
              {t("results.actionPlan.readinessSummary")}
            </span>
            <span className={`inline-block mt-0.5 px-2.5 py-0.5 text-xs font-bold rounded-full border ${getReadinessBadge(bankReadiness.overall_status)}`}>
              {bankReadiness.overall_status.replace("_", " ")}
            </span>
          </div>
        )}
      </div>

      <div className="p-6 md:p-8 space-y-8">
        {/* Bank-Readiness Assessment Card */}
        {bankReadiness && (
          <div className="rounded-xl border border-stone-200/80 bg-stone-50/50 p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <span>🏦</span> Pre-Loan Readiness Assessment
              </h3>
            </div>

            <p className="text-xs text-stone-600 leading-relaxed">
              {bankReadiness.summary}
            </p>

            {/* 5 Dimension Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
              {bankReadiness.categories.map((cat, idx) => (
                <div key={idx} className="rounded-lg border border-stone-200/80 bg-white p-3 flex flex-col justify-between">
                  <div>
                    <span className="text-xs font-bold text-slate-800 block mb-1">
                      {cat.title}
                    </span>
                    <p className="text-[11px] text-stone-500 line-clamp-3 leading-relaxed">
                      {cat.reason}
                    </p>
                  </div>
                  <div className="mt-2.5 pt-2 border-t border-stone-100 flex justify-between items-center">
                    <span className="text-[9px] text-stone-400 uppercase tracking-wider font-mono">
                      {cat.category}
                    </span>
                    <span className={`px-1.5 py-0.5 text-[9px] font-bold rounded border ${getReadinessBadge(cat.status)}`}>
                      {cat.status.replace("_", " ")}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* Top Priorities */}
            {bankReadiness.top_actions && bankReadiness.top_actions.length > 0 && (
              <div className="pt-3 border-t border-stone-200/70">
                <span className="text-[10px] font-bold text-stone-500 uppercase tracking-wider block mb-1.5">
                  Top Priority Milestones:
                </span>
                <div className="flex flex-wrap gap-2">
                  {bankReadiness.top_actions.map((actTitle, aIdx) => (
                    <span
                      key={aIdx}
                      className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-white border border-stone-200 text-slate-800 text-xs rounded-lg font-medium shadow-2xs"
                    >
                      <span className="w-4 h-4 rounded-full bg-emerald-700 text-white flex items-center justify-center text-[10px] font-bold">
                        {aIdx + 1}
                      </span>
                      {actTitle}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Action Roadmap - Numbered 01, 02, 03 */}
        <div>
          <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">
                Action Roadmap ({filteredActions.length} of {actions.length})
              </h3>
              <p className="text-xs text-stone-500 mt-0.5">
                Targeted preparation steps before presenting your loan application.
              </p>
            </div>

            {/* Category and Status Filters */}
            <div className="flex flex-wrap items-center gap-2">
              <select
                className="text-xs rounded-lg border border-stone-200 bg-white text-slate-700 px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                aria-label="Filter by category"
              >
                <option value="ALL">All Categories</option>
                <option value="FINANCIAL">Financial</option>
                <option value="MARKET">Market</option>
                <option value="SCHEME">Scheme</option>
                <option value="DOCUMENTATION">Documentation</option>
                <option value="VALIDATION">Validation</option>
                <option value="BUSINESS_OPERATIONS">Operations</option>
              </select>

              <div className="flex rounded-lg border border-stone-200 p-0.5 bg-stone-100 text-xs">
                <button
                  type="button"
                  className={`px-2.5 py-1 rounded-md transition-colors ${selectedStatus === "ALL" ? "bg-white text-slate-900 font-semibold shadow-xs" : "text-stone-600 hover:text-slate-900"}`}
                  onClick={() => setSelectedStatus("ALL")}
                >
                  All
                </button>
                <button
                  type="button"
                  className={`px-2.5 py-1 rounded-md transition-colors ${selectedStatus === "TODO" ? "bg-white text-slate-900 font-semibold shadow-xs" : "text-stone-600 hover:text-slate-900"}`}
                  onClick={() => setSelectedStatus("TODO")}
                >
                  Pending
                </button>
                <button
                  type="button"
                  className={`px-2.5 py-1 rounded-md transition-colors ${selectedStatus === "COMPLETED" ? "bg-white text-slate-900 font-semibold shadow-xs" : "text-stone-600 hover:text-slate-900"}`}
                  onClick={() => setSelectedStatus("COMPLETED")}
                >
                  Completed ({completedActionIds.size})
                </button>
              </div>
            </div>
          </div>

          {/* Action Cards Grid - Numbered Roadmap Style */}
          <div className="space-y-3">
            {filteredActions.length === 0 ? (
              <div className="p-8 text-center border border-dashed border-stone-200 rounded-xl">
                <p className="text-xs text-stone-500">No action items match the selected filter criteria.</p>
              </div>
            ) : (
              filteredActions.map((action, idx) => {
                const isCompleted = completedActionIds.has(action.action_id);
                const stepNumber = String(idx + 1).padStart(2, "0");

                return (
                  <div
                    key={action.action_id}
                    className={`rounded-xl border p-4 transition-all ${
                      isCompleted
                        ? "bg-stone-50/60 border-stone-200 opacity-75"
                        : "bg-white border-stone-200/80 hover:border-emerald-300 shadow-2xs"
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      {/* Step Number Tag */}
                      <span className={`w-8 h-8 rounded-lg flex items-center justify-center font-mono font-bold text-xs shrink-0 ${
                        isCompleted
                          ? "bg-stone-200 text-stone-600"
                          : "bg-emerald-50 text-emerald-800 border border-emerald-200"
                      }`}>
                        {stepNumber}
                      </span>

                      {/* Checkbox Toggle */}
                      <button
                        type="button"
                        onClick={() => toggleActionCompleted(action.action_id)}
                        className={`mt-1 w-5 h-5 rounded border flex items-center justify-center transition-colors shrink-0 ${
                          isCompleted
                            ? "bg-emerald-600 border-emerald-600 text-white"
                            : "border-stone-300 hover:border-emerald-500 bg-white"
                        }`}
                        aria-label={`Mark ${action.title} as ${isCompleted ? "pending" : "completed"}`}
                      >
                        {isCompleted && (
                          <svg className="w-3.5 h-3.5 stroke-[3]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                          </svg>
                        )}
                      </button>

                      <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap items-center gap-2 mb-1">
                          <span className={`px-2 py-0.5 text-[10px] font-bold rounded border ${getPriorityBadge(action.priority)}`}>
                            {action.priority}
                          </span>
                          <span className="px-2 py-0.5 text-[10px] font-medium rounded bg-stone-100 text-stone-700">
                            {action.category}
                          </span>
                          {action.estimated_effort && (
                            <span className="text-[11px] text-stone-400">
                              &bull; {action.estimated_effort}
                            </span>
                          )}
                        </div>

                        <h4 className={`text-sm font-bold text-slate-900 ${isCompleted ? "line-through text-stone-400" : ""}`}>
                          {action.title}
                        </h4>

                        <div className="mt-1.5 space-y-1 text-xs">
                          <p className="text-stone-600">
                            <strong className="text-slate-800">Action:</strong> {action.description}
                          </p>
                          <p className="text-stone-500">
                            <strong className="text-slate-700">Why:</strong> {action.reason}
                          </p>
                          {action.completion_effect && (
                            <p className="text-emerald-700 font-medium">
                              <strong>Expected Outcome:</strong> {action.completion_effect}
                            </p>
                          )}
                        </div>

                        {/* Technical Evidence Accordion for Evaluators / Judges */}
                        {(action.related_rule_ids?.length || action.related_evidence_ids?.length) && (
                          <details className="mt-2 pt-1 border-t border-stone-100 text-[11px] text-stone-400">
                            <summary className="cursor-pointer hover:text-slate-700 font-medium text-[10px]">
                              Technical Evidence & Rule Trace
                            </summary>
                            <div className="mt-1 flex flex-wrap items-center gap-1 font-mono text-[10px]">
                              {action.related_rule_ids?.map((rid) => (
                                <span key={rid} className="px-1.5 py-0.5 rounded bg-stone-100 text-stone-600">
                                  {rid}
                                </span>
                              ))}
                              {action.related_evidence_ids?.map((eid) => (
                                <span key={eid} className="px-1.5 py-0.5 rounded bg-stone-100 text-stone-600">
                                  {eid}
                                </span>
                              ))}
                            </div>
                          </details>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Scheme-Supported Document Checklist */}
        {documentReadiness && documentReadiness.documents.length > 0 && (
          <div className="rounded-xl border border-stone-200/80 bg-stone-50/50 p-5 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <FileText className="w-4 h-4 text-emerald-700" />
                Required Document Checklist ({documentReadiness.documents.length})
              </h3>
              <span className="text-[11px] text-stone-400">
                Derived directly from matched scheme eligibility rules
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {documentReadiness.documents.map((doc) => (
                <div key={doc.document_id} className="rounded-lg border border-stone-200/70 bg-white p-3.5 space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h4 className="text-xs font-bold text-slate-900">
                        {doc.name}
                      </h4>
                      <p className="text-[11px] text-stone-500 mt-0.5">
                        {doc.purpose}
                      </p>
                    </div>
                    <span className="px-2 py-0.5 text-[9px] font-bold rounded border bg-amber-50 text-amber-800 border-amber-200 shrink-0">
                      {doc.status}
                    </span>
                  </div>
                  <div className="text-[10px] text-stone-400">
                    Required for: <strong className="text-slate-700">{doc.required_for}</strong>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Completion Invariant & Re-Analyze CTA */}
        <div className="rounded-xl border border-emerald-200 bg-emerald-50/40 p-5 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="space-y-1 text-center sm:text-left">
            <h4 className="text-sm font-bold text-slate-900">
              Ready to recalculate with newly verified numbers?
            </h4>
            <p className="text-xs text-stone-600 max-w-xl">
              Updating your assumptions with real ground quotes will refresh your deterministic verdict and financial margins.
            </p>
          </div>
          <Link
            href="/onboarding"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold rounded-xl shadow-xs transition-all shrink-0"
          >
            <span>Update Assumptions & Re-Run</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </section>
  );
};
