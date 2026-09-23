"use client";

import React from "react";

interface BreakEvenChartProps {
  breakEvenUnitsDaily: number;
  expectedDailyUnits?: number;
}

export const BreakEvenChart: React.FC<BreakEvenChartProps> = ({
  breakEvenUnitsDaily,
  expectedDailyUnits,
}) => {
  const hasTarget = expectedDailyUnits !== undefined && expectedDailyUnits > 0;
  const target = hasTarget ? expectedDailyUnits : 0;
  const safetyBuffer = hasTarget ? target - breakEvenUnitsDaily : 0;
  const isSafe = hasTarget ? safetyBuffer >= 0 : false;

  const maxScale = Math.max(breakEvenUnitsDaily, target, 1);
  const breakEvenPct = Math.min(100, (breakEvenUnitsDaily / maxScale) * 100);

  return (
    <div className="p-4 bg-[#0E2635] rounded-xl border border-slate-700/60 space-y-3">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
        <h4 className="text-sm font-bold text-white">Daily Break-Even Volume Analysis</h4>
        <span className="text-xs text-slate-500">
          Threshold: <strong className="text-slate-200">{breakEvenUnitsDaily} orders/day</strong>
        </span>
      </div>

      {hasTarget ? (
        <>
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>
              Break-Even: <strong className="text-slate-200">{breakEvenUnitsDaily} orders/day</strong>
            </span>
            <span>
              Target Volume: <strong className="text-slate-200">{target} orders/day</strong>
            </span>
          </div>

          <div className="w-full bg-slate-800 h-3 rounded-full overflow-hidden flex shadow-inner">
            <div
              className="bg-amber-500 h-full transition-all"
              style={{ width: `${(Math.min(breakEvenUnitsDaily, target) / Math.max(target, breakEvenUnitsDaily, 1)) * 100}%` }}
              title={`Break-Even: ${breakEvenUnitsDaily} orders/day`}
            />
            {isSafe && (
              <div
                className="bg-emerald-500 h-full transition-all"
                style={{ width: `${((target - breakEvenUnitsDaily) / Math.max(target, breakEvenUnitsDaily, 1)) * 100}%` }}
                title={`Profit Cushion: +${safetyBuffer} orders/day`}
              />
            )}
          </div>

          <p className="text-xs text-slate-400">
            {isSafe
              ? `Operating at a daily safety cushion of +${safetyBuffer} orders above break-even point.`
              : `Deficit: Projected demand is ${Math.abs(safetyBuffer)} orders below break-even threshold.`}
          </p>
        </>
      ) : (
        <div className="text-xs text-slate-400 space-y-1">
          <p>
            The enterprise requires a minimum of <strong className="text-slate-200">{breakEvenUnitsDaily} orders/day</strong> to cover all fixed operating expenses and loan EMI.
          </p>
          <p className="text-slate-600 italic text-[11px]">
            (Target daily customer count was not specified in the initial assumptions.)
          </p>
        </div>
      )}
    </div>
  );
};
