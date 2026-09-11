export const APP_NAME = "GramaVise";
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export const SUPPORTED_LANGUAGES = [
  { code: "en", label: "English" },
  { code: "hi", label: "हिन्दी (Hindi)" },
  { code: "mr", label: "मराठी (Marathi)" },
  { code: "bn", label: "বাংলা (Bengali)" },
  { code: "te", label: "తెలుగు (Telugu)" },
  { code: "ta", label: "தமிழ் (Tamil)" },
] as const;

export const POPULAR_BUSINESS_CATEGORIES = [
  "Kirana & General Store",
  "Flour & Spice Milling (Atta Chakki)",
  "Dairy Farming & Milk Chilling",
  "Poultry Farming",
  "Tailoring & Garment Making",
  "Small Agro / Food Processing",
  "Mobile & Electronics Repair",
  "Building Material & Hardware",
] as const;

export const EVIDENCE_BADGE_COLORS = {
  OBSERVED: "bg-blue-100 text-blue-800 border-blue-300",
  CALCULATED: "bg-emerald-100 text-emerald-800 border-emerald-300",
  MODELLED: "bg-purple-100 text-purple-800 border-purple-300",
  ASSUMED: "bg-amber-100 text-amber-800 border-amber-300",
  NEEDS_VERIFICATION: "bg-rose-100 text-rose-800 border-rose-300",
} as const;
