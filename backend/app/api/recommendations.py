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
