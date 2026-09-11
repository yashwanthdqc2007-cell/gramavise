import { apiClient } from "@/lib/api";
import { MarketResult } from "@/lib/types";

export interface MarketEvidenceParams {
  state: string;
  district: string;
  village: string;
  category: string;
  latitude?: number;
  longitude?: number;
  radius_km?: number;
}

export async function fetchMarketEvidence(params: MarketEvidenceParams): Promise<MarketResult> {
  const query = new URLSearchParams({
    state: params.state,
    district: params.district,
    village: params.village,
    category: params.category,
    ...(params.latitude ? { latitude: String(params.latitude) } : {}),
    ...(params.longitude ? { longitude: String(params.longitude) } : {}),
    ...(params.radius_km ? { radius_km: String(params.radius_km) } : {}),
  });

  return apiClient<MarketResult>(`/market/evidence?${query.toString()}`);
}
