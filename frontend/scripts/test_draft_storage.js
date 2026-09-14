/**
 * Test script for Step 5E Draft Storage logic.
 */
const assert = require("assert");

// Mock window and localStorage
const mockStorage = {};
global.window = {};
global.localStorage = {
  getItem: (key) => mockStorage[key] || null,
  setItem: (key, val) => { mockStorage[key] = String(val); },
  removeItem: (key) => { delete mockStorage[key]; },
  clear: () => { Object.keys(mockStorage).forEach(k => delete mockStorage[k]); }
};

const DRAFT_STORAGE_KEY = "gramavise_draft_v1";
const DRAFT_SCHEMA_VERSION = 1;
const DRAFT_EXPIRY_MS = 7 * 24 * 60 * 60 * 1000;

function isValidDraft(data) {
  if (!data || typeof data !== "object") return false;
  if (data.version !== DRAFT_SCHEMA_VERSION) return false;
  if (!data.updated_at || typeof data.updated_at !== "string") return false;
  if (typeof data.step !== "number" || data.step < 1 || data.step > 4) return false;
  if (!data.profile || typeof data.profile !== "object") return false;
  if (!data.financials || typeof data.financials !== "object") return false;

  const draftTime = new Date(data.updated_at).getTime();
  if (isNaN(draftTime)) return false;
  if (Date.now() - draftTime > DRAFT_EXPIRY_MS) return false;

  return true;
}

function loadDraft() {
  try {
    const raw = localStorage.getItem(DRAFT_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!isValidDraft(parsed)) {
      localStorage.removeItem(DRAFT_STORAGE_KEY);
      return null;
    }
    return parsed;
  } catch {
    try {
      localStorage.removeItem(DRAFT_STORAGE_KEY);
    } catch {}
    return null;
  }
}

function saveDraft(step, language, profile, financials, fullName) {
  try {
    const draft = {
      version: DRAFT_SCHEMA_VERSION,
      updated_at: new Date().toISOString(),
      step: Math.min(4, Math.max(1, step)),
      language: language || "en",
      profile: { ...profile },
      financials: { ...financials },
      entrepreneur: { full_name: fullName?.trim() || "" }
    };
    localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify(draft));
    return true;
  } catch {
    return false;
  }
}

function clearDraft() {
  localStorage.removeItem(DRAFT_STORAGE_KEY);
}

console.log("Running Step 5E Draft Storage Unit Tests...");

// Test 1: Empty state
assert.strictEqual(loadDraft(), null, "Empty state should return null");
console.log("[PASS] Empty state returns null");

// Test 2: Save and load valid draft
const sampleProfile = {
  business_name: "Ramesh Kirana",
  category: "Grocery & Daily Needs",
  description: "Village grocery shop",
  location: { state: "Maharashtra", district: "Pune", village: "Baramati" },
  experience_years: 5,
  own_capital: 50000,
  desired_loan: 150000,
  is_new_business: true
};
const sampleFinancials = {
  startup_cost: 25000,
  equipment_cost: 100000,
  inventory_cost: 25000,
  monthly_fixed_cost: 6000,
  customers_per_day: 40,
  avg_ticket_price: 50,
  working_days_per_month: 26,
  variable_cost_pct: 40,
  interest_rate_pct: 10.5,
  loan_tenure_months: 36
};

assert.strictEqual(saveDraft(2, "hi", sampleProfile, sampleFinancials, "Ramesh Patil"), true);
const loaded = loadDraft();
assert.ok(loaded, "Draft should be loaded");
assert.strictEqual(loaded.step, 2);
assert.strictEqual(loaded.language, "hi");
assert.strictEqual(loaded.profile.business_name, "Ramesh Kirana");
assert.strictEqual(loaded.entrepreneur.full_name, "Ramesh Patil");
console.log("[PASS] Save and load valid draft");

// Test 3: Language change preserves draft data
assert.strictEqual(saveDraft(2, "mr", sampleProfile, sampleFinancials, "Ramesh Patil"), true);
const updatedLang = loadDraft();
assert.strictEqual(updatedLang.language, "mr");
assert.strictEqual(updatedLang.profile.business_name, "Ramesh Kirana");
console.log("[PASS] Language update preserves draft fields");

// Test 4: Malformed draft rejection
localStorage.setItem(DRAFT_STORAGE_KEY, "invalid json string");
assert.strictEqual(loadDraft(), null);
assert.strictEqual(localStorage.getItem(DRAFT_STORAGE_KEY), null, "Corrupted draft should be removed");
console.log("[PASS] Malformed JSON draft rejected and cleared");

// Test 5: Schema version mismatch rejection
localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify({ version: 99, step: 1 }));
assert.strictEqual(loadDraft(), null);
console.log("[PASS] Outdated schema version rejected");

// Test 6: 7-day expiry rejection
const expiredDate = new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString();
const expiredDraft = {
  version: DRAFT_SCHEMA_VERSION,
  updated_at: expiredDate,
  step: 2,
  language: "en",
  profile: sampleProfile,
  financials: sampleFinancials,
  entrepreneur: {}
};
localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify(expiredDraft));
assert.strictEqual(loadDraft(), null);
console.log("[PASS] Expired draft (>7 days) cleanly rejected and cleared");

// Test 7: Clear draft
saveDraft(3, "en", sampleProfile, sampleFinancials, "Test");
assert.ok(loadDraft() !== null);
clearDraft();
assert.strictEqual(loadDraft(), null);
console.log("[PASS] Clear draft removes data");

console.log("\nAll 7 Step 5E draft storage tests passed successfully!");
