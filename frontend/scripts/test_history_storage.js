/**
 * Unit test for client-side bounded history storage (Phase 6H).
 */

const assert = require("assert");

// Mock window and localStorage environment
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => {
      store[key] = String(value);
    },
    removeItem: (key) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

global.window = {};
global.localStorage = localStorageMock;

const HISTORY_STORAGE_KEY = "gramavise_history_v1";
const MAX_HISTORY_ENTRIES = 20;

function isValidHistoryEntry(data) {
  if (!data || typeof data !== "object") return false;
  if (!data.analysis_id || typeof data.analysis_id !== "string") return false;
  if (!data.business_name || typeof data.business_name !== "string") return false;
  if (!data.business_category || typeof data.business_category !== "string") return false;
  if (!data.recommendation_status || typeof data.recommendation_status !== "string") return false;
  if (!["PROCEED", "VALIDATE_FIRST", "RECONSIDER"].includes(data.recommendation_status)) return false;
  if (!data.created_at || typeof data.created_at !== "string") return false;
  return true;
}

function normalizeHistoryEntry(data) {
  if (!data || typeof data !== "object") return null;
  if (isValidHistoryEntry(data)) return data;

  const rawId = data.analysis_id || data.id;
  if (!rawId || typeof rawId !== "string" || !rawId.trim()) return null;

  const rawName = data.business_name;
  const business_name = typeof rawName === "string" && rawName.trim() ? rawName.trim() : "Untitled Business";

  const rawCategory = data.business_category || data.business_type;
  const business_category = typeof rawCategory === "string" && rawCategory.trim() ? rawCategory.trim() : "General";

  let recommendation_status = null;
  const rawStatus = data.recommendation_status || data.overall_verdict;
  if (typeof rawStatus === "string") {
    const normalizedStatusStr = rawStatus.trim().toUpperCase();
    if (["PROCEED", "VALIDATE_FIRST", "RECONSIDER"].includes(normalizedStatusStr)) {
      recommendation_status = normalizedStatusStr;
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

  const candidate = {
    analysis_id: rawId.trim(),
    business_name,
    business_category,
    recommendation_status,
    created_at,
    ...(last_opened_at ? { last_opened_at } : {}),
  };

  return isValidHistoryEntry(candidate) ? candidate : null;
}

function loadHistory() {
  try {
    const raw = localStorage.getItem(HISTORY_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];

    let needsMigration = false;
    const validEntries = [];

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
    if (needsMigration) {
      localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(bounded));
    }
    return bounded;
  } catch {
    return [];
  }
}

function saveHistoryEntry(entry) {
  try {
    const current = loadHistory();
    const existingIndex = current.findIndex((item) => item.analysis_id === entry.analysis_id);
    const nowIso = new Date().toISOString();
    let updatedList;

    if (existingIndex >= 0) {
      const existing = current[existingIndex];
      const updatedEntry = {
        analysis_id: entry.analysis_id,
        business_name: entry.business_name || existing.business_name,
        business_category: entry.business_category || existing.business_category,
        recommendation_status: entry.recommendation_status || existing.recommendation_status,
        created_at: existing.created_at || entry.created_at,
        last_opened_at: entry.last_opened_at || nowIso,
      };
      updatedList = [updatedEntry, ...current.filter((_, idx) => idx !== existingIndex)];
    } else {
      const newEntry = {
        analysis_id: entry.analysis_id,
        business_name: entry.business_name?.trim() || "Untitled Business",
        business_category: entry.business_category?.trim() || "General",
        recommendation_status: entry.recommendation_status,
        created_at: entry.created_at || nowIso,
        last_opened_at: entry.last_opened_at || nowIso,
      };
      updatedList = [newEntry, ...current];
    }

    const boundedList = updatedList.slice(0, MAX_HISTORY_ENTRIES);
    localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(boundedList));
    return true;
  } catch {
    return false;
  }
}

function removeHistoryEntry(analysisId) {
  try {
    const current = loadHistory();
    const filtered = current.filter((item) => item.analysis_id !== analysisId);
    localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(filtered));
    return true;
  } catch {
    return false;
  }
}

console.log("Running Phase 6H History Storage tests...");

// Test 1: Empty history initialization
localStorage.clear();
assert.deepStrictEqual(loadHistory(), [], "Initial load on empty storage must return empty array");
console.log("[PASS] Test 1: Empty history initialization");

