import React from "react";
import { CompetitorInfo } from "@/lib/types";

interface CompetitorListProps {
  competitors: CompetitorInfo[];
}

export const CompetitorList: React.FC<CompetitorListProps> = ({ competitors }) => {
  return (
    <div className="space-y-2">
      <h4 className="text-sm font-semibold text-gray-800">Nearby Commercial Units</h4>
      {competitors.length === 0 ? (
        <p className="text-xs text-gray-500">No registered competitors within 5km radius.</p>
      ) : (
        <div className="divide-y divide-gray-100">
          {competitors.map((c, i) => (
            <div key={i} className="py-2 flex justify-between items-center text-xs">
              <span className="font-medium text-gray-700">{c.name}</span>
              <span className="text-gray-400">{c.distance_km.toFixed(1)} km away</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
