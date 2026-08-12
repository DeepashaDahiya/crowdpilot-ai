import requests
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any



from app.ai.recommender import get_candidate_actions
from app.ai.hf_client import get_structured_recommendation, validate_recommendation

router = APIRouter()


class AnalyticsPayload(BaseModel):
    crowd_size: int
    bottlenecks: list[dict[str, Any]]
    alternatives: list[dict[str, Any]]
    metrics: dict[str, Any]


@router.post("/recommendation")
def recommend(payload: AnalyticsPayload):
    analytics = payload.dict()

    candidates = get_candidate_actions(analytics)
    if not candidates:
        return {"status": "ok", "message": "No congestion detected. No action needed."}

    parsed = get_structured_recommendation(analytics, candidates)
    validated = validate_recommendation(parsed, candidates)

    return {"status": "ok", "recommendation": validated}


SIMULATION_BASE_URL = "http://localhost:8000"  # update once you confirm Person 1's actual port


class ApplyPayload(BaseModel):
    from_node: str
    to_node: str
    redirect_percentage: int


@router.post("/apply-recommendation")
def apply_recommendation(payload: ApplyPayload):
    reroute_body = {
        "from_node": payload.from_node,
        "to_node": payload.to_node,
        "redirect_percentage": payload.redirect_percentage,
    }

    try:
        # TODO: confirm this matches Person 1's real /simulation/reroute once it exists
        response = requests.post(f"{SIMULATION_BASE_URL}/simulation/reroute", json=reroute_body, timeout=5)
        response.raise_for_status()
        return {"status": "ok", "reroute_result": response.json()}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Could not reach simulation service: {e}"}
