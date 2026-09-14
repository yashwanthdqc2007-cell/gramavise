import { RecommendationStatus } from "@/lib/types";

export const HISTORY_STORAGE_KEY = "gramavise_history_v1";
export const MAX_HISTORY_ENTRIES = 20;

export interface HistoryEntry {
  analysis_id: string;
  business_name: string;
  business_category: string;
  recommendation_status: RecommendationStatus;
  created_at: string;
  last_opened_at?: string;
}

/**
 * Validate that an unknown object adheres to the expected HistoryEntry schema.
 */
export function isValidHistoryEntry(data: any): data is HistoryEntry {
  if (!data || typeof data !== "object") return false;
  if (!data.analysis_id || typeof data.analysis_id !== "string") return false;
  if (!data.business_name || typeof data.business_name !== "string") return false;
  if (!data.business_category || typeof data.business_category !== "string") return false;
  if (!data.recommendation_status || typeof data.recommendation_status !== "string") return false;
  if (!["PROCEED", "VALIDATE_FIRST", "RECONSIDER"].includes(data.recommendation_status)) return false;
  if (!data.created_at || typeof data.created_at !== "string") return false;

  return true;
}

/**
 * Normalize and migrate legacy or variant history entries into canonical HistoryEntry schema.
 * Supports legacy fields: id -> analysis_id, business_type -> business_category, overall_verdict -> recommendation_status.
 * Supports legacy verdicts: FEASIBLE_TO_PROCEED -> PROCEED, NOT_FEASIBLE -> RECONSIDER, etc.
 */
export function normalizeHistoryEntry(data: any): HistoryEntry | null {
  if (!data || typeof data !== "object") return null;

  // If already fully valid, return as-is
  if (isValidHistoryEntry(data)) return data;

  const rawId = data.analysis_id || data.id;
  if (!rawId || typeof rawId !== "string" || !rawId.trim()) return null;

  const rawName = data.business_name;
  const business_name = typeof rawName === "string" && rawName.trim() ? rawName.trim() : "Untitled Business";

  const rawCategory = data.business_category || data.business_type;
  const business_category = typeof rawCategory === "string" && rawCategory.trim() ? rawCategory.trim() : "General";

  // Map recommendation status from recommendation_status or legacy overall_verdict
  let recommendation_status: RecommendationStatus | null = null;
  const rawStatus = data.recommendation_status || data.overall_verdict;
  if (typeof rawStatus === "string") {
    const normalizedStatusStr = rawStatus.trim().toUpperCase();
    if (["PROCEED", "VALIDATE_FIRST", "RECONSIDER"].includes(normalizedStatusStr)) {
      recommendation_status = normalizedStatusStr as RecommendationStatus;
    } else if (normalizedStatusStr === "FEASIBLE_TO_PROCEED" || normalizedStatusStr === "FEASIBLE") {
      recommendation_status = "PROCEED";
    } else if (normalizedStatusStr === "NOT_FEASIBLE" || normalizedStatusStr === "HIGH_RISK") {
      recommendation_status = "RECONSIDER";
    } else if (normalizedStatusStr === "MODERATE_RISK" || normalizedStatusStr === "VALIDATE") {
      recommendation_status = "VALIDATE_FIRST";
    }
  }

  if (!recommendation_status) return null;

  const rawCreatedAt = data.created_at;
  const created_at = typeof rawCreatedAt === "string" && !isNaN(Date.parse(rawCreatedAt))
    ? rawCreatedAt
    : new Date().toISOString();

  const rawOpenedAt = data.last_opened_at;
  const last_opened_at = typeof rawOpenedAt === "string" && !isNaN(Date.parse(rawOpenedAt))
    ? rawOpenedAt
    : undefined;

  const candidate: HistoryEntry = {
    analysis_id: rawId.trim(),
    business_name,
    business_category,
    recommendation_status,
    created_at,
    ...(last_opened_at ? { last_opened_at } : {}),
  };

  return isValidHistoryEntry(candidate) ? candidate : null;
}

/**
 * Load saved analysis history entries from browser localStorage safely.
 */
