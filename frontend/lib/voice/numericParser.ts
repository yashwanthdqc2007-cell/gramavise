import { VoiceFieldType, VoiceFieldConfig, ParseResult } from "./types";

export const VOICE_FIELD_CONFIGS: Record<VoiceFieldType, VoiceFieldConfig> = {
  own_capital: {
    fieldType: "own_capital",
    labelKey: "onboarding.profile.ownCapital",
    min: 0,
    max: 100000000, // 10 crore max
    isFloat: false,
    unit: "INR",
    isRolloutActive: true,
  },
  desired_loan: {
    fieldType: "desired_loan",
    labelKey: "onboarding.profile.desiredLoan",
    min: 0,
    max: 100000000,
    isFloat: false,
    unit: "INR",
    isRolloutActive: true,
  },
  startup_cost: {
    fieldType: "startup_cost",
    labelKey: "onboarding.financial.startupCost",
    min: 0,
    max: 50000000,
    isFloat: false,
    unit: "INR",
    isRolloutActive: true,
  },
  equipment_cost: {
    fieldType: "equipment_cost",
    labelKey: "onboarding.financial.equipmentCost",
    min: 0,
    max: 50000000,
    isFloat: false,
    unit: "INR",
    isRolloutActive: true,
  },
  inventory_cost: {
    fieldType: "inventory_cost",
    labelKey: "onboarding.financial.inventoryCost",
    min: 0,
    max: 50000000,
    isFloat: false,
    unit: "INR",
    isRolloutActive: true,
  },
  monthly_fixed_cost: {
    fieldType: "monthly_fixed_cost",
    labelKey: "onboarding.financial.monthlyFixedCost",
    min: 0,
    max: 10000000,
    isFloat: false,
    unit: "INR",
    isRolloutActive: true,
  },
  customers_per_day: {
    fieldType: "customers_per_day",
    labelKey: "onboarding.financial.customersPerDay",
    min: 0,
    max: 50000,
    isFloat: false,
    unit: "UNITS",
    isRolloutActive: true,
  },
  avg_ticket_price: {
    fieldType: "avg_ticket_price",
    labelKey: "onboarding.financial.avgTicketPrice",
    min: 0,
    max: 1000000,
    isFloat: true,
    unit: "INR",
    isRolloutActive: true,
  },
  working_days_per_month: {
    fieldType: "working_days_per_month",
    labelKey: "onboarding.financial.workingDays",
    min: 1,
    max: 31,
    isFloat: false,
    unit: "DAYS",
    isRolloutActive: false, // Architected for future rollout
  },
  variable_cost_pct: {
    fieldType: "variable_cost_pct",
    labelKey: "onboarding.financial.variableCostPct",
    min: 0,
    max: 100,
    isFloat: true,
    unit: "PERCENT",
    isRolloutActive: false, // Architected for future rollout
  },
  interest_rate_pct: {
    fieldType: "interest_rate_pct",
    labelKey: "onboarding.financial.interestRate",
    min: 0,
    max: 50,
    isFloat: true,
    unit: "PERCENT",
    isRolloutActive: false, // Architected for future rollout
  },
  loan_tenure_months: {
    fieldType: "loan_tenure_months",
    labelKey: "onboarding.financial.loanTenure",
    min: 1,
    max: 360,
    isFloat: false,
    unit: "MONTHS",
    isRolloutActive: false, // Architected for future rollout
  },
};

// Word-to-number mapping for simple deterministic English numbers
const SIMPLE_WORDS: Record<string, number> = {
  zero: 0,
  one: 1,
  two: 2,
  three: 3,
  four: 4,
  five: 5,
  six: 6,
  seven: 7,
  eight: 8,
  nine: 9,
  ten: 10,
  eleven: 11,
  twelve: 12,
  thirteen: 13,
  fourteen: 14,
  fifteen: 15,
  sixteen: 16,
  seventeen: 17,
  eighteen: 18,
  nineteen: 19,
  twenty: 20,
  thirty: 30,
  forty: 40,
  fifty: 50,
  sixty: 60,
  seventy: 70,
  eighty: 80,
  ninety: 90,
  hundred: 100,
};

function formatDisplayValue(val: number, unit: VoiceFieldConfig["unit"]): string {
  switch (unit) {
    case "INR":
      return `₹${val.toLocaleString("en-IN")}`;
    case "PERCENT":
      return `${val}%`;
    case "DAYS":
      return `${val} days/month`;
    case "MONTHS":
      return `${val} months`;
    case "UNITS":
      return `${val} customers/day`;
    default:
      return `${val}`;
  }
}

/**
 * Pure deterministic numeric parser for voice transcripts.
 * Never guesses or modifies calculations.
 */
