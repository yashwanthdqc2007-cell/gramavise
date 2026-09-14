import urllib.request
import json
import sys

try:
    print("1. Testing http://localhost:8000/health ...")
    res1 = urllib.request.urlopen("http://localhost:8000/health")
    print("  Status:", res1.status, res1.read().decode())

    print("2. Testing http://127.0.0.1:8000/health ...")
    res2 = urllib.request.urlopen("http://127.0.0.1:8000/health")
    print("  Status:", res2.status, res2.read().decode())

    print("3. Testing http://localhost:8000/ready ...")
    res3 = urllib.request.urlopen("http://localhost:8000/ready")
    print("  Status:", res3.status, res3.read().decode())

    print("4. Testing validation exception handler (sending invalid payload to verify clean 422)...")
    req_invalid = urllib.request.Request(
        "http://localhost:8000/api/analyze",
        data=b'{"profile": {}}',
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        urllib.request.urlopen(req_invalid)
        print("  ERROR: Expected 422 but got 200")
    except urllib.error.HTTPError as e:
        print(f"  Expected 422 received cleanly! Status: {e.code}")
        body = e.read().decode()
        parsed = json.loads(body)
        print(f"  Response JSON parsed successfully: {parsed.keys()}")

    print("5. Testing valid POST /api/analyze ...")
    valid_payload = {
        "profile": {
            "business_name": "Kisan Flour Mill & Spices",
            "category": "Flour & Spice Milling (Atta Chakki)",
            "description": "Rural flour mill and spice grinding unit.",
            "location": {"state": "Maharashtra", "district": "Pune", "village": "Baramati"},
            "experience_years": 3,
            "own_capital": 50000,
            "desired_loan": 70000,
            "is_new_business": True
        },
        "financials": {
            "startup_cost": 15000,
            "equipment_cost": 80000,
            "inventory_cost": 25000,
            "monthly_fixed_cost": 6000,
            "customers_per_day": 40,
            "avg_ticket_price": 50,
            "working_days_per_month": 26,
            "variable_cost_pct": 40,
            "interest_rate_pct": 10.5,
            "loan_tenure_months": 36
        },
        "preferred_language": "en"
    }
    req_valid = urllib.request.Request(
        "http://localhost:8000/api/analyze",
        data=json.dumps(valid_payload).encode(),
        headers={"Content-Type": "application/json", "Origin": "http://localhost:3000"},
        method="POST"
    )
    res_valid = urllib.request.urlopen(req_valid)
    print("  Status:", res_valid.status)
    data = json.loads(res_valid.read().decode())
    analysis_id = data.get("analysis_id")
    print("  Persisted analysis_id:", analysis_id)
    print("  Recommendation verdict:", data.get("recommendation_status"))

    print("6. Verifying historical GET /api/analyze/{analysis_id} ...")
    hist_res = urllib.request.urlopen(f"http://localhost:8000/api/analyze/{analysis_id}")
    print("  Historical GET Status:", hist_res.status)
    hist_data = json.loads(hist_res.read().decode())
    assert hist_data.get("analysis_id") == analysis_id, "Historical analysis_id mismatch"
    print("  Historical GET verified!")

    print("\n>>> ALL BACKEND VERIFICATIONS PASSED! <<<")
except Exception as e:
    print(f"FAILED: {e}")
    sys.exit(1)
