import requests
import time

print("Triggering screening via API (POST /api/screen)...")
resp = requests.post("http://localhost:8000/api/screen", json={
    "date_from": "2026-09-14",
    "date_to": "2026-09-21",
    "lookback_days": 60,
    "mode": "smart"
})
print("Trigger response:", resp.status_code, resp.json())
scan_id = resp.json().get("scan_id")

for i in range(25):
    time.sleep(2)
    r = requests.get("http://localhost:8000/api/scans/latest").json()
    scan = r.get("scan", {})
    summary = r.get("summary", {})
    status = scan.get("status")
    prog = summary.get("progress_percent")
    msg = summary.get("stage_message")
    print(f"[{i*2}s] Scan #{scan.get('id')} - Status: {status} ({prog}%) - {msg}")
    if status in ["COMPLETED", "FAILED"]:
        print("Final Scan Details:", scan)
        break