export function parseVoiceNumber(
  transcript: string,
  fieldType: VoiceFieldType
): ParseResult {
  const config = VOICE_FIELD_CONFIGS[fieldType];
  if (!config) {
    return {
      status: "INVALID",
      raw_transcript: transcript,
      parsed_value: null,
      formatted_display: "",
      ambiguity_reason: "Unsupported field configuration",
    };
  }

  if (!transcript || typeof transcript !== "string") {
    return {
      status: "INVALID",
      raw_transcript: "",
      parsed_value: null,
      formatted_display: "",
      ambiguity_reason: "Empty transcript",
    };
  }

  const raw = transcript.trim();
  let normalized = raw.toLowerCase();

  // Explicit check for negative numbers
  if (
    normalized.includes("minus") ||
    normalized.includes("negative") ||
    normalized.startsWith("-") ||
    normalized.includes("ऋण")
  ) {
    return {
      status: "INVALID",
      raw_transcript: raw,
      parsed_value: null,
      formatted_display: "",
      ambiguity_reason: "Financial and operational parameters cannot be negative.",
    };
  }

  // Pre-process: strip currency indicators, filler words, and punctuation
  normalized = normalized
    .replace(/[₹$,]/g, "")
    .replace(/\b(rupees?|rupee|inr|rs\.?|re\.?|रुपये|रुपया|ரூபாய்|రూపాయలు|টাকা)\b/gi, "")
    .replace(/\b(please|enter|set|it|is|amount|to|for|make|about|around)\b/gi, "")
    .trim();

  // Check for tenure in years (e.g. "3 years" -> 36 months)
  if (config.unit === "MONTHS" && /\b(years?|year|साल|वर्ष|வருடம்|సంవత్సరాలు|বছর)\b/i.test(normalized)) {
    const yearMatch = normalized.match(/([0-9]+(?:\.[0-9]+)?)\s*(?:years?|year|साल|वर्ष|வருடம்|సంవత్సరాలు|বছর)/i);
    if (yearMatch) {
      const numYears = parseFloat(yearMatch[1]);
      if (!isNaN(numYears) && numYears > 0) {
        const totalMonths = Math.round(numYears * 12);
        if (totalMonths < config.min || totalMonths > config.max) {
          return {
            status: "OUT_OF_RANGE",
            raw_transcript: raw,
            parsed_value: totalMonths,
            formatted_display: formatDisplayValue(totalMonths, config.unit),
            unit: config.unit,
            ambiguity_reason: `Value ${totalMonths} months is outside allowed range (${config.min} - ${config.max}).`,
          };
        }
        return {
          status: "SUCCESS",
          raw_transcript: raw,
          parsed_value: totalMonths,
          formatted_display: formatDisplayValue(totalMonths, config.unit),
          unit: config.unit,
        };
      }
    }
  }

  // Strip trailing unit labels (percent, days, months, customers)
  normalized = normalized
    .replace(/\b(percent|percentage|pct|%|प्रतिशत|శాతం|சதவீதம்|শতাংশ)\b/gi, "")
    .replace(/\b(days?|day|दिन|दिवस|நாட்கள்|రోజులు|দিন)\b/gi, "")
    .replace(/\b(months?|month|महीने|महिने|மாதங்கள்|నెలలు|মাস)\b/gi, "")
    .replace(/\b(customers?|customer|clients?|people|units?|ग्राहक|লোক)\b/gi, "")
    .trim();

  let candidateNumber: number | null = null;

  // Case 1: Spoken magnitude notation (Lakh, Crore, Thousand, K)
  const magnitudeRegex = /([0-9]+(?:\.[0-9]+)?)\s*(lakhs?|lac|lacs|crores?|cr|thousands?|k|लाख|करोड़|हजार|हज़ार|லட்சம்|கோடி|ஆயிரம்|లక్ష|కోట్లు|వేలు|লাখ|কোটি|হাজার)(?:\s|$|[^a-zA-Z0-9])/i;
  const magMatch = normalized.match(magnitudeRegex);

  if (magMatch) {
    const base = parseFloat(magMatch[1]);
    const term = magMatch[2].toLowerCase();

    if (!isNaN(base)) {
      if (/^(lakhs?|lac|lacs|लाख|லட்சம்|లక్ష|লাখ)$/i.test(term)) {
        candidateNumber = base * 100000;
      } else if (/^(crores?|cr|करोड़|கோடி|కోట్లు|কোটি)$/i.test(term)) {
        candidateNumber = base * 10000000;
      } else if (/^(thousands?|k|हजार|हज़ार|ஆயிரம்|వేలు|হাজার)$/i.test(term)) {
        candidateNumber = base * 1000;
      }
    }
  }

  // Case 2: Written English combinations (e.g. "two point five lakh", "fifty thousand", "twenty five thousand")
  if (candidateNumber === null) {
    const writtenMagMatch = normalized.match(
      /\b(one|two|three|four|five|six|seven|eight|nine|ten|fifteen|twenty|twenty\s+five|thirty|thirty\s+five|forty|fifty|seventy\s+five)\s+(?:point\s+(one|two|three|four|five|six|seven|eight|nine|[0-9]+)\s+)?(lakhs?|lac|lacs|crores?|cr|thousands?|k)\b/i
    );

    if (writtenMagMatch) {
      const intWord = writtenMagMatch[1].toLowerCase().replace(/\s+/g, "_");
      let intPart = 0;
      if (intWord === "twenty_five") intPart = 25;
      else if (intWord === "thirty_five") intPart = 35;
      else if (intWord === "seventy_five") intPart = 75;
      else intPart = SIMPLE_WORDS[intWord] || 0;

      let decPart = 0;
      if (writtenMagMatch[2]) {
        const decWord = writtenMagMatch[2].toLowerCase();
        decPart = SIMPLE_WORDS[decWord] !== undefined ? SIMPLE_WORDS[decWord] / 10 : parseFloat("0." + decWord) || 0;
      }

      const totalBase = intPart + decPart;
      const term = writtenMagMatch[3].toLowerCase();

      if (totalBase > 0) {
        if (/^(lakhs?|lac|lacs)$/i.test(term)) {
          candidateNumber = totalBase * 100000;
        } else if (/^(crores?|cr)$/i.test(term)) {
          candidateNumber = totalBase * 10000000;
        } else if (/^(thousands?|k)$/i.test(term)) {
          candidateNumber = totalBase * 1000;
        }
      }
    }
  }

  // Case 3: Direct standard digit format (e.g. "50000", "50000.5", "12.5")
  if (candidateNumber === null) {
    const directMatch = normalized.match(/\b([0-9]+(?:\.[0-9]+)?)\b/);
    if (directMatch) {
      const parsed = parseFloat(directMatch[1]);
      if (!isNaN(parsed)) {
        candidateNumber = parsed;
      }
    }
  }

  // Case 4: Standalone simple word number (e.g. "fifty", "twenty five")
  if (candidateNumber === null) {
    const words = normalized.split(/\s+/).filter(Boolean);
    if (words.length === 1 && SIMPLE_WORDS[words[0]] !== undefined) {
      candidateNumber = SIMPLE_WORDS[words[0]];
    } else if (words.length === 2 && SIMPLE_WORDS[words[0]] !== undefined && SIMPLE_WORDS[words[1]] !== undefined) {
      candidateNumber = SIMPLE_WORDS[words[0]] + SIMPLE_WORDS[words[1]];
    }
  }

  // If no number was parsed at all
  if (candidateNumber === null) {
    return {
      status: "INVALID",
      raw_transcript: raw,
      parsed_value: null,
      formatted_display: "",
      ambiguity_reason: "Could not find a valid number in the spoken text.",
    };
  }

  // Ambiguity check: if user said a small number like "50" for capex or loan (where thousands are usually intended)
  // We do NOT guess; we ask user to confirm or flag ambiguity if needed.
  if (
    config.unit === "INR" &&
    (fieldType === "own_capital" || fieldType === "desired_loan" || fieldType === "startup_cost" || fieldType === "equipment_cost") &&
    candidateNumber > 0 &&
    candidateNumber < 100 &&
    !normalized.match(/(rupees?|rs|re|रुपये)/i) &&
    !raw.match(/(lakh|thousand|हजार|लाख)/i)
  ) {
    // For small standalone integers in large capital fields, mark as AMBIGUOUS to safeguard entrepreneur
    return {
      status: "AMBIGUOUS",
      raw_transcript: raw,
      parsed_value: candidateNumber,
      formatted_display: formatDisplayValue(candidateNumber, config.unit),
      unit: config.unit,
      ambiguity_reason: `Interpreted as ₹${candidateNumber}. If you meant thousands or lakhs (e.g., ₹${candidateNumber},000 or ₹${candidateNumber} lakh), please say the magnitude or type manually.`,
    };
  }

  // Field range validation against conservative bounds
  if (candidateNumber < config.min || candidateNumber > config.max) {
    return {
      status: "OUT_OF_RANGE",
      raw_transcript: raw,
      parsed_value: candidateNumber,
      formatted_display: formatDisplayValue(candidateNumber, config.unit),
      unit: config.unit,
      ambiguity_reason: `Value ${candidateNumber} is outside the allowable range (${config.min} - ${config.max}).`,
    };
  }

  const finalValue = config.isFloat ? candidateNumber : Math.round(candidateNumber);

  return {
    status: "SUCCESS",
    raw_transcript: raw,
    parsed_value: finalValue,
    formatted_display: formatDisplayValue(finalValue, config.unit),
    unit: config.unit,
  };
}
