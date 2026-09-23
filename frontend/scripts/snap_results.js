const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

const SCREENSHOT_DIR = path.resolve('C:/Users/garag/.gemini/antigravity-ide/brain/394afd9b-5944-4796-b479-7be3d504795f/screenshots');
const EDGE_PATH = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const PORT = 9222;
const BASE_URL = "http://localhost:3000";
const ANALYSIS_ID = "ba7cac4c-fe57-45b6-b1a3-11bf2d911e58";

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
  }

  async setViewport(width, height) {
    await this.send('Emulation.setDeviceMetricsOverride', {
      width,
      height,
      deviceScaleFactor: 1,
      mobile: width < 600,
    });
    await sleep(300);
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
  const analysisData = await getJson(`http://127.0.0.1:8000/api/analyze/${ANALYSIS_ID}`);
  const historyList = [
    {
      analysis_id: ANALYSIS_ID,
      business_name: "Kisan Flour Mill",
      business_category: "Flour & Spice Milling (Atta Chakki)",
      recommendation_status: "PROCEED",
      created_at: new Date().toISOString()
    }
  ];

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
    const cdp = new CDPClient(pageTarget.webSocketDebuggerUrl);
    await cdp.ready();
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');

    // Navigate to origin first so localStorage/sessionStorage can be set
    await cdp.navigate(`${BASE_URL}/`);
    await sleep(2000);

    await cdp.send('Runtime.evaluate', {
      expression: `
        localStorage.setItem('gramavise_history_v1', ${JSON.stringify(JSON.stringify(historyList))});
        sessionStorage.setItem('gramavise_latest_result', ${JSON.stringify(JSON.stringify(analysisData))});
        sessionStorage.setItem('gramavise_financials', ${JSON.stringify(JSON.stringify({
          startup_cost: 50000,
          equipment_cost: 200000,
          inventory_cost: 50000,
          monthly_fixed_cost: 20000,
          customers_per_day: 35,
          avg_ticket_price: 500,
          working_days_per_month: 26,
          variable_cost_pct: 45,
          interest_rate_pct: 10.5,
          loan_tenure_months: 60
        }))});
      `
    });

    // 5. History page with a saved report
    await cdp.setViewport(1280, 900);
    await cdp.navigate(`${BASE_URL}/history`);
    await sleep(2500);
    await cdp.captureScreenshot('05_history_page_saved_report.png');

    // 4. Results page with Kisan Flour Mill analysis
    await cdp.navigate(`${BASE_URL}/results`);
    await sleep(3500);
    await cdp.captureScreenshot('04_results_page_kisan_flour_mill.png');

    // 7. Scenario Lab section in Results
    await cdp.send('Runtime.evaluate', {
      expression: `
        const el = document.getElementById('scenario-lab') || document.querySelector('[id*="scenario"]');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
      `
    });
    await sleep(2000);
    await cdp.captureScreenshot('07_scenario_lab_saved_scenario.png');

    // 9. Results at 375px
    await cdp.setViewport(375, 812);
    await cdp.navigate(`${BASE_URL}/results`);
    await sleep(3500);
    await cdp.captureScreenshot('09_results_mobile_375px.png');

    console.log("All results screenshots captured successfully!");
  } catch (e) {
    console.error("Error:", e);
  } finally {
    try { edge.kill(); } catch(e) {}
  }
}

main();
