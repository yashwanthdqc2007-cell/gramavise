"use client";

import React from "react";

export const SensitivityChart: React.FC = () => {
  // TODO [Frontend Lead]: Render dynamic scenario bar charts (Baseline vs Demand Dip vs Cost Shock)
  return (
    <div className="p-4 bg-gray-50 rounded-xl border border-gray-100">
      <h4 className="text-sm font-semibold text-gray-800 mb-2">Sensitivity & Stress Testing</h4>
      <p className="text-xs text-gray-500">
        Stress-testing projections against -20% footfall shock and +15% raw material cost increases.
      </p>
    </div>
  );
};
