const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

const ARTIFACT_DIR = path.resolve('C:/Users/garag/.gemini/antigravity-ide/brain/394afd9b-5944-4796-b479-7be3d504795f');
const SCREENSHOT_DIR = path.join(ARTIFACT_DIR, 'screenshots');
const EDGE_PATH = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const PORT = 9228;
const BASE_URL = "http://localhost:3000";
const ANALYSIS_ID = "f0f9bfe2-823f-4477-ae77-4ca2614ef624";

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
    await sleep(3500);
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
  console.log("Starting Edge on port " + PORT + "...");
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

    // 1. Overview tab with SWOT section (Desktop 1440x1100)
    console.log("Navigating to historical analysis report...");
    await cdp.setViewport(1440, 1100);
    await cdp.navigate(`${BASE_URL}/history/${ANALYSIS_ID}?tab=overview`);
    await sleep(2000);

    // Capture full desktop view
    await cdp.captureScreenshot('swot_desktop_overview.png');

    // 2. Scroll SWOT into view
    console.log("Scrolling SWOT into view...");
    await cdp.evaluate(`
      const el = document.getElementById('business-factors');
      if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
    `);
    await sleep(800);
    await cdp.captureScreenshot('swot_desktop_section_view.png');

    // 3. Expand evidence on SWOT item
    console.log("Expanding evidence on SWOT item...");
    await cdp.evaluate(`
      const btn = document.querySelector('[data-testid^="swot-item-"] button');
      if (btn) btn.click();
    `);
    await sleep(800);
    await cdp.captureScreenshot('swot_desktop_evidence_expanded.png');

    // 4. Mobile Viewport (375x900)
    console.log("Capturing Mobile 375px...");
    await cdp.setViewport(375, 900);
    await cdp.navigate(`${BASE_URL}/history/${ANALYSIS_ID}?tab=overview`);
    await sleep(2000);
    await cdp.evaluate(`
      const el = document.getElementById('business-factors');
      if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
    `);
    await sleep(800);
    await cdp.captureScreenshot('swot_mobile_375px.png');

    console.log("Visual QA completed successfully!");
  } catch (err) {
    console.error("CDP error:", err);
  } finally {
    edge.kill();
  }
}

main();
