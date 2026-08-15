# check_timing.py
import requests, time

BASE = "http://localhost:8000"
requests.post(f"{BASE}/simulation/reset")
requests.post(f"{BASE}/simulation/start")

for i in range(6):
    print(f"t={i*0.5:.1f}s:", requests.get(f"{BASE}/simulation/debug").json())
    time.sleep(0.5)
    