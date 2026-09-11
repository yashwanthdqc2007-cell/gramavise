"use client";

import { useState } from "react";
import { BusinessProfile } from "@/lib/types";

const initialProfile: BusinessProfile = {
  business_name: "",
  category: "",
  description: "",
  location: {
    state: "",
    district: "",
    village: "",
  },
  experience_years: 0,
  own_capital: 0,
  desired_loan: 0,
  is_new_business: true,
};

export function useBusinessProfile() {
  const [profile, setProfile] = useState<BusinessProfile>(initialProfile);

  const updateProfile = (updates: Partial<BusinessProfile>) => {
    setProfile((prev) => ({ ...prev, ...updates }));
  };

  const resetProfile = () => {
    setProfile(initialProfile);
  };

  return { profile, updateProfile, resetProfile };
}
