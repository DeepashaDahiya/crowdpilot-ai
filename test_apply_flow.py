import requests
import time

BASE = "http://localhost:8000"

def simulate_apply_recommendation(from_node, to_node, redirect_percentage):
    """This is exactly what Person 3's /apply-recommendation will do internally."""
    response = requests.post(f"{BASE}/simulation/reroute", json={
        "from_node": from_node,
        "to_node": to_node,
        "redirect_percentage": redirect_percentage
    })
    print("Reroute response:", response.json())

if __name__ == "__main__":
    for trial in range(5):
        print(f"\n--- Trial {trial+1} ---")
        requests.post(f"{BASE}/simulation/reset")
        requests.post(f"{BASE}/simulation/start")
        time.sleep(3)
        before = requests.get(f"{BASE}/simulation/state").json()
        exit_a_before = next(n for n in before["nodes"] if n["id"] == "exit_a")
        print("exit_a utilization before:", exit_a_before["utilization"])

        simulate_apply_recommendation("exit_a", "exit_c", 30)
        time.sleep(2)

        after = requests.get(f"{BASE}/simulation/state").json()
        exit_a_after = next(n for n in after["nodes"] if n["id"] == "exit_a")
        print("exit_a utilization after:", exit_a_after["utilization"])