"use client";

import React from "react";
import { Card } from "@/components/ui/Card";
import { MetricCard } from "@/components/financial/MetricCard";
import { FinancialResult } from "@/lib/types";
import { formatCurrencyINR, formatPercentage } from "@/lib/utils";

interface FinancialSummaryProps {
  financials: FinancialResult;
}

export const FinancialSummary: React.FC<FinancialSummaryProps> = ({ financials }) => {
  // TODO [Frontend Lead]: Add export to PDF / project report download trigger
  return (
    <Card>
      <h3 className="text-lg font-bold text-gray-900 mb-4">Financial Structuring & Unit Economics</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard label="Total Project Cost (Capex)" value={formatCurrencyINR(financials.total_capex)} />
        <MetricCard label="Monthly Revenue" value={formatCurrencyINR(financials.monthly_revenue)} />
        <MetricCard label="Monthly Net Profit" value={formatCurrencyINR(financials.monthly_net_profit)} isPositive={financials.monthly_net_profit > 0} />
        <MetricCard label="DSCR (Debt Cover)" value={financials.dscr.toFixed(2)} isPositive={financials.dscr >= 1.5} />
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-100 text-sm">
        <div>
          <span className="text-gray-500">Monthly Loan EMI:</span>
          <span className="font-semibold text-gray-800 ml-2">{formatCurrencyINR(financials.monthly_emi)}</span>
        </div>
        <div>
          <span className="text-gray-500">Break-Even Revenue:</span>
          <span className="font-semibold text-gray-800 ml-2">{formatCurrencyINR(financials.break_even_revenue_monthly)}/mo</span>
        </div>
        <div>
          <span className="text-gray-500">Daily Break-Even Units:</span>
          <span className="font-semibold text-gray-800 ml-2">{financials.break_even_units_daily} orders/day</span>
        </div>
      </div>
    </Card>
  );
};