export function loadHistory(): HistoryEntry[] {
  if (typeof window === "undefined") return [];

  try {
    const raw = localStorage.getItem(HISTORY_STORAGE_KEY);
    if (!raw) return [];

    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      localStorage.removeItem(HISTORY_STORAGE_KEY);
      return [];
    }

    let needsMigration = false;
    const validEntries: HistoryEntry[] = [];

    for (const item of parsed) {
      const normalized = normalizeHistoryEntry(item);
      if (normalized) {
        validEntries.push(normalized);
        if (normalized !== item) {
          needsMigration = true;
        }
      } else {
        needsMigration = true;
      }
    }

    const bounded = validEntries.slice(0, MAX_HISTORY_ENTRIES);

    // If any legacy item was migrated, persist clean canonical format back to localStorage
    if (needsMigration) {
      localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(bounded));
    }

    return bounded;
  } catch (err) {
    console.error("Failed to load history from localStorage:", err);
    return [];
  }
}

/**
 * Save an analysis to local history index.
 * Deduplicates by analysis_id and bounds list to MAX_HISTORY_ENTRIES.
 */
export function saveHistoryEntry(
  entry: Omit<HistoryEntry, "last_opened_at"> & { last_opened_at?: string }
): boolean {
  if (typeof window === "undefined") return false;

  try {
    const current = loadHistory();
    const existingIndex = current.findIndex((item) => item.analysis_id === entry.analysis_id);

    const nowIso = new Date().toISOString();
    let updatedList: HistoryEntry[];

    if (existingIndex >= 0) {
      // Update existing entry without duplicating
      const existing = current[existingIndex];
      const updatedEntry: HistoryEntry = {
        analysis_id: entry.analysis_id,
        business_name: entry.business_name || existing.business_name,
        business_category: entry.business_category || existing.business_category,
        recommendation_status: entry.recommendation_status || existing.recommendation_status,
        created_at: existing.created_at || entry.created_at,
        last_opened_at: entry.last_opened_at || nowIso,
      };

      // Move updated entry to the front of the list
      updatedList = [
        updatedEntry,
        ...current.filter((_, idx) => idx !== existingIndex),
      ];
    } else {
      // Prepend new entry
      const newEntry: HistoryEntry = {
        analysis_id: entry.analysis_id,
        business_name: entry.business_name?.trim() || "Untitled Business",
        business_category: entry.business_category?.trim() || "General",
        recommendation_status: entry.recommendation_status,
        created_at: entry.created_at || nowIso,
        last_opened_at: entry.last_opened_at || nowIso,
      };

      updatedList = [newEntry, ...current];
    }

    // Enforce hard maximum limit of 20 entries
    const boundedList = updatedList.slice(0, MAX_HISTORY_ENTRIES);
    localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(boundedList));
    return true;
  } catch (err) {
    console.error("Failed to save history entry to localStorage:", err);
    return false;
  }
}

/**
 * Update the last_opened_at timestamp for a specific analysis in local history.
 */
export function updateHistoryEntryOpened(analysisId: string): void {
  if (typeof window === "undefined") return;

  try {
    const current = loadHistory();
    const target = current.find((item) => item.analysis_id === analysisId);
    if (target) {
      saveHistoryEntry({
        ...target,
        last_opened_at: new Date().toISOString(),
      });
    }
  } catch (err) {
    console.error("Failed to update history opened timestamp:", err);
  }
}

/**
 * Remove a specific entry from local device history.
 * Note: This only deletes the local device index; it does NOT mutate or delete the permanent backend Analysis record.
 */
export function removeHistoryEntry(analysisId: string): boolean {
  if (typeof window === "undefined") return false;

  try {
    const current = loadHistory();
    const filtered = current.filter((item) => item.analysis_id !== analysisId);
    localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(filtered));
    return true;
  } catch (err) {
    console.error("Failed to remove history entry from localStorage:", err);
    return false;
  }
}

/**
 * Clear all local device history.
 */
export function clearHistory(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(HISTORY_STORAGE_KEY);
  } catch (err) {
    console.error("Failed to clear local history:", err);
  }
}
