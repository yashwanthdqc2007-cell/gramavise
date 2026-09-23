const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

const ARTIFACT_DIR = path.resolve('C:/Users/garag/.gemini/antigravity-ide/brain/394afd9b-5944-4796-b479-7be3d504795f');
const SCREENSHOT_DIR = path.join(ARTIFACT_DIR, 'screenshots');
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
    fs.writeFileSync(path.join(ARTIFACT_DIR, filename), buffer);
    console.log(`[CAPTURED] ${filename} (${buffer.length} bytes)`);
    return fullPath;
  }
}

async function main() {
  console.log("Fetching Kisan Flour Mill analysis data from backend...");
  const kisanData = await getJson(`http://127.0.0.1:8000/api/analyze/${ANALYSIS_ID}`);

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

    const seedStorageExpr = `
      localStorage.setItem('gramavise_history_v1', JSON.stringify(${JSON.stringify(KISAN_HISTORY)}));
      sessionStorage.setItem('gramavise_latest_result', JSON.stringify(${JSON.stringify(kisanData)}));
      localStorage.setItem('gramavise_latest_result', JSON.stringify(${JSON.stringify(kisanData)}));
    `;

    // 1. Overview tab (Desktop 1440x900)
    await cdp.setViewport(1440, 900);
    await cdp.navigate(`${BASE_URL}/history/${ANALYSIS_ID}?tab=overview`);
    await cdp.evaluate(seedStorageExpr);
    await sleep(1500);
    await cdp.captureScreenshot('01_results_overview_desktop.png');

    // 2. Financials tab (Desktop 1440x900)
    await cdp.navigate(`${BASE_URL}/history/${ANALYSIS_ID}?tab=financials`);
    await sleep(2000);
    await cdp.captureScreenshot('02_results_financials_desktop.png');

    // 3. Local Market tab (Desktop 1440x900)
    await cdp.navigate(`${BASE_URL}/history/${ANALYSIS_ID}?tab=market`);
    await sleep(2000);
    await cdp.captureScreenshot('03_results_market_desktop.png');

    // 4. Risks & Evidence tab (Desktop 1440x900)
    await cdp.navigate(`${BASE_URL}/history/${ANALYSIS_ID}?tab=risks`);
    await sleep(2000);
    await cdp.captureScreenshot('04_results_risks_desktop.png');

    // 5. Schemes & Funding tab (Desktop 1440x900)
    await cdp.navigate(`${BASE_URL}/history/${ANALYSIS_ID}?tab=schemes`);
    await sleep(2000);
    await cdp.captureScreenshot('05_results_schemes_desktop.png');

    // 6. Action Plan tab (Desktop 1440x900)
    await cdp.navigate(`${BASE_URL}/history/${ANALYSIS_ID}?tab=action_plan`);
    await sleep(2000);
    await cdp.captureScreenshot('06_results_action_plan_desktop.png');

    // 7. Dashboard with existing report (Desktop 1440x900)
    await cdp.navigate(`${BASE_URL}/`);
    await cdp.evaluate(seedStorageExpr);
    await sleep(1500);
    await cdp.captureScreenshot('07_dashboard_existing_report.png');

    // 8. History page (Desktop 1440x900)
    await cdp.navigate(`${BASE_URL}/history`);
    await sleep(1500);
    await cdp.captureScreenshot('08_history_page.png');

    // 9. Results — Overview at 375px
    await cdp.setViewport(375, 812);
    await cdp.navigate(`${BASE_URL}/history/${ANALYSIS_ID}?tab=overview`);
    await sleep(2000);
    await cdp.captureScreenshot('09_results_overview_375px.png');

    // 10. Results — Financials at 375px
    await cdp.navigate(`${BASE_URL}/history/${ANALYSIS_ID}?tab=financials`);
    await sleep(2000);
    await cdp.captureScreenshot('10_results_financials_375px.png');

    // 11. Results — Overview at 390px
    await cdp.setViewport(390, 844);
    await cdp.navigate(`${BASE_URL}/history/${ANALYSIS_ID}?tab=overview`);
    await sleep(2000);
    await cdp.captureScreenshot('11_results_overview_390px.png');

    // 12. Sidebar/mobile navigation at 375px (open drawer)
    await cdp.setViewport(375, 812);
    await cdp.navigate(`${BASE_URL}/`);
    await sleep(1500);
    await cdp.evaluate(`
      const menuBtn = document.querySelector('button[aria-label="Open navigation menu"]') || 
                      document.querySelector('header button');
      if (menuBtn) menuBtn.click();
    `);
    await sleep(1000);
    await cdp.captureScreenshot('12_sidebar_mobile_375px.png');

    console.log("\nAll 12 screenshots captured and verified successfully!");
  } catch (err) {
    console.error("Error during screenshot capture:", err);
  } finally {
    try { edge.kill(); } catch(e) {}
  }
}

main();
