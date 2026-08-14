import requests
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any
import os

ANALYSIS_URL = os.getenv("ANALYSIS_URL", "http://localhost:8000/analysis")

from app.ai.recommender import get_candidate_actions
from app.ai.hf_client import get_structured_recommendation, validate_recommendation

router = APIRouter()


class AnalyticsPayload(BaseModel):
    crowd_size: int
    bottlenecks: list[dict[str, Any]]
    alternatives: list[dict[str, Any]]
    metrics: dict[str, Any]
def adapt_analytics_contract(raw: dict) -> dict:
    """
    Translates Person 2's real /analysis response shape into the
    shape recommender.py expects (node/utilization keys).
    """
    adapted_bottlenecks = [
        {"node": b["node_id"], "utilization": b["severity"]}
        for b in raw.get("bottlenecks", [])
    ]
    adapted_alternatives = [
        {"node": a["node_id"], "utilization": a["utilization"]}
        for a in raw.get("alternatives", [])
    ]
    return {
        "crowd_size": raw.get("crowd", {}).get("total", 0),
        "bottlenecks": adapted_bottlenecks,
        "alternatives": adapted_alternatives,
        "metrics": raw.get("metrics", {}),
    }

@router.post("/recommendation")
def recommend():
    try:
        response = requests.get(ANALYSIS_URL, timeout=5)
        response.raise_for_status()
        raw_analytics = response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Could not reach analytics service: {e}"}

    analytics = adapt_analytics_contract(raw_analytics)

    candidates = get_candidate_actions(analytics)
    if not candidates:
        return {"status": "ok", "message": "No congestion detected. No action needed."}

    parsed = get_structured_recommendation(analytics, candidates)
    validated = validate_recommendation(parsed, candidates)

    return {"status": "ok", "recommendation": validated}


SIMULATION_BASE_URL = os.getenv("SIMULATION_BASE_URL", "http://localhost:8000")


class ApplyPayload(BaseModel):
    from_node: str
    to_node: str
    redirect_percentage: int



VALID_EXITS = {"exit_a", "exit_b", "exit_c"}  # from data/venues/stadium.json — confirm with Person 1 if this list ever changes


@router.post("/apply-recommendation")
def apply_recommendation(payload: ApplyPayload):
    if payload.from_node not in VALID_EXITS or payload.to_node not in VALID_EXITS:
        return {
            "status": "error",
            "message": f"Invalid node(s): from_node='{payload.from_node}', to_node='{payload.to_node}'. Must be one of {VALID_EXITS}.",
        }

    reroute_body = {
        "from_node": payload.from_node,
        "to_node": payload.to_node,
        "redirect_percentage": payload.redirect_percentage,
    }

    try:
        response = requests.post(f"{SIMULATION_BASE_URL}/simulation/reroute", json=reroute_body, timeout=5)
        response.raise_for_status()
        result = response.json()
        return {"status": "ok", "rerouted_count": result.get("rerouted_count"), "raw_result": result}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Could not reach simulation service: {e}"}