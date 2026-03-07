import asyncio
from huggingface_hub import AsyncInferenceClient
from app.config import settings
from app.utils.prompts import MEDGEMMA_PROMPT

MODEL_ID = "google/gemma-2-2bd-it" # Assuming we substitute with a widely available HF conversational model (gemmas are very standard) or exactly as requested below if allowed
# user specified google/medgemma-27b-it
MODEL_ID = "google/medgemma-27b-it"

client = AsyncInferenceClient(model=MODEL_ID, token=settings.HF_TOKEN)

async def query(user_query: str, system_prompt: str = MEDGEMMA_PROMPT) -> str | None:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]
    try:
        response = await client.chat_completion(
            messages=messages,
            max_tokens=1024,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling MedGemma 27B: {e}")
        return None

async def query_with_image(image_base64: str, user_query: str) -> str | None:
    # Requires a visual-based multi-modal call format (may vary depending on actual medgemma implementation in HF)
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user_query},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]
        }
    ]
    try:
        response = await client.chat_completion(
            messages=messages,
            max_tokens=1024,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling MedGemma Multimodal: {e}")
        return None
