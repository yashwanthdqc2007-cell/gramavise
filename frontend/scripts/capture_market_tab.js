const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

const ARTIFACT_DIR = path.resolve('C:/Users/garag/.gemini/antigravity-ide/brain/394afd9b-5944-4796-b479-7be3d504795f');
const SCREENSHOT_DIR = path.join(ARTIFACT_DIR, 'screenshots');
const EDGE_PATH = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const PORT = 9222;
const BASE_URL = "http://localhost:3000";

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

  close() {
    this.ws.close();
  }
}

async function captureScreenshot(client, filepath) {
  const result = await client.send("Page.captureScreenshot", { format: "png", fromSurface: true });
  fs.writeFileSync(filepath, Buffer.from(result.data, 'base64'));
  const stats = fs.statSync(filepath);
  console.log(`[CAPTURED] ${path.basename(filepath)} (${stats.size} bytes)`);
}

async function runVisualQA() {
  if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  }

  console.log("Fetching Kisan Flour Mill analysis data from backend...");
  let analysisData = null;
  try {
    const postData = JSON.stringify({
      profile: {
        business_name: "Kisan Flour Mill",
        category: "Flour & Spice Milling (Atta Chakki)",
        description: "Small commercial flour mill",
        location: { state: "Uttar Pradesh", district: "Agra", village: "Khanda" },
        experience_years: 3,
        own_capital: 150000.0,
        desired_loan: 200000.0,
        is_new_business: true
      },
      financials: {
        startup_cost: 50000.0,
        equipment_cost: 200000.0,
        inventory_cost: 50000.0,
        monthly_fixed_cost: 12000.0,
        customers_per_day: 35,
        avg_ticket_price: 120.0,
        working_days_per_month: 26,
        variable_cost_pct: 35.0,
        interest_rate_pct: 9.5,
        loan_tenure_months: 36
      },
      preferred_language: "en"
    });

    const options = {
      hostname: 'localhost',
      port: 8000,
      path: '/api/analyze',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    analysisData = await new Promise((resolve, reject) => {
      const req = http.request(options, (res) => {
        let body = '';
        res.on('data', chunk => body += chunk);
        res.on('end', () => {
          try { resolve(JSON.parse(body)); } catch (e) { reject(e); }
        });
      });
      req.on('error', reject);
      req.write(postData);
      req.end();
    });
    console.log("Analysis data fetched successfully for: " + analysisData.business_name);
  } catch (err) {
    console.warn("Backend /api/analyze call failed:", err.message);
  }

  console.log("Starting Edge for Market Tab verification...");
  const edge = spawn(EDGE_PATH, [
    `--remote-debugging-port=${PORT}`,
    "--headless=new",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "--user-data-dir=" + path.join(ARTIFACT_DIR, ".edge_user_data_market")
  ]);

  await sleep(2500);

  try {
    const list = await getJson(`http://localhost:${PORT}/json/list`);
    const pageTarget = list.find(t => t.type === 'page') || list[0];
    const client = new CDPClient(pageTarget.webSocketDebuggerUrl);
    await client.ready();

    await client.send("Page.enable");
    await client.send("DOM.enable");
    await client.send("Runtime.enable");

    // Seed local storage with analysis data
    if (analysisData) {
      await client.send("Page.navigate", { url: `${BASE_URL}/` });
      await sleep(1500);
      const seedScript = `
        localStorage.setItem('gramavise_latest_result', '${JSON.stringify(analysisData).replace(/\\/g, '\\\\').replace(/'/g, "\\'")}');
        sessionStorage.setItem('gramavise_latest_result', '${JSON.stringify(analysisData).replace(/\\/g, '\\\\').replace(/'/g, "\\'")}');
        localStorage.setItem('gramavise_financials', '${JSON.stringify({
          startup_cost: 50000.0,
          equipment_cost: 200000.0,
          inventory_cost: 50000.0,
          monthly_fixed_cost: 12000.0,
          customers_per_day: 35,
          avg_ticket_price: 120.0,
          working_days_per_month: 26,
          variable_cost_pct: 35.0,
          interest_rate_pct: 9.5,
          loan_tenure_months: 36
        }).replace(/\\/g, '\\\\').replace(/'/g, "\\'")}');
      `;
      await client.send("Runtime.evaluate", { expression: seedScript });
    }

    // 1. Desktop 1440px - Market Tab
    console.log("Capturing 1440px Desktop Market Tab...");
    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 1440,
      height: 900,
      deviceScaleFactor: 1,
      mobile: false
    });
    await client.send("Page.navigate", { url: `${BASE_URL}/results?tab=market` });
    await sleep(2500);
    await captureScreenshot(client, path.join(SCREENSHOT_DIR, "market_tab_desktop_1440px.png"));

    // 2. Tablet Landscape 1024px - Market Tab
    console.log("Capturing 1024px Tablet Landscape Market Tab...");
    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 1024,
      height: 768,
      deviceScaleFactor: 1,
      mobile: false
    });
    await client.send("Page.navigate", { url: `${BASE_URL}/results?tab=market` });
    await sleep(2500);
    await captureScreenshot(client, path.join(SCREENSHOT_DIR, "market_tab_tablet_1024px.png"));

    // 3. Tablet Portrait 768px - Market Tab
    console.log("Capturing 768px Tablet Portrait Market Tab...");
    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 768,
      height: 1024,
      deviceScaleFactor: 2,
      mobile: true
    });
    await client.send("Page.navigate", { url: `${BASE_URL}/results?tab=market` });
    await sleep(2500);
    await captureScreenshot(client, path.join(SCREENSHOT_DIR, "market_tab_tablet_768px.png"));

    // 4. Mobile 390px - Market Tab
    console.log("Capturing 390px Mobile Market Tab...");
    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 390,
      height: 844,
      deviceScaleFactor: 3,
      mobile: true
    });
    await client.send("Page.navigate", { url: `${BASE_URL}/results?tab=market` });
    await sleep(2500);
    await captureScreenshot(client, path.join(SCREENSHOT_DIR, "market_tab_mobile_390px.png"));

    // 5. Mobile 375px - Market Tab
    console.log("Capturing 375px Mobile Market Tab...");
    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 375,
      height: 812,
      deviceScaleFactor: 2,
      mobile: true
    });
    await client.send("Page.navigate", { url: `${BASE_URL}/results?tab=market` });
    await sleep(2500);
    await captureScreenshot(client, path.join(SCREENSHOT_DIR, "market_tab_mobile_375px.png"));

    client.close();
    console.log("Visual QA screenshots captured successfully across all 5 viewports!");
  } finally {
    edge.kill();
  }
}

runVisualQA().catch(console.error);
