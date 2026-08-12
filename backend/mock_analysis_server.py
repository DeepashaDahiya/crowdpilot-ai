"""
TEMPORARY mock of Person 2's /analysis endpoint.
Used only to test /recommendation's real-data path before her real endpoint exists.
Delete this file once Person 2's real endpoint is live.
"""
from fastapi import FastAPI

app = FastAPI()


@app.get("/analysis")
def mock_analysis():
    return {
        "crowd_size": 500,
        "bottlenecks": [{"node": "exit_a", "utilization": 0.92}],
        "alternatives": [
            {"node": "exit_b", "utilization": 0.34},
            {"node": "exit_c", "utilization": 0.21},
        ],
        "metrics": {"average_wait": 8.1, "congestion_score": 92},
    }