import asyncio
from openai import OpenAI
from app.config import settings
from app.utils.prompts import MEDGEMMA_PROMPT

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=settings.HF_TOKEN,
)

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"

async def query(user_query: str, system_prompt: str = MEDGEMMA_PROMPT) -> str | None:
    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            max_tokens=1024,
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[Gemma] Error: {e}")
        return None

async def query_with_image(image_base64: str, user_query: str) -> str | None:
    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": MEDGEMMA_PROMPT},
                {"role": "user", "content": user_query + " [User uploaded a medical image for analysis]"}
            ],
            max_tokens=1024,
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[Gemma Image] Error: {e}")
        return None