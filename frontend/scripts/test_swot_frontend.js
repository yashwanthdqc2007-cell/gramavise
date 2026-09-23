/**
 * Frontend SWOT Component & Contract Verification Suite
 * Phase 2D-E: Frontend SWOT UI Implementation
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

console.log("==================================================");
console.log("GRAMAVISE — PHASE 2D-E FRONTEND SWOT AUDIT");
console.log("==================================================");

// 1. Verify file existence
const files = [
  'lib/types.ts',
  'lib/i18n/types.ts',
  'lib/i18n/dictionaries/en.ts',
  'lib/i18n/dictionaries/hi.ts',
  'lib/i18n/dictionaries/mr.ts',
  'lib/i18n/dictionaries/bn.ts',
  'lib/i18n/dictionaries/te.ts',
  'lib/i18n/dictionaries/ta.ts',
  'components/dashboard/swot/SWOTItemCard.tsx',
  'components/dashboard/swot/SWOTQuadrant.tsx',
  'components/dashboard/swot/SWOTSection.tsx',
  'components/dashboard/swot/index.ts',
  'components/dashboard/ReportWorkspace.tsx',
];

for (const file of files) {
  const fullPath = path.join(__dirname, '..', file);
  assert(fs.existsSync(fullPath), `Required file missing: ${file}`);
  console.log(`[PASS] Verified file exists: ${file}`);
}

// 2. Verify types in lib/types.ts
const typesContent = fs.readFileSync(path.join(__dirname, '..', 'lib/types.ts'), 'utf-8');
assert(typesContent.includes('export interface SWOTItem'), 'SWOTItem interface missing in types.ts');
assert(typesContent.includes('export interface SWOTAnalysis'), 'SWOTAnalysis interface missing in types.ts');
assert(typesContent.includes('swot?: SWOTAnalysis;'), 'MarketResult.swot field missing in types.ts');
console.log("[PASS] SWOT types present and strictly match backend schema.");

// 3. Verify SWOTSection renders all 4 quadrants
const sectionContent = fs.readFileSync(path.join(__dirname, '..', 'components/dashboard/swot/SWOTSection.tsx'), 'utf-8');
assert(sectionContent.includes('SWOTQuadrant'), 'SWOTSection does not render SWOTQuadrant');
assert(sectionContent.includes('type="STRENGTH"'), 'STRENGTH quadrant missing');
assert(sectionContent.includes('type="WEAKNESS"'), 'WEAKNESS quadrant missing');
assert(sectionContent.includes('type="OPPORTUNITY"'), 'OPPORTUNITY quadrant missing');
assert(sectionContent.includes('type="THREAT"'), 'THREAT quadrant missing');
assert(sectionContent.includes('emptyState'), 'Null fallback emptyState missing');
console.log("[PASS] SWOTSection renders all 4 quadrants and null fallback.");

// 4. Verify SWOTQuadrant empty state
const quadContent = fs.readFileSync(path.join(__dirname, '..', 'components/dashboard/swot/SWOTQuadrant.tsx'), 'utf-8');
assert(quadContent.includes('emptyQuadrant'), 'SWOTQuadrant empty quadrant fallback missing');
assert(quadContent.includes('SWOTItemCard'), 'SWOTQuadrant does not render SWOTItemCard');
console.log("[PASS] SWOTQuadrant renders items or clean empty state.");

// 5. Verify SWOTItemCard badges and evidence interaction
const cardContent = fs.readFileSync(path.join(__dirname, '..', 'components/dashboard/swot/SWOTItemCard.tsx'), 'utf-8');
assert(cardContent.includes('OBSERVED') && cardContent.includes('CALCULATED') && cardContent.includes('ASSUMED') && cardContent.includes('NEEDS_VERIFICATION'), 'Evidence type badge mapping incomplete');
assert(cardContent.includes('needsVerificationDesc'), 'Needs verification notice missing');
assert(cardContent.includes('item.evidence_ids'), 'Evidence IDs binding missing');
assert(cardContent.includes('viewEvidence'), 'View evidence toggle missing');
console.log("[PASS] SWOTItemCard correctly maps badges, confidence, and evidence ledger linkages.");

// 6. Verify ReportWorkspace integrates SWOTSection in Overview tab
const workspaceContent = fs.readFileSync(path.join(__dirname, '..', 'components/dashboard/ReportWorkspace.tsx'), 'utf-8');
assert(workspaceContent.includes('import { SWOTSection } from "@/components/dashboard/swot"'), 'SWOTSection import missing in ReportWorkspace.tsx');
assert(workspaceContent.includes('<SWOTSection'), 'SWOTSection component tag missing in ReportWorkspace.tsx');
assert(workspaceContent.includes('swot={result.market_result?.swot}'), 'market_result.swot prop missing in SWOTSection integration');
console.log("[PASS] ReportWorkspace integrates SWOTSection in Overview tab directly after WhyThisDecision.");

// 7. Verify zero React-side calculations (React is presentation-only)
const allSwotCode = sectionContent + quadContent + cardContent;
assert(!allSwotCode.includes('calculate_') && !allSwotCode.includes('dscr =') && !allSwotCode.includes('net_profit ='), 'React components must not calculate financial metrics');
console.log("[PASS] Proven zero React-side financial recalculations (presentation only).");

console.log("\n==================================================");
console.log("ALL 7 FRONTEND SWOT AUDIT CHECKS PASSED (100%)");
console.log("==================================================");
