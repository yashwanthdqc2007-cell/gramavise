"use client";

import React, { useState } from "react";
import { MarketResult, EvidenceItem, VerificationCheckItem } from "@/lib/types";
import { EvidenceBadge } from "@/components/evidence/EvidenceBadge";
import { useTranslation } from "@/lib/i18n";
import { formatCurrencyINR } from "@/lib/utils";
import {
  Users,
  Store,
  Tag,
  Wallet,
  Calendar,
  Truck,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Info,
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  CheckCircle2,
  MapPin,
  Building2,
} from "lucide-react";

interface LocalMarketSaysProps {
  market: MarketResult;
  evidenceList?: EvidenceItem[];
  verificationChecklist?: VerificationCheckItem[];
  onOpenEvidenceDrawer?: () => void;
}

export const LocalMarketSays: React.FC<LocalMarketSaysProps> = ({
  market,
  evidenceList = [],
  verificationChecklist = [],
  onOpenEvidenceDrawer,
}) => {
  const { t } = useTranslation();
  const [expandedDetails, setExpandedDetails] = useState<Record<string, boolean>>({});
  const [showCoverageInfo, setShowCoverageInfo] = useState<boolean>(false);

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
  const arrivalDate = priceObs?.arrival_date ?? priceBenchmark?.arrival_date;
  const pricePerKg = priceObs?.price_per_kg ?? priceBenchmark?.price_per_kg;

  const directCount = market.direct_competitor_count ?? market.competitor_count ?? 0;
  const adjacentCount = market.adjacent_competitor_count ?? 0;
  const radius = market.catchment_radius_km ?? 5;
  const coverageConfidence = market.coverage_confidence ?? "LOW";

  // Market Evidence Level (from backend confidence_level)
  const confidenceLevel = market.confidence_level ?? "LOW";

  const confidenceTheme = {
    HIGH: {
      badge: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
      label: "High Coverage",
      summary: "Most key market signals have verified supporting data.",
      dotColor: "bg-emerald-400",
    },
    MEDIUM: {
      badge: "bg-amber-500/15 text-amber-300 border-amber-500/30",
      label: "Moderate Coverage",
      summary: "Useful local signals are available, but some information still needs verification.",
      dotColor: "bg-amber-400",
    },
    LOW: {
      badge: "bg-rose-500/15 text-rose-300 border-rose-500/30",
      label: "Limited Coverage",
      summary: "Market evidence is limited or location data could not be fully verified.",
      dotColor: "bg-rose-400",
    },
    UNKNOWN: {
      badge: "bg-slate-700 text-slate-300 border-slate-600",
      label: "Unverified",
      summary: "Market evidence could not be established reliably.",
      dotColor: "bg-slate-400",
    },
  }[confidenceLevel] || {
    badge: "bg-slate-700 text-slate-300 border-slate-600",
    label: "Unverified",
    summary: "Market evidence could not be established reliably.",
    dotColor: "bg-slate-400",
  };

  // Find linked evidence records
  const demandEvidence = evidenceList.find(
    (e) => e.indicator.toLowerCase().includes("catchment") || e.indicator.toLowerCase().includes("population")
  );
  const competitorEvidence = evidenceList.find((e) => e.indicator.toLowerCase().includes("competitor"));
  const mandiEvidence = evidenceList.find(
    (e) => e.indicator.toLowerCase().includes("mandi") || e.indicator.toLowerCase().includes("price")
  );
  const udyamEvidence = evidenceList.find((e) => e.indicator.toLowerCase().includes("udyam") || e.indicator.toLowerCase().includes("msme"));

  // Secondary signals
  const seasonalThreats = market.seasonal_threats || [];
  const supplyChainRisks = market.supply_chain || [];
  const purchasingPower = market.purchasing_power;

  const renderEvidenceExpander = (key: string, ev?: EvidenceItem, fallbackSourceTitle?: string, fallbackUrl?: string) => {
    const isExpanded = !!expandedDetails[key];
    const sourceTitle = ev?.source_title || ev?.source || fallbackSourceTitle;
    const sourceUrl = ev?.source_url || fallbackUrl;
    const confidenceBasis = ev?.confidence_explanation;
    const limitations = ev?.limitations;
    const notes = ev?.notes;

    if (!ev && !sourceTitle && !sourceUrl) return null;

    return (
      <div className="pt-2">
        <button
          type="button"
          onClick={() => toggleDetails(key)}
          className="text-[11px] font-medium text-slate-400 hover:text-slate-200 inline-flex items-center gap-1 transition-colors focus:outline-hidden focus:ring-1 focus:ring-emerald-400/50 rounded-sm px-1 py-0.5"
          aria-expanded={isExpanded}
        >
          <span>{isExpanded ? t("results.localMarket.hideEvidenceDetails") : t("results.localMarket.viewEvidenceDetails")}</span>
          {isExpanded ? <ChevronUp className="w-3 h-3 text-slate-400" /> : <ChevronDown className="w-3 h-3 text-slate-400" />}
        </button>

        {isExpanded && (
          <div className="mt-2.5 p-3 rounded-lg bg-[#06131F] border border-slate-800 text-[11px] text-slate-300 space-y-2 font-sans animate-in fade-in duration-100">
            {confidenceBasis && (
              <div>
                <strong className="text-slate-100">{t("results.localMarket.confidenceBasis")}:</strong>{" "}
                <span className="text-slate-300 leading-relaxed">{confidenceBasis}</span>
              </div>
            )}
            {limitations && (
              <div className="text-amber-300 bg-amber-950/30 p-2 rounded border border-amber-800/40">
                <strong className="text-amber-200">{t("results.localMarket.limitations")}:</strong> {limitations}
              </div>
            )}
            {notes && !confidenceBasis && (
              <div className="text-slate-400 italic">
                {notes}
              </div>
            )}
            <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-800 text-slate-400 text-[10px]">
              {sourceTitle && (
                <span>
                  {t("results.localMarket.source")}: <strong className="text-slate-200">{sourceTitle}</strong>
                </span>
              )}
              {sourceUrl && (
                <a
                  href={sourceUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-emerald-400 hover:text-emerald-300 font-semibold inline-flex items-center gap-1 underline underline-offset-2"
                >
                  <span>{t("results.localMarket.officialSource")}</span>
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
    <section
      className="bg-[#0B1F2D] rounded-2xl border border-slate-800/80 p-5 sm:p-7 shadow-xl shadow-slate-950/20 space-y-6 sm:space-y-8"
      id="local-market-says"
      aria-label="Local Market Intelligence"
    >
      {/* 1. Header & Evidence Coverage Bar */}
      <div className="space-y-3 border-b border-slate-800 pb-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold font-mono tracking-wider uppercase text-cyan-400 bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-800/40">
                LOCAL MARKET
              </span>
              <span className="text-xs text-slate-500 font-medium">
                • {geo?.village_name || market.location_summary.split(",")[0]}, {geo?.district_name || market.location_summary.split(",")[1] || "Local Catchment"}
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight mt-1.5">
              {t("results.localMarket.title")}
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
              {t("results.localMarket.subtitle")}
            </p>
          </div>

          {/* Market Evidence Status Pill */}
          <div className="self-start sm:self-auto flex flex-col items-start sm:items-end gap-1">
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wide">
                Market Evidence:
              </span>
              <button
                type="button"
                onClick={() => setShowCoverageInfo(!showCoverageInfo)}
                className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border transition-all ${confidenceTheme.badge} hover:brightness-110`}
                title="Click to learn about Market Evidence coverage"
                aria-expanded={showCoverageInfo}
              >
                <span className={`w-1.5 h-1.5 rounded-full ${confidenceTheme.dotColor}`} />
                <span>{confidenceTheme.label}</span>
                <Info className="w-3.5 h-3.5 opacity-80" />
              </button>
            </div>
            <span className="text-[11px] text-slate-400 max-w-xs text-left sm:text-right">
              {confidenceTheme.summary}
            </span>
          </div>
        </div>

        {/* Expandable Coverage Explanation */}
        {showCoverageInfo && (
          <div className="mt-3 p-4 rounded-xl bg-[#06131F] border border-cyan-500/30 text-xs text-slate-300 space-y-2 animate-in fade-in duration-150">
            <div className="flex items-start justify-between gap-2">
              <strong className="text-cyan-300 font-bold flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-cyan-400 shrink-0" />
                Understanding Market Evidence Coverage
              </strong>
              <button
                type="button"
                onClick={() => setShowCoverageInfo(false)}
                className="text-slate-500 hover:text-slate-300 text-xs font-bold px-1"
              >
                ✕
              </button>
            </div>
            <p className="text-slate-300 leading-relaxed">
              Market evidence coverage measures the completeness of verified data feeds (Census 2011, OpenStreetMap commercial POIs, Agmarknet mandi arrivals, and Ministry of MSME registrations).
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-2 border-t border-slate-800 text-[11px]">
              <div className="p-2 rounded bg-[#0E2635] border border-slate-800">
                <span className="text-emerald-400 font-bold block">HIGH</span>
                <span className="text-slate-400">Most key market signals have verified supporting data.</span>
              </div>
              <div className="p-2 rounded bg-[#0E2635] border border-slate-800">
                <span className="text-amber-400 font-bold block">MEDIUM</span>
                <span className="text-slate-400">Useful signals available, but some require local validation.</span>
              </div>
              <div className="p-2 rounded bg-[#0E2635] border border-slate-800">
                <span className="text-rose-400 font-bold block">LOW / UNKNOWN</span>
                <span className="text-slate-400">Limited mapped data or unverified coordinates.</span>
              </div>
            </div>
            <p className="text-[10px] text-slate-400 italic pt-1">
              Note: Market evidence coverage reflects data completeness only. It is NOT a credit score, business ranking, or guarantee of profitability.
            </p>
          </div>
        )}
      </div>

      {/* 2. Core Market Signal Cards (2x2 Grid) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-5">
        {/* Card A: Local Demand */}
        <div className="p-4 sm:p-5 rounded-xl border border-slate-700/60 bg-[#0E2635] space-y-3.5 flex flex-col justify-between hover:border-slate-600/80 transition-colors">
          <div className="space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Users className="w-3.5 h-3.5 text-cyan-400" />
                {t("results.localMarket.demandGroup")}
              </span>
              <EvidenceBadge type="MODELLED" confidence="MEDIUM" />
            </div>

            <div className="flex items-baseline gap-2">
              <div className="text-xl sm:text-2xl font-black text-white">
                {market.demand_indicator} Demand Signal
              </div>
            </div>

            <div className="text-xs text-slate-300 space-y-1 leading-relaxed">
              {demo?.population ? (
                <p>
                  <strong className="text-white">{demo.population.toLocaleString()} residents</strong> ({demo.households?.toLocaleString() || "—"} households) in official Census 2011 record.
                </p>
              ) : (
                <p>
                  Catchment demographic baseline: ~{market.catchment_population_estimate?.toLocaleString() || "4,500"} residents within {radius} km.
                </p>
              )}
              <p className="text-[11px] text-slate-400">
                Modelled demand signal based on local business density, radius geography, and population baseline.
              </p>
            </div>
          </div>

          {renderEvidenceExpander("demand", demandEvidence, "Census 2011 / GramaVise Catchment Model", demo?.source_url)}
        </div>

        {/* Card B: Local Competition */}
        <div className="p-4 sm:p-5 rounded-xl border border-slate-700/60 bg-[#0E2635] space-y-3.5 flex flex-col justify-between hover:border-slate-600/80 transition-colors">
          <div className="space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Store className="w-3.5 h-3.5 text-emerald-400" />
                {t("results.localMarket.competitionGroup")}
              </span>
              <EvidenceBadge
                type={directCount > 0 ? "OBSERVED" : "NEEDS_VERIFICATION"}
                confidence={coverageConfidence === "HIGH" ? "HIGH" : "MEDIUM"}
              />
            </div>

            <div className="flex items-baseline gap-2">
              <div className="text-xl sm:text-2xl font-black text-white">
                {directCount} Direct Mapped Unit{directCount === 1 ? "" : "s"}
              </div>
              <span className="text-xs text-slate-400">
                ({radius} km radius)
              </span>
            </div>

            <div className="text-xs text-slate-300 space-y-1 leading-relaxed">
              {directCount === 0 ? (
                <p className="text-amber-300">
                  0 mapped competitors found in OpenStreetMap. Map coverage is incomplete, so this does not confirm absence of competition.
                </p>
              ) : (
                <p>
                  {directCount} direct competing commercial POI{directCount > 1 ? "s" : ""} verified within {radius} km catchment.
                  {adjacentCount > 0 && ` (${adjacentCount} adjacent trade units).`}
                </p>
              )}
              {market.competitors && market.competitors.length > 0 && (
                <p className="text-[11px] text-slate-400">
                  Nearest mapped unit: <span className="text-slate-200 font-semibold">{market.competitors[0].business_name}</span> (~{market.competitors[0].distance_km} km away, straight-line).
                </p>
              )}
            </div>
          </div>

          {renderEvidenceExpander("competition", competitorEvidence, "OpenStreetMap / Overpass API", "https://www.openstreetmap.org/")}
        </div>

        {/* Card C: Purchasing Power Indicator */}
        <div className="p-4 sm:p-5 rounded-xl border border-slate-700/60 bg-[#0E2635] space-y-3.5 flex flex-col justify-between hover:border-slate-600/80 transition-colors">
          <div className="space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Wallet className="w-3.5 h-3.5 text-cyan-400" />
                PURCHASING POWER
              </span>
              <EvidenceBadge type="MODELLED" confidence="LOW" />
            </div>

            <div className="flex items-baseline gap-2">
              <div className="text-xl sm:text-2xl font-black text-white">
                {purchasingPower?.purchasing_power_level || (demo?.population ? "MODERATE" : "UNKNOWN")} Indicator
              </div>
            </div>

            <div className="text-xs text-slate-300 space-y-1 leading-relaxed">
              <p>
                Purchasing power indicator for {geo?.district_name || "district"} catchment.
                {purchasingPower?.affordability_level && ` Affordability status: ${purchasingPower.affordability_level}.`}
              </p>
              <p className="text-[11px] text-slate-400">
                Modelled purchasing power proxy for rural catchment; local customer price tolerance requires on-ground validation.
              </p>
            </div>
          </div>

          {renderEvidenceExpander("purchasing_power", undefined, "GramaVise Purchasing Power Proxy Model")}
        </div>

        {/* Card D: Mandi Price Reference */}
        <div className="p-4 sm:p-5 rounded-xl border border-slate-700/60 bg-[#0E2635] space-y-3.5 flex flex-col justify-between hover:border-slate-600/80 transition-colors">
          <div className="space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Tag className="w-3.5 h-3.5 text-amber-400" />
                {t("results.localMarket.pricingGroup")}
              </span>
              <EvidenceBadge
                type={priceObs ? "OBSERVED" : "NEEDS_VERIFICATION"}
                confidence={priceObs ? "HIGH" : "UNKNOWN"}
              />
            </div>

            <div className="flex items-baseline gap-2">
              <div className="text-xl sm:text-2xl font-black text-white">
                {modalOrMedianPrice ? (
                  <>
                    {formatCurrencyINR(modalOrMedianPrice)} <span className="text-xs font-normal text-slate-400">/ {priceUnit}</span>
                  </>
                ) : (
                  "Wholesale Inquiry Required"
                )}
              </div>
              {pricePerKg && (
                <span className="text-xs text-emerald-400 font-semibold">
                  (₹{pricePerKg.toFixed(2)}/kg)
                </span>
              )}
            </div>

            <div className="text-xs text-slate-300 space-y-1 leading-relaxed">
              <p>
                {commodityName ? `${commodityName} price reference` : "Commodity price reference"} at {marketLocation || "nearest APMC Mandi"}
                {arrivalDate && ` (arrival: ${arrivalDate})`}.
              </p>
              <p className="text-[11px] text-slate-400">
                Observed wholesale mandi modal price from Agmarknet / OGD. Reference market benchmark only; not a retail selling price recommendation.
              </p>
            </div>
          </div>

          {renderEvidenceExpander("pricing", mandiEvidence, "Agmarknet / DMI data.gov.in", priceBenchmark?.source_url)}
        </div>
      </div>

      {/* 3. Secondary Intelligence: Seasonal Threats & Supply-Chain Risks */}
      <div className="space-y-4 pt-2">
        <div className="border-t border-slate-800 pt-5">
          <h3 className="text-xs font-bold font-mono tracking-wider uppercase text-slate-400">
            SEASONAL & SUPPLY CHAIN VECTORS
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Seasonal Risks */}
          <div className="p-4 rounded-xl border border-slate-800 bg-[#0E2635]/80 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-cyan-400" />
                Seasonal & Climatic Factors
              </span>
              <span className="text-[10px] font-semibold text-slate-400 px-2 py-0.5 rounded bg-slate-800">
                {seasonalThreats.length > 0 ? `${seasonalThreats.length} vector(s)` : "Standard"}
              </span>
            </div>

            {seasonalThreats.length > 0 ? (
              <div className="space-y-2.5">
                {seasonalThreats.map((st, idx) => (
                  <div key={st.threat_id || idx} className="p-2.5 rounded-lg bg-[#06131F] border border-slate-800 text-xs space-y-1">
                    <div className="flex items-center justify-between gap-2">
                      <strong className="text-slate-100 font-semibold">{st.title}</strong>
                      <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded border ${
                        st.severity === "HIGH" ? "bg-rose-950 text-rose-300 border-rose-800" : "bg-amber-950 text-amber-300 border-amber-800"
                      }`}>
                        {st.severity}
                      </span>
                    </div>
                    <p className="text-slate-300 text-[11px]">{st.explanation}</p>
                    {st.affected_period && (
                      <span className="text-[10px] text-cyan-400 font-mono block">
                        Affected Period: {st.affected_period}
                      </span>
                    )}
                    {st.mitigation_hint && (
                      <p className="text-[10px] text-slate-400 pt-0.5 italic">
                        Tip: {st.mitigation_hint}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400 leading-relaxed">
                No evidence-backed seasonal risk identified in checked baseline. (Suggested check: Confirm seasonal agricultural and monsoon sales cycles with local traders).
              </p>
            )}
          </div>

          {/* Supply Chain Risks */}
          <div className="p-4 rounded-xl border border-slate-800 bg-[#0E2635]/80 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                <Truck className="w-3.5 h-3.5 text-amber-400" />
                Raw Material & Supply Chain
              </span>
              <span className="text-[10px] font-semibold text-slate-400 px-2 py-0.5 rounded bg-slate-800">
                {supplyChainRisks.length > 0 ? `${supplyChainRisks.length} vector(s)` : "Standard"}
              </span>
            </div>

            {supplyChainRisks.length > 0 ? (
              <div className="space-y-2.5">
                {supplyChainRisks.map((sc, idx) => (
                  <div key={sc.risk_id || idx} className="p-2.5 rounded-lg bg-[#06131F] border border-slate-800 text-xs space-y-1">
                    <div className="flex items-center justify-between gap-2">
                      <strong className="text-slate-100 font-semibold">{sc.input_material}</strong>
                      <span className="text-[10px] text-amber-300 font-mono">
                        {sc.supplier_dependency || "LOCAL_MARKET"}
                      </span>
                    </div>
                    {sc.logistics_concern && (
                      <p className="text-slate-300 text-[11px]">{sc.logistics_concern}</p>
                    )}
                    {sc.estimated_distance_km && (
                      <span className="text-[10px] text-slate-400 font-mono block">
                        Estimated supplier distance: ~{sc.estimated_distance_km} km
                      </span>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400 leading-relaxed">
                No evidence-backed supply-chain risk identified in checked baseline. (Suggested check: Verify local supplier delivery lead times and credit terms before initial stock procurement).
              </p>
            )}
          </div>
        </div>
      </div>

      {/* 4. Actionable: What to Verify Locally */}
      <div className="p-5 rounded-xl border border-cyan-500/30 bg-[#0A2233] space-y-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold text-white uppercase tracking-wide">
                WHAT TO VERIFY LOCALLY BEFORE BORROWING
              </h3>
            </div>
            <p className="text-xs text-slate-300 mt-1">
              On-ground verification checks derived from unverified assumptions and data limitations before submitting bank credit applications.
            </p>
          </div>
        </div>

        {verificationChecklist && verificationChecklist.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            {verificationChecklist
              .filter(
                (item) =>
                  item.category === "MARKET" ||
                  item.category === "PRICING" ||
                  item.category === "ASSUMPTION" ||
                  item.action_type === "ON_GROUND_SURVEY" ||
                  item.action_type === "SUPPLIER_CHECK"
              )
              .map((item, idx) => (
                <div key={item.item_id || idx} className="p-3 rounded-lg bg-[#06131F] border border-slate-800 space-y-1">
                  <div className="flex items-center justify-between gap-2 text-slate-200 font-semibold">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 flex items-center justify-center font-mono text-[10px] shrink-0">
                        {idx + 1}
                      </span>
                      <span>{item.title}</span>
                    </div>
                    {item.source_evidence_id && (
                      <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                        {item.source_evidence_id}
                      </span>
                    )}
                  </div>
                  <p className="text-slate-400 text-[11px] pl-7">
                    {item.description}
                  </p>
                </div>
              ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            {/* Fallback Check 1: Competitor Survey */}
            <div className="p-3 rounded-lg bg-[#06131F] border border-slate-800 space-y-1">
              <div className="flex items-center gap-2 text-slate-200 font-semibold">
                <span className="w-5 h-5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 flex items-center justify-center font-mono text-[10px] shrink-0">
                  1
                </span>
                <span>On-Ground Competitor Survey</span>
              </div>
              <p className="text-slate-400 text-[11px] pl-7">
                Visit the market cluster within {radius} km to count unmapped or informal competing vendors.
              </p>
            </div>

            {/* Fallback Check 2: Mandi / Supplier Pricing */}
            <div className="p-3 rounded-lg bg-[#06131F] border border-slate-800 space-y-1">
              <div className="flex items-center gap-2 text-slate-200 font-semibold">
                <span className="w-5 h-5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 flex items-center justify-center font-mono text-[10px] shrink-0">
                  2
                </span>
                <span>Wholesale Supplier Inquiries</span>
              </div>
              <p className="text-slate-400 text-[11px] pl-7">
                Inquire at the nearest APMC mandi or wholesale distributor to lock in raw material unit prices.
              </p>
            </div>

            {/* Fallback Check 3: Customer Footfall Count */}
            <div className="p-3 rounded-lg bg-[#06131F] border border-slate-800 space-y-1">
              <div className="flex items-center gap-2 text-slate-200 font-semibold">
                <span className="w-5 h-5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 flex items-center justify-center font-mono text-[10px] shrink-0">
                  3
                </span>
                <span>3-Day Footfall Validation</span>
              </div>
              <p className="text-slate-400 text-[11px] pl-7">
                Observe foot traffic at the proposed location on weekday and weekend market days.
              </p>
            </div>

            {/* Fallback Check 4: Formal MSME Density */}
            <div className="p-3 rounded-lg bg-[#06131F] border border-slate-800 space-y-1">
              <div className="flex items-center gap-2 text-slate-200 font-semibold">
                <span className="w-5 h-5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 flex items-center justify-center font-mono text-[10px] shrink-0">
                  4
                </span>
                <span>District MSME Context</span>
              </div>
              <p className="text-slate-400 text-[11px] pl-7">
                {udyam?.registered_msme_count
                  ? `${udyam.registered_msme_count.toLocaleString()} registered enterprises in ${geo?.district_name || "district"} (Udyam formal density).`
                  : "Verify local enterprise registration requirements with District Industries Centre (DIC)."}
              </p>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};
