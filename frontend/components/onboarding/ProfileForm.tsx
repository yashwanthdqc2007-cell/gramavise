"use client";

import React from "react";
import { Input } from "@/components/ui/Input";
import { useTranslation } from "@/lib/i18n";

interface ProfileFormProps {
  fullName: string;
  phoneNumber: string;
  experienceYears: number;
  errors?: Record<string, string>;
  onChange: (fields: { full_name?: string; phone_number?: string; experience_years?: number }) => void;
}

export const ProfileForm: React.FC<ProfileFormProps> = ({
  fullName,
  phoneNumber,
  experienceYears,
  errors = {},
  onChange,
}) => {
  const { t } = useTranslation();

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-bold text-white">{t("onboarding.step1Title")}</h3>
        <p className="text-xs text-slate-400 mt-0.5">
          {t("onboarding.step1Sub")}
        </p>
      </div>

      <Input
        label={`${t("onboarding.profile.fullName")} *`}
        placeholder={t("onboarding.profile.fullNamePlaceholder")}
        value={fullName}
        error={errors.full_name}
        onChange={(e) => onChange({ full_name: e.target.value })}
      />

      <Input
        label={`${t("onboarding.profile.phone")} *`}
        placeholder={t("onboarding.profile.phonePlaceholder")}
        type="tel"
        maxLength={10}
        value={phoneNumber}
        error={errors.phone_number}
        onChange={(e) => onChange({ phone_number: e.target.value.replace(/\D/g, "") })}
      />

      <Input
        label={`${t("onboarding.profile.experience")} *`}
        type="number"
        min={0}
        max={60}
        placeholder={t("onboarding.profile.experiencePlaceholder")}
        value={experienceYears ?? ""}
        error={errors.experience_years}
        helperText={t("onboarding.profile.experienceHelp")}
        onChange={(e) => {
          const val = e.target.value === "" ? 0 : parseInt(e.target.value, 10);
          onChange({ experience_years: isNaN(val) ? 0 : val });
        }}
      />
    </div>
  );
};
