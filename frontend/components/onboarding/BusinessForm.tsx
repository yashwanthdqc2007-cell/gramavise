"use client";

import React from "react";
import { Input } from "@/components/ui/Input";
import { POPULAR_BUSINESS_CATEGORIES } from "@/lib/constants";
import { useTranslation } from "@/lib/i18n";
import { Briefcase, User, Sparkles } from "lucide-react";

interface BusinessFormProps {
  businessName: string;
  category: string;
  description?: string;
  isNewBusiness: boolean;
  fullName: string;
  phoneNumber: string;
  experienceYears: number;
  errors?: Record<string, string>;
  onChange: (fields: {
    business_name?: string;
    category?: string;
    description?: string;
    is_new_business?: boolean;
    full_name?: string;
    phone_number?: string;
    experience_years?: number;
  }) => void;
}

export const BusinessForm: React.FC<BusinessFormProps> = ({
  businessName,
  category,
  description = "",
  isNewBusiness,
  fullName,
  phoneNumber,
  experienceYears,
  errors = {},
  onChange,
}) => {
  const { t } = useTranslation();

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <span className="w-6 h-6 rounded-full bg-emerald-500/15 text-emerald-300 flex items-center justify-center text-xs font-bold border border-emerald-500/30">
            2
          </span>
          <h2 className="text-xl font-bold text-white tracking-tight">
            {t("onboarding.step2Title")}
          </h2>
        </div>
        <p className="text-xs sm:text-sm text-slate-400">
          {t("onboarding.step2Sub")}
        </p>
      </div>

      {/* Enterprise Stage Selection */}
      <div className="space-y-2">
        <label className="block text-xs font-bold uppercase tracking-wider text-slate-300">
          {t("onboarding.profile.businessType")} *
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => onChange({ is_new_business: true })}
            className={`p-4 text-left rounded-xl border-2 transition-all flex flex-col justify-between min-h-[88px] ${
              isNewBusiness
                ? "border-emerald-500 bg-emerald-500/10 text-emerald-200 ring-2 ring-emerald-500/20 shadow-md"
                : "border-slate-800 hover:border-emerald-500/50 bg-[#0E2635] text-slate-300"
            }`}
          >
            <div className="flex items-center justify-between w-full mb-1">
              <span className="font-bold text-sm text-white flex items-center gap-1.5">
                <span>🌱</span> {t("onboarding.profile.newBusiness")}
              </span>
              <span
                className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                  isNewBusiness ? "border-emerald-400 bg-emerald-500" : "border-slate-600"
                }`}
              >
                {isNewBusiness && <span className="w-1.5 h-1.5 rounded-full bg-white" />}
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              {t("onboarding.profile.newBusinessDesc")}
            </p>
          </button>

          <button
            type="button"
            onClick={() => onChange({ is_new_business: false })}
            className={`p-4 text-left rounded-xl border-2 transition-all flex flex-col justify-between min-h-[88px] ${
              !isNewBusiness
                ? "border-emerald-500 bg-emerald-500/10 text-emerald-200 ring-2 ring-emerald-500/20 shadow-md"
                : "border-slate-800 hover:border-emerald-500/50 bg-[#0E2635] text-slate-300"
            }`}
          >
            <div className="flex items-center justify-between w-full mb-1">
              <span className="font-bold text-sm text-white flex items-center gap-1.5">
                <span>📈</span> {t("onboarding.profile.existingBusiness")}
              </span>
              <span
                className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                  !isNewBusiness ? "border-emerald-400 bg-emerald-500" : "border-slate-600"
                }`}
              >
                {!isNewBusiness && <span className="w-1.5 h-1.5 rounded-full bg-white" />}
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              {t("onboarding.profile.existingBusinessDesc")}
            </p>
          </button>
        </div>
      </div>

      {/* Business Details Section */}
      <div className="bg-[#0B1F2D] p-4 sm:p-5 rounded-xl border border-slate-800 space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-800/80 pb-3">
          <Briefcase className="w-4 h-4 text-emerald-400" aria-hidden="true" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Business Details
          </span>
        </div>

        <Input
          label={`${t("onboarding.profile.businessName")} *`}
          placeholder="e.g. Kisan Flour Mill & Spices, Shri Balaji Kirana, Lakshmi Tailoring"
          value={businessName}
          error={errors.business_name}
          helperText="The name of your shop, unit, or proposed venture."
          onChange={(e) => onChange({ business_name: e.target.value })}
        />

        <div className="w-full space-y-1.5">
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-300">
            {t("onboarding.business.category")} *
          </label>
          <select
            aria-label={t("onboarding.business.category")}
            className={`w-full px-3.5 py-2.5 min-h-[44px] rounded-xl border text-sm font-medium bg-[#102B3A] transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
              errors.category ? "border-rose-500 focus:ring-rose-500 text-rose-300" : "border-slate-700 text-white"
            } ${category ? "text-white" : "text-slate-400"}`}
            value={category}
            onChange={(e) => onChange({ category: e.target.value })}
          >
            <option value="" disabled className="text-slate-500 bg-[#0B1F2D]">
              {t("onboarding.business.selectCategory")}
            </option>
            {POPULAR_BUSINESS_CATEGORIES.map((cat) => (
              <option key={cat} value={cat} className="text-white bg-[#0B1F2D]">
                {cat}
              </option>
            ))}
          </select>
          {errors.category ? (
            <p className="text-xs text-rose-400 mt-1">{errors.category}</p>
          ) : (
            <p className="text-[11px] text-slate-400">Select the primary trade or service line for your venture.</p>
          )}
        </div>

        <div className="w-full space-y-1.5">
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-300">
            {t("onboarding.business.description")} *
          </label>
          <textarea
            rows={3}
            aria-label={t("onboarding.business.description")}
            className={`w-full p-3 rounded-xl border text-sm text-white bg-[#102B3A] placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-colors ${
              errors.description ? "border-rose-500 focus:ring-rose-500" : "border-slate-700"
            }`}
            placeholder={t("onboarding.business.descriptionPlaceholder")}
            value={description}
            onChange={(e) => onChange({ description: e.target.value })}
          />
          {errors.description ? (
            <p className="text-xs text-rose-400 mt-1">{errors.description}</p>
          ) : (
            <p className="text-[11px] text-slate-400">Briefly explain what products you will sell or services you will provide.</p>
          )}
        </div>
      </div>

      {/* Entrepreneur / Owner Details Section */}
      <div className="bg-[#0B1F2D] p-4 sm:p-5 rounded-xl border border-slate-800 space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-800/80 pb-3">
          <User className="w-4 h-4 text-emerald-400" aria-hidden="true" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Owner Information
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label={`${t("onboarding.profile.fullName")} *`}
            placeholder={t("onboarding.profile.fullNamePlaceholder")}
            value={fullName}
            error={errors.full_name}
            helperText="Name of primary entrepreneur or borrower."
            onChange={(e) => onChange({ full_name: e.target.value })}
          />

          <Input
            label={`${t("onboarding.profile.phone")} *`}
            placeholder={t("onboarding.profile.phonePlaceholder")}
            type="tel"
            maxLength={10}
            value={phoneNumber}
            error={errors.phone_number}
            helperText="10-digit mobile number for communication."
            onChange={(e) => onChange({ phone_number: e.target.value.replace(/\D/g, "") })}
          />
        </div>

        <Input
          label={`${t("onboarding.profile.experience")} *`}
          type="number"
          min={0}
          max={60}
          placeholder={t("onboarding.profile.experiencePlaceholder")}
          value={experienceYears === 0 ? "0" : experienceYears || ""}
          error={errors.experience_years}
          helperText={t("onboarding.profile.experienceHelp")}
          onChange={(e) => {
            const val = e.target.value === "" ? 0 : parseInt(e.target.value, 10);
            onChange({ experience_years: isNaN(val) ? 0 : val });
          }}
        />
      </div>
    </div>
  );
};
