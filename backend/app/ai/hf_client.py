import os
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