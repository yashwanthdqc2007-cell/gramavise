import subprocess
import os
import time

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
SCREENSHOT_DIR = r"C:\Users\garag\.gemini\antigravity-ide\brain\394afd9b-5944-4796-b479-7be3d504795f\screenshots"
ANALYSIS_ID = "ba7cac4c-fe57-45b6-b1a3-11bf2d911e58"

# Write a tiny HTML page that sets localStorage and redirects to /history
seed_html_path = r"C:\Users\garag\.gemini\antigravity-ide\scratch\gramavise\frontend\public\seed_history.html"
with open(seed_html_path, "w", encoding="utf-8") as f:
    f.write(f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Seeding</title></head>
<body>
<script>
  const historyList = [
    {{
      analysis_id: "{ANALYSIS_ID}",
      business_name: "Kisan Flour Mill",
      business_category: "Flour & Spice Milling (Atta Chakki)",
      recommendation_status: "PROCEED",
      created_at: "{time.strftime('%Y-%m-%dT%H:%M:%S.000Z')}"
    }}
  ];
  localStorage.setItem('gramavise_history_v1', JSON.stringify(historyList));
  window.location.href = '/history';
</script>
</body>
</html>
""")

def snap_with_delay(url, filename, width=1280, height=900, delay=4):
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

# 5. History page with saved report
snap_with_delay("http://localhost:3000/seed_history.html", "05_history_page_saved_report.png", 1280, 900, 5)

# Also create a seed page for scenario lab that scrolls to scenario-lab
scenario_html_path = r"C:\Users\garag\.gemini\antigravity-ide\scratch\gramavise\frontend\public\seed_scenario.html"
with open(scenario_html_path, "w", encoding="utf-8") as f:
    f.write(f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Scenario Lab</title></head>
<body>
<script>
  window.location.href = '/history/{ANALYSIS_ID}#scenario-lab';
</script>
</body>
</html>
""")

# 7. Scenario lab with tall viewport so the whole Scenario Lab is visible
snap_with_delay(f"http://localhost:3000/history/{ANALYSIS_ID}#scenario-lab", "07_scenario_lab_saved_scenario.png", 1280, 2400, 6)

print("Finished snapping 05 and 07!")
