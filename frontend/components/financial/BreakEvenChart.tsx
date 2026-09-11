"use client";

import React from "react";

interface BreakEvenChartProps {
  breakEvenUnitsDaily: number;
  expectedDailyUnits: number;
}

export const BreakEvenChart: React.FC<BreakEvenChartProps> = ({
  breakEvenUnitsDaily,
  expectedDailyUnits,
}) => {
  // TODO [Frontend Lead]: Replace with interactive SVG or Recharts line/area visualization
  const safetyBuffer = expectedDailyUnits - breakEvenUnitsDaily;
  const isSafe = safetyBuffer >= 0;

  return (
    <div className="p-4 bg-gray-50 rounded-xl border border-gray-100">
      <h4 className="text-sm font-semibold text-gray-800 mb-2">Break-Even Volume Comparison</h4>
      <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
        <span>Break-Even Threshold: <strong>{breakEvenUnitsDaily} orders/day</strong></span>
        <span>Target Volume: <strong>{expectedDailyUnits} orders/day</strong></span>
      </div>
      <div className="w-full bg-gray-200 h-3 rounded-full overflow-hidden flex">
        <div
          className="bg-amber-500 h-full"
          style={{ width: `${Math.min(100, (breakEvenUnitsDaily / Math.max(expectedDailyUnits, 1)) * 100)}%` }}
          title="Break-Even Threshold"
        />
        {isSafe && (
          <div
            className="bg-brand-500 h-full"
            style={{ width: `${Math.max(0, 100 - (breakEvenUnitsDaily / Math.max(expectedDailyUnits, 1)) * 100)}%` }}
            title="Profit Cushion"
          />
        )}
      </div>
      <p className="text-[11px] text-gray-500 mt-2">
        {isSafe
          ? `Operating at a daily safety cushion of +${safetyBuffer} orders above break-even.`
          : `Deficit: Projected demand is ${Math.abs(safetyBuffer)} orders below break-even point.`}
      </p>
    </div>
  );
};
