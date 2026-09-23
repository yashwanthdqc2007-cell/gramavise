import subprocess
import time
import os
import urllib.request
import json

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
SCREENSHOT_DIR = r"C:\Users\garag\.gemini\antigravity-ide\brain\394afd9b-5944-4796-b479-7be3d504795f\screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def snap(url, filename, width=1280, height=900, delay=3):
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
    print(f"[CAPTURED] {filename} ({os.path.getsize(out_path)} bytes)")

# 3. New Advisory desktop
snap("http://localhost:3000/onboarding", "03_new_advisory_desktop.png", 1280, 900, 3)

# 5. History page
snap("http://localhost:3000/history", "05_history_page_saved_report.png", 1280, 900, 3)

# 6. Government Schemes page
snap("http://localhost:3000/schemes", "06_government_schemes_page.png", 1280, 900, 3)

# 8. Dashboard at 375px
snap("http://localhost:3000/", "08_dashboard_mobile_375px.png", 375, 812, 3)

print("Edge CLI snapshots completed!")
