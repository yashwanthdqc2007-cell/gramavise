"use client";

import React from "react";

interface MarketMapProps {
  latitude?: number;
  longitude?: number;
  village?: string;
}

export const MarketMap: React.FC<MarketMapProps> = ({ village }) => {
  // TODO [Frontend Lead]: Embed interactive OpenStreetMap / Leaflet container
  return (
    <div className="h-48 w-full bg-emerald-50 rounded-xl border border-emerald-200 flex flex-col items-center justify-center text-gray-500 text-sm">
      <span className="font-semibold text-emerald-800">Map View Placeholder</span>
      <span className="text-xs text-emerald-600 mt-1">Village Catchment: {village || "Target Location"}</span>
    </div>
  );
};
