import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

token = os.getenv("HF_TOKEN")
if not token:
    raise ValueError("HF_TOKEN not found in environment variables")

# Test 1: Setting base_url explicitly
print("Running test 1: base_url='https://router.huggingface.co/hf-inference'")
client = InferenceClient(api_key=token, base_url="https://router.huggingface.co/hf-inference")
try:
    response = client.chat_completion(
        model="google/gemma-3-27b-it",
        messages=[{"role": "user", "content": "hi"}],
        max_tokens=10
    )
    print("Success 1:", response.choices[0].message.content)
except Exception as e:
    print("Fail 1:", e)

# Test 2: Try with provider
print("Running test 2: provider='hf-inference'")
client = InferenceClient(api_key=token)
try:
    response = client.chat_completion(
        model="google/gemma-3-27b-it",
        messages=[{"role": "user", "content": "hi"}],
        max_tokens=10,
        provider="hf-inference"
    )
    print("Success 2:", response.choices[0].message.content)
except Exception as e:
    print("Fail 2:", e)
