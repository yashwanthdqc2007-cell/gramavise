"use client";

import React, { useMemo } from "react";
import { BusinessProfile, FinancialAssumptions, LocationData } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";
import { Button } from "@/components/ui/Button";
import { MapPin, Briefcase, Coins, TrendingUp, Edit3, ShieldAlert, Sparkles } from "lucide-react";

interface ReviewSummaryProps {
  profile: BusinessProfile;
  financials: FinancialAssumptions;
  fullName: string;
  phoneNumber: string;
  onEditStep: (stepNumber: number) => void;
}

export const ReviewSummary: React.FC<ReviewSummaryProps> = ({
  profile,
  financials,
  fullName,
  phoneNumber,
  onEditStep,
}) => {
  const { t } = useTranslation();

  const totalCapex = useMemo(() => {
    const startup = Number(financials.startup_cost) || 0;
    const equipment = Number(financials.equipment_cost) || 0;
    const inventory = Number(financials.inventory_cost) || 0;
    return startup + equipment + inventory;
  }, [financials.startup_cost, financials.equipment_cost, financials.inventory_cost]);

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <span className="w-6 h-6 rounded-full bg-emerald-500/15 text-emerald-300 flex items-center justify-center text-xs font-bold border border-emerald-500/30">
            5
          </span>
          <h2 className="text-xl font-bold text-white tracking-tight">
            {t("onboarding.step5Title")}
          </h2>
        </div>
        <p className="text-xs sm:text-sm text-slate-400">
          {t("onboarding.step5Sub")}
        </p>
      </div>

      {/* 1. Location Section */}
      <div className="bg-[#0B1F2D] rounded-xl border border-slate-800 p-4 sm:p-5 space-y-3">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-2.5">
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-emerald-400" aria-hidden="true" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              {t("onboarding.review.sectionLocation")}
            </h3>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => onEditStep(1)}
            className="text-xs text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10 min-h-[36px] flex items-center gap-1 px-2.5"
          >
            <Edit3 className="w-3.5 h-3.5" aria-hidden="true" />
            <span>{t("onboarding.review.edit")}</span>
          </Button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div>
            <span className="text-slate-400 block text-[11px]">{t("onboarding.location.state")}</span>
            <span className="font-semibold text-white mt-0.5 block">{profile.location.state || "—"}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[11px]">{t("onboarding.location.district")}</span>
            <span className="font-semibold text-white mt-0.5 block">{profile.location.district || "—"}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[11px]">{t("onboarding.location.subDistrict")}</span>
            <span className="font-semibold text-white mt-0.5 block">{profile.location.block || "—"}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[11px]">{t("onboarding.location.village")}</span>
            <span className="font-semibold text-white mt-0.5 block">{profile.location.village || "—"}</span>
          </div>
        </div>
      </div>

      {/* 2. Business & Owner Section */}
      <div className="bg-[#0B1F2D] rounded-xl border border-slate-800 p-4 sm:p-5 space-y-3">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-2.5">
          <div className="flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-emerald-400" aria-hidden="true" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              {t("onboarding.review.sectionBusiness")}
            </h3>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => onEditStep(2)}
            className="text-xs text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10 min-h-[36px] flex items-center gap-1 px-2.5"
          >
            <Edit3 className="w-3.5 h-3.5" aria-hidden="true" />
            <span>{t("onboarding.review.edit")}</span>
          </Button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div>
            <span className="text-slate-400 block text-[11px]">{t("onboarding.profile.businessName")}</span>
            <span className="font-semibold text-white mt-0.5 block">{profile.business_name || "—"}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[11px]">{t("onboarding.business.category")}</span>
            <span className="font-semibold text-cyan-300 mt-0.5 block">{profile.category || "—"}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[11px]">{t("onboarding.profile.businessType")}</span>
            <span className="font-semibold text-emerald-300 mt-0.5 block">
              {profile.is_new_business ? `🌱 ${t("onboarding.profile.newBusiness")}` : `📈 ${t("onboarding.profile.existingBusiness")}`}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs pt-1 border-t border-slate-800/50">
          <div>
            <span className="text-slate-400 block text-[11px]">{t("onboarding.profile.fullName")}</span>
            <span className="font-semibold text-white mt-0.5 block">{fullName || "—"}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[11px]">{t("onboarding.profile.phone")}</span>
            <span className="font-semibold text-white mt-0.5 block">{phoneNumber || "—"}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[11px]">{t("onboarding.profile.experience")}</span>
            <span className="font-semibold text-white mt-0.5 block">{profile.experience_years} Years</span>
          </div>
        </div>

        {profile.description && (
          <div className="pt-1 text-xs">
            <span className="text-slate-400 block text-[11px]">{t("onboarding.business.description")}</span>
            <p className="text-slate-300 mt-0.5 line-clamp-2 leading-relaxed">{profile.description}</p>
          </div>
        )}
      </div>

      {/* 3. Your Money Section */}
      <div className="bg-[#0B1F2D] rounded-xl border border-slate-800 p-4 sm:p-5 space-y-3">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-2.5">
          <div className="flex items-center gap-2">
            <Coins className="w-4 h-4 text-emerald-400" aria-hidden="true" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              {t("onboarding.review.sectionMoney")}
            </h3>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => onEditStep(3)}
            className="text-xs text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10 min-h-[36px] flex items-center gap-1 px-2.5"
          >
            <Edit3 className="w-3.5 h-3.5" aria-hidden="true" />
            <span>{t("onboarding.review.edit")}</span>
          </Button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
          <div>
            <span className="text-slate-400 block text-[11px]">{t("onboarding.profile.ownCapital")}</span>
            <span className="font-bold text-emerald-300 mt-0.5 block text-sm">
              ₹{(Number(profile.own_capital) || 0).toLocaleString("en-IN")}
            </span>
          </div>
          <div>
            <span className="text-slate-400 block text-[11px]">{t("onboarding.profile.desiredLoan")}</span>
            <span className="font-bold text-cyan-300 mt-0.5 block text-sm">
              ₹{(Number(profile.desired_loan) || 0).toLocaleString("en-IN")}
            </span>
          </div>
          <div>
            <span className="text-slate-400 block text-[11px]">{t("onboarding.review.totalCapex")}</span>
            <span className="font-bold text-white mt-0.5 block text-sm">
              ₹{totalCapex.toLocaleString("en-IN")}
            </span>
          </div>
          <div>
            <span className="text-slate-400 block text-[11px]">{t("onboarding.financial.startupCost")}</span>
            <span className="font-semibold text-white mt-0.5 block">
              ₹{(Number(financials.startup_cost) || 0).toLocaleString("en-IN")}
            </span>
          </div>
          <div>
            <span className="text-slate-400 block text-[11px]">{t("onboarding.financial.equipmentCost")}</span>
            <span className="font-semibold text-white mt-0.5 block">
              ₹{(Number(financials.equipment_cost) || 0).toLocaleString("en-IN")}
            </span>
          </div>
          <div>
            <span className="text-slate-400 block text-[11px]">{t("onboarding.financial.inventoryCost")}</span>
            <span className="font-semibold text-white mt-0.5 block">
              ₹{(Number(financials.inventory_cost) || 0).toLocaleString("en-IN")}
            </span>
          </div>
        </div>
      </div>

      {/* 4. Expected Sales Section */}
      <div className="bg-[#0B1F2D] rounded-xl border border-slate-800 p-4 sm:p-5 space-y-3">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-2.5">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-emerald-400" aria-hidden="true" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              {t("onboarding.review.sectionSales")}
            </h3>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => onEditStep(4)}
            className="text-xs text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10 min-h-[36px] flex items-center gap-1 px-2.5"
          >
            <Edit3 className="w-3.5 h-3.5" aria-hidden="true" />
            <span>{t("onboarding.review.edit")}</span>
          </Button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
          <div>
            <span className="text-slate-400 block text-[11px]">{t("onboarding.financial.customersPerDay")}</span>
            <span className="font-semibold text-white mt-0.5 block">{financials.customers_per_day} Customers</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[11px]">{t("onboarding.financial.avgTicketPrice")}</span>
            <span className="font-semibold text-white mt-0.5 block">₹{financials.avg_ticket_price}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[11px]">{t("onboarding.financial.workingDaysPerMonth")}</span>
            <span className="font-semibold text-white mt-0.5 block">{financials.working_days_per_month} Days / Mo</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[11px]">{t("onboarding.financial.variableCostPct")}</span>
            <span className="font-semibold text-white mt-0.5 block">{financials.variable_cost_pct}%</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[11px]">{t("onboarding.financial.monthlyFixedCost")}</span>
            <span className="font-semibold text-white mt-0.5 block">₹{(Number(financials.monthly_fixed_cost) || 0).toLocaleString("en-IN")}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[11px]">Interest & Tenure</span>
            <span className="font-semibold text-white mt-0.5 block">{financials.interest_rate_pct}% / {financials.loan_tenure_months} Mo</span>
          </div>
        </div>
      </div>

      {/* Ready Box & Final Confirmation */}
      <div className="p-5 bg-[#0E2635] rounded-2xl border border-emerald-500/40 shadow-md space-y-3">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-emerald-400" aria-hidden="true" />
          <h3 className="text-base font-bold text-white">
            {t("onboarding.review.readyHeading")}
          </h3>
        </div>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          {t("onboarding.review.readyDesc")}
        </p>
        <p className="text-[11px] text-slate-400 pt-2 border-t border-slate-800/80 leading-relaxed">
          ℹ️ {t("onboarding.review.disclaimer")}
        </p>
      </div>
    </div>
  );
};
