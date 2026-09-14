const assert = require("assert");

// Pure JS reproduction of the parser logic to test in node environment
const VOICE_FIELD_CONFIGS = {
  own_capital: { fieldType: "own_capital", min: 0, max: 100000000, isFloat: false, unit: "INR" },
  desired_loan: { fieldType: "desired_loan", min: 0, max: 100000000, isFloat: false, unit: "INR" },
  startup_cost: { fieldType: "startup_cost", min: 0, max: 50000000, isFloat: false, unit: "INR" },
  equipment_cost: { fieldType: "equipment_cost", min: 0, max: 50000000, isFloat: false, unit: "INR" },
  inventory_cost: { fieldType: "inventory_cost", min: 0, max: 50000000, isFloat: false, unit: "INR" },
  monthly_fixed_cost: { fieldType: "monthly_fixed_cost", min: 0, max: 10000000, isFloat: false, unit: "INR" },
  customers_per_day: { fieldType: "customers_per_day", min: 0, max: 50000, isFloat: false, unit: "UNITS" },
  avg_ticket_price: { fieldType: "avg_ticket_price", min: 0, max: 1000000, isFloat: true, unit: "INR" },
  working_days_per_month: { fieldType: "working_days_per_month", min: 1, max: 31, isFloat: false, unit: "DAYS" },
  variable_cost_pct: { fieldType: "variable_cost_pct", min: 0, max: 100, isFloat: true, unit: "PERCENT" },
  interest_rate_pct: { fieldType: "interest_rate_pct", min: 0, max: 50, isFloat: true, unit: "PERCENT" },
  loan_tenure_months: { fieldType: "loan_tenure_months", min: 1, max: 360, isFloat: false, unit: "MONTHS" },
};

const SIMPLE_WORDS = {
  zero: 0, one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9, ten: 10,
  eleven: 11, twelve: 12, thirteen: 13, fourteen: 14, fifteen: 15, sixteen: 16, seventeen: 17, eighteen: 18, nineteen: 19,
  twenty: 20, thirty: 30, forty: 40, fifty: 50, sixty: 60, seventy: 70, eighty: 80, ninety: 90, hundred: 100
};

