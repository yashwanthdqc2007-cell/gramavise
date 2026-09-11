"use client";

import React from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { MarketResult } from "@/lib/types";

interface MarketSnapshotProps {
  market: MarketResult;
}

export const MarketSnapshot: React.FC<MarketSnapshotProps> = ({ market }) => {
  // TODO [Frontend Lead]: Integrate interactive Leaflet / Mapbox map container
  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">Local Market & Catchment Intelligence</h3>
        <Badge variant={market.demand_indicator === "HIGH" ? "success" : "neutral"}>
          Demand: {market.demand_indicator}
        </Badge>
      </div>
      <p className="text-sm text-gray-600 mb-2">
        <strong>Location:</strong> {market.location_summary}
      </p>
      <p className="text-sm text-gray-600 mb-2">
        <strong>Nearby Direct Competitors:</strong> {market.competitor_count} units within 5km
      </p>
      {market.notes && (
        <p className="text-xs text-gray-500 bg-gray-50 p-2.5 rounded-lg border border-gray-100">
          {market.notes}
        </p>
      )}
    </Card>
  );
};
