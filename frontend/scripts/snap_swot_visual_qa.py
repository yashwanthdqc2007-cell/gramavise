import subprocess
import os
import time

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
SCREENSHOT_DIR = r"C:\Users\garag\.gemini\antigravity-ide\brain\394afd9b-5944-4796-b479-7be3d504795f\screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
ANALYSIS_ID = "f0f9bfe2-823f-4477-ae77-4ca2614ef624"

def snap(url, filename, width=1280, height=1200, delay=10):
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

# 1. Desktop full report overview with SWOT
snap(f"http://localhost:3000/history/{ANALYSIS_ID}", "swot_desktop_overview.png", 1440, 1400, 10)

# 2. Mobile report overview with SWOT at 375px
snap(f"http://localhost:3000/history/{ANALYSIS_ID}", "swot_mobile_375px.png", 375, 1200, 10)

print("Visual QA capture complete.")
