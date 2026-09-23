"use client";

import React from "react";
import { Input } from "@/components/ui/Input";
import { LocationData } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";
import { MapPin, Info } from "lucide-react";

interface LocationFormProps {
  location: LocationData;
  errors?: Record<string, string>;
  onChange: (location: LocationData) => void;
}

export const LocationForm: React.FC<LocationFormProps> = ({
  location,
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
            1
          </span>
          <h2 className="text-xl font-bold text-white tracking-tight">
            {t("onboarding.step1Title")}
          </h2>
        </div>
        <p className="text-xs sm:text-sm text-slate-400">
          {t("onboarding.step1Sub")}
        </p>
      </div>

      {/* Purpose Explanation Callout */}
      <div className="p-4 bg-[#0E2635] border border-cyan-500/30 rounded-xl flex items-start gap-3 text-xs sm:text-sm text-slate-300 shadow-xs">
        <div className="w-7 h-7 rounded-lg bg-cyan-500/15 text-cyan-300 flex items-center justify-center flex-shrink-0 mt-0.5 border border-cyan-500/30">
          <Info className="w-4 h-4" aria-hidden="true" />
        </div>
        <div>
          <span className="font-semibold text-cyan-200 block mb-0.5">Why we need your location</span>
          <p className="text-slate-300 text-xs sm:text-sm leading-relaxed">
            {t("onboarding.location.explanation")}
          </p>
        </div>
      </div>

      {/* Hierarchical Location Inputs */}
      <div className="bg-[#0B1F2D] p-4 sm:p-5 rounded-xl border border-slate-800 space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-800/80 pb-3">
          <MapPin className="w-4 h-4 text-emerald-400" aria-hidden="true" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Location Hierarchy
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label={`${t("onboarding.location.state")} *`}
            placeholder="e.g. Uttar Pradesh, Maharashtra, Bihar, Tamil Nadu"
            value={location.state || ""}
            error={errors.state}
            helperText="Select or enter the state of your enterprise."
            onChange={(e) => onChange({ ...location, state: e.target.value })}
          />

          <Input
            label={`${t("onboarding.location.district")} *`}
            placeholder="e.g. Varanasi, Pune, Patna, Madurai"
            value={location.district || ""}
            error={errors.district}
            helperText="District administrative headquarters."
            onChange={(e) => onChange({ ...location, district: e.target.value })}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label={t("onboarding.location.subDistrict")}
            placeholder={t("onboarding.location.subDistrictPlaceholder")}
            value={location.block || ""}
            error={errors.block}
            helperText="Sub-district, tehsil, or taluka name (optional)."
            onChange={(e) => onChange({ ...location, block: e.target.value })}
          />

          <Input
            label={`${t("onboarding.location.village")} *`}
            placeholder={t("onboarding.location.villagePlaceholder")}
            value={location.village || ""}
            error={errors.village}
            helperText={t("onboarding.location.locationHelp")}
            onChange={(e) => onChange({ ...location, village: e.target.value })}
          />
        </div>
      </div>
    </div>
  );
};
