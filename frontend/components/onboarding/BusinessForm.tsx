"use client";

import React from "react";
import { Input } from "@/components/ui/Input";
import { POPULAR_BUSINESS_CATEGORIES } from "@/lib/constants";
import { useTranslation } from "@/lib/i18n";

interface BusinessFormProps {
  businessName: string;
  category: string;
  description?: string;
  isNewBusiness: boolean;
  errors?: Record<string, string>;
  onChange: (fields: {
    business_name?: string;
    category?: string;
    description?: string;
    is_new_business?: boolean;
  }) => void;
}

export const BusinessForm: React.FC<BusinessFormProps> = ({
  businessName,
  category,
  description = "",
  isNewBusiness,
  errors = {},
  onChange,
}) => {
  const { t } = useTranslation();

  return (
    <div className="space-y-5">
      <div>
        <h3 className="text-lg font-bold text-white">{t("onboarding.step3Title")}</h3>
        <p className="text-xs text-slate-400 mt-0.5">
          {t("onboarding.step3Sub")}
        </p>
      </div>

      {/* Enterprise Type Selection */}
      <div className="space-y-1.5">
        <label className="block text-sm font-medium text-slate-200">{t("onboarding.profile.businessType")} *</label>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => onChange({ is_new_business: true })}
            className={`p-3.5 text-left rounded-xl border-2 transition-all flex flex-col justify-between ${
              isNewBusiness
                ? "border-emerald-500 bg-emerald-500/10 text-emerald-200 ring-2 ring-emerald-500/20 shadow-2xs"
                : "border-slate-700 hover:border-emerald-500/50 bg-slate-950/40 text-slate-200"
            }`}
          >
            <div className="flex items-center justify-between w-full mb-1">
              <span className="font-semibold text-sm">🌱 {t("onboarding.profile.newBusiness")}</span>
              <span
                className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                  isNewBusiness ? "border-emerald-500 bg-emerald-500" : "border-slate-600"
                }`}
              >
                {isNewBusiness && <span className="w-1.5 h-1.5 rounded-full bg-white" />}
              </span>
            </div>
            <p className="text-xs text-slate-400">
              {t("onboarding.profile.newBusinessDesc")}
            </p>
          </button>

          <button
            type="button"
            onClick={() => onChange({ is_new_business: false })}
            className={`p-3.5 text-left rounded-xl border-2 transition-all flex flex-col justify-between ${
              !isNewBusiness
                ? "border-emerald-500 bg-emerald-500/10 text-emerald-200 ring-2 ring-emerald-500/20 shadow-2xs"
                : "border-slate-700 hover:border-emerald-500/50 bg-slate-950/40 text-slate-200"
            }`}
          >
            <div className="flex items-center justify-between w-full mb-1">
              <span className="font-semibold text-sm">📈 {t("onboarding.profile.existingBusiness")}</span>
              <span
                className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                  !isNewBusiness ? "border-emerald-500 bg-emerald-500" : "border-slate-600"
                }`}
              >
                {!isNewBusiness && <span className="w-1.5 h-1.5 rounded-full bg-white" />}
              </span>
            </div>
            <p className="text-xs text-slate-400">
              {t("onboarding.profile.existingBusinessDesc")}
            </p>
          </button>
        </div>
      </div>

      <Input
        label={`${t("onboarding.profile.businessName")} *`}
        placeholder="e.g. Kisan Flour Mill & Spices, Shri Balaji Kirana"
        value={businessName}
        error={errors.business_name}
        onChange={(e) => onChange({ business_name: e.target.value })}
      />

      <div className="w-full space-y-1">
        <label className="block text-sm font-medium text-slate-200">{t("onboarding.business.category")} *</label>
        <select
          aria-label={t("onboarding.business.category")}
          className={`w-full px-3 py-2 border rounded-xl shadow-xs focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm bg-slate-900 ${
            errors.category ? "border-rose-500 focus:ring-rose-500" : "border-slate-700"
          } ${category ? "text-slate-100" : "text-slate-400"}`}
          value={category}
          onChange={(e) => onChange({ category: e.target.value })}
        >
          <option value="" disabled className="text-slate-400">
            {t("onboarding.business.selectCategory")}
          </option>
          {POPULAR_BUSINESS_CATEGORIES.map((cat) => (
            <option key={cat} value={cat} className="text-slate-100 bg-slate-900">
              {cat}
            </option>
          ))}
        </select>
        {errors.category && <p className="text-xs text-rose-600 mt-1">{errors.category}</p>}
      </div>

      <div className="w-full space-y-1">
        <label className="block text-sm font-medium text-slate-200">
          {t("onboarding.business.description")} *
        </label>
        <textarea
          rows={3}
          aria-label={t("onboarding.business.description")}
          className={`w-full px-3 py-2 border rounded-xl shadow-xs focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm text-slate-100 bg-slate-900 placeholder:text-slate-500 ${
            errors.description ? "border-rose-500 focus:ring-rose-500" : "border-slate-700"
          }`}
          placeholder={t("onboarding.business.descriptionPlaceholder")}
          value={description}
          onChange={(e) => onChange({ description: e.target.value })}
        />
        {errors.description && <p className="text-xs text-rose-600 mt-1">{errors.description}</p>}
      </div>
    </div>
  );
};
