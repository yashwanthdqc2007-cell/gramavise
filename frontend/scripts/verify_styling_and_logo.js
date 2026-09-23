const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

const EDGE_PATH = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const PORT = 9223;
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
    this.events = [];
    this.consoleLogs = [];
    this.failedRequests = [];

    this.ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.method === 'Log.entryAdded') {
        this.consoleLogs.push(msg.params.entry);
      }
      if (msg.method === 'Network.responseReceived') {
        const { response } = msg.params;
        if (response.status >= 400) {
          this.failedRequests.push({ url: response.url, status: response.status });
        }
      }
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
    try { this.ws.close(); } catch(e) {}
  }
}

async function run() {
  const userDataDir = path.join(process.env.TEMP || 'C:\\Temp', 'edge_style_audit_' + Date.now());
  const edgeProc = spawn(EDGE_PATH, [
    `--remote-debugging-port=${PORT}`,
    '--headless=new',
    '--disable-gpu',
    '--no-first-run',
    '--no-default-browser-check',
    `--user-data-dir=${userDataDir}`,
    'about:blank'
  ]);

  try {
    let version = null;
    for (let i = 0; i < 30; i++) {
      try {
        version = await getJson(`http://127.0.0.1:${PORT}/json/version`);
        if (version && version.webSocketDebuggerUrl) break;
      } catch (e) {}
      await sleep(300);
    }

    if (!version) {
      console.error("Failed to connect to browser on port " + PORT);
      process.exit(1);
    }

    const pages = await getJson(`http://127.0.0.1:${PORT}/json/list`);
    const pageTarget = pages.find(p => p.type === 'page') || pages[0];
    const client = new CDPClient(pageTarget.webSocketDebuggerUrl);
    await client.ready();

    await client.send('Page.enable');
    await client.send('DOM.enable');
    await client.send('Runtime.enable');
    await client.send('Log.enable');
    await client.send('Network.enable');

    await client.send('Emulation.setDeviceMetricsOverride', {
      width: 1440,
      height: 900,
      deviceScaleFactor: 2,
      mobile: false
    });

    const routes = [
      { name: 'Dashboard / Home', url: `${BASE_URL}/` },
      { name: 'Onboarding Step 1', url: `${BASE_URL}/onboarding` },
      { name: 'History', url: `${BASE_URL}/history` },
      { name: 'Government Schemes', url: `${BASE_URL}/schemes` },
      { name: 'Scenario Lab', url: `${BASE_URL}/scenario-lab` },
      { name: 'Results Overview', url: `${BASE_URL}/history/${ANALYSIS_ID}?tab=overview` }
    ];

    const results = [];

    for (const route of routes) {
      console.log(`\n========================================`);
      console.log(`Checking route: ${route.name} (${route.url})`);
      client.failedRequests = [];

      await client.send('Page.navigate', { url: route.url });
      await sleep(2500);

      // Seed localStorage if history page
      if (route.url.includes('/history')) {
        await client.send('Runtime.evaluate', {
          expression: `
            localStorage.setItem('gramavise_history', JSON.stringify(${JSON.stringify(KISAN_HISTORY)}));
            localStorage.setItem('gramavise_active_analysis', "${ANALYSIS_ID}");
          `
        });
        await client.send('Page.navigate', { url: route.url });
        await sleep(1500);
      }

      // Query styling metrics
      const evalRes = await client.send('Runtime.evaluate', {
        expression: `
          (function() {
            const bodyStyle = window.getComputedStyle(document.body);
            const htmlStyle = window.getComputedStyle(document.documentElement);
            const header = document.querySelector('header');
            const headerStyle = header ? window.getComputedStyle(header) : null;
            const sidebar = document.querySelector('aside');
            const sidebarStyle = sidebar ? window.getComputedStyle(sidebar) : null;
            const card = document.querySelector('.bg-\\\\[\\\\#0B1F2D\\\\], .bg-card, [class*="bg-[#0B1F2D]"], [class*="rounded-xl"]');
            const cardStyle = card ? window.getComputedStyle(card) : null;
            const logoSvg = document.querySelector('header svg, aside svg, [aria-label="GramaVise logo"]');
            const logoRect = logoSvg ? logoSvg.getBoundingClientRect() : null;

            return {
              title: document.title,
              bodyBg: bodyStyle.backgroundColor,
              bodyColor: bodyStyle.color,
              fontFamily: bodyStyle.fontFamily,
              headerBg: headerStyle ? headerStyle.backgroundColor : null,
              sidebarBg: sidebarStyle ? sidebarStyle.backgroundColor : null,
              cardBg: cardStyle ? cardStyle.backgroundColor : null,
              hasLogo: !!logoSvg,
              logoVisible: logoRect ? (logoRect.width > 0 && logoRect.height > 0) : false,
              logoWidth: logoRect ? Math.round(logoRect.width) : 0,
              logoHeight: logoRect ? Math.round(logoRect.height) : 0,
              elementCount: document.querySelectorAll('*').length
            };
          })()
        `,
        returnByValue: true
      });

      const metrics = evalRes.result.value;
      const failedCss = client.failedRequests.filter(r => r.url.endsWith('.css') || r.url.includes('/static/css/'));

      console.log(`Title: ${metrics.title}`);
      console.log(`Body Background: ${metrics.bodyBg}`);
      console.log(`Body Color: ${metrics.bodyColor}`);
      console.log(`Font Family: ${metrics.fontFamily.substring(0, 40)}...`);
      console.log(`Header Bg: ${metrics.headerBg}`);
      console.log(`Sidebar Bg: ${metrics.sidebarBg}`);
      console.log(`Card Bg: ${metrics.cardBg}`);
      console.log(`Logo present & visible: ${metrics.hasLogo && metrics.logoVisible} (${metrics.logoWidth}x${metrics.logoHeight}px)`);
      console.log(`Failed requests: ${client.failedRequests.length} (CSS failures: ${failedCss.length})`);

      results.push({
        route: route.name,
        url: route.url,
        metrics,
        failedRequestsCount: client.failedRequests.length,
        failedCssCount: failedCss.length
      });
    }

    client.close();
    console.log(`\n\nALL ROUTES AUDIT SUMMARY:`);
    console.table(results.map(r => ({
      Page: r.route,
      'Body Bg': r.metrics.bodyBg,
      'Card Bg': r.metrics.cardBg,
      'Logo Visible': r.metrics.logoVisible ? `YES (${r.metrics.logoWidth}x${r.metrics.logoHeight})` : 'NO',
      'CSS Errors': r.failedCssCount
    })));

  } finally {
    edgeProc.kill();
    try { fs.rmSync(userDataDir, { recursive: true, force: true }); } catch(e) {}
  }
}

run().catch(err => {
  console.error(err);
  process.exit(1);
});