// Test 2: Save first history entry
const entry1 = {
  analysis_id: "uuid-1",
  business_name: "Ramesh Atta Chakki",
  business_category: "Flour Milling",
  recommendation_status: "PROCEED",
  created_at: new Date().toISOString(),
};
saveHistoryEntry(entry1);
const historyAfter1 = loadHistory();
assert.strictEqual(historyAfter1.length, 1);
assert.strictEqual(historyAfter1[0].analysis_id, "uuid-1");
assert.strictEqual(historyAfter1[0].business_name, "Ramesh Atta Chakki");
console.log("[PASS] Test 2: Single entry creation");

// Test 3: Idempotent replay with same analysis_id does not duplicate
saveHistoryEntry({
  analysis_id: "uuid-1",
  business_name: "Ramesh Atta Chakki",
  business_category: "Flour Milling",
  recommendation_status: "PROCEED",
  created_at: new Date().toISOString(),
});
const historyAfterReplay = loadHistory();
assert.strictEqual(historyAfterReplay.length, 1, "Idempotent replay must not create duplicate history entries");
console.log("[PASS] Test 3: Idempotent duplicate protection");

// Test 4: Maximum 20 bounded capacity
for (let i = 2; i <= 25; i++) {
  saveHistoryEntry({
    analysis_id: `uuid-${i}`,
    business_name: `Business ${i}`,
    business_category: "Retail",
    recommendation_status: "VALIDATE_FIRST",
    created_at: new Date().toISOString(),
  });
}
const boundedHistory = loadHistory();
assert.strictEqual(boundedHistory.length, 20, "History must be strictly capped at 20 entries");
assert.strictEqual(boundedHistory[0].analysis_id, "uuid-25", "Most recent entry must be at the top");
assert.strictEqual(
  boundedHistory.some((e) => e.analysis_id === "uuid-1"),
  false,
  "Oldest entries beyond limit must be purged"
);
console.log("[PASS] Test 4: Bounded 20-entry FIFO eviction");

// Test 5: Removal of specific history entry
removeHistoryEntry("uuid-25");
const historyAfterRemoval = loadHistory();
assert.strictEqual(historyAfterRemoval.length, 19);
assert.strictEqual(
  historyAfterRemoval.some((e) => e.analysis_id === "uuid-25"),
  false
);
console.log("[PASS] Test 5: Local removal isolation");

// Test 6: Storage schema payload minimization
const rawStored = JSON.parse(localStorage.getItem(HISTORY_STORAGE_KEY));
for (const item of rawStored) {
  assert.strictEqual(item.financial_result, undefined, "Financial result must NOT be stored in localStorage");
  assert.strictEqual(item.evidence_ledger, undefined, "Evidence ledger must NOT be stored in localStorage");
  assert.strictEqual(item.ai_explanation, undefined, "AI explanation must NOT be stored in localStorage");
  assert.strictEqual(item.pan, undefined, "PII must NOT be stored in localStorage");
}
// Test 7: Legacy history migration & normalization
localStorage.clear();
const legacyData = [
  {
    id: "legacy-uuid-1",
    business_name: "Kisan Flour Mill",
    business_type: "Kirana & General Store",
    overall_verdict: "FEASIBLE_TO_PROCEED",
    created_at: "2026-09-13T03:35:00.000Z",
  },
  {
    id: "legacy-uuid-2",
    business_name: "Pig Farming Unit",
    business_type: "Animal Husbandry",
    overall_verdict: "NOT_FEASIBLE",
    created_at: "2026-09-13T04:00:00.000Z",
  },
  {
    // Completely invalid/corrupted entry that must be discarded safely
    foo: "bar",
  },
];
localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(legacyData));

const migratedHistory = loadHistory();
assert.strictEqual(migratedHistory.length, 2, "Only 2 valid legacy entries should be migrated");
assert.strictEqual(migratedHistory[0].analysis_id, "legacy-uuid-1");
assert.strictEqual(migratedHistory[0].business_category, "Kirana & General Store");
assert.strictEqual(migratedHistory[0].recommendation_status, "PROCEED");
assert.strictEqual(migratedHistory[1].analysis_id, "legacy-uuid-2");
assert.strictEqual(migratedHistory[1].recommendation_status, "RECONSIDER");

// Verify that migrated clean format was written back to localStorage
const reloadedRaw = JSON.parse(localStorage.getItem(HISTORY_STORAGE_KEY));
assert.strictEqual(reloadedRaw[0].analysis_id, "legacy-uuid-1");
assert.strictEqual(reloadedRaw[0].id, undefined, "Legacy 'id' should be normalized to 'analysis_id'");
assert.strictEqual(reloadedRaw[0].business_category, "Kirana & General Store");
assert.strictEqual(reloadedRaw[0].recommendation_status, "PROCEED");
console.log("[PASS] Test 7: Legacy history entry migration & normalization");

console.log("All Phase 6H History Storage tests passed successfully!");
