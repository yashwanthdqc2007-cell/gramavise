"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  AnalysisResult,
  FinancialAssumptions,
  ScenarioEvaluationRequest,
  ScenarioEvaluationResponse,
  CreateScenarioRequest,
  ScenarioRecordResponse,
  MetricComparison,
  ComparisonDirection,
  NumberExplanation
} from "@/lib/types";
import { useTranslation } from "@/lib/i18n";
import { ExplainNumberModal } from "@/components/financial/ExplainNumberModal";
import { HelpCircle, Save, Check, AlertCircle } from "lucide-react";

import { useNetworkStatus } from "@/hooks/useNetworkStatus";
import { apiClient } from "@/lib/api";

interface ScenarioLabSectionProps {
  result: AnalysisResult;
  baselineFinancials?: FinancialAssumptions | null;
}

interface SavedScenario {
  id: string;
  name: string;
  ownCapital: number;
  desiredLoan: number;
  financials: FinancialAssumptions;
  evaluation?: ScenarioEvaluationResponse | null;
  isLoading?: boolean;
  isSaved?: boolean;
  persistentId?: string;
  savedAt?: string;
}

export const ScenarioLabSection: React.FC<ScenarioLabSectionProps> = ({
  result,
  baselineFinancials
}) => {
  const { t } = useTranslation();
  const { isOnline } = useNetworkStatus();
  const [scenarios, setScenarios] = useState<SavedScenario[]>([]);
  const [activeScenarioId, setActiveScenarioId] = useState<string | null>(null);
  const [isEvaluating, setIsEvaluating] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [activeExplanation, setActiveExplanation] = useState<NumberExplanation | null>(null);
  const [isOpen, setIsOpen] = useState<boolean>(false);

  // Safely derive baseline parameters from explanations metadata, profile, or financial result
  const baselineOwnCapital = React.useMemo(() => {
    // 1. Try from explanations metadata if available
    const explInput = result.financial_result.explanations?.required_loan_amount?.inputs?.find(
      (i) => i.name === "own_capital"
    );
    if (explInput && typeof explInput.raw_value === "number" && !isNaN(explInput.raw_value)) {
      return Math.max(0, explInput.raw_value);
    }
    // 2. Try from sessionStorage if in browser
    if (typeof window !== "undefined") {
      try {
        const storedProfile = sessionStorage.getItem("gramavise_profile");
        if (storedProfile) {
          const parsed = JSON.parse(storedProfile);
          if (typeof parsed?.own_capital === "number" && !isNaN(parsed.own_capital)) {
            return Math.max(0, parsed.own_capital);
          }
        }
      } catch {
        // ignore
      }
    }
    // 3. Fallback to Capex - Loan clamped to >= 0
    return Math.max(0, (result.financial_result.total_capex || 0) - (result.financial_result.required_loan_amount || 0));
  }, [result]);

  const baselineDesiredLoan = React.useMemo(() => {
    return Math.max(0, result.financial_result.required_loan_amount || 0);
  }, [result.financial_result.required_loan_amount]);

  const baselineFin: FinancialAssumptions = React.useMemo(() => {
    return (
      baselineFinancials || {
        startup_cost: 25000,
        equipment_cost: 100000,
        inventory_cost: 25000,
        monthly_fixed_cost: result.financial_result.monthly_fixed_cost || 6000,
        customers_per_day: 50,
        avg_ticket_price: 30,
        working_days_per_month: 26,
        variable_cost_pct: 50,
        interest_rate_pct: 10.5,
        loan_tenure_months: 60,
      }
    );
  }, [baselineFinancials, result.financial_result.monthly_fixed_cost]);

  // Helper to open explanation for a metric key
  const handleInspectMetric = (metricKey: string, preferScenario: boolean = true) => {
    if (!activeScenario?.evaluation) return;
    if (preferScenario && activeScenario.evaluation.scenario_result.explanations?.[metricKey]) {
      setActiveExplanation(activeScenario.evaluation.scenario_result.explanations[metricKey]);
    } else if (activeScenario.evaluation.baseline_result.explanations?.[metricKey]) {
      setActiveExplanation(activeScenario.evaluation.baseline_result.explanations[metricKey]);
    }
  };

  // Load persisted saved scenarios on mount if analysis_id exists
  useEffect(() => {
    let isMounted = true;
    const loadSavedScenarios = async () => {
      if (!result.analysis_id || !isOnline) {
        if (scenarios.length === 0) {
          const initScen: SavedScenario = {
            id: "scenario-1",
            name: "Scenario A",
            ownCapital: baselineOwnCapital,
            desiredLoan: baselineDesiredLoan,
            financials: { ...baselineFin },
            isSaved: false,
          };
          setScenarios([initScen]);
          setActiveScenarioId("scenario-1");
        }
        return;
      }

      try {
        const records = await apiClient<ScenarioRecordResponse[]>(`/analyze/${result.analysis_id}/scenarios`);
        if (isMounted && Array.isArray(records) && records.length > 0) {
          const loaded: SavedScenario[] = records.map((r, idx) => ({
            id: r.scenario_id,
            persistentId: r.scenario_id,
            name: r.name || `Scenario ${String.fromCharCode(65 + idx)}`,
            ownCapital: r.scenario_inputs?.own_capital ?? Math.max(0, r.scenario_result.total_capex - r.scenario_result.required_loan_amount),
            desiredLoan: r.scenario_inputs?.desired_loan ?? Math.max(0, r.scenario_result.required_loan_amount),
            financials: {
              startup_cost: r.scenario_inputs?.startup_cost ?? 25000,
              equipment_cost: r.scenario_inputs?.equipment_cost ?? 100000,
              inventory_cost: r.scenario_inputs?.inventory_cost ?? 25000,
              monthly_fixed_cost: r.scenario_inputs?.monthly_fixed_cost ?? r.scenario_result.monthly_fixed_cost,
              customers_per_day: r.scenario_inputs?.customers_per_day ?? 50,
              avg_ticket_price: r.scenario_inputs?.avg_ticket_price ?? 30,
              working_days_per_month: r.scenario_inputs?.working_days_per_month ?? 26,
              variable_cost_pct: r.scenario_inputs?.variable_cost_pct ?? 50,
              interest_rate_pct: r.scenario_inputs?.interest_rate_pct ?? 10.5,
              loan_tenure_months: r.scenario_inputs?.loan_tenure_months ?? 60,
            },
            evaluation: r, // Pure read-only display of stored evaluation (NO recalculation!)
            isSaved: true,
            savedAt: r.created_at,
          }));
          setScenarios(loaded);
          setActiveScenarioId(loaded[0].id);
        } else if (isMounted && scenarios.length === 0) {
          const initScen: SavedScenario = {
            id: "scenario-1",
            name: "Scenario A",
            ownCapital: baselineOwnCapital,
            desiredLoan: baselineDesiredLoan,
            financials: { ...baselineFin },
            isSaved: false,
          };
          setScenarios([initScen]);
          setActiveScenarioId("scenario-1");
        }
      } catch (err: any) {
        console.warn("Could not load saved scenarios:", err);
        if (isMounted && scenarios.length === 0) {
          const initScen: SavedScenario = {
            id: "scenario-1",
            name: "Scenario A",
            ownCapital: baselineOwnCapital,
            desiredLoan: baselineDesiredLoan,
            financials: { ...baselineFin },
            isSaved: false,
          };
          setScenarios([initScen]);
          setActiveScenarioId("scenario-1");
        }
      }
    };

    loadSavedScenarios();
    return () => {
      isMounted = false;
    };
  }, [result.analysis_id, baselineOwnCapital, baselineDesiredLoan, isOnline, baselineFin]);

  const activeScenario = scenarios.find((s) => s.id === activeScenarioId) || scenarios[0];
  const savedCount = scenarios.filter((s) => s.isSaved).length;
  const isMaxSavedReached = savedCount >= 3;

  // Evaluate scenario via backend API for live stateless preview
  const handleEvaluateScenario = useCallback(async (scen: SavedScenario) => {
    if (!isOnline && typeof navigator !== "undefined" && !navigator.onLine) {
      setApiError(t("results.scenarioLab.offlineNotice"));
      return;
    }

    setIsEvaluating(true);
    setApiError(null);
    try {
      const reqPayload: ScenarioEvaluationRequest = {
        scenario_id: scen.id,
        name: scen.name,
        baseline_own_capital: Math.max(0, baselineOwnCapital),
        baseline_desired_loan: Math.max(0, baselineDesiredLoan),
        baseline_financials: baselineFin,
        scenario_own_capital: Math.max(0, scen.ownCapital),
        scenario_desired_loan: Math.max(0, scen.desiredLoan),
        scenario_financials: scen.financials,
        market_context: result.market_result
      };

      const evalData = await apiClient<ScenarioEvaluationResponse>("/analyze/scenario", {
        method: "POST",
        body: JSON.stringify(reqPayload)
      });

      setScenarios((prev) =>
        prev.map((s) => (s.id === scen.id ? { ...s, evaluation: evalData } : s))
      );
    } catch (err: any) {
      console.error("Scenario evaluation error:", err);
      setApiError(err.message || t("results.scenarioLab.offlineNotice"));
    } finally {
      setIsEvaluating(false);
    }
  }, [isOnline, baselineOwnCapital, baselineDesiredLoan, baselineFin, result.market_result, t]);

  // Run evaluation when active scenario changes if not evaluated yet
  useEffect(() => {
    if (activeScenario && !activeScenario.evaluation && !isEvaluating && isOnline) {
      handleEvaluateScenario(activeScenario);
    }
  }, [activeScenario?.id, activeScenario?.evaluation, isEvaluating, isOnline, handleEvaluateScenario]);

  // Save active scenario to backend API
  const handleSaveScenario = async () => {
    if (!activeScenario) return;

    if (!isOnline && typeof navigator !== "undefined" && !navigator.onLine) {
      setApiError(t("results.scenarioLab.saveFailedOffline"));
      return;
    }

    if (!result.analysis_id) {
      setApiError(t("results.scenarioLab.error404"));
      return;
    }

    if (isMaxSavedReached && !activeScenario.isSaved) {
      setApiError(t("results.scenarioLab.maxScenariosReached"));
      return;
    }

    setIsSaving(true);
    setApiError(null);
    setSaveSuccessMsg(null);

    try {
      const payload: CreateScenarioRequest = {
        name: activeScenario.name,
        description: activeScenario.evaluation?.description || undefined,
        scenario_own_capital: activeScenario.ownCapital,
        scenario_desired_loan: activeScenario.desiredLoan,
        scenario_financials: activeScenario.financials,
      };

      const idempotencyKey = typeof crypto !== "undefined" && crypto.randomUUID ? crypto.randomUUID() : `scen-${Date.now()}`;
      const savedRecord = await apiClient<ScenarioRecordResponse>(`/analyze/${result.analysis_id}/scenarios`, {
        method: "POST",
        headers: {
          "Idempotency-Key": idempotencyKey,
        },
        body: JSON.stringify(payload),
      });

      setScenarios((prev) =>
        prev.map((s) =>
          s.id === activeScenario.id
            ? {
                ...s,
                id: savedRecord.scenario_id,
                persistentId: savedRecord.scenario_id,
                name: savedRecord.name,
                evaluation: savedRecord,
                isSaved: true,
                savedAt: savedRecord.created_at,
              }
            : s
        )
      );
      setActiveScenarioId(savedRecord.scenario_id);
      setSaveSuccessMsg(t("results.scenarioLab.saved"));
      setTimeout(() => setSaveSuccessMsg(null), 3500);
    } catch (err: any) {
      console.error("Save scenario error:", err);
      if (err.status === 409 || err.message?.includes("409") || err.message?.toLowerCase().includes("limit of 3")) {
        setApiError(t("results.scenarioLab.error409"));
      } else if (err.status === 404 || err.message?.includes("404")) {
        setApiError(t("results.scenarioLab.error404"));
      } else if (err.status === 422 || err.message?.includes("422")) {
        setApiError(t("results.scenarioLab.error422"));
      } else {
        setApiError(err.message || t("results.scenarioLab.saveFailedOffline"));
      }
    } finally {
      setIsSaving(false);
    }
  };

  // Update a field in active scenario
  const updateActiveScenarioField = (field: string, value: number) => {
    if (!activeScenario) return;

    let updated: SavedScenario;
    if (field === "ownCapital") {
      updated = { ...activeScenario, ownCapital: Math.max(0, value), evaluation: null, isSaved: false };
    } else if (field === "desiredLoan") {
      updated = { ...activeScenario, desiredLoan: Math.max(0, value), evaluation: null, isSaved: false };
    } else {
      updated = {
        ...activeScenario,
        financials: { ...activeScenario.financials, [field]: value },
        evaluation: null,
        isSaved: false,
      };
    }

    setScenarios((prev) => prev.map((s) => (s.id === activeScenario.id ? updated : s)));
  };

  const handleAddScenario = () => {
    if (scenarios.length >= 3) return;
    const nextIdx = scenarios.length + 1;
    const newScen: SavedScenario = {
      id: `scenario-${Date.now()}`,
      name: `Scenario ${String.fromCharCode(64 + nextIdx)}`,
      ownCapital: baselineOwnCapital,
      desiredLoan: baselineDesiredLoan,
      financials: { ...baselineFin },
      isSaved: false,
    };
    setScenarios((prev) => [...prev, newScen]);
    setActiveScenarioId(newScen.id);
  };

  const handleDeleteScenario = (id: string) => {
    if (scenarios.length <= 1) return;
    const remaining = scenarios.filter((s) => s.id !== id);
    setScenarios(remaining);
    if (activeScenarioId === id) {
      setActiveScenarioId(remaining[0].id);
    }
  };

  const handleResetScenario = () => {
    if (!activeScenario) return;
    setScenarios((prev) =>
      prev.map((s) =>
        s.id === activeScenario.id
          ? {
              ...s,
              ownCapital: baselineOwnCapital,
              desiredLoan: baselineDesiredLoan,
              financials: { ...baselineFin },
              evaluation: null,
              isSaved: false,
            }
          : s
      )
    );
  };

  const handleApplyPreset = (presetType: "conservative_demand" | "lower_loan" | "higher_fixed") => {
    if (!activeScenario) return;
    let updatedFin = { ...activeScenario.financials };
    let updatedLoan = activeScenario.desiredLoan;
    let updatedCapital = activeScenario.ownCapital;

    if (presetType === "conservative_demand") {
      updatedFin.customers_per_day = Math.max(1, Math.round(baselineFin.customers_per_day * 0.8));
    } else if (presetType === "lower_loan") {
      const loanReduction = baselineDesiredLoan * 0.3;
      updatedLoan = Math.max(0, baselineDesiredLoan - loanReduction);
      updatedCapital = baselineOwnCapital + loanReduction;
    } else if (presetType === "higher_fixed") {
      updatedFin.monthly_fixed_cost = Math.round(baselineFin.monthly_fixed_cost * 1.25);
    }

    setScenarios((prev) =>
      prev.map((s) =>
        s.id === activeScenario.id
          ? {
              ...s,
              ownCapital: updatedCapital,
              desiredLoan: updatedLoan,
              financials: updatedFin,
              evaluation: null,
              isSaved: false,
            }
          : s
      )
    );
  };

  const getDirectionBadge = (dir: ComparisonDirection) => {
    switch (dir) {
      case "IMPROVED":
        return "bg-emerald-500/15 text-emerald-300 border-emerald-500/30";
      case "WORSENED":
        return "bg-rose-500/15 text-rose-300 border-rose-500/30";
      case "UNCHANGED":
        return "bg-slate-700 text-slate-400 border-slate-600";
      default:
        return "bg-cyan-500/15 text-cyan-300 border-cyan-500/30";
    }
  };

  const getVerdictBadge = (status: string) => {
    switch (status) {
      case "PROCEED":
        return "bg-emerald-500/15 text-emerald-300 border-emerald-500/30";
      case "VALIDATE_FIRST":
        return "bg-amber-500/15 text-amber-300 border-amber-500/30";
      case "RECONSIDER":
        return "bg-rose-500/15 text-rose-300 border-rose-500/30";
      default:
        return "bg-slate-700 text-slate-400 border-slate-600";
    }
  };

  return (
    <section className="bg-[#0B1F2D] rounded-2xl border border-slate-800/80 shadow-xl shadow-slate-950/20 overflow-hidden" id="scenario-lab">
      {/* Header Banner */}
      <div className="bg-slate-900 text-white p-6 md:p-8">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-stone-300 text-xs font-semibold tracking-wider uppercase mb-1">
              <span>Decision Stress-Testing</span>
              {savedCount > 0 && (
                <span className="px-2 py-0.5 rounded-full bg-white/20 text-white text-[10px] font-bold">
                  {t("results.scenarioLab.savedScenariosCount")}: {savedCount}/3
                </span>
              )}
            </div>
            <h2 className="text-xl md:text-2xl font-black tracking-tight text-white flex items-center gap-2.5">
              <span>🧪</span> {t("results.scenarioSection.title")}
            </h2>
            <p className="mt-1 text-slate-300 text-xs md:text-sm max-w-2xl">
              {t("results.scenarioSection.subtitle")}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setIsOpen(!isOpen)}
              className="px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 bg-emerald-700 hover:bg-emerald-600 text-white shadow-sm"
              aria-expanded={isOpen}
            >
              <span>{isOpen ? t("results.scenarioSection.closeLab") : t("results.scenarioSection.openLab")}</span>
              <span>{isOpen ? "▲" : "▼"}</span>
            </button>
          </div>
        </div>

        {/* Saved Scenarios Indicator Bar */}
        <div className="mt-4 pt-4 border-t border-white/10 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-300">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-stone-300 font-semibold">{t("results.scenarioSection.savedScenariosPreview")}:</span>
            {scenarios.map((s) => (
              <span
                key={s.id}
                className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md bg-white/10 text-white text-[11px]"
              >
                <span>{s.name}</span>
                {s.isSaved && <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />}
              </span>
            ))}
          </div>
          {!isOpen && (
            <button
              type="button"
              onClick={() => setIsOpen(true)}
              className="text-emerald-400 hover:text-emerald-300 text-xs font-semibold underline"
            >
              {t("results.scenarioSection.openLab")} →
            </button>
          )}
        </div>
      </div>

      {/* Interactive Editor - Progressively Disclosed */}
      {isOpen && (
        <div className="p-6 md:p-8 space-y-8">
          <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-800">
            <div className="flex items-center gap-2">
              {scenarios.map((s) => (
                <button
                  key={s.id}
                  onClick={() => setActiveScenarioId(s.id)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all flex items-center gap-1.5 ${
                    s.id === activeScenarioId
                      ? "bg-emerald-600 text-white shadow-sm"
                      : "bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
                  }`}
                >
                  <span>{s.name}</span>
                  {s.isSaved && (
                    <span className="w-2 h-2 rounded-full bg-emerald-500" title={t("results.scenarioLab.savedBadge")} />
                  )}
                </button>
              ))}
              {scenarios.length < 3 && (
                <button
                  onClick={handleAddScenario}
                  className="px-3 py-1.5 rounded-xl text-xs font-bold bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/30 text-emerald-300 flex items-center gap-1"
                  title="Create up to 3 comparison scenarios"
                >
                  {t("results.scenarioLab.newScenario")}
                </button>
              )}
            </div>
          </div>
        {/* Scenario Editor Controls */}
        {activeScenario && (
          <div className="rounded-xl border border-slate-700/60 bg-[#0E2635] p-6">
            <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
              <div>
                <div className="flex items-center gap-2.5">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>⚙️</span> {activeScenario.name}
                  </h3>
                  {activeScenario.isSaved ? (
                    <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                      <Check className="w-3 h-3 text-emerald-400" /> {t("results.scenarioLab.savedBadge")}
                      {activeScenario.savedAt ? ` • ${new Date(activeScenario.savedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}` : ""}
                    </span>
                  ) : (
                    <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30 flex items-center gap-1">
                      ✎ {t("results.scenarioLab.draftBadge")}
                    </span>
                  )}
                </div>
                <p className="text-sm leading-relaxed text-slate-400 mt-1 max-w-xl">
                  Modifying these inputs simulates a new scenario without altering your baseline analysis.
                </p>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  onClick={handleResetScenario}
                  className="px-3 py-1.5 rounded-lg border border-slate-600 bg-[#102B3A] text-xs font-medium text-slate-300 hover:bg-slate-700"
                >
                  {t("results.scenarioLab.resetBaseline")}
                </button>
                {scenarios.length > 1 && (
                  <button
                    type="button"
                    onClick={() => handleDeleteScenario(activeScenario.id)}
                    className="px-3 py-1.5 rounded-lg border border-rose-500/30 bg-rose-500/10 text-xs font-medium text-rose-300 hover:bg-rose-500/20"
                  >
                    {t("results.scenarioLab.deleteScenario")}
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => handleEvaluateScenario(activeScenario)}
                  disabled={isEvaluating}
                  className="px-3 py-1.5 rounded-lg border border-cyan-500/30 bg-cyan-500/10 text-cyan-300 text-xs font-bold shadow-sm flex items-center gap-1.5 disabled:opacity-50"
                >
                  {isEvaluating ? (
                    <>
                      <div className="w-3.5 h-3.5 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
                      <span>{t("common.loading")}</span>
                    </>
                  ) : (
                    <span>Recalculate</span>
                  )}
                </button>
                {/* Save Scenario Action */}
                <button
                  type="button"
                  onClick={handleSaveScenario}
                  disabled={isSaving || (isMaxSavedReached && !activeScenario.isSaved)}
                  className={`px-4 py-1.5 rounded-lg text-xs font-bold shadow-sm flex items-center gap-1.5 transition-all ${
                    activeScenario.isSaved
                      ? "bg-emerald-600 hover:bg-emerald-700 text-white"
                      : "bg-indigo-600 hover:bg-indigo-700 text-white"
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                  title={isMaxSavedReached && !activeScenario.isSaved ? t("results.scenarioLab.maxScenariosReached") : t("results.scenarioLab.saveScenario")}
                >
                  {isSaving ? (
                    <>
                      <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>{t("results.scenarioLab.saving")}</span>
                    </>
                  ) : activeScenario.isSaved ? (
                    <>
                      <Check className="w-3.5 h-3.5" />
                      <span>{t("results.scenarioLab.saved")}</span>
                    </>
                  ) : (
                    <>
                      <Save className="w-3.5 h-3.5" />
                      <span>{t("results.scenarioLab.saveScenario")}</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {saveSuccessMsg && (
              <div className="mb-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
                <Check className="w-4 h-4 text-emerald-400" />
                <span>{saveSuccessMsg}</span>
              </div>
            )}

            {apiError && (
              <div className="mb-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                <span>{apiError}</span>
              </div>
            )}

            {/* Quick Test Presets */}
            <div className="mb-6 flex flex-wrap items-center gap-2">
              <span className="text-xs font-semibold text-slate-400">
                {t("results.scenarioLab.presetsTitle")}:
              </span>
              <button
                type="button"
                onClick={() => handleApplyPreset("conservative_demand")}
                className="px-2.5 py-1 rounded-md text-[11px] font-medium min-h-[44px] bg-[#102B3A] border border-slate-600 text-slate-300 hover:border-emerald-500/60 transition-colors"
              >
                📉 {t("results.scenarioLab.presetConservativeDemand")}
              </button>
              <button
                type="button"
                onClick={() => handleApplyPreset("lower_loan")}
                className="px-2.5 py-1 rounded-md text-[11px] font-medium min-h-[44px] bg-[#102B3A] border border-slate-600 text-slate-300 hover:border-emerald-500/60 transition-colors"
              >
                🛡️ {t("results.scenarioLab.presetLowerLoan")}
              </button>
              <button
                type="button"
                onClick={() => handleApplyPreset("higher_fixed")}
                className="px-2.5 py-1 rounded-md text-[11px] font-medium min-h-[44px] bg-[#102B3A] border border-slate-600 text-slate-300 hover:border-emerald-500/60 transition-colors"
              >
                🏢 {t("results.scenarioLab.presetHigherFixed")}
              </button>
            </div>

            {/* Input Groups Grid */}
            <details className="rounded-xl border border-slate-700/60 bg-[#06131F]" open={false}>
              <summary className="cursor-pointer list-none px-4 py-3 text-sm font-semibold text-slate-200 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500">
                {t("results.scenarioLab.advancedInputs")}
              </summary>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-4 pt-1">
              {/* Group 1: Financing Structure */}
              <div className="rounded-lg border border-slate-700/60 bg-[#102B3A] p-4 space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-400">
                  {t("results.scenarioLab.financingGroup")}
                </h4>
                <div>
                  <label htmlFor="scenario-own-capital" className="block text-xs font-medium text-slate-400 mb-1">
                    Own Equity Savings (₹)
                  </label>
                  <input
                    id="scenario-own-capital"
                    type="number"
                    min="0"
                    step="5000"
                    aria-label="Own Equity Savings in Rupees"
                    className="w-full text-xs rounded-lg border border-slate-600 bg-[#0B1F2D] px-3 py-1.5 text-white placeholder:text-slate-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
                    value={activeScenario.ownCapital}
                    onChange={(e) => updateActiveScenarioField("ownCapital", parseFloat(e.target.value) || 0)}
                  />
                  <span className="text-[10px] text-slate-600">Baseline: ₹{baselineOwnCapital.toLocaleString()}</span>
                </div>
                <div>
                  <label htmlFor="scenario-desired-loan" className="block text-xs font-medium text-slate-400 mb-1">
                    Desired Bank Loan (₹)
                  </label>
                  <input
                    id="scenario-desired-loan"
                    type="number"
                    min="0"
                    step="5000"
                    aria-label="Desired Bank Loan in Rupees"
                    className="w-full text-xs rounded-lg border border-slate-600 bg-[#0B1F2D] px-3 py-1.5 text-white placeholder:text-slate-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
                    value={activeScenario.desiredLoan}
                    onChange={(e) => updateActiveScenarioField("desiredLoan", parseFloat(e.target.value) || 0)}
                  />
                  <span className="text-[10px] text-slate-600">Baseline: ₹{baselineDesiredLoan.toLocaleString()}</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label htmlFor="scenario-interest-rate" className="block text-[11px] font-medium text-slate-400 mb-1">
                      Interest Rate (%)
                    </label>
                    <input
                      id="scenario-interest-rate"
                      type="number"
                      min="0"
                      max="40"
                      step="0.5"
                      aria-label="Interest Rate Percentage"
                      className="w-full text-xs rounded-lg border border-slate-600 bg-[#0B1F2D] px-2 py-1 text-white placeholder:text-slate-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
                      value={activeScenario.financials.interest_rate_pct}
                      onChange={(e) => updateActiveScenarioField("interest_rate_pct", parseFloat(e.target.value) || 0)}
                    />
                  </div>
                  <div>
                    <label htmlFor="scenario-loan-tenure" className="block text-[11px] font-medium text-slate-400 mb-1">
                      Tenure (Months)
                    </label>
                    <input
                      id="scenario-loan-tenure"
                      type="number"
                      min="6"
                      max="120"
                      step="6"
                      aria-label="Loan Tenure in Months"
                      className="w-full text-xs rounded-lg border border-slate-600 bg-[#0B1F2D] px-2 py-1 text-white placeholder:text-slate-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
                      value={activeScenario.financials.loan_tenure_months}
                      onChange={(e) => updateActiveScenarioField("loan_tenure_months", parseInt(e.target.value) || 36)}
                    />
                  </div>
                </div>
              </div>

              {/* Group 2: Business Costs & Capex */}
              <div className="rounded-lg border border-slate-700/60 bg-[#102B3A] p-4 space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-purple-300">
                  {t("results.scenarioLab.costGroup")}
                </h4>
                <div>
                  <label htmlFor="scenario-equipment-cost" className="block text-xs font-medium text-slate-400 mb-1">
                    Equipment / Machinery (₹)
                  </label>
                  <input
                    id="scenario-equipment-cost"
                    type="number"
                    min="0"
                    step="5000"
                    aria-label="Equipment and Machinery Cost in Rupees"
                    className="w-full text-xs rounded-lg border border-slate-600 bg-[#0B1F2D] px-3 py-1.5 text-white placeholder:text-slate-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
                    value={activeScenario.financials.equipment_cost}
                    onChange={(e) => updateActiveScenarioField("equipment_cost", parseFloat(e.target.value) || 0)}
                  />
                  <span className="text-[10px] text-slate-600">Baseline: ₹{baselineFin.equipment_cost.toLocaleString()}</span>
                </div>
                <div>
                  <label htmlFor="scenario-monthly-fixed-cost" className="block text-xs font-medium text-slate-400 mb-1">
                    Monthly Fixed Overhead (₹)
                  </label>
                  <input
                    id="scenario-monthly-fixed-cost"
                    type="number"
                    min="0"
                    step="1000"
                    aria-label="Monthly Fixed Overhead Cost in Rupees"
                    className="w-full text-xs rounded-lg border border-slate-600 bg-[#0B1F2D] px-3 py-1.5 text-white placeholder:text-slate-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
                    value={activeScenario.financials.monthly_fixed_cost}
                    onChange={(e) => updateActiveScenarioField("monthly_fixed_cost", parseFloat(e.target.value) || 0)}
                  />
                  <span className="text-[10px] text-slate-600">Baseline: ₹{baselineFin.monthly_fixed_cost.toLocaleString()}</span>
                </div>
                <div>
                  <label htmlFor="scenario-variable-cost" className="block text-xs font-medium text-slate-400 mb-1">
                    Variable COGS (%)
                  </label>
                  <input
                    id="scenario-variable-cost"
                    type="number"
                    min="0"
                    max="99"
                    step="5"
                    aria-label="Variable Cost Percentage"
                    className="w-full text-xs rounded-lg border border-slate-600 bg-[#0B1F2D] px-3 py-1.5 text-white placeholder:text-slate-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
                    value={activeScenario.financials.variable_cost_pct}
                    onChange={(e) => updateActiveScenarioField("variable_cost_pct", parseFloat(e.target.value) || 0)}
                  />
                  <span className="text-[10px] text-slate-600">Baseline: {baselineFin.variable_cost_pct}%</span>
                </div>
              </div>

              {/* Group 3: Demand & Pricing */}
              <div className="rounded-lg border border-slate-700/60 bg-[#102B3A] p-4 space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-teal-300">
                  {t("results.scenarioLab.demandGroup")}
                </h4>
                <div>
                  <label htmlFor="scenario-customers-day" className="block text-xs font-medium text-slate-400 mb-1">
                    Expected Daily Footfall
                  </label>
                  <input
                    id="scenario-customers-day"
                    type="number"
                    min="1"
                    step="5"
                    aria-label="Expected Daily Footfall in customers per day"
                    className="w-full text-xs rounded-lg border border-slate-600 bg-[#0B1F2D] px-3 py-1.5 text-white placeholder:text-slate-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
                    value={activeScenario.financials.customers_per_day}
                    onChange={(e) => updateActiveScenarioField("customers_per_day", parseInt(e.target.value) || 1)}
                  />
                  <span className="text-[10px] text-slate-600">Baseline: {baselineFin.customers_per_day} orders/day</span>
                </div>
                <div>
                  <label htmlFor="scenario-ticket-price" className="block text-xs font-medium text-slate-400 mb-1">
                    Average Ticket Price (₹)
                  </label>
                  <input
                    id="scenario-ticket-price"
                    type="number"
                    min="1"
                    step="5"
                    aria-label="Average Ticket Price in Rupees"
                    className="w-full text-xs rounded-lg border border-slate-600 bg-[#0B1F2D] px-3 py-1.5 text-white placeholder:text-slate-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
                    value={activeScenario.financials.avg_ticket_price}
                    onChange={(e) => updateActiveScenarioField("avg_ticket_price", parseFloat(e.target.value) || 1)}
                  />
                  <span className="text-[10px] text-slate-600">Baseline: ₹{baselineFin.avg_ticket_price}</span>
                </div>
                <div>
                  <label htmlFor="scenario-working-days" className="block text-xs font-medium text-slate-400 mb-1">
                    Working Days / Month
                  </label>
                  <input
                    id="scenario-working-days"
                    type="number"
                    min="1"
                    max="31"
                    step="1"
                    aria-label="Working Days per Month"
                    className="w-full text-xs rounded-lg border border-slate-600 bg-[#0B1F2D] px-3 py-1.5 text-white placeholder:text-slate-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
                    value={activeScenario.financials.working_days_per_month}
                    onChange={(e) => updateActiveScenarioField("working_days_per_month", parseInt(e.target.value) || 26)}
                  />
                  <span className="text-[10px] text-slate-600">Baseline: {baselineFin.working_days_per_month} days</span>
                </div>
              </div>
            </div>
            </details>
          </div>
        )}

        {/* Side-by-Side Comparison Results */}
        {activeScenario?.evaluation && (
          <div className="space-y-6" role="status" aria-live="polite">
            {/* Verdict Comparison Banner */}
            <div className="rounded-xl border border-slate-700/60 bg-[#0E2635] p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <span className="text-xs uppercase tracking-wider text-cyan-400 font-bold block mb-1">
                  Recommendation Outcome
                </span>
                <div className="flex items-center gap-3">
                  <span className={`px-3 py-1 text-xs font-bold rounded-full border ${getVerdictBadge(activeScenario.evaluation.baseline_status)}`}>
                    Baseline: {activeScenario.evaluation.baseline_status}
                  </span>
                  <span className="text-slate-600 text-sm">&rarr;</span>
                  <span className={`px-3 py-1 text-xs font-bold rounded-full border ${getVerdictBadge(activeScenario.evaluation.scenario_status)}`}>
                    {activeScenario.name}: {activeScenario.evaluation.scenario_status}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-2">
                  {activeScenario.evaluation.recommendation_change.summary}
                </p>
              </div>

              {activeScenario.evaluation.recommendation_change.changed && (
                <div className="px-3.5 py-2 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-semibold">
                  Rule Trigger Shifted Verdict
                </div>
              )}
            </div>

            {/* Comparison Table */}
            <div className="rounded-xl border border-slate-700/60 overflow-hidden">
              <div className="bg-[#06131F] px-6 py-3 border-b border-slate-800 flex justify-between items-center">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                  {t("results.scenarioLab.comparisonTableTitle")}
                </h4>
                <span className="text-[11px] text-slate-500">
                  Computed via authoritative FinancialService
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#06131F] text-slate-500 uppercase font-mono text-[10px] border-b border-slate-800">
                    <tr>
                      <th className="px-6 py-3">{t("results.scenarioLab.metricCol")}</th>
                      <th className="px-6 py-3">{t("results.scenarioLab.baselineCol")}</th>
                      <th className="px-6 py-3">{activeScenario.name}</th>
                      <th className="px-6 py-3">{t("results.scenarioLab.deltaCol")}</th>
                      <th className="px-6 py-3">% Shift</th>
                      <th className="px-6 py-3">Effect</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 bg-[#0B1F2D]">
                    {activeScenario.evaluation.metric_comparisons.map((m: MetricComparison) => (
                      <tr key={m.metric_key} className="hover:bg-[#0E2635]">
                        <td className="px-6 py-3 font-semibold text-white">
                          <div className="flex items-center gap-1.5">
                            <span>{m.metric_name}</span>
                            <button
                              type="button"
                              onClick={() => handleInspectMetric(m.metric_key, true)}
                              className="text-slate-600 hover:text-emerald-400 p-0.5 rounded transition-colors"
                              title={t("results.explainNumber.explainButtonLabel")}
                              aria-label={`${t("results.explainNumber.explainButtonLabel")}: ${m.metric_name}`}
                            >
                              <HelpCircle className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </td>
                        <td className="px-6 py-3 text-slate-400 font-mono">
                          {m.unit === "INR" ? `₹${m.baseline_value.toLocaleString()}` : `${m.baseline_value} ${m.unit}`}
                        </td>
                        <td className="px-6 py-3 text-white font-mono font-bold">
                          {m.unit === "INR" ? `₹${m.scenario_value.toLocaleString()}` : `${m.scenario_value} ${m.unit}`}
                        </td>
                        <td className="px-6 py-3 font-mono">
                           <span className={m.absolute_change > 0 ? "text-emerald-400" : (m.absolute_change < 0 ? "text-rose-400" : "text-slate-500")}>
                            {m.absolute_change > 0 ? "+" : ""}{m.unit === "INR" ? `₹${m.absolute_change.toLocaleString()}` : `${m.absolute_change} ${m.unit}`}
                          </span>
                        </td>
                        <td className="px-6 py-3 font-mono text-slate-500">
                          {m.percentage_change !== null && m.percentage_change !== undefined
                            ? `${m.percentage_change > 0 ? "+" : ""}${m.percentage_change}%`
                            : "N/A"}
                        </td>
                        <td className="px-6 py-3">
                          <span className={`px-2 py-0.5 text-[10px] font-bold rounded-md border ${getDirectionBadge(m.direction)}`}>
                            {m.direction}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* "What changed?" & "Why did it change?" Dual Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* What Changed */}
              <div className="rounded-xl border border-slate-700/60 bg-[#0E2635] p-5 space-y-3">
                <h4 className="text-sm font-bold text-white flex items-center gap-2">
                  <span>📊</span> {t("results.scenarioLab.whatChangedTitle")}
                </h4>
                <ul className="space-y-2 text-xs text-slate-400">
                  {activeScenario.evaluation.what_changed.map((item, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-slate-600 mt-0.5">&bull;</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Why Did It Change */}
              <div className="rounded-xl border border-slate-700/60 bg-[#0E2635] p-5 space-y-3">
                <h4 className="text-sm font-bold text-white flex items-center gap-2">
                  <span>💡</span> {t("results.scenarioLab.whyChangedTitle")}
                </h4>
                <ul className="space-y-2 text-xs text-slate-400">
                  {activeScenario.evaluation.why_it_changed.map((item, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-emerald-500 font-bold mt-0.5">&rsaquo;</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Safety & Immutability Disclaimer */}
            <div className="p-4 bg-[#06131F] border border-slate-800 rounded-xl text-slate-400 text-xs flex items-start gap-3">
              <svg className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <strong className="text-slate-300">Simulation Notice:</strong> {activeScenario.evaluation.disclaimer} All scenario calculations are exploratory unit economic tests. They do not alter your baseline analysis or external evidence.
              </div>
            </div>
          </div>
        )}
        </div>
      )}

      {/* Scenario Inspector Modal */}
      <ExplainNumberModal
        explanation={activeExplanation}
        isOpen={activeExplanation !== null}
        onClose={() => setActiveExplanation(null)}
      />
    </section>
  );
};
