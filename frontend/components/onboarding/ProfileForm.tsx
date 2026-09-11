"use client";

import React from "react";
import { Input } from "@/components/ui/Input";

interface ProfileFormProps {
  fullName: string;
  phoneNumber: string;
  experienceYears: number;
  onChange: (fields: Record<string, any>) => void;
}

export const ProfileForm: React.FC<ProfileFormProps> = ({
  fullName,
  phoneNumber,
  experienceYears,
  onChange,
}) => {
  // TODO [Frontend Lead]: Add validation, OTP verification stubs, and CSC operator mode toggle
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Entrepreneur Profile</h3>
      <Input
        label="Full Name"
        placeholder="Enter entrepreneur's full name"
        value={fullName}
        onChange={(e) => onChange({ full_name: e.target.value })}
      />
      <Input
        label="Mobile Phone Number"
        placeholder="10-digit Indian mobile number"
        value={phoneNumber}
        onChange={(e) => onChange({ phone_number: e.target.value })}
      />
      <Input
        label="Relevant Experience (Years)"
        type="number"
        min={0}
        value={experienceYears || 0}
        onChange={(e) => onChange({ experience_years: parseInt(e.target.value) || 0 })}
      />
    </div>
  );
};
