"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { FeasibilityCard } from "@/components/dashboard/FeasibilityCard";
import { FinancialSummary } from "@/components/dashboard/FinancialSummary";
import { MarketSnapshot } from "@/components/dashboard/MarketSnapshot";
import { RiskSection } from "@/components/dashboard/RiskSection";
import { SchemeSection } from "@/components/dashboard/SchemeSection";
import { RecommendationCard } from "@/components/dashboard/RecommendationCard";
import { EvidenceDrawer } from "@/components/evidence/EvidenceDrawer";
import { BreakEvenChart } from "@/components/financial/BreakEvenChart";
import { Button } from "@/components/ui/Button";
import { AnalysisResult } from "@/lib/types";

export default function ResultsPage() {
  const [data, setData] = useState<AnalysisResult | null>(null);

  useEffect(() => {
    // TODO [Frontend Lead]: Hydrate from API / URL params or session storage
    if (typeof window !== "undefined") {
      const stored = sessionStorage.getItem("gramavise_latest_result");
      if (stored) {
        try {
          setData(JSON.parse(stored));
        } catch (e) {
          console.error("Failed to parse stored results", e);
        }
      }
    }
  }, []);

  // Fallback placeholder structure for skeleton presentation
  const result: AnalysisResult = data || {
    analysis_id: "preview-id",
    recommendation_status: "PROCEED",
    confidence_score: 0.88,
    financial_result: {
      total_capex: 120000,
      required_loan_amount: 90000,
      monthly_revenue: 39000,
      monthly_variable_cost: 13650,
      monthly_gross_profit: 25350,
      monthly_fixed_cost: 6000,
      monthly_emi: 2925,
      monthly_net_profit: 16425,
      net_profit_margin_pct: 42.1,
      break_even_revenue_monthly: 13730,
      break_even_units_daily: 9,
      dscr: 3.2,
      is_financially_viable: true,
    },
    market_result: {
      location_summary: "Rampur, Varanasi, Uttar Pradesh",
      competitor_count: 2,
      competitor_list: [
        { name: "Gupta Atta Chakki", distance_km: 1.4, category: "Flour Mill" },
        { name: "Kisan Grain Services", distance_km: 3.1, category: "Flour Mill" },
      ],
      demand_indicator: "HIGH",
      notes: "Catchment village exhibits strong demand for local packaging.",
    },
    scheme_result: {
      eligible_schemes_count: 2,
      schemes: [
        {
          scheme_code: "PMEGP",
          scheme_name: "Prime Minister Employment Generation Programme",
          subsidy_eligible_amount: 42000,
          own_contribution_required: 6000,
          max_bank_loan: 90000,
          eligibility_status: "ELIGIBLE",
          reasons: ["Rural special category subsidy rate applied (35%)."],
          portal_url: "https://www.kviconline.gov.in/pmegpeportal",
        },
      ],
      total_potential_subsidy: 42000,
    },
    risk_factors: [
      {
        factor: "Raw grain price surge during off-season",
        severity: "MEDIUM",
        mitigation: "Establish procurement tie-ups with local farmer producer organizations (FPOs).",
      },
    ],
    evidence_list: [
      {
        indicator: "Projected Operating Margin",
        value: "42.1% net profit",
        evidence_type: "CALCULATED",
        confidence: 1.0,
      },
      {
        indicator: "Nearby Category Competitors",
        value: "2 units within 5km",
        evidence_type: "OBSERVED",
        confidence: 0.85,
        source: "OpenStreetMap",
      },
    ],
    ai_explanation: {
      language: "en",
      summary: "This enterprise has strong operating viability with a low break-even threshold and good eligibility for PMEGP subsidy.",
      strengths: ["DSCR of 3.2 exceeds banking safety standard of 1.5.", "Break-even is just 9 customers/day."],
      cautions_and_risks: ["Ensure consistent electricity supply at site."],
      actionable_next_steps: ["Apply for PMEGP loan subsidy.", "Obtain quotations for 10HP mill."],
      disclaimer: "Guidance is based on mathematical modeling and local indicators. Please consult a bank officer before financial commitments.",
    },
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-black text-gray-900">Business Advisory & Structuring Report</h2>
          <p className="text-sm text-gray-500">Analysis ID: {result.analysis_id}</p>
        </div>
        <div className="flex gap-2">
          <Link href="/onboarding">
            <Button variant="outline" size="sm">
              New Assessment
            </Button>
          </Link>
          <Button size="sm" onClick={() => window.print()}>
            Print / Save Report ⎙
          </Button>
        </div>
      </div>

      <FeasibilityCard
        status={result.recommendation_status}
        confidence={result.confidence_score}
        summary={result.ai_explanation?.summary}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <FinancialSummary financials={result.financial_result} />
          <BreakEvenChart
            breakEvenUnitsDaily={result.financial_result.break_even_units_daily}
            expectedDailyUnits={25}
          />
          <SchemeSection schemeResult={result.scheme_result} />
        </div>

        <div className="space-y-6">
          <RecommendationCard explanation={result.ai_explanation} />
          <MarketSnapshot market={result.market_result} />
          <RiskSection risks={result.risk_factors} />
        </div>
      </div>

      <EvidenceDrawer evidenceList={result.evidence_list} />
    </div>
  );
}
