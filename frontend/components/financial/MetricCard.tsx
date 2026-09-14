import React from "react";
import { cn } from "@/lib/utils";
import { HelpCircle } from "lucide-react";

interface MetricCardProps {
  label: string;
  value: string;
  subtitle?: string;
  isPositive?: boolean;
  onExplain?: () => void;
  explainLabel?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subtitle,
  isPositive,
  onExplain,
  explainLabel = "Explain this calculation",
}) => {
  return (
    <div className="bg-gray-50 rounded-xl p-3 border border-gray-100 flex flex-col justify-between relative group">
      <div>
        <div className="flex items-center justify-between gap-1">
          <span className="text-xs text-gray-500 font-medium block truncate">{label}</span>
          {onExplain && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onExplain();
              }}
              className="text-gray-400 hover:text-indigo-600 p-0.5 rounded transition-colors focus:outline-none focus:ring-1 focus:ring-indigo-500"
              title={explainLabel}
              aria-label={`${explainLabel}: ${label}`}
            >
              <HelpCircle className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
        <span
          className={cn(
            "text-lg font-bold block mt-1",
            isPositive !== undefined
              ? isPositive
                ? "text-emerald-700"
                : "text-rose-600"
              : "text-gray-900"
          )}
        >
          {value}
        </span>
      </div>
      {subtitle && <span className="text-[11px] text-gray-400 block mt-1">{subtitle}</span>}
    </div>
  );
};

