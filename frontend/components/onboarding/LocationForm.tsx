"use client";

import React from "react";
import { Input } from "@/components/ui/Input";
import { LocationData } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";

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
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-white">{t("onboarding.step2Title")}</h3>
        <p className="text-xs text-slate-400 mt-0.5">
          {t("onboarding.step2Sub")}
        </p>
      </div>

      <Input
        label={`${t("onboarding.location.state")} *`}
        placeholder="e.g. Uttar Pradesh, Maharashtra, Bihar"
        value={location.state}
        error={errors.state}
        onChange={(e) => onChange({ ...location, state: e.target.value })}
      />

      <Input
        label={`${t("onboarding.location.district")} *`}
        placeholder="e.g. Varanasi, Pune, Patna"
        value={location.district}
        error={errors.district}
        onChange={(e) => onChange({ ...location, district: e.target.value })}
      />

      <Input
        label={`${t("onboarding.location.village")} *`}
        placeholder={t("onboarding.location.villagePlaceholder")}
        value={location.village}
        error={errors.village}
        helperText={t("onboarding.location.locationHelp")}
        onChange={(e) => onChange({ ...location, village: e.target.value })}
      />
    </div>
  );
};
