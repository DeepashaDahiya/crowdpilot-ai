import json


def build_recommendation_prompt(analytics: dict, candidates: list[dict]) -> str:
    """
    Build a prompt that gives the model the situation + valid candidate
    actions, and forces a structured, specific JSON-only response.
    """
    prompt = f"""You are an experienced event operations AI advising a live venue control room during an active crowd congestion event.

CURRENT SITUATION (JSON):
{json.dumps(analytics, indent=2)}

VALID CANDIDATE ACTIONS (you MUST pick exactly one of these, do not invent others):
{json.dumps(candidates, indent=2)}

Pick the single best candidate action to reduce congestion. Write like a confident, experienced operations lead speaking to a control room — specific and numeric, not generic.

Rules for your response:
- ALWAYS cite the actual utilization numbers from the situation JSON (e.g. "92% utilization" not "high utilization").
- ALWAYS name the specific nodes involved (e.g. "Exit A" and "Exit C"), never vague terms like "the congested area".
- Keep "reason" to one clear sentence, under 30 words.
- Keep "expected_effect" to one short sentence describing a concrete outcome (e.g. reduced wait time, lower congestion score) — not a vague promise.
- Do not hedge with words like "might," "could," or "possibly" — state the recommendation with operational confidence.

Respond with ONLY a JSON object in this exact shape, and nothing else — no explanation outside the JSON, no markdown code fences:

{{
  "action": "<the action string from your chosen candidate>",
  "redirect_percentage": <integer between 10 and 50>,
  "reason": "<one confident, numeric sentence>",
  "expected_effect": "<one short, concrete sentence>"
}}
"""
    return prompt


if __name__ == "__main__":
    mock_analytics = {
        "crowd_size": 500,
        "bottlenecks": [{"node": "exit_a", "utilization": 0.92}],
        "alternatives": [
            {"node": "exit_b", "utilization": 0.34},
            {"node": "exit_c", "utilization": 0.21},
        ],
        "metrics": {"average_wait": 8.1, "congestion_score": 92},
    }
    mock_candidates = [
        {"action": "Open Exit C", "from_node": "exit_a", "to_node": "exit_c", "alt_utilization": 0.21},
        {"action": "Open Exit B", "from_node": "exit_a", "to_node": "exit_b", "alt_utilization": 0.34},
    ]
    print(build_recommendation_prompt(mock_analytics, mock_candidates))