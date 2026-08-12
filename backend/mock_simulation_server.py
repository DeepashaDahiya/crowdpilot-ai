"""
TEMPORARY mock of Person 1's /simulation/reroute endpoint.
Used only to test /apply-recommendation locally before the real one exists.
Delete this file once Person 1's real endpoint is live.
"""
from fastapi import FastAPI

app = FastAPI()


@app.post("/simulation/reroute")
def mock_reroute(payload: dict):
    print("MOCK RECEIVED REROUTE REQUEST:", payload)
    return {
        "status": "rerouted",
        "from_node": payload.get("from_node"),
        "to_node": payload.get("to_node"),
        "redirect_percentage": payload.get("redirect_percentage"),
        "agents_rerouted": 120,  # fake number just to prove the flow works
    }