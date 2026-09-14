"use client";

import React from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { CompetitorList } from "@/components/market/CompetitorList";
import { MarketResult } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";

interface MarketSnapshotProps {
  market: MarketResult;
}

export const MarketSnapshot: React.FC<MarketSnapshotProps> = ({ market }) => {
  const { t } = useTranslation();
  const geo = market.geography;
  const demo = market.demographics;
  const udyam = market.udyam_context;
  const directCount = market.direct_competitor_count ?? market.competitor_count ?? 0;
  const adjacentCount = market.adjacent_competitor_count ?? 0;
  const catchmentRadius = market.catchment_radius_km ?? market.catchment?.radius_km ?? 5;

  return (
    <Card className="space-y-4">
      {/* 1. Official Geographic & Demographic Evidence Header */}
      <div className="flex items-center justify-between border-b border-gray-100 pb-2.5">
        <div>
          <h3 className="text-base font-bold text-gray-900">{t("results.market.title")}</h3>
          <span className="text-[10px] uppercase font-bold text-emerald-700 bg-emerald-100 px-1.5 py-0.5 rounded">
            Official Data (LGD & Census 2011)
          </span>
        </div>
        <Badge
          variant={
            market.demand_indicator === "HIGH"
              ? "success"
              : market.demand_indicator === "MEDIUM"
              ? "warning"
              : "neutral"
          }
        >
          Demand Context: {market.demand_indicator}
        </Badge>
      </div>

      {/* 2. LGD & Census 2011 Verified Attributes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 bg-gray-50 p-3 rounded-lg border border-gray-100 text-xs">
        {/* Geography (LGD) */}
        <div className="space-y-1">
          <div className="flex items-center justify-between">
            <span className="font-bold text-gray-800 uppercase tracking-wider text-[10px]">
              Administrative Identity (LGD)
            </span>
            <span
              className={`text-[9px] font-bold px-1.5 py-0.2 rounded ${
                geo?.village_lgd_code
                  ? "bg-emerald-100 text-emerald-800"
                  : "bg-amber-100 text-amber-800"
              }`}
            >
              {geo?.village_lgd_code ? "LGD Verified" : "Needs Field Verification"}
            </span>
          </div>
          <p className="text-gray-900 font-medium">
            {geo?.village_name || market.location_summary.split(",")[0]}, {geo?.district_name || market.location_summary.split(",")[1]}, {geo?.state_name || market.location_summary.split(",")[2]}
          </p>
          {geo?.village_lgd_code ? (
            <p className="text-[11px] text-gray-600">
              Village LGD: <code className="bg-gray-200 px-1 rounded text-gray-800 font-mono">{geo.village_lgd_code}</code> · District LGD: <code className="bg-gray-200 px-1 rounded text-gray-800 font-mono">{geo.district_lgd_code}</code>
            </p>
          ) : (
            <p className="text-[10px] text-gray-500 italic">
              Village identity outside checked-in LGD snapshot.
            </p>
          )}
          <p className="text-[9px] text-gray-400">
            Source: Ministry of Panchayati Raj / Local Government Directory
          </p>
        </div>

        {/* Demographics (Census 2011) */}
        <div className="space-y-1 border-t md:border-t-0 md:border-l border-gray-200 pt-2 md:pt-0 md:pl-3">
          <div className="flex items-center justify-between">
            <span className="font-bold text-gray-800 uppercase tracking-wider text-[10px]">
              Demographics (Census 2011)
            </span>
            <span className="text-[9px] font-bold bg-blue-100 text-blue-800 px-1.5 py-0.2 rounded">
              Ref Year: 2011
            </span>
          </div>
          {demo && demo.population !== undefined ? (
            <>
              <p className="text-gray-900 font-medium">
                Population: <strong className="text-gray-900">{demo.population.toLocaleString("en-IN")}</strong> residents
                {demo.households !== undefined && (
                  <span className="text-gray-600 font-normal"> · {demo.households.toLocaleString("en-IN")} households</span>
                )}
              </p>
              <p className="text-[9px] text-gray-400">
                Source: Office of the Registrar General & Census Commissioner, India
              </p>
            </>
          ) : (
            <p className="text-[10px] text-gray-500 italic">
              Village demographic count outside checked-in Census 2011 snapshot.
            </p>
          )}
          <p className="text-[9px] text-amber-700 italic font-medium">
            * Population figures are from Census 2011 and are not current population estimates.
          </p>
        </div>
      </div>

      {/* 3. Official Agricultural Mandi Price Evidence (Agmarknet / OGD) */}
      <div className="pt-2 border-t border-gray-100 space-y-2">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-xs font-bold text-gray-800 uppercase tracking-wider">
              Market Price Evidence (Mandi Wholesale)
            </h4>
            <span className="text-[9px] text-gray-500 font-medium">
              Source: Directorate of Marketing & Inspection / OGD (Agmarknet)
            </span>
          </div>
          <span
            className={`text-[9px] uppercase font-bold px-1.5 py-0.5 rounded ${
              market.price_benchmark?.median_price !== undefined && market.price_benchmark?.median_price !== null
                ? "text-emerald-700 bg-emerald-100"
                : "text-amber-800 bg-amber-100"
            }`}
          >
            {market.price_benchmark?.median_price !== undefined && market.price_benchmark?.median_price !== null
              ? "OBSERVED · HIGH"
              : "NEEDS VERIFICATION"}
          </span>
        </div>

        {market.price_benchmark?.median_price !== undefined && market.price_benchmark?.median_price !== null ? (
          <div className="bg-emerald-50/50 p-3 rounded-lg border border-emerald-100 text-xs space-y-2">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              <div>
                <span className="text-[10px] text-gray-500 uppercase block font-semibold">Commodity</span>
                <span className="text-gray-900 font-bold">
                  {market.price_benchmark.category}
                  {market.price_benchmark.variety ? ` (${market.price_benchmark.variety})` : ""}
                </span>
              </div>
              <div>
                <span className="text-[10px] text-gray-500 uppercase block font-semibold">Reported Mandi</span>
                <span className="text-gray-900 font-medium">
                  {market.price_benchmark.market_name || "APMC Market"}
                </span>
              </div>
              <div>
                <span className="text-[10px] text-gray-500 uppercase block font-semibold">Observed Date</span>
                <span className="text-gray-900 font-medium">
                  {market.price_benchmark.arrival_date || "Observed in Source"}
                </span>
              </div>
              <div>
                <span className="text-[10px] text-gray-500 uppercase block font-semibold">Modal Price</span>
                <span className="text-emerald-900 font-bold">
                  ₹{market.price_benchmark.median_price.toLocaleString("en-IN")} / {market.price_benchmark.unit || "quintal"}
                  {market.price_benchmark.price_per_kg ? (
                    <span className="text-[10px] text-emerald-700 font-normal block">
                      (₹{market.price_benchmark.price_per_kg.toFixed(2)} / kg)
                    </span>
                  ) : null}
                </span>
              </div>
            </div>

            {market.price_benchmark.low_price !== undefined && market.price_benchmark.high_price !== undefined && (
              <div className="flex items-center justify-between text-[11px] pt-1 border-t border-emerald-100/60 text-gray-700">
                <span>
                  Reported Price Range: <strong>₹{market.price_benchmark.low_price.toLocaleString("en-IN")}</strong> – <strong>₹{market.price_benchmark.high_price.toLocaleString("en-IN")}</strong> / {market.price_benchmark.unit || "quintal"}
                </span>
                <a
                  href={market.price_benchmark.source_url || "https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi"}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[10px] text-emerald-700 hover:underline font-medium"
                >
                  Verify on Agmarknet / OGD ↗
                </a>
              </div>
            )}

            <p className="text-[10px] text-amber-900 bg-amber-50/80 p-1.5 rounded border border-amber-200/60 font-medium">
              Important: Market prices are mandi wholesale observations and are not retail selling-price recommendations.
            </p>
          </div>
        ) : (
          <div className="bg-gray-50 p-2.5 rounded-lg border border-gray-100 text-[11px] text-gray-600 space-y-1">
            <p>
              Commodity price feed for <strong>{market.price_benchmark?.category || "this category"}</strong> is outside the checked-in verified Agmarknet mandi snapshot.
            </p>
            <p className="text-[10px] text-gray-500 italic">
              On-ground wholesale APMC inquiry required. Market observations do not dictate entrepreneur retail selling price.
            </p>
          </div>
        )}
      </div>

      {/* 4. Nearby Commercial POIs & Competitor Evidence (OpenStreetMap / Overpass) */}
      <div className="pt-2 border-t border-gray-100 space-y-2.5">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-xs font-bold text-gray-800 uppercase tracking-wider">
              Nearby Competition (OpenStreetMap)
            </h4>
            <span className="text-[9px] text-gray-500 font-medium">
              Catchment: {catchmentRadius} km straight-line radius · Source: OpenStreetMap (Overpass)
            </span>
          </div>
          <span
            className={`text-[9px] uppercase font-bold px-1.5 py-0.5 rounded ${
              directCount > 0
                ? "text-blue-700 bg-blue-100"
                : "text-amber-800 bg-amber-100"
            }`}
          >
            {directCount > 0 ? `OBSERVED · ${directCount} DIRECT` : "NEEDS VERIFICATION · 0 MAPPED"}
          </span>
        </div>

        <div className="bg-blue-50/40 p-3 rounded-lg border border-blue-100/70 text-xs space-y-2">
          <div className="flex items-center justify-between text-gray-700">
            <div>
              <span className="font-semibold text-gray-900">Mapped Direct Competitors:</span>{" "}
              <strong className="text-blue-900 text-sm">{directCount}</strong>
              {adjacentCount > 0 && (
                <span className="text-gray-500 text-[11px] ml-1.5">
                  ({adjacentCount} adjacent category units)
                </span>
              )}
            </div>
            <a
              href="https://www.openstreetmap.org/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[10px] text-blue-700 hover:underline font-medium"
            >
              OpenStreetMap ↗
            </a>
          </div>

          {/* Competitor List */}
          <CompetitorList
            competitors={market.competitors}
            legacyCompetitors={market.competitor_list}
            catchmentRadiusKm={catchmentRadius}
          />

          {/* Coverage Warning Disclaimer */}
          <p className="text-[10px] text-amber-900 bg-amber-50/90 p-2 rounded border border-amber-200/60 leading-relaxed font-medium">
            <strong>Coverage Notice:</strong> Competition is based on mapped OpenStreetMap locations within the configured {catchmentRadius} km catchment. Rural and informal businesses may be missing. A low mapped count does not prove low competition.
          </p>
        </div>
      </div>

      {/* 5. Official District-Level MSME Context (Ministry of MSME / Udyam OGD) */}
      {udyam && (
        <div className="pt-2 border-t border-gray-100 space-y-2">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-xs font-bold text-gray-800 uppercase tracking-wider">
                District Business Context (Udyam MSME Registry)
              </h4>
              <span className="text-[9px] text-gray-500 font-medium">
                Source: Ministry of Micro, Small and Medium Enterprises / data.gov.in
              </span>
            </div>
            <span className="text-[9px] uppercase font-bold text-emerald-700 bg-emerald-100 px-1.5 py-0.5 rounded">
              DISTRICT CONTEXT
            </span>
          </div>

          <div className="bg-emerald-50/40 p-3 rounded-lg border border-emerald-100/70 text-xs space-y-2">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-gray-800">
              <div>
                <span className="text-[10px] text-gray-500 uppercase block font-semibold">District Formal MSMEs</span>
                <span className="text-emerald-950 font-bold text-sm">
                  {udyam.registered_msme_count.toLocaleString("en-IN")}
                </span>
              </div>
              {udyam.micro_count !== undefined && udyam.micro_count !== null && (
                <div>
                  <span className="text-[10px] text-gray-500 uppercase block font-semibold">Micro Enterprises</span>
                  <span className="text-gray-900 font-medium">
                    {udyam.micro_count.toLocaleString("en-IN")}
                  </span>
                </div>
              )}
              {udyam.small_count !== undefined && udyam.small_count !== null && (
                <div>
                  <span className="text-[10px] text-gray-500 uppercase block font-semibold">Small Enterprises</span>
                  <span className="text-gray-900 font-medium">
                    {udyam.small_count.toLocaleString("en-IN")}
                  </span>
                </div>
              )}
              {udyam.manufacturing_count !== undefined && udyam.manufacturing_count !== null && (
                <div>
                  <span className="text-[10px] text-gray-500 uppercase block font-semibold">Manufacturing Units</span>
                  <span className="text-gray-900 font-medium">
                    {udyam.manufacturing_count.toLocaleString("en-IN")}
                  </span>
                </div>
              )}
            </div>

            <div className="flex items-center justify-between text-[10px] pt-1 border-t border-emerald-100/60 text-gray-600">
              <span>
                Geography: <strong>{udyam.district_name} District, {udyam.state_name}</strong>
              </span>
              <a
                href={udyam.source_url || "https://udyamregistration.gov.in/"}
                target="_blank"
                rel="noopener noreferrer"
                className="text-emerald-700 hover:underline font-medium"
              >
                Verify on Udyam Portal ↗
              </a>
            </div>

            <p className="text-[10px] text-gray-600 bg-white/80 p-1.5 rounded border border-emerald-100 italic">
              * This is district-level formal MSME context only, not a count of nearby competitors.
            </p>
          </div>
        </div>
      )}

      {/* 6. Market Advisory Signals */}
      {market.market_signals && market.market_signals.length > 0 && (
        <div className="pt-2 border-t border-gray-100 space-y-1.5">
          <span className="text-[10px] font-bold text-gray-700 uppercase tracking-wider block">
            Advisory Market Signals:
          </span>
          <div className="flex flex-wrap gap-1.5">
            {market.market_signals.map((sig, sIdx) => (
              <span
                key={sIdx}
                className="text-[10px] font-semibold bg-gray-100 text-gray-700 px-2 py-0.5 rounded border border-gray-200"
              >
                {sig.replace(/_/g, " ")}
              </span>
            ))}
          </div>
        </div>
      )}

      {market.notes && (
        <p className="text-[10px] text-gray-500 bg-gray-50 p-2 rounded-lg border border-gray-100 italic leading-relaxed">
          {market.notes}
        </p>
      )}

      <p className="text-[9px] text-gray-400 italic">
        * Absence of market evidence is not evidence of market demand. Village population is historical from Census 2011; competitor data is from OpenStreetMap and requires on-ground physical survey.
      </p>
    </Card>
  );
};
