import subprocess
import time
import os

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
SCREENSHOT_DIR = r"C:\Users\garag\.gemini\antigravity-ide\brain\394afd9b-5944-4796-b479-7be3d504795f\screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
ANALYSIS_ID = "ba7cac4c-fe57-45b6-b1a3-11bf2d911e58"

def snap(url, filename, width=1280, height=900, delay=5):
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

# 4. Results page with Kisan Flour Mill analysis
snap(f"http://localhost:3000/history/{ANALYSIS_ID}", "04_results_page_kisan_flour_mill.png", 1280, 900, 5)

# 7. Scenario Lab with a saved scenario
snap(f"http://localhost:3000/history/{ANALYSIS_ID}#scenario-lab", "07_scenario_lab_saved_scenario.png", 1280, 900, 5)

# 9. Results at 375px
snap(f"http://localhost:3000/history/{ANALYSIS_ID}", "09_results_mobile_375px.png", 375, 812, 5)

print("Remaining screenshots completed!")
