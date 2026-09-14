"use client";

import { useState, useEffect } from "react";
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
  const [profile, setProfile] = useState<BusinessProfile>(() => {
    if (typeof window !== "undefined") {
      try {
        const stored = sessionStorage.getItem("gramavise_profile");
        if (stored) {
          return { ...initialProfile, ...JSON.parse(stored) };
        }
      } catch {
        // Fallback to initialProfile
      }
    }
    return initialProfile;
  });

  const updateProfile = (updates: Partial<BusinessProfile>) => {
    setProfile((prev) => {
      const updated = { ...prev, ...updates };
      if (typeof window !== "undefined") {
        try {
          sessionStorage.setItem("gramavise_profile", JSON.stringify(updated));
        } catch {
          // Ignore storage quota errors
        }
      }
      return updated;
    });
  };

  const resetProfile = () => {
    setProfile(initialProfile);
    if (typeof window !== "undefined") {
      try {
        sessionStorage.removeItem("gramavise_profile");
      } catch {
        // Ignore storage errors
      }
    }
  };

  return { profile, updateProfile, resetProfile };
}

