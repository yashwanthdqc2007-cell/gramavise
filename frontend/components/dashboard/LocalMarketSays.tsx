"use client";

import React, { useState } from "react";
import { MarketResult, EvidenceItem } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";
import { formatCurrencyINR } from "@/lib/utils";
import { Users, Store, Tag, ChevronDown, ChevronUp, ExternalLink } from "lucide-react";

interface LocalMarketSaysProps {
  market: MarketResult;
  evidenceList?: EvidenceItem[];
}

export const LocalMarketSays: React.FC<LocalMarketSaysProps> = ({
  market,
  evidenceList = [],
}) => {
  const { t } = useTranslation();
  const [expandedDetails, setExpandedDetails] = useState<Record<string, boolean>>({});

  const toggleDetails = (key: string) => {
    setExpandedDetails((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const geo = market.geography;
  const demo = market.demographics;
  const udyam = market.udyam_context;
  const priceBenchmark = market.price_benchmark;
  const priceObs = market.price_observations?.[0];
  const modalOrMedianPrice = priceObs?.modal_price ?? priceBenchmark?.median_price;
  const priceUnit = priceObs?.price_unit ?? priceBenchmark?.unit ?? "unit";
  const commodityName = priceObs?.commodity ?? priceBenchmark?.category;
  const marketLocation = priceObs?.market_name ?? priceBenchmark?.market_name;

  const directCount = market.direct_competitor_count ?? market.competitor_count ?? 0;
  const adjacentCount = market.adjacent_competitor_count ?? 0;
  const radius = market.catchment_radius_km ?? 5;

  const demandEvidence = evidenceList.find((e) => e.indicator.toLowerCase().includes("population") || e.indicator.toLowerCase().includes("demand"));
  const competitorEvidence = evidenceList.find((e) => e.indicator.toLowerCase().includes("competitor"));
  const mandiEvidence = evidenceList.find((e) => e.indicator.toLowerCase().includes("mandi") || e.indicator.toLowerCase().includes("price"));

  const renderEvidenceExpander = (key: string, ev?: EvidenceItem) => {
    const sourceUrl = ev?.source_url || priceBenchmark?.source_url || geo?.source_url;
    const sourceTitle = ev?.source_title || ev?.source || priceBenchmark?.source || geo?.source;
    if (!ev && !sourceUrl) return null;
    const isExpanded = !!expandedDetails[key];
    const confidenceBasis = ev?.confidence_explanation;
    const limitations = ev?.limitations;

    return (
      <div className="pt-2">
        <button
          type="button"
          onClick={() => toggleDetails(key)}
          className="text-[11px] font-medium text-stone-500 hover:text-slate-900 inline-flex items-center gap-1 transition-colors"
        >
          <span>{isExpanded ? t("results.localMarket.hideEvidenceDetails") : t("results.localMarket.viewEvidenceDetails")}</span>
          {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>

        {isExpanded && (
          <div className="mt-2 p-3 rounded-lg bg-stone-50 border border-stone-200/80 text-[11px] text-slate-700 space-y-1.5 font-sans">
            {confidenceBasis && (
              <div>
                <strong className="text-slate-900">{t("results.localMarket.confidenceBasis")}:</strong> {confidenceBasis}
              </div>
            )}
            {limitations && (
              <div className="text-amber-800">
                <strong>{t("results.localMarket.limitations")}:</strong> {limitations}
              </div>
            )}
            <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-stone-200 text-stone-500 text-[10px]">
              {sourceTitle && (
                <span>
                  {t("results.localMarket.source")}: <strong className="text-slate-700">{sourceTitle}</strong>
                </span>
              )}
              {sourceUrl && (
                <a
                  href={sourceUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-emerald-700 hover:text-emerald-900 font-semibold inline-flex items-center gap-1 underline"
                >
                  {t("results.localMarket.officialSource")}
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <section className="bg-white rounded-2xl border border-stone-200/80 p-6 md:p-7 shadow-sm space-y-6" id="local-market-says">
      {/* Header */}
      <div className="border-b border-stone-100 pb-3">
        <h2 className="text-xl font-black text-slate-900 tracking-tight">
          {t("results.localMarket.title")}
        </h2>
        <p className="text-xs md:text-sm text-slate-600 mt-1">
          {t("results.localMarket.subtitle")}
        </p>
      </div>

      {/* 3 Compact Groups */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* 1. Demand Group */}
        <div className="p-4 rounded-xl border border-stone-200/80 bg-stone-50/40 space-y-3 flex flex-col justify-between">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <Users className="w-3.5 h-3.5 text-blue-600" />
                {t("results.localMarket.demandGroup")}
              </span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-blue-50 text-blue-800 border border-blue-200">
                {market.demand_indicator}
              </span>
            </div>

            <div className="text-lg font-black text-slate-900">
              {demo?.population ? `${demo.population.toLocaleString()} residents` : geo?.village_name || market.location_summary.split(",")[0]}
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              {demo?.households ? `${demo.households.toLocaleString()} local households (Census 2011)` : "Demographics verified from local catchment."}
              {udyam?.registered_msme_count ? ` • ${udyam.registered_msme_count.toLocaleString()} registered MSMEs in district.` : udyam?.micro_count ? ` • ${udyam.micro_count.toLocaleString()} micro units in district.` : ""}
            </p>
          </div>

          {renderEvidenceExpander("demand", demandEvidence)}
        </div>

        {/* 2. Competition Group */}
        <div className="p-4 rounded-xl border border-stone-200/80 bg-stone-50/40 space-y-3 flex flex-col justify-between">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <Store className="w-3.5 h-3.5 text-emerald-600" />
                {t("results.localMarket.competitionGroup")}
              </span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200">
                {radius} km Radius
              </span>
            </div>

            <div className="text-lg font-black text-slate-900">
              {directCount} Direct Competitor{directCount === 1 ? "" : "s"}
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              {adjacentCount > 0
                ? `${adjacentCount} adjacent trade businesses mapped in immediate village cluster.`
                : "Mapped within immediate catchment via OpenStreetMap directory."}
            </p>
          </div>

          {renderEvidenceExpander("competition", competitorEvidence)}
        </div>

        {/* 3. Pricing Group */}
        <div className="p-4 rounded-xl border border-stone-200/80 bg-stone-50/40 space-y-3 flex flex-col justify-between">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <Tag className="w-3.5 h-3.5 text-amber-600" />
                {t("results.localMarket.pricingGroup")}
              </span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200">
                Agmarknet
              </span>
            </div>

            <div className="text-lg font-black text-slate-900">
              {modalOrMedianPrice
                ? `${formatCurrencyINR(modalOrMedianPrice)} / ${priceUnit}`
                : "Local Commodity Reference"}
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              {commodityName
                ? `${commodityName} benchmark at ${marketLocation || "APMC Mandi"}`
                : "Wholesale benchmark prices tracked from nearest state agricultural market."}
            </p>
          </div>

          {renderEvidenceExpander("pricing", mandiEvidence)}
        </div>
      </div>
    </section>
  );
};
