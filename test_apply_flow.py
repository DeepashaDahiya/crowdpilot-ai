import requests
import time

BASE = "http://localhost:8000"

def get_utilization(state, node_id):
    for n in state["nodes"]:
        if n["id"] == node_id:
            return n["utilization"]
    return 0.0

def run_trial(apply_reroute):
    requests.post(f"{BASE}/simulation/reset")
    requests.post(f"{BASE}/simulation/start")
    time.sleep(1.2)

    if apply_reroute:
        resp = requests.post(f"{BASE}/simulation/reroute", json={
            "from_node": "exit_a",
            "to_node": "exit_c",
            "redirect_percentage": 30
        })
        print("Reroute response:", resp.json())

    time.sleep(1.5)  # let the (remaining) agents actually arrive
    final = requests.get(f"{BASE}/simulation/state").json()
    return get_utilization(final, "exit_a")

if __name__ == "__main__":
    print("--- Baseline (no reroute) ---")
    baseline = run_trial(apply_reroute=False)
    print("exit_a utilization:", baseline)

    print("\n--- With reroute ---")
    rerouted = run_trial(apply_reroute=True)
    print("exit_a utilization:", rerouted)

    print(f"\nResult: baseline={baseline}, with reroute={rerouted}")