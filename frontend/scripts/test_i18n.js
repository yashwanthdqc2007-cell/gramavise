/**
 * Frontend Node.js verification script for i18n dictionaries.
 */

const fs = require('fs');
const path = require('path');

const DICT_DIR = path.join(__dirname, '..', 'lib', 'i18n', 'dictionaries');
const LANGUAGES = ['en', 'hi', 'mr', 'bn', 'te', 'ta'];

function parseDictKeys(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const clean = content.replace(/\/\/.*|\/\*[\s\S]*?\*\//g, '');
  const lines = clean.split('\n');
  const keys = new Set();
  const stack = [];

  for (let line of lines) {
    line = line.trim();
    if (!line) continue;
    
    const objMatch = line.match(/^(\w+)\s*:\s*\{/);
    if (objMatch) {
      stack.push(objMatch[1]);
      continue;
    }

    if (line.startsWith('}')) {
      if (stack.length > 0) stack.pop();
      continue;
    }

    const propMatch = line.match(/^(\w+)\s*:\s*["`]/);
    if (propMatch) {
      const fullKey = [...stack, propMatch[1]].join('.');
      keys.add(fullKey);
    }
  }
  return keys;
}

console.log("Checking i18n dictionary completeness & parity...");

const enKeys = parseDictKeys(path.join(DICT_DIR, 'en.ts'));
console.log(`[PASS] Canonical English dictionary contains ${enKeys.size} translation keys.`);

let allPassed = true;

for (const lang of LANGUAGES) {
  if (lang === 'en') continue;
  const filePath = path.join(DICT_DIR, `${lang}.ts`);
  if (!fs.existsSync(filePath)) {
    console.error(`[FAIL] Dictionary missing: ${lang}.ts`);
    allPassed = false;
    continue;
  }

  const langKeys = parseDictKeys(filePath);
  const missing = [...enKeys].filter(k => !langKeys.has(k));
  const extra = [...langKeys].filter(k => !enKeys.has(k));

  if (missing.length > 0) {
    console.error(`[FAIL] ${lang}.ts is missing keys:`, missing);
    allPassed = false;
  }
  if (extra.length > 0) {
    console.error(`[FAIL] ${lang}.ts has unexpected extra keys:`, extra);
    allPassed = false;
  }

  if (missing.length === 0 && extra.length === 0) {
    console.log(`[PASS] ${lang}.ts has 100% key parity (${langKeys.size}/${enKeys.size} keys).`);
  }
}

if (!allPassed) {
  process.exit(1);
}

console.log("All 6 i18n dictionaries validated successfully with 100% key parity!");
