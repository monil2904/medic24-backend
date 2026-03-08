import asyncio
from huggingface_hub import InferenceClient
from app.config import settings
from app.utils.prompts import MEDITRON_PROMPT

client = InferenceClient(model="epfl-llm/meditron-7b", token=settings.HF_TOKEN)

async def query(user_query: str, system_prompt: str = MEDITRON_PROMPT) -> str | None:
    """Query Meditron via Hugging Face Inference API."""
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
        print(f"[Meditron] Error: {e}")
        return None
