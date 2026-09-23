import subprocess
import os

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
SCREENSHOT_DIR = r"C:\Users\garag\.gemini\antigravity-ide\brain\394afd9b-5944-4796-b479-7be3d504795f\screenshots"
ANALYSIS_ID = "ba7cac4c-fe57-45b6-b1a3-11bf2d911e58"

# Write an HTML that loads the page and immediately scrolls the window down to scenario lab
scenario_scroll_html = r"C:\Users\garag\.gemini\antigravity-ide\scratch\gramavise\frontend\public\snap_scenario.html"
with open(scenario_scroll_html, "w", encoding="utf-8") as f:
    f.write(f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Scenario Lab Snapshot</title></head>
<body>
<iframe id="appFrame" src="/history/{ANALYSIS_ID}" style="width:1280px;height:2400px;border:none;"></iframe>
<script>
  window.onload = () => {{
    setTimeout(() => {{
      const doc = document.getElementById('appFrame').contentWindow.document;
      const el = doc.getElementById('scenario-lab') || doc.querySelector('[id*="scenario"]');
      if (el) el.scrollIntoView({{ behavior: 'instant' }});
    }}, 4000);
  }};
</script>
</body>
</html>
""")

def snap_scenario():
    out_path = os.path.join(SCREENSHOT_DIR, "07_scenario_lab_saved_scenario.png")
    cmd = [
        EDGE,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        "--window-size=1280,3800",
        "--virtual-time-budget=6000",
        f"--screenshot={out_path}",
        f"http://localhost:3000/history/{ANALYSIS_ID}#scenario-lab"
    ]
    subprocess.run(cmd, check=True)
    print(f"[CAPTURED] 07_scenario_lab_saved_scenario.png ({os.path.getsize(out_path)} bytes)")

snap_scenario()
