import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
token = os.getenv("HF_TOKEN")

models = [
    "google/medgemma-27b-it",
    "epfl-llm/meditron-7b",
    "sethuiyer/Medichat-Llama3-8B",
    "google/gemma-2-2b-it",
    "meta-llama/Llama-3.2-3B-Instruct"
]

client = InferenceClient(api_key=token)

for model in models:
    try:
        response = client.chat_completion(
            model=model,
            messages=[{"role": "user", "content": "hello"}],
            max_tokens=5
        )
        print(f"[SUCCESS] {model}: {response.choices[0].message.content}")
    except Exception as e:
        print(f"[FAIL] {model}: {str(e)[:100]}")