function parseVoiceNumber(transcript, fieldType) {
  const config = VOICE_FIELD_CONFIGS[fieldType];
  if (!config) return { status: "INVALID", parsed_value: null };
  if (!transcript || typeof transcript !== "string") return { status: "INVALID", parsed_value: null };

  const raw = transcript.trim();
  let normalized = raw.toLowerCase();

  if (normalized.includes("minus") || normalized.includes("negative") || normalized.startsWith("-") || normalized.includes("ऋण")) {
    return { status: "INVALID", parsed_value: null, ambiguity_reason: "Financial values cannot be negative" };
  }

  normalized = normalized
    .replace(/[₹$,]/g, "")
    .replace(/\b(rupees?|rupee|inr|rs\.?|re\.?|रुपये|रुपया|ரூபாய்|రూపాయలు|টাকা)\b/gi, "")
    .replace(/\b(please|enter|set|it|is|amount|to|for|make|about|around)\b/gi, "")
    .trim();

  if (config.unit === "MONTHS" && /\b(years?|year|साल|वर्ष|வருடம்|సంవత్సరాలు|বছর)\b/i.test(normalized)) {
    const yearMatch = normalized.match(/([0-9]+(?:\.[0-9]+)?)\s*(?:years?|year|साल|वर्ष|வருடம்|సంవత్సరాలు|বছর)/i);
    if (yearMatch) {
      const numYears = parseFloat(yearMatch[1]);
      if (!isNaN(numYears) && numYears > 0) {
        const totalMonths = Math.round(numYears * 12);
        if (totalMonths < config.min || totalMonths > config.max) {
          return { status: "OUT_OF_RANGE", parsed_value: totalMonths };
        }
        return { status: "SUCCESS", parsed_value: totalMonths };
      }
    }
  }

  normalized = normalized
    .replace(/\b(percent|percentage|pct|%|प्रतिशत|శాతం|சதவீதம்|শতাংশ)\b/gi, "")
    .replace(/\b(days?|day|दिन|दिवस|நாட்கள்|రోజులు|দিন)\b/gi, "")
    .replace(/\b(months?|month|महीने|महिने|மாதங்கள்|నెలలు|মাস)\b/gi, "")
    .replace(/\b(customers?|customer|clients?|people|units?|ग्राहक|লোক)\b/gi, "")
    .trim();

  let candidateNumber = null;

  const magnitudeRegex = /([0-9]+(?:\.[0-9]+)?)\s*(lakhs?|lac|lacs|crores?|cr|thousands?|k|लाख|करोड़|हजार|हज़ार|லட்சம்|கோடி|ஆயிரம்|లక్ష|కోట్లు|వేలు|লাখ|কোটি|হাজার)(?:\s|$|[^a-zA-Z0-9])/i;
  const magMatch = normalized.match(magnitudeRegex);

  if (magMatch) {
    const base = parseFloat(magMatch[1]);
    const term = magMatch[2].toLowerCase();
    if (!isNaN(base)) {
      if (/^(lakhs?|lac|lacs|लाख|லட்சம்|లక్ష|লাখ)$/i.test(term)) candidateNumber = base * 100000;
      else if (/^(crores?|cr|करोड़|கோடி|కోట్లు|কোটি)$/i.test(term)) candidateNumber = base * 10000000;
      else if (/^(thousands?|k|हजार|हज़ार|ஆயிரம்|వేలు|হাজার)$/i.test(term)) candidateNumber = base * 1000;
    }
  }

  if (candidateNumber === null) {
    const writtenMagMatch = normalized.match(
      /\b(one|two|three|four|five|six|seven|eight|nine|ten|fifteen|twenty|twenty\s+five|thirty|thirty\s+five|forty|fifty|seventy\s+five)\s+(?:point\s+(one|two|three|four|five|six|seven|eight|nine|[0-9]+)\s+)?(lakhs?|lac|lacs|crores?|cr|thousands?|k)\b/i
    );
    if (writtenMagMatch) {
      const intWord = writtenMagMatch[1].toLowerCase().replace(/\s+/g, "_");
      let intPart = intWord === "twenty_five" ? 25 : (intWord === "thirty_five" ? 35 : (intWord === "seventy_five" ? 75 : (SIMPLE_WORDS[intWord] || 0)));
      let decPart = 0;
      if (writtenMagMatch[2]) {
        const decWord = writtenMagMatch[2].toLowerCase();
        decPart = SIMPLE_WORDS[decWord] !== undefined ? SIMPLE_WORDS[decWord] / 10 : parseFloat("0." + decWord) || 0;
      }
      const totalBase = intPart + decPart;
      const term = writtenMagMatch[3].toLowerCase();
      if (totalBase > 0) {
        if (/^(lakhs?|lac|lacs)$/i.test(term)) candidateNumber = totalBase * 100000;
        else if (/^(crores?|cr)$/i.test(term)) candidateNumber = totalBase * 10000000;
        else if (/^(thousands?|k)$/i.test(term)) candidateNumber = totalBase * 1000;
      }
    }
  }

  if (candidateNumber === null) {
    const directMatch = normalized.match(/\b([0-9]+(?:\.[0-9]+)?)\b/);
    if (directMatch) {
      const parsed = parseFloat(directMatch[1]);
      if (!isNaN(parsed)) candidateNumber = parsed;
    }
  }

  if (candidateNumber === null) {
    const words = normalized.split(/\s+/).filter(Boolean);
    if (words.length === 1 && SIMPLE_WORDS[words[0]] !== undefined) {
      candidateNumber = SIMPLE_WORDS[words[0]];
    } else if (words.length === 2 && SIMPLE_WORDS[words[0]] !== undefined && SIMPLE_WORDS[words[1]] !== undefined) {
      candidateNumber = SIMPLE_WORDS[words[0]] + SIMPLE_WORDS[words[1]];
    }
  }

  if (candidateNumber === null) {
    return { status: "INVALID", parsed_value: null };
  }

  if (
    config.unit === "INR" &&
    (fieldType === "own_capital" || fieldType === "desired_loan" || fieldType === "startup_cost" || fieldType === "equipment_cost") &&
    candidateNumber > 0 &&
    candidateNumber < 100 &&
    !normalized.match(/(rupees?|rs|re|रुपये)/i) &&
    !raw.match(/(lakh|thousand|हजार|लाख)/i)
  ) {
    return { status: "AMBIGUOUS", parsed_value: candidateNumber };
  }

  if (candidateNumber < config.min || candidateNumber > config.max) {
    return { status: "OUT_OF_RANGE", parsed_value: candidateNumber };
  }

  const finalValue = config.isFloat ? candidateNumber : Math.round(candidateNumber);
  return { status: "SUCCESS", parsed_value: finalValue };
}

console.log("Running Step 5D Deterministic Numeric Parser Tests...\n");

// Mandatory Required Test Cases
const testCases = [
  { transcript: "50000", field: "desired_loan", expectedStatus: "SUCCESS", expectedVal: 50000 },
  { transcript: "50,000", field: "desired_loan", expectedStatus: "SUCCESS", expectedVal: 50000 },
  { transcript: "₹50,000", field: "startup_cost", expectedStatus: "SUCCESS", expectedVal: 50000 },
  { transcript: "50,000 rupees", field: "equipment_cost", expectedStatus: "SUCCESS", expectedVal: 50000 },
  { transcript: "2 lakh", field: "own_capital", expectedStatus: "SUCCESS", expectedVal: 200000 },
  { transcript: "2.5 lakh", field: "desired_loan", expectedStatus: "SUCCESS", expectedVal: 250000 },
  { transcript: "50 thousand", field: "inventory_cost", expectedStatus: "SUCCESS", expectedVal: 50000 },
  { transcript: "35 percent", field: "variable_cost_pct", expectedStatus: "SUCCESS", expectedVal: 35 },
  { transcript: "26 days", field: "working_days_per_month", expectedStatus: "SUCCESS", expectedVal: 26 },
  { transcript: "3 years", field: "loan_tenure_months", expectedStatus: "SUCCESS", expectedVal: 36 },
  // Indic term tests
  { transcript: "50 हजार", field: "inventory_cost", expectedStatus: "SUCCESS", expectedVal: 50000 },
  { transcript: "2 लाख", field: "desired_loan", expectedStatus: "SUCCESS", expectedVal: 200000 },
  // Negative value
  { transcript: "minus 5000", field: "startup_cost", expectedStatus: "INVALID", expectedVal: null },
  // Invalid text
  { transcript: "hello world", field: "startup_cost", expectedStatus: "INVALID", expectedVal: null },
  // Ambiguous text (small integer for capex without magnitude or currency)
  { transcript: "fifty", field: "own_capital", expectedStatus: "AMBIGUOUS", expectedVal: 50 },
  // Out of range (45 days in month)
  { transcript: "45 days", field: "working_days_per_month", expectedStatus: "OUT_OF_RANGE", expectedVal: 45 },
];

let passed = 0;
for (const tc of testCases) {
  const res = parseVoiceNumber(tc.transcript, tc.field);
  assert.strictEqual(res.status, tc.expectedStatus, `Status mismatch for "${tc.transcript}" on field ${tc.field}`);
  assert.strictEqual(res.parsed_value, tc.expectedVal, `Value mismatch for "${tc.transcript}" on field ${tc.field}`);
  console.log(`[PASS] "${tc.transcript}" (${tc.field}) -> ${res.status} (${res.parsed_value})`);
  passed++;
}

console.log(`\nAll ${passed} parser tests passed successfully!`);
