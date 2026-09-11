"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { LoadingState } from "@/components/common/LoadingState";
import { runAnalysis } from "@/services/api/analysis";

export default function AnalysisLoadingPage() {
  const router = useRouter();

  useEffect(() => {
    // TODO [Frontend Lead]: Fetch session state and dispatch live API call to /api/analyze
    const execute = async () => {
      try {
        const storedProfile = sessionStorage.getItem("gramavise_profile");
        const storedFinancials = sessionStorage.getItem("gramavise_financials");

        const profile = storedProfile
          ? JSON.parse(storedProfile)
          : {
              business_name: "Sample Flour Mill",
              category: "Food Processing",
              location: { state: "Uttar Pradesh", district: "Varanasi", village: "Rampur" },
              experience_years: 2,
              own_capital: 30000,
              desired_loan: 120000,
              is_new_business: true,
            };

        const financials = storedFinancials
          ? JSON.parse(storedFinancials)
          : {
              startup_cost: 15000,
              equipment_cost: 80000,
              inventory_cost: 25000,
              monthly_fixed_cost: 6000,
              customers_per_day: 25,
              avg_ticket_price: 60,
              working_days_per_month: 26,
              variable_cost_pct: 35,
              interest_rate_pct: 10.5,
              loan_tenure_months: 36,
            };

        const result = await runAnalysis({
          profile,
          financials,
          preferred_language: "en",
        });

        sessionStorage.setItem("gramavise_latest_result", JSON.stringify(result));
        router.push("/results");
      } catch (err) {
        console.error("Analysis execution error:", err);
        // Fallback to results page with mock state if offline
        router.push("/results");
      }
    };

    const timer = setTimeout(execute, 1500);
    return () => clearTimeout(timer);
  }, [router]);

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <LoadingState message="Processing geospatial data, computing break-even economics & matching subsidies..." />
    </div>
  );
}
