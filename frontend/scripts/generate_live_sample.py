import urllib.request
import json
import subprocess
import os

payload = {
    "profile": {
        "business_name": "Kisan Flour Mill",
        "category": "Flour & Spice Milling (Atta Chakki)",
        "description": "Small rural flour and spice milling unit serving local farmers.",
        "location": {
            "state": "Maharashtra",
            "district": "Pune",
            "village": "Baramati Rural"
        },
        "experience_years": 3,
        "own_capital": 40000.0,
        "desired_loan": 110000.0,
        "is_new_business": True
    },
    "financials": {
        "startup_cost": 45000.0,
        "equipment_cost": 75000.0,
        "inventory_cost": 30000.0,
        "monthly_fixed_cost": 12000.0,
        "customers_per_day": 35,
        "avg_ticket_price": 65.0,
        "working_days_per_month": 26,
        "variable_cost_pct": 32.0,
        "loan_tenure_months": 36,
        "interest_rate_pct": 11.5
    },
    "preferred_language": "en"
}

req = urllib.request.Request(
    'http://localhost:8000/api/analyze',
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

analysis_id = None
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        analysis_id = data.get('analysis_id')
        print(f"Created analysis ID: {analysis_id}")
        swot = data.get('market_result', {}).get('swot')
        print("SWOT Present:", swot is not None)
        if swot:
            print("Strengths:", len(swot.get('strengths', [])))
            print("Weaknesses:", len(swot.get('weaknesses', [])))
            print("Opportunities:", len(swot.get('opportunities', [])))
            print("Threats:", len(swot.get('threats', [])))
            for s in swot.get('strengths', []):
                print(f"  STR: {s.get('id')} - {s.get('title')} ({s.get('evidence_type')})")
            for w in swot.get('weaknesses', []):
                print(f"  WKN: {w.get('id')} - {w.get('title')} ({w.get('evidence_type')})")
            for o in swot.get('opportunities', []):
                print(f"  OPP: {o.get('id')} - {o.get('title')} ({o.get('evidence_type')})")
            for t in swot.get('threats', []):
                print(f"  THR: {t.get('id')} - {t.get('title')} ({t.get('evidence_type')})")
except Exception as e:
    print(f"Backend API error: {e}")

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
SCREENSHOT_DIR = r"C:\Users\garag\.gemini\antigravity-ide\brain\394afd9b-5944-4796-b479-7be3d504795f\screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def snap(url, filename, width=1280, height=1000, delay=4):
    out_path = os.path.join(SCREENSHOT_DIR, filename)
    cmd = [
        EDGE,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        f"--window-size={width},{height}",
        f"--virtual-time-budget={delay * 1000}",
        f"--screenshot={out_path}",
        url
    ]
    subprocess.run(cmd, check=True)
    if os.path.exists(out_path):
        print(f"[CAPTURED] {filename} ({os.path.getsize(out_path)} bytes)")

if analysis_id:
    # 1. Desktop full report overview with SWOT
    snap(f"http://localhost:3000/history/{analysis_id}", "swot_desktop_overview.png", 1440, 1100, 4)
    # 2. Mobile report overview with SWOT
    snap(f"http://localhost:3000/history/{analysis_id}", "swot_mobile_375px.png", 375, 900, 4)
    print("Visual QA screenshots saved successfully!")
