import React from "react";
import { CompetitorDetail, CompetitorInfo } from "@/lib/types";

interface CompetitorListProps {
  competitors?: CompetitorDetail[];
  legacyCompetitors?: CompetitorInfo[];
  catchmentRadiusKm?: number;
}

export const CompetitorList: React.FC<CompetitorListProps> = ({
  competitors = [],
  legacyCompetitors = [],
  catchmentRadiusKm = 5
}) => {
  // If structured competitors are available, use them
  if (competitors && competitors.length > 0) {
    return (
      <div className="space-y-2">
        <div className="divide-y divide-gray-100">
          {competitors.slice(0, 8).map((c, i) => (
            <div key={c.competitor_id || i} className="py-2 flex items-start justify-between text-xs gap-2">
              <div className="space-y-0.5 min-w-0">
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className="font-semibold text-gray-800 truncate">{c.business_name}</span>
                  <span
                    className={`text-[9px] font-bold px-1.5 py-0.2 rounded uppercase ${
                      c.relationship === "DIRECT"
                        ? "bg-blue-100 text-blue-800 border border-blue-200"
                        : "bg-gray-100 text-gray-600 border border-gray-200"
                    }`}
                  >
                    {c.relationship || "DIRECT"}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-[10px] text-gray-500 flex-wrap">
                  <span className="capitalize">{c.subcategory ? c.subcategory.replace(/_/g, " ") : c.category}</span>
                  <span>•</span>
                  <span>Straight-line: <strong>{c.distance_km.toFixed(1)} km</strong></span>
                  {c.match_reason && (
                    <>
                      <span>•</span>
                      <span className="font-mono text-gray-400 text-[9px]">{c.match_reason}</span>
                    </>
                  )}
                </div>
              </div>
              <div className="text-right flex-shrink-0">
                {c.source_url ? (
                  <a
                    href={c.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[10px] text-emerald-700 hover:underline font-medium block"
                  >
                    OSM ↗
                  </a>
                ) : (
                  <span className="text-[10px] text-gray-400">OSM</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Legacy fallback if available
  if (legacyCompetitors && legacyCompetitors.length > 0) {
    return (
      <div className="space-y-2">
        <div className="divide-y divide-gray-100">
          {legacyCompetitors.map((c, i) => (
            <div key={i} className="py-2 flex justify-between items-center text-xs">
              <div className="space-y-0.5">
                <span className="font-medium text-gray-700">{c.name}</span>
                <span className="text-[10px] text-gray-400 block capitalize">{c.category}</span>
              </div>
              <span className="text-gray-500 font-medium">{c.distance_km.toFixed(1)} km away</span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 p-2.5 rounded border border-gray-100 text-xs text-gray-500 italic">
      No mapped commercial units in OpenStreetMap within {catchmentRadiusKm} km catchment. Physical on-ground survey required.
    </div>
  );
};
