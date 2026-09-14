"use client";

import React, { useState } from "react";
import { DEMO_SCENARIOS, DemoScenario } from "@/lib/demo/demoScenarios";
import { Sparkles, ChevronDown, ChevronUp, Check } from "lucide-react";

interface DemoScenarioSelectorProps {
  onSelectScenario: (scenario: DemoScenario) => void;
  activeScenarioId?: string | null;
}

export const DemoScenarioSelector: React.FC<DemoScenarioSelectorProps> = ({
  onSelectScenario,
  activeScenarioId,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [lastSelected, setLastSelected] = useState<string | null>(null);

  const handleSelect = (scen: DemoScenario) => {
    onSelectScenario(scen);
    setLastSelected(scen.name);
    setIsOpen(false);
  };

  return (
    <div className="mb-6 rounded-2xl border border-slate-800 bg-[#0B1C29]/95 backdrop-blur-xs p-3.5 shadow-lg shadow-slate-950/20">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-500/15 text-emerald-300 text-xs font-bold border border-emerald-500/25">
            ⚡
          </span>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-white tracking-tight">Demo Scenarios</span>
              <span className="rounded-full bg-slate-800 px-2 py-0.5 text-[10px] font-semibold text-slate-300 border border-slate-700">
                Evaluation Playbook
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Pre-load verified business input profiles to evaluate deterministic financial & risk outcomes.
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs font-semibold text-slate-200 hover:bg-slate-800 hover:border-emerald-500/50 transition-colors"
          aria-expanded={isOpen}
        >
          <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
          <span>{isOpen ? "Hide Profiles" : "Select Demo Profile"}</span>
          {isOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>

      {lastSelected && !isOpen && (
        <div className="mt-2 pt-2 border-t border-slate-800 flex items-center justify-between text-[11px] text-emerald-300 font-medium">
          <span>Active Input Profile: <strong>{lastSelected}</strong></span>
          <span className="text-slate-500">All fields editable below</span>
        </div>
      )}

      {isOpen && (
        <div className="mt-3 pt-3 border-t border-slate-800 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
          {DEMO_SCENARIOS.map((scen) => {
            const isSelected = activeScenarioId === scen.id || lastSelected === scen.name;

            return (
              <button
                key={scen.id}
                type="button"
                onClick={() => handleSelect(scen)}
                className={`text-left p-3 rounded-xl border transition-all flex flex-col justify-between space-y-2 ${
                  isSelected
                    ? "border-emerald-400 bg-emerald-500/10 ring-1 ring-emerald-500"
                    : "border-slate-700 bg-slate-950/40 hover:bg-slate-900 hover:border-emerald-500/50"
                }`}
              >
                <div>
                  <div className="flex items-center justify-between gap-1 mb-1">
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-md border border-emerald-500/30 bg-emerald-500/10 text-emerald-300">
                      {scen.badge}
                    </span>
                    {isSelected && <Check className="w-3.5 h-3.5 text-emerald-300" />}
                  </div>
                  <h4 className="text-xs font-bold text-white leading-tight">
                    {scen.name}
                  </h4>
                  <p className="text-[11px] text-cyan-300 font-medium mt-0.5">
                    {scen.category}
                  </p>
                  <p className="text-[10px] text-slate-400 mt-1 line-clamp-2">
                    {scen.tagline}
                  </p>
                </div>

                <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-400">
                  <span>Capex: ₹{(scen.financials.startup_cost + scen.financials.equipment_cost + scen.financials.inventory_cost).toLocaleString("en-IN")}</span>
                  <span className="font-bold text-emerald-300">Loan: ₹{scen.profile.desired_loan.toLocaleString("en-IN")}</span>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};
