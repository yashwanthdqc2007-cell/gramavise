"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { ProfileForm } from "@/components/onboarding/ProfileForm";
import { LocationForm } from "@/components/onboarding/LocationForm";
import { BusinessForm } from "@/components/onboarding/BusinessForm";
import { FinancialForm } from "@/components/onboarding/FinancialForm";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useBusinessProfile } from "@/hooks/useBusinessProfile";
import { FinancialAssumptions } from "@/lib/types";

const defaultFinancials: FinancialAssumptions = {
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

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const { profile, updateProfile } = useBusinessProfile();
  const [financials, setFinancials] = useState<FinancialAssumptions>(defaultFinancials);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [fullName, setFullName] = useState("");

  const handleNext = () => {
    if (step < 4) {
      setStep(step + 1);
    } else {
      // TODO [Frontend Lead]: Dispatch state to global store / session storage before navigation
      if (typeof window !== "undefined") {
        sessionStorage.setItem("gramavise_profile", JSON.stringify(profile));
        sessionStorage.setItem("gramavise_financials", JSON.stringify(financials));
      }
      router.push("/analysis/loading");
    }
  };

  const handlePrev = () => {
    if (step > 1) setStep(step - 1);
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">New Business Feasibility Assessment</h2>
        <p className="text-sm text-gray-500">Step {step} of 4: Enter entrepreneur & operational parameters</p>
      </div>

      <Card>
        {step === 1 && (
          <ProfileForm
            fullName={fullName}
            phoneNumber={phoneNumber}
            experienceYears={profile.experience_years}
            onChange={(fields) => {
              if (fields.full_name !== undefined) setFullName(fields.full_name);
              if (fields.phone_number !== undefined) setPhoneNumber(fields.phone_number);
              if (fields.experience_years !== undefined) updateProfile({ experience_years: fields.experience_years });
            }}
          />
        )}

        {step === 2 && (
          <LocationForm
            location={profile.location}
            onChange={(loc) => updateProfile({ location: loc })}
          />
        )}

        {step === 3 && (
          <BusinessForm
            businessName={profile.business_name}
            category={profile.category}
            description={profile.description}
            isNewBusiness={profile.is_new_business}
            onChange={updateProfile}
          />
        )}

        {step === 4 && (
          <FinancialForm
            financials={financials}
            ownCapital={profile.own_capital}
            desiredLoan={profile.desired_loan}
            onChangeFinancials={setFinancials}
            onChangeCapital={updateProfile}
          />
        )}

        <div className="flex justify-between items-center mt-8 pt-6 border-t border-gray-100">
          <Button variant="outline" onClick={handlePrev} disabled={step === 1}>
            ← Previous
          </Button>
          <Button onClick={handleNext}>
            {step === 4 ? "Run Feasibility Analysis →" : "Continue →"}
          </Button>
        </div>
      </Card>
    </div>
  );
}
