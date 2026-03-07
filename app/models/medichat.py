from huggingface_hub import AsyncInferenceClient
from app.config import settings
from app.utils.prompts import MEDICHAT_PROMPT

MODEL_ID = "sethuiyer/Medichat-Llama3-8B"

client = AsyncInferenceClient(model=MODEL_ID, token=settings.HF_TOKEN)

async def query(user_query: str, system_prompt: str = MEDICHAT_PROMPT) -> str | None:
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
        print(f"Error calling MediChat-Llama3-8B: {e}")
        return None
