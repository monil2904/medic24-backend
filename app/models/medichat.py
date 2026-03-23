import asyncio
from huggingface_hub import InferenceClient
from app.config import settings
from app.utils.prompts import MEDICHAT_PROMPT

client = InferenceClient(model="Qwen/Qwen2.5-72B-Instruct", token=settings.HF_TOKEN)

async def query(user_query: str, system_prompt: str = MEDICHAT_PROMPT) -> str | None:
    """Query MediChat via Hugging Face Inference API."""
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
        print(f"[MediChat] Error: {e}")
        return None
