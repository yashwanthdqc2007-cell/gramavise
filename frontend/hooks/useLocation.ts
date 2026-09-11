"use client";

import { useState } from "react";
import { LocationData } from "@/lib/types";

export function useLocation() {
  const [location, setLocation] = useState<LocationData>({
    state: "",
    district: "",
    village: "",
  });

  const setCoordinates = (latitude: number, longitude: number) => {
    setLocation((prev) => ({ ...prev, latitude, longitude }));
  };

  const setLocationDetails = (state: string, district: string, village: string) => {
    setLocation((prev) => ({ ...prev, state, district, village }));
  };

  return { location, setCoordinates, setLocationDetails };
}
