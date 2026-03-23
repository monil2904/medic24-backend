import asyncio
import base64
import time
from huggingface_hub import InferenceClient
from app.config import settings
from app.utils.prompts import MEDGEMMA_PROMPT

client = InferenceClient(model="google/gemma-3-27b-it", token=settings.HF_TOKEN)

async def query(user_query: str, system_prompt: str = MEDGEMMA_PROMPT) -> str | None:
    """Query MedGemma via Hugging Face Inference API."""
    try:
        response = await asyncio.to_thread(
            client.chat_completion,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            max_tokens=1024,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[MedGemma] Error: {e}")
        return None

async def query_with_image(image_base64: str, user_query: str) -> str | None:
    """Query MedGemma with an image (multimodal)."""
    try:
        response = await asyncio.to_thread(
            client.chat_completion,
            messages=[
                {"role": "system", "content": MEDGEMMA_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                        },
                        {"type": "text", "text": user_query}
                    ]
                }
            ],
            max_tokens=1024,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[MedGemma Image] Error: {e}")
        return None
