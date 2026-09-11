import React from "react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  label: string;
  value: string;
  subtitle?: string;
  isPositive?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subtitle,
  isPositive,
}) => {
  return (
    <div className="bg-gray-50 rounded-xl p-3 border border-gray-100">
      <span className="text-xs text-gray-500 font-medium block truncate">{label}</span>
      <span
        className={cn(
          "text-lg font-bold block mt-1",
          isPositive !== undefined
            ? isPositive
              ? "text-brand-700"
              : "text-rose-600"
            : "text-gray-900"
        )}
      >
        {value}
      </span>
      {subtitle && <span className="text-[11px] text-gray-400 block mt-0.5">{subtitle}</span>}
    </div>
  );
};
