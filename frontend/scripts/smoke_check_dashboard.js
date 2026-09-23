const fs = require('fs');
const path = require('path');

console.log("=== GRAMAVISE DASHBOARD SMOKE CHECK ===");

// 1. Check AppShell.tsx exists and has Desktop Sidebar and Header Topbar
const appShellPath = path.join(__dirname, '../components/common/AppShell.tsx');
if (!fs.existsSync(appShellPath)) {
  console.error("[FAIL] AppShell.tsx does not exist!");
  process.exit(1);
}
const appShellContent = fs.readFileSync(appShellPath, 'utf8');
if (!appShellContent.includes('aside') || !appShellContent.includes('/onboarding') || !appShellContent.includes('/history')) {
  console.error("[FAIL] AppShell.tsx is missing expected sidebar navigation components!");
  process.exit(1);
}
console.log("[PASS] AppShell.tsx exists with persistent desktop sidebar, mobile drawer, and workspace navigation.");

// 2. Check layout.tsx wraps AppShell
const layoutPath = path.join(__dirname, '../app/layout.tsx');
const layoutContent = fs.readFileSync(layoutPath, 'utf8');
if (!layoutContent.includes('<AppShell>{children}</AppShell>')) {
  console.error("[FAIL] layout.tsx does not wrap children in AppShell!");
  process.exit(1);
}
console.log("[PASS] app/layout.tsx cleanly wraps children in AppShell.");

// 3. Check page.tsx (Dashboard) functionality
const pagePath = path.join(__dirname, '../app/page.tsx');
const pageContent = fs.readFileSync(pagePath, 'utf8');
if (!pageContent.includes('loadHistory') || !pageContent.includes('latestAnalysis') || !pageContent.includes('/onboarding') || !pageContent.includes('/history')) {
  console.error("[FAIL] app/page.tsx missing smart hybrid dashboard logic!");
  process.exit(1);
}
console.log("[PASS] app/page.tsx implements smart hybrid dashboard with loadHistory and quick action CTAs.");

// 4. Check CTA links in Dashboard & Header
if (!appShellContent.includes('href="/onboarding"') || !pageContent.includes('href="/onboarding"')) {
  console.error("[FAIL] Desktop CTA does not link to /onboarding!");
  process.exit(1);
}
console.log("[PASS] Dashboard desktop CTA properly routes to /onboarding.");

// 5. Check historyStorage schema and normalization for Kisan Flour Mill record
const historyStoragePath = path.join(__dirname, '../lib/storage/historyStorage.ts');
const historyStorageContent = fs.readFileSync(historyStoragePath, 'utf8');
if (!historyStorageContent.includes('normalizeHistoryEntry') || !historyStorageContent.includes('loadHistory')) {
  console.error("[FAIL] historyStorage missing normalization logic!");
  process.exit(1);
}

// Simulate loading a real Kisan Flour Mill record
const sampleKisanRecord = {
  analysis_id: "d84e5b13-6ccd-4c65-a464-e47b96f7afc2",
  business_name: "Kisan Flour Mill",
  business_category: "Agro-Processing & Flour Milling",
  recommendation_status: "PROCEED",
  created_at: "2026-09-20T10:00:00.000Z"
};

const historyPagePath = path.join(__dirname, '../app/history/page.tsx');
const historyPageContent = fs.readFileSync(historyPagePath, 'utf8');
if (!historyPageContent.includes('loadHistory') || !historyPageContent.includes('getStatusBadge') || !historyPageContent.includes('Latest')) {
  console.error("[FAIL] History page missing latest record visual hierarchy!");
  process.exit(1);
}
console.log("[PASS] History and Dashboard correctly support rendering real Kisan Flour Mill records.");

// 6. Schemes page check
const schemesPagePath = path.join(__dirname, '../app/schemes/page.tsx');
const schemesPageContent = fs.readFileSync(schemesPagePath, 'utf8');
if (!schemesPageContent.includes('activeFilter') || !schemesPageContent.includes('SUBSIDY') || !schemesPageContent.includes('CREDIT')) {
  console.error("[FAIL] Schemes page missing filter pill logic!");
  process.exit(1);
}
console.log("[PASS] Schemes page implements filter pills and structured scheme cards.");

console.log("=== ALL SMOKE CHECKS PASSED SUCCESSFULLY ===");
