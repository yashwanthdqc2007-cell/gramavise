"use client";

import React from "react";
import { Input } from "@/components/ui/Input";
import { FinancialAssumptions } from "@/lib/types";

interface FinancialFormProps {
  financials: FinancialAssumptions;
  ownCapital: number;
  desiredLoan: number;
  onChangeFinancials: (financials: FinancialAssumptions) => void;
  onChangeCapital: (fields: { own_capital?: number; desired_loan?: number }) => void;
}

export const FinancialForm: React.FC<FinancialFormProps> = ({
  financials,
  ownCapital,
  desiredLoan,
  onChangeFinancials,
  onChangeCapital,
}) => {
  // TODO [Frontend Lead]: Add interactive sliders and real-time Capex summation
  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900">Capital & Operational Assumptions</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          label="Available Own Capital (INR)"
          type="number"
          value={ownCapital || ""}
          onChange={(e) => onChangeCapital({ own_capital: parseFloat(e.target.value) || 0 })}
        />
        <Input
          label="Desired Bank Loan (INR)"
          type="number"
          value={desiredLoan || ""}
          onChange={(e) => onChangeCapital({ desired_loan: parseFloat(e.target.value) || 0 })}
        />
      </div>

      <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wider">Initial Setup (Capex)</h4>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Input
          label="Setup & Civil Work (INR)"
          type="number"
          value={financials.startup_cost || ""}
          onChange={(e) => onChangeFinancials({ ...financials, startup_cost: parseFloat(e.target.value) || 0 })}
        />
        <Input
          label="Machinery / Tools (INR)"
          type="number"
          value={financials.equipment_cost || ""}
          onChange={(e) => onChangeFinancials({ ...financials, equipment_cost: parseFloat(e.target.value) || 0 })}
        />
        <Input
          label="Initial Stock / Inventory (INR)"
          type="number"
          value={financials.inventory_cost || ""}
          onChange={(e) => onChangeFinancials({ ...financials, inventory_cost: parseFloat(e.target.value) || 0 })}
        />
      </div>

      <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wider">Unit Economics & Sales</h4>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Input
          label="Expected Customers / Day"
          type="number"
          value={financials.customers_per_day || ""}
          onChange={(e) => onChangeFinancials({ ...financials, customers_per_day: parseInt(e.target.value) || 0 })}
        />
        <Input
          label="Average Ticket / Price (INR)"
          type="number"
          value={financials.avg_ticket_price || ""}
          onChange={(e) => onChangeFinancials({ ...financials, avg_ticket_price: parseFloat(e.target.value) || 0 })}
        />
        <Input
          label="Monthly Fixed Overheads (INR)"
          type="number"
          value={financials.monthly_fixed_cost || ""}
          onChange={(e) => onChangeFinancials({ ...financials, monthly_fixed_cost: parseFloat(e.target.value) || 0 })}
        />
      </div>
    </div>
  );
};
