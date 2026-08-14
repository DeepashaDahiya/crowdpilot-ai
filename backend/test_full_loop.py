"""
Full end-to-end test: reset -> start -> get real recommendation ->
apply that EXACT recommendation -> confirm improvement.
"""
import requests
import time

BASE = "http://localhost:8000"

print("1. Resetting...")
requests.post(f"{BASE}/simulation/reset")

print("2. Starting simulation...")
requests.post(f"{BASE}/simulation/start")

print("3. Waiting for agents to build congestion at an exit...")
time.sleep(6)  # ~3 ticks, agents should be at exits by now

before = requests.get(f"{BASE}/analysis").json()
print("BEFORE:", before["metrics"], before["bottlenecks"])

print("4. Getting AI recommendation...")
rec_response = requests.post(f"{BASE}/recommendation").json()
print("RECOMMENDATION:", rec_response)

if rec_response.get("recommendation"):
    rec = rec_response["recommendation"]
    from_node = rec["from_node"]
    to_node = rec["to_node"]
    redirect_pct = rec["redirect_percentage"]

    print(f"5. Applying: {from_node} -> {to_node} at {redirect_pct}%...")
    apply_response = requests.post(f"{BASE}/apply-recommendation", json={
        "from_node": from_node,
        "to_node": to_node,
        "redirect_percentage": redirect_pct,
    }).json()
    print("APPLY RESULT:", apply_response)

    time.sleep(3)
    after = requests.get(f"{BASE}/analysis").json()
    print("AFTER:", after["metrics"], after["bottlenecks"])
else:
    print("No recommendation returned — no congestion detected at this moment.")