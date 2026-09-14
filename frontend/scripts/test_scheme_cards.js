/**
 * Schemes Card Display Mapping & Formatting Regression Test Suite.
 * 
 * Verifies that the SchemeCatalogItem / active_version API shape is safely
 * transformed into SchemeInfo and formatted for the Scheme card display without
 * ever producing:
 * - NaN
 * - undefined
 * - empty %
 * - invalid currency display
 */

const assert = require("assert");

console.log("Running Schemes Card Display & Formatting Regression Test Suite...\n");

// --- 1. Pure display formatting functions as implemented in Schemes Directory ---

function formatCurrencyINR(amount) {
  if (amount === null || amount === undefined || typeof amount !== "number" || isNaN(amount)) {
    return "N/A";
  }
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatLoan(amount, naLabel = "N/A") {
  if (amount === null || amount === undefined || typeof amount !== "number" || isNaN(amount) || amount <= 0) {
    return naLabel;
  }
  return formatCurrencyINR(amount);
}

function formatSubsidy(pct, naLabel = "N/A") {
  if (pct === null || pct === undefined || typeof pct !== "number" || isNaN(pct)) {
    return naLabel;
  }
  return `${pct}%`;
}

function catalogItemToSchemeInfo(item) {
  if (!item || typeof item !== "object") {
    return {
      scheme_code: "UNKNOWN",
      scheme_name: "Unknown Scheme",
      ministry_or_dept: undefined,
      max_loan_amount: null,
      subsidy_percentage_general: null,
      subsidy_percentage_special: null,
      official_portal_url: undefined,
    };
  }

  const ver = item.active_version;
  return {
    scheme_code: item.scheme_code || "UNKNOWN",
    scheme_name: item.scheme_name || "Unknown Scheme",
    ministry_or_dept: item.ministry || item.department || undefined,
    max_loan_amount:
      ver && typeof ver.max_loan_amount === "number" && !isNaN(ver.max_loan_amount) && ver.max_loan_amount > 0
        ? ver.max_loan_amount
        : null,
    subsidy_percentage_general:
      ver && typeof ver.subsidy_percentage_general === "number" && !isNaN(ver.subsidy_percentage_general)
        ? ver.subsidy_percentage_general
        : null,
    subsidy_percentage_special:
      ver && typeof ver.subsidy_percentage_special === "number" && !isNaN(ver.subsidy_percentage_special)
        ? ver.subsidy_percentage_special
        : null,
    official_portal_url: ver ? ver.official_portal_url : undefined,
  };
}

function renderSchemeCardText(schemeInfo, naLabel = "N/A") {
  const maxLoanStr = formatLoan(schemeInfo.max_loan_amount, naLabel);
  const genSubsidyStr = formatSubsidy(schemeInfo.subsidy_percentage_general, naLabel);
  const speSubsidyStr = formatSubsidy(schemeInfo.subsidy_percentage_special, naLabel);
  const subsidyCombined = `${genSubsidyStr} / ${speSubsidyStr}`;

  return {
    title: schemeInfo.scheme_name,
    code: schemeInfo.scheme_code,
    dept: schemeInfo.ministry_or_dept || naLabel,
    maxLoan: maxLoanStr,
    subsidy: subsidyCombined,
    fullText: `${schemeInfo.scheme_code} - ${schemeInfo.scheme_name} | Dept: ${schemeInfo.ministry_or_dept || naLabel} | Max Loan: ${maxLoanStr} | Subsidy: ${subsidyCombined}`
  };
}

// --- Test 1: PMEGP Catalog Item with Active Version ---
const pmegpItem = {
  id: "sch-1",
  scheme_code: "PMEGP",
  scheme_name: "Prime Minister's Employment Generation Programme",
  ministry: "Ministry of MSME",
  department: null,
  active_version: {
    id: "ver-1",
    scheme_code: "PMEGP",
    version: "2024.1",
    status: "ACTIVE",
    max_loan_amount: 5000000,
    subsidy_percentage_general: 15,
    subsidy_percentage_special: 25,
    official_portal_url: "https://www.kviconline.gov.in/pmegpeportal",
  },
  total_versions: 1,
};

const pmegpInfo = catalogItemToSchemeInfo(pmegpItem);
assert.strictEqual(pmegpInfo.max_loan_amount, 5000000);
assert.strictEqual(pmegpInfo.subsidy_percentage_general, 15);
assert.strictEqual(pmegpInfo.subsidy_percentage_special, 25);

const pmegpCard = renderSchemeCardText(pmegpInfo);
assert.ok(pmegpCard.maxLoan.includes("50,00,000") || pmegpCard.maxLoan.includes("5,000,000"), "Formatted currency should contain formatted 50 Lakhs");
assert.strictEqual(pmegpCard.subsidy, "15% / 25%");
console.log("✓ Test 1: PMEGP active version correctly mapped and formatted with valid currency & percentages.");

// --- Test 2: PMMY Zero-Subsidy Scheme ---
const pmmyItem = {
  id: "sch-2",
  scheme_code: "PMMY",
  scheme_name: "Pradhan Mantri MUDRA Yojana",
  ministry: "Ministry of Finance",
  active_version: {
    id: "ver-2",
    scheme_code: "PMMY",
    version: "2024.1",
    status: "ACTIVE",
    max_loan_amount: 2000000,
    subsidy_percentage_general: 0,
    subsidy_percentage_special: 0,
    official_portal_url: "https://www.mudra.org.in",
  },
  total_versions: 1,
};

const pmmyInfo = catalogItemToSchemeInfo(pmmyItem);
assert.strictEqual(pmmyInfo.subsidy_percentage_general, 0);
const pmmyCard = renderSchemeCardText(pmmyInfo);
assert.strictEqual(pmmyCard.subsidy, "0% / 0%", "Zero percent subsidy must render as '0%', not empty '%' or 'N/A'");
console.log("✓ Test 2: PMMY zero-subsidy scheme correctly renders 0% instead of empty % or missing value.");

// --- Test 3: PMFME Uncapped Loan (max_loan_amount = 0) ---
const pmfmeItem = {
  id: "sch-3",
  scheme_code: "PMFME",
  scheme_name: "PM Formalisation of Micro Food Processing Enterprises",
  ministry: "Ministry of Food Processing Industries",
  active_version: {
    id: "ver-3",
    scheme_code: "PMFME",
    version: "2024.1",
    status: "ACTIVE",
    max_loan_amount: 0, // Uncapped / project-cost-linked
    subsidy_percentage_general: 35,
    subsidy_percentage_special: 35,
  },
  total_versions: 1,
};

const pmfmeInfo = catalogItemToSchemeInfo(pmfmeItem);
assert.strictEqual(pmfmeInfo.max_loan_amount, null, "0 max_loan_amount should be normalized to null");
const pmfmeCard = renderSchemeCardText(pmfmeInfo);
assert.strictEqual(pmfmeCard.maxLoan, "N/A", "Uncapped loan amount should render as 'N/A'");
assert.strictEqual(pmfmeCard.subsidy, "35% / 35%");
console.log("✓ Test 3: PMFME uncapped loan amount gracefully renders N/A without ₹0 or NaN.");

// --- Test 4: Scheme with active_version = null ---
const noVersionItem = {
  id: "sch-4",
  scheme_code: "STANDUP_INDIA",
  scheme_name: "Stand-Up India Scheme",
  ministry: "Ministry of Finance",
  active_version: null,
  total_versions: 0,
};

const noVersionInfo = catalogItemToSchemeInfo(noVersionItem);
const noVersionCard = renderSchemeCardText(noVersionInfo);
assert.strictEqual(noVersionCard.maxLoan, "N/A");
assert.strictEqual(noVersionCard.subsidy, "N/A / N/A");
console.log("✓ Test 4: Scheme with null active_version renders clean N/A placeholders.");

// --- Test 5: Malformed / Edge Case API Payload with NaNs and Undefineds ---
const malformedItem = {
  id: "sch-5",
  scheme_code: "TEST_CORRUPT",
  scheme_name: "Corrupt Scheme Item",
  active_version: {
    max_loan_amount: NaN,
    subsidy_percentage_general: undefined,
    subsidy_percentage_special: NaN,
  },
};

const malformedInfo = catalogItemToSchemeInfo(malformedItem);
const malformedCard = renderSchemeCardText(malformedInfo);
assert.strictEqual(malformedCard.maxLoan, "N/A");
assert.strictEqual(malformedCard.subsidy, "N/A / N/A");
console.log("✓ Test 5: Malformed payload containing NaNs and undefineds gracefully sanitized to N/A.");

// --- Test 6: Strict Regex Assertions across rendered cards ---
const allCards = [pmegpCard, pmmyCard, pmfmeCard, noVersionCard, malformedCard];

for (const card of allCards) {
  const text = card.fullText;

  // Must never produce "NaN"
  assert.ok(!text.includes("NaN"), `Found NaN in card text: ${text}`);

  // Must never produce "undefined"
  assert.ok(!text.includes("undefined"), `Found undefined in card text: ${text}`);

  // Must never produce empty percent (e.g. " %", "/ %", "% /", or isolated "%")
  assert.ok(!/\s%/.test(text), `Found empty/space percent in: ${text}`);
  assert.ok(!/\/\s*%/.test(text), `Found empty slash percent in: ${text}`);
  assert.ok(!/%\s*\//.test(text) || /\d+%\s*\//.test(text), `Found invalid percent before slash in: ${text}`);

  // Max loan must be either N/A or begin with ₹ or currency symbol
  assert.ok(card.maxLoan === "N/A" || /^[₹$€£\s\w]+[\d,]+/.test(card.maxLoan), `Invalid currency display: ${card.maxLoan}`);
}

console.log("✓ Test 6: Strict regex checks confirm 0 instances of NaN, undefined, empty %, or invalid currency.");

// --- Test 7: Multilingual N/A Label Support ---
const hindiCard = renderSchemeCardText(pmfmeInfo, "लागू नहीं");
assert.strictEqual(hindiCard.maxLoan, "लागू नहीं");
assert.strictEqual(hindiCard.subsidy, "35% / 35%");

const teluguCard = renderSchemeCardText(noVersionInfo, "వర్తించదు");
assert.strictEqual(teluguCard.maxLoan, "వర్తించదు");
assert.strictEqual(teluguCard.subsidy, "వర్తించదు / వర్తించదు");
console.log("✓ Test 7: Multilingual N/A label propagation verified across Hindi and Telugu.");

console.log("\nAll 7 Schemes Card Display & Formatting Regression Tests PASSED successfully!");
