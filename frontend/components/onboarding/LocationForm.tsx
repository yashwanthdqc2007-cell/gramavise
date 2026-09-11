"use client";

import React from "react";
import { Input } from "@/components/ui/Input";
import { LocationData } from "@/lib/types";

interface LocationFormProps {
  location: LocationData;
  onChange: (location: LocationData) => void;
}

export const LocationForm: React.FC<LocationFormProps> = ({ location, onChange }) => {
  // TODO [Frontend Lead]: Add auto-complete dropdown for State / District / Village from Census data
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Enterprise Location</h3>
      <Input
        label="State"
        placeholder="e.g. Uttar Pradesh, Maharashtra"
        value={location.state}
        onChange={(e) => onChange({ ...location, state: e.target.value })}
      />
      <Input
        label="District"
        placeholder="e.g. Varanasi, Pune"
        value={location.district}
        onChange={(e) => onChange({ ...location, district: e.target.value })}
      />
      <Input
        label="Village / Town / Gram Panchayat"
        placeholder="e.g. Rampur"
        value={location.village}
        onChange={(e) => onChange({ ...location, village: e.target.value })}
      />
    </div>
  );
};
