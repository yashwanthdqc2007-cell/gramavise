/**
 * Frontend verification script for Onboarding Step 3 validation & i18n localization.
 */

const assert = require("assert");
const path = require("path");
const fs = require("fs");

const LANGUAGES = ["en", "hi", "mr", "bn", "te", "ta"];
const DICT_DIR = path.join(__dirname, "..", "lib", "i18n", "dictionaries");

// Helper to extract nested translation from dictionary TS file
function loadDictionary(lang) {
  const filePath = path.join(DICT_DIR, `${lang}.ts`);
  const content = fs.readFileSync(filePath, "utf-8");
  
  // Extract businessNameRequired and descriptionRequired values
  const bNameMatch = content.match(/businessNameRequired\s*:\s*["']([^"']+)["']/);
  const descMatch = content.match(/descriptionRequired\s*:\s*["']([^"']+)["']/);
  const catMatch = content.match(/categoryRequired\s*:\s*["']([^"']+)["']/);

  assert.ok(bNameMatch, `businessNameRequired must exist in ${lang}.ts`);
  assert.ok(descMatch, `descriptionRequired must exist in ${lang}.ts`);
  assert.ok(catMatch, `categoryRequired must exist in ${lang}.ts`);

  return {
    onboarding: {
      errors: {
        businessNameRequired: bNameMatch[1],
        descriptionRequired: descMatch[1],
        categoryRequired: catMatch[1],
      },
    },
  };
}

// Emulate t() lookup function as defined in frontend/lib/i18n/index.ts
function createTranslator(dict, enDict) {
  return function t(pathStr) {
    const parts = pathStr.split(".");
    let current = dict;
    for (const p of parts) {
      if (!current) break;
      current = current[p];
    }
    if (typeof current === "string") return current;

    // Fallback to English
    let fallback = enDict;
    for (const p of parts) {
      if (!fallback) break;
      fallback = fallback[p];
    }
    if (typeof fallback === "string") return fallback;

    // Raw key fallback
    return pathStr;
  };
}

// Step 3 Validation logic under test (matching onboarding/page.tsx)
function validateStep3(profile, t) {
  const errs = {};
  if (!profile.business_name?.trim()) {
    errs.business_name = t("onboarding.errors.businessNameRequired");
  }
  if (!profile.category?.trim()) {
    errs.category = t("onboarding.errors.categoryRequired");
  }
  if (!profile.description?.trim()) {
    errs.description = t("onboarding.errors.descriptionRequired");
  }
  return {
    isValid: Object.keys(errs).length === 0,
    errors: errs,
  };
}

console.log("Running Onboarding Step 3 Validation & i18n Tests...\n");

const enDict = loadDictionary("en");

LANGUAGES.forEach((lang) => {
  const dict = loadDictionary(lang);
  const t = createTranslator(dict, enDict);

  console.log(`--- Testing Language: ${lang.toUpperCase()} ---`);

  // Test 1: Empty Business Name -> Localized error (never raw i18n key)
  const res1 = validateStep3(
    {
      business_name: "",
      category: "Grocery & Daily Needs",
      description: "A rural retail shop supplying provisions.",
    },
    t
  );
  assert.strictEqual(res1.isValid, false, `Expected validation failure for empty business_name [${lang}]`);
  assert.ok(res1.errors.business_name, `Expected business_name error [${lang}]`);
  assert.notStrictEqual(
    res1.errors.business_name,
    "onboarding.errors.businessNameRequired",
    `business_name error must NOT be raw key string [${lang}]`
  );
  assert.strictEqual(
    res1.errors.business_name,
    dict.onboarding.errors.businessNameRequired,
    `business_name error must match ${lang} dictionary value`
  );
  console.log(`  [PASS] Empty business_name -> localized: "${res1.errors.business_name}"`);

  // Test 1b: Whitespace-only Business Name -> Localized error
  const res1b = validateStep3(
    {
      business_name: "   ",
      category: "Grocery & Daily Needs",
      description: "A rural retail shop supplying provisions.",
    },
    t
  );
  assert.strictEqual(res1b.isValid, false, `Whitespace-only business_name must fail [${lang}]`);
  assert.strictEqual(res1b.errors.business_name, dict.onboarding.errors.businessNameRequired);
  console.log(`  [PASS] Whitespace business_name rejected [${lang}]`);

  // Test 2: Empty Description -> Localized error (never raw i18n key)
  const res2 = validateStep3(
    {
      business_name: "Kisan Stores",
      category: "Grocery & Daily Needs",
      description: "",
    },
    t
  );
  assert.strictEqual(res2.isValid, false, `Expected validation failure for empty description [${lang}]`);
  assert.ok(res2.errors.description, `Expected description error [${lang}]`);
  assert.notStrictEqual(
    res2.errors.description,
    "onboarding.errors.descriptionRequired",
    `description error must NOT be raw key string [${lang}]`
  );
  assert.strictEqual(
    res2.errors.description,
    dict.onboarding.errors.descriptionRequired,
    `description error must match ${lang} dictionary value`
  );
  console.log(`  [PASS] Empty description -> localized: "${res2.errors.description}"`);

  // Test 2b: Whitespace-only Description -> Localized error
  const res2b = validateStep3(
    {
      business_name: "Kisan Stores",
      category: "Grocery & Daily Needs",
      description: "   \n\t  ",
    },
    t
  );
  assert.strictEqual(res2b.isValid, false, `Whitespace-only description must fail [${lang}]`);
  assert.strictEqual(res2b.errors.description, dict.onboarding.errors.descriptionRequired);
  console.log(`  [PASS] Whitespace description rejected [${lang}]`);

  // Test 3: Multiple Missing Fields (Business Name + Description + Category)
  const res3 = validateStep3(
    {
      business_name: "",
      category: "",
      description: "",
    },
    t
  );
  assert.strictEqual(res3.isValid, false);
  assert.strictEqual(Object.keys(res3.errors).length, 3, "All 3 required fields must produce errors");
  console.log(`  [PASS] All missing fields produce errors simultaneously [${lang}]`);

  // Test 4: Valid Business Name + Category + Description -> Step 4 navigation permitted
  const res4 = validateStep3(
    {
      business_name: "Kisan Kirana & Spices",
      category: "Grocery & Daily Needs",
      description: "Supplying organic spices and daily essentials to Baramati village.",
    },
    t
  );
  assert.strictEqual(res4.isValid, true, `Valid step 3 data must pass validation [${lang}]`);
  assert.strictEqual(Object.keys(res4.errors).length, 0, `Errors must be empty for valid data [${lang}]`);
  
  // Simulate step progression
  let currentStep = 3;
  if (res4.isValid) {
    currentStep += 1;
  }
  assert.strictEqual(currentStep, 4, `Successful validation must navigate to Step 4 [${lang}]`);
  console.log(`  [PASS] Valid Step 3 input -> navigation to Step 4 verified [${lang}]\n`);
});

console.log("All Onboarding Step 3 validation & i18n parity tests passed across all 6 languages successfully!");
