const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

const SCREENSHOT_DIR = path.resolve('C:/Users/garag/.gemini/antigravity-ide/brain/394afd9b-5944-4796-b479-7be3d504795f/screenshots');
const EDGE_PATH = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const PORT = 9222;
const BASE_URL = "http://localhost:3000";
const ANALYSIS_ID = "ba7cac4c-fe57-45b6-b1a3-11bf2d911e58";

const KISAN_HISTORY = [
  {
    analysis_id: ANALYSIS_ID,
    business_name: "Kisan Flour Mill",
    business_category: "Flour & Spice Milling (Atta Chakki)",
    recommendation_status: "PROCEED",
    created_at: new Date().toISOString()
  }
];

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function getJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); } catch(e) { reject(e); }
      });
    }).on('error', reject);
  });
}

class CDPClient {
  constructor(wsUrl) {
    this.ws = new WebSocket(wsUrl);
    this.id = 1;
    this.callbacks = new Map();
    this.ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.id && this.callbacks.has(msg.id)) {
        const { resolve, reject } = this.callbacks.get(msg.id);
        this.callbacks.delete(msg.id);
        if (msg.error) reject(msg.error);
        else resolve(msg.result);
      }
    };
  }

  async ready() {
    if (this.ws.readyState === WebSocket.OPEN) return;
    return new Promise((resolve) => {
      this.ws.onopen = () => resolve();
    });
  }

  send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = this.id++;
      this.callbacks.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async navigate(url) {
    await this.send('Page.navigate', { url });
    await sleep(2500);
  }

  async setViewport(width, height) {
    await this.send('Emulation.setDeviceMetricsOverride', {
      width,
      height,
      deviceScaleFactor: 1,
      mobile: width < 600,
    });
    await sleep(400);
  }

  async evaluate(expression) {
    return await this.send('Runtime.evaluate', {
      expression,
      awaitPromise: true,
      returnByValue: true
    });
  }

  async captureScreenshot(filename) {
    const result = await this.send('Page.captureScreenshot', { format: 'png' });
    const buffer = Buffer.from(result.data, 'base64');
    const fullPath = path.join(SCREENSHOT_DIR, filename);
    fs.writeFileSync(fullPath, buffer);
    console.log(`[CAPTURED] ${filename} (${buffer.length} bytes) -> ${fullPath}`);
    return fullPath;
  }
}

async function main() {
  console.log("Fetching full analysis data from backend...");
  const kisanAnalysisData = await getJson(`http://127.0.0.1:8000/api/analyze/${ANALYSIS_ID}`);

  console.log("Starting Edge for screenshots...");
  const edge = spawn(EDGE_PATH, [
    `--remote-debugging-port=${PORT}`,
    '--headless=new',
    '--disable-gpu',
    '--no-sandbox',
    '--hide-scrollbars',
    '--disable-web-security',
    'about:blank'
  ], { detached: false });

  await sleep(2000);

  try {
    const list = await getJson(`http://127.0.0.1:${PORT}/json/list`);
    const pageTarget = list.find(t => t.type === 'page') || list[0];
    const wsUrl = pageTarget.webSocketDebuggerUrl;

    const cdp = new CDPClient(wsUrl);
    await cdp.ready();
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');

    console.log("\n--- Capturing 9 Requested Verification Screenshots ---");

    // Helper to seed localStorage and sessionStorage
    const seedStorageExpr = `
      localStorage.setItem('gramavise_history_v1', JSON.stringify(${JSON.stringify(KISAN_HISTORY)}));
      sessionStorage.setItem('gramavise_latest_result', JSON.stringify(${JSON.stringify(kisanAnalysisData)}));
    `;

    // 1. Dashboard with real Kisan Flour Mill record
    await cdp.setViewport(1280, 900);
    await cdp.navigate(`${BASE_URL}/`);
    await cdp.evaluate(seedStorageExpr);
    await cdp.navigate(`${BASE_URL}/`);
    await sleep(1500);
    await cdp.captureScreenshot('01_dashboard_with_kisan_flour_mill.png');

    // 2. Dashboard empty state
    await cdp.evaluate(`localStorage.clear(); sessionStorage.clear();`);
    await cdp.navigate(`${BASE_URL}/`);
    await sleep(1500);
    await cdp.captureScreenshot('02_dashboard_empty_state.png');

    // Restore history and session storage
    await cdp.evaluate(seedStorageExpr);

    // 3. New Advisory desktop
    await cdp.navigate(`${BASE_URL}/onboarding`);
    await sleep(1500);
    await cdp.captureScreenshot('03_new_advisory_desktop.png');

    // 4. Results page with Kisan Flour Mill analysis
    await cdp.navigate(`${BASE_URL}/results`);
    await sleep(2500);
    await cdp.captureScreenshot('04_results_page_kisan_flour_mill.png');

    // 5. History page with a saved report
    await cdp.navigate(`${BASE_URL}/history`);
    await sleep(1500);
    await cdp.captureScreenshot('05_history_page_saved_report.png');

    // 6. Government Schemes page
    await cdp.navigate(`${BASE_URL}/schemes`);
    await sleep(1500);
    await cdp.captureScreenshot('06_government_schemes_page.png');

    // 7. Scenario Lab with a saved scenario
    await cdp.navigate(`${BASE_URL}/results#scenario-lab`);
    await sleep(2000);
    await cdp.evaluate(`
      const el = document.getElementById('scenario-lab') || document.querySelector('[id*="scenario"]');
      if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
    `);
    await sleep(1500);
    await cdp.captureScreenshot('07_scenario_lab_saved_scenario.png');

    // 8. Dashboard at 375px
    await cdp.setViewport(375, 812);
    await cdp.navigate(`${BASE_URL}/`);
    await sleep(2000);
    await cdp.captureScreenshot('08_dashboard_mobile_375px.png');

    // 9. Results at 375px
    await cdp.navigate(`${BASE_URL}/results`);
    await sleep(2500);
    await cdp.captureScreenshot('09_results_mobile_375px.png');

    console.log("\nAll 9 screenshots captured successfully!");
  } catch (err) {
    console.error("Error during screenshot capture:", err);
  } finally {
    try { edge.kill(); } catch(e) {}
  }
}

main();
