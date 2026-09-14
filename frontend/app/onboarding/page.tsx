"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { ProfileForm } from "@/components/onboarding/ProfileForm";
import { LocationForm } from "@/components/onboarding/LocationForm";
import { BusinessForm } from "@/components/onboarding/BusinessForm";
import { FinancialForm } from "@/components/onboarding/FinancialForm";
import { DraftRecoveryBanner } from "@/components/onboarding/DraftRecoveryBanner";
import { DemoScenarioSelector } from "@/components/onboarding/DemoScenarioSelector";
import { DemoScenario } from "@/lib/demo/demoScenarios";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useBusinessProfile } from "@/hooks/useBusinessProfile";
import { FinancialAssumptions } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";
import { loadDraft, saveDraft, clearDraft, OnboardingDraft } from "@/lib/storage/draftStorage";
import { useNetworkStatus } from "@/hooks/useNetworkStatus";
import { WifiOff } from "lucide-react";

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
  const { t, language } = useTranslation();
  const { isOnline } = useNetworkStatus();
  const [step, setStep] = useState(1);
  const { profile, updateProfile, resetProfile } = useBusinessProfile();
  const [existingDraft, setExistingDraft] = useState<OnboardingDraft | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const [financials, setFinancials] = useState<FinancialAssumptions>(() => {
    if (typeof window !== "undefined") {
      try {
        const stored = sessionStorage.getItem("gramavise_financials");
        if (stored) return JSON.parse(stored);
      } catch {
        // Fallback to default
      }
    }
    return defaultFinancials;
  });

  const [fullName, setFullName] = useState(() => {
    if (typeof window !== "undefined") {
      try {
        const stored = sessionStorage.getItem("gramavise_entrepreneur");
        if (stored) return JSON.parse(stored).full_name || "";
      } catch {
        // ignore
      }
    }
    return "";
  });

  const [phoneNumber, setPhoneNumber] = useState(() => {
    if (typeof window !== "undefined") {
      try {
        const stored = sessionStorage.getItem("gramavise_entrepreneur");
        if (stored) return JSON.parse(stored).phone_number || "";
      } catch {
        // ignore
      }
    }
    return "";
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Check for saved draft on initial mount
  useEffect(() => {
    const draft = loadDraft();
    if (draft) {
      setExistingDraft(draft);
    }
  }, []);

  // Debounced auto-save (300ms)
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  useEffect(() => {
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    saveTimeoutRef.current = setTimeout(() => {
      saveDraft(step, language, profile, financials, fullName);
    }, 300);

    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, [step, language, profile, financials, fullName]);

  const handleContinueDraft = (draft: OnboardingDraft) => {
    updateProfile(draft.profile);
    setFinancials(draft.financials);
    if (draft.entrepreneur?.full_name) {
      setFullName(draft.entrepreneur.full_name);
    }
    setStep(draft.step || 1);
    setExistingDraft(null);

    // Sync session storage
    if (typeof window !== "undefined") {
      try {
        sessionStorage.setItem("gramavise_profile", JSON.stringify(draft.profile));
        sessionStorage.setItem("gramavise_financials", JSON.stringify(draft.financials));
        sessionStorage.setItem(
          "gramavise_entrepreneur",
          JSON.stringify({ full_name: draft.entrepreneur?.full_name || "", phone_number: phoneNumber })
        );
      } catch {
        // ignore
      }
    }
  };

  const handleStartFresh = () => {
    clearDraft();
    resetProfile();
    setFinancials(defaultFinancials);
    setFullName("");
    setPhoneNumber("");
    setStep(1);
    setExistingDraft(null);
    setErrors({});

    if (typeof window !== "undefined") {
      try {
        sessionStorage.removeItem("gramavise_profile");
        sessionStorage.removeItem("gramavise_financials");
        sessionStorage.removeItem("gramavise_entrepreneur");
      } catch {
        // ignore
      }
    }
  };

  const STEP_TITLES = [
    { step: 1, title: t("onboarding.step1Title"), subtitle: t("onboarding.step1Sub") },
    { step: 2, title: t("onboarding.step2Title"), subtitle: t("onboarding.step2Sub") },
    { step: 3, title: t("onboarding.step3Title"), subtitle: t("onboarding.step3Sub") },
    { step: 4, title: t("onboarding.step4Title"), subtitle: t("onboarding.step4Sub") },
  ];

  // Save financial changes
  const handleFinancialChange = (updated: FinancialAssumptions) => {
    setFinancials(updated);
    if (typeof window !== "undefined") {
      try {
        sessionStorage.setItem("gramavise_financials", JSON.stringify(updated));
      } catch {
        // ignore
      }
    }
  };

  // Step 1 validation
  const validateStep1 = (): boolean => {
    const errs: Record<string, string> = {};
    if (!fullName.trim()) {
      errs.full_name = t("onboarding.errors.fullNameRequired");
    }
    const cleanPhone = phoneNumber.replace(/\D/g, "");
    if (!cleanPhone || cleanPhone.length !== 10) {
      errs.phone_number = t("onboarding.errors.phoneInvalid");
    }
    if (profile.experience_years === undefined || profile.experience_years < 0 || isNaN(profile.experience_years)) {
      errs.experience_years = t("onboarding.errors.experienceRequired");
    }

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  // Step 2 validation
  const validateStep2 = (): boolean => {
    const errs: Record<string, string> = {};
    if (!profile.location.state?.trim()) {
      errs.state = t("onboarding.errors.stateRequired");
    }
    if (!profile.location.district?.trim()) {
      errs.district = t("onboarding.errors.districtRequired");
    }
    if (!profile.location.village?.trim()) {
      errs.village = t("onboarding.errors.villageRequired");
    }

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  // Step 3 validation
  const validateStep3 = (): boolean => {
    const errs: Record<string, string> = {};
    if (!profile.business_name?.trim()) {
      errs.business_name = t("onboarding.errors.businessNameRequired");
    }
    if (!profile.category?.trim()) {
      errs.category = t("onboarding.errors.categoryRequired");
    }
    if (!profile.description?.trim()) {
      errs.description = t("onboarding.errors.descriptionRequired");
    }

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  // Step 4 validation
  const validateStep4 = (): boolean => {
    const errs: Record<string, string> = {};

    if (profile.own_capital === undefined || profile.own_capital < 0 || isNaN(profile.own_capital)) {
      errs.own_capital = "Own investment must be 0 or greater.";
    }
    if (profile.desired_loan === undefined || profile.desired_loan < 0 || isNaN(profile.desired_loan)) {
      errs.desired_loan = "Desired loan must be 0 or greater.";
    }
    if (financials.startup_cost === undefined || financials.startup_cost < 0 || isNaN(financials.startup_cost)) {
      errs.startup_cost = "Startup cost cannot be negative.";
    }
    if (financials.equipment_cost === undefined || financials.equipment_cost < 0 || isNaN(financials.equipment_cost)) {
      errs.equipment_cost = "Equipment cost cannot be negative.";
    }
    if (financials.inventory_cost === undefined || financials.inventory_cost < 0 || isNaN(financials.inventory_cost)) {
      errs.inventory_cost = "Inventory cost cannot be negative.";
    }
    if (financials.monthly_fixed_cost === undefined || financials.monthly_fixed_cost < 0 || isNaN(financials.monthly_fixed_cost)) {
      errs.monthly_fixed_cost = "Monthly fixed cost cannot be negative.";
    }
    if (financials.customers_per_day === undefined || financials.customers_per_day <= 0 || isNaN(financials.customers_per_day)) {
      errs.customers_per_day = "Estimated daily customers must be greater than 0.";
    }
    if (financials.avg_ticket_price === undefined || financials.avg_ticket_price <= 0 || isNaN(financials.avg_ticket_price)) {
      errs.avg_ticket_price = "Average sale price must be greater than ₹0.";
    }
    if (
      financials.working_days_per_month === undefined ||
      financials.working_days_per_month < 1 ||
      financials.working_days_per_month > 31 ||
      isNaN(financials.working_days_per_month)
    ) {
      errs.working_days_per_month = "Working days must be between 1 and 31.";
    }
    if (
      financials.variable_cost_pct === undefined ||
      financials.variable_cost_pct < 0 ||
      financials.variable_cost_pct >= 100 ||
      isNaN(financials.variable_cost_pct)
    ) {
      errs.variable_cost_pct = "Variable cost percentage must be between 0% and 99.9%.";
    }
    if (
      financials.interest_rate_pct === undefined ||
      financials.interest_rate_pct < 0 ||
      financials.interest_rate_pct > 40 ||
      isNaN(financials.interest_rate_pct)
    ) {
      errs.interest_rate_pct = "Interest rate must be between 0% and 40%.";
    }
    if (
      financials.loan_tenure_months === undefined ||
      financials.loan_tenure_months < 1 ||
      financials.loan_tenure_months > 120 ||
      isNaN(financials.loan_tenure_months)
    ) {
      errs.loan_tenure_months = "Loan tenure must be between 1 and 120 months.";
    }

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleNext = () => {
    let isValid = false;
    if (step === 1) isValid = validateStep1();
    else if (step === 2) isValid = validateStep2();
    else if (step === 3) isValid = validateStep3();
    else if (step === 4) isValid = validateStep4();

    if (!isValid) {
      setValidationSummary(t("onboarding.validationErrorSummary"));
      return;
    }

    setValidationSummary(null);

    if (step < 4) {
      setErrors({});
      setStep(step + 1);
    } else {
      // Check online connectivity before navigating to analysis execution
      if (!isOnline && typeof navigator !== "undefined" && !navigator.onLine) {
        setErrors({
          submit: t("network.offlineDesc"),
        });
        return;
      }

      setIsSubmitting(true);

      // Save all information before navigating
      if (typeof window !== "undefined") {
        try {
          sessionStorage.setItem("gramavise_profile", JSON.stringify(profile));
          sessionStorage.setItem("gramavise_financials", JSON.stringify(financials));
          sessionStorage.setItem("gramavise_language", language);
          sessionStorage.setItem(
            "gramavise_entrepreneur",
            JSON.stringify({ full_name: fullName, phone_number: phoneNumber })
          );
        } catch {
          // ignore
        }
      }
      router.push("/analysis/loading");
    }
  };

  const [validationSummary, setValidationSummary] = useState<string | null>(null);

  const handlePrev = () => {
    if (step > 1) {
      setErrors({});
      setValidationSummary(null);
      setStep(step - 1);
    }
  };

  const handleSelectDemoScenario = (scenario: DemoScenario) => {
    setFullName(scenario.entrepreneur.fullName);
    setPhoneNumber(scenario.entrepreneur.phoneNumber);
    updateProfile({
      business_name: scenario.profile.business_name,
      category: scenario.profile.category,
      description: scenario.profile.description,
      location: { ...scenario.profile.location },
      experience_years: scenario.profile.experience_years,
      own_capital: scenario.profile.own_capital,
      desired_loan: scenario.profile.desired_loan,
      is_new_business: scenario.profile.is_new_business,
    });
    setFinancials({ ...scenario.financials });
    setErrors({});
    setValidationSummary(null);

    // Save to session storage
    if (typeof window !== "undefined") {
      try {
        sessionStorage.setItem("gramavise_profile", JSON.stringify(scenario.profile));
        sessionStorage.setItem("gramavise_financials", JSON.stringify(scenario.financials));
        sessionStorage.setItem(
          "gramavise_entrepreneur",
          JSON.stringify({ full_name: scenario.entrepreneur.fullName, phone_number: scenario.entrepreneur.phoneNumber })
        );
      } catch {
        // ignore
      }
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      {/* Demo Scenarios Quick Loader */}
      <DemoScenarioSelector onSelectScenario={handleSelectDemoScenario} />

      {/* Draft Recovery Banner */}
      {existingDraft && (
        <DraftRecoveryBanner
          draft={existingDraft}
          onContinue={handleContinueDraft}
          onStartFresh={handleStartFresh}
        />
      )}

      {/* Header & Step progress */}
      <div className="mb-8 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-300 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/30 inline-block mb-2">
              Business Assessment
            </span>
            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              Tell us about your business
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Step {step} of 4: <span className="font-semibold text-white">{STEP_TITLES[step - 1].title}</span> — {STEP_TITLES[step - 1].subtitle}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 self-start sm:self-auto shadow-2xs">
              {Math.round((step / 4) * 100)}% Complete
            </span>
          </div>
        </div>

        {/* Stepper Semantic Navigation */}
        <nav aria-label={t("onboarding.stepNav")}>
          <ol className="grid grid-cols-4 gap-2.5 pt-1 list-none p-0 m-0">
            {STEP_TITLES.map((s) => (
              <li
                key={s.step}
                className="space-y-1.5"
                aria-current={s.step === step ? "step" : undefined}
              >
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${
                    s.step <= step ? "bg-emerald-500 shadow-2xs" : "bg-slate-700"
                  }`}
                  aria-hidden="true"
                />
                <span
                  className={`text-[11px] hidden sm:block font-medium truncate ${
                    s.step === step ? "text-emerald-300 font-bold" : s.step < step ? "text-slate-300" : "text-slate-500"
                  }`}
                >
                  <span className="sr-only">Step {s.step}: </span>
                  {s.title}
                </span>
              </li>
            ))}
          </ol>
        </nav>
      </div>

      {/* Validation Summary Alert */}
      {validationSummary && (
        <div
          role="alert"
          className="mb-6 p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 flex items-start gap-2.5 animate-in fade-in duration-200 shadow-2xs"
        >
          <span aria-hidden="true" className="font-bold text-sm">⚠️</span>
          <span>{validationSummary}</span>
        </div>
      )}

      <Card className="p-6 sm:p-8 shadow-sm border border-slate-800 rounded-2xl">
        {step === 1 && (
          <ProfileForm
            fullName={fullName}
            phoneNumber={phoneNumber}
            experienceYears={profile.experience_years}
            errors={errors}
            onChange={(fields) => {
              if (fields.full_name !== undefined) {
                setFullName(fields.full_name);
                if (typeof window !== "undefined") {
                  try {
                    sessionStorage.setItem(
                      "gramavise_entrepreneur",
                      JSON.stringify({ full_name: fields.full_name, phone_number: phoneNumber })
                    );
                  } catch {
                    // ignore
                  }
                }
              }
              if (fields.phone_number !== undefined) {
                setPhoneNumber(fields.phone_number);
                if (typeof window !== "undefined") {
                  try {
                    sessionStorage.setItem(
                      "gramavise_entrepreneur",
                      JSON.stringify({ full_name: fullName, phone_number: fields.phone_number })
                    );
                  } catch {
                    // ignore
                  }
                }
              }
              if (fields.experience_years !== undefined) {
                updateProfile({ experience_years: fields.experience_years });
              }
            }}
          />
        )}

        {step === 2 && (
          <LocationForm
            location={profile.location}
            errors={errors}
            onChange={(loc) => updateProfile({ location: loc })}
          />
        )}

        {step === 3 && (
          <BusinessForm
            businessName={profile.business_name}
            category={profile.category}
            description={profile.description}
            isNewBusiness={profile.is_new_business}
            errors={errors}
            onChange={(fields) => updateProfile(fields)}
          />
        )}

        {step === 4 && (
          <FinancialForm
            financials={financials}
            ownCapital={profile.own_capital}
            desiredLoan={profile.desired_loan}
            errors={errors}
            onChangeFinancials={handleFinancialChange}
            onChangeCapital={updateProfile}
          />
        )}

        {/* Offline warning banner if trying to submit while offline */}
        {errors.submit && (
          <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-start gap-2.5 text-xs text-amber-800">
            <WifiOff className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" aria-hidden="true" />
            <span>{errors.submit}</span>
          </div>
        )}

        <div className="flex justify-between items-center mt-8 pt-6 border-t border-slate-800">
          <Button variant="secondary" onClick={handlePrev} disabled={step === 1 || isSubmitting} className="min-h-[44px]">
            {t("onboarding.actions.previous")}
          </Button>
          <Button onClick={handleNext} disabled={isSubmitting} className="min-h-[44px] font-bold">
            {isSubmitting
              ? t("common.loading")
              : step === 4
              ? t("onboarding.actions.runAnalysis")
              : t("onboarding.actions.next")}
          </Button>
        </div>
      </Card>
    </div>
  );
}
