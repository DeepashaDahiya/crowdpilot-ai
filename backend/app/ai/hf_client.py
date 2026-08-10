import os
import json
import re
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "meta-llama/Llama-3.1-8B-Instruct")

client = InferenceClient(token=HF_API_TOKEN)


def call_model(prompt: str) -> str:
    """Send a prompt to the HF-hosted model and return raw text response."""
    response = client.chat_completion(
        model=HF_MODEL_ID,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    # quick manual test
    result = call_model("Say hello in exactly 5 words.")
    print("MODEL RESPONSE:", result)

    


def get_structured_recommendation(analytics: dict, candidates: list[dict]) -> dict:
    """
    Calls the HF model with the recommendation prompt and returns a
    parsed JSON dict. Strips markdown fences defensively if present.
    """
    from app.ai.prompts import build_recommendation_prompt

    prompt = build_recommendation_prompt(analytics, candidates)
    raw = call_model(prompt)

    # strip markdown code fences if the model added them anyway
    cleaned = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()

    try:
        parsed = json.loads(cleaned)
        return parsed
    except json.JSONDecodeError:
        print("WARNING: could not parse model output as JSON. Raw output was:")
        print(raw)
        return None


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
    result = get_structured_recommendation(mock_analytics, mock_candidates)
    print("PARSED RESULT:", result)