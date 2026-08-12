import os
import json
import re
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "meta-llama/Llama-3.1-8B-Instruct")

client = InferenceClient(token=HF_API_TOKEN)

_last_good_response = {}  # simple in-memory cache, keyed by bottleneck signature


def call_model(prompt: str) -> str:
    """Send a prompt to the HF-hosted model and return raw text response."""
    response = client.chat_completion(
        model=HF_MODEL_ID,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    return response.choices[0].message.content


def _cache_key(analytics: dict) -> str:
    bottlenecks = analytics.get("bottlenecks", [])
    if not bottlenecks:
        return "none"
    worst = max(bottlenecks, key=lambda b: b["utilization"])
    return worst["node"]


def get_structured_recommendation(analytics: dict, candidates: list[dict]) -> dict:
    """
    Calls the HF model with the recommendation prompt and returns a
    parsed JSON dict. Falls back to cached last-good response on failure/timeout.
    """
    from app.ai.prompts import build_recommendation_prompt

    key = _cache_key(analytics)
    prompt = build_recommendation_prompt(analytics, candidates)

    try:
        raw = call_model(prompt)
        cleaned = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
        parsed = json.loads(cleaned)
        _last_good_response[key] = parsed
        return parsed
    except Exception as e:
        print(f"WARNING: HF call/parse failed ({e}). Trying cache.")
        if key in _last_good_response:
            print("Serving cached recommendation instead.")
            return _last_good_response[key]
        print("No cache available. Returning None.")
        return None


def validate_recommendation(parsed: dict, candidates: list[dict]) -> dict:
    """
    Ensures the model's chosen action is actually in the valid candidates list
    and redirect_percentage is sane. Falls back to the best candidate if not.
    """
    if not candidates:
        return None

    best_candidate = candidates[0]

    if not parsed:
        return _fallback(best_candidate)

    valid_actions = {c["action"] for c in candidates}
    action = parsed.get("action")
    redirect = parsed.get("redirect_percentage")

    if action not in valid_actions:
        print(f"WARNING: model picked invalid action '{action}', falling back.")
        return _fallback(best_candidate)

    if not isinstance(redirect, (int, float)) or not (0 < redirect <= 100):
        print(f"WARNING: invalid redirect_percentage '{redirect}', clamping to 30.")
        parsed["redirect_percentage"] = 30

    return parsed


def _fallback(candidate: dict) -> dict:
    return {
        "action": candidate["action"],
        "redirect_percentage": 30,
        "reason": f"{candidate['to_node']} has significantly lower utilization ({candidate['alt_utilization']*100:.0f}%) and can absorb additional traffic.",
        "expected_effect": f"Reduce congestion at {candidate['from_node']}.",
    }


if __name__ == "__main__":
    from app.ai.recommender import get_candidate_actions

    mock_analytics = {
        "crowd_size": 500,
        "bottlenecks": [{"node": "exit_a", "utilization": 0.92}],
        "alternatives": [
            {"node": "exit_b", "utilization": 0.34},
            {"node": "exit_c", "utilization": 0.21},
        ],
        "metrics": {"average_wait": 8.1, "congestion_score": 92},
    }
    candidates = get_candidate_actions(mock_analytics)
    parsed = get_structured_recommendation(mock_analytics, candidates)
    validated = validate_recommendation(parsed, candidates)
    print("VALIDATED RESULT:", validated)