import asyncio
from openai import OpenAI
from app.config import settings
from app.utils.prompts import MEDICHAT_PROMPT

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=settings.HF_TOKEN,
)

MODEL_ID = "Qwen/Qwen2.5-Coder-32B-Instruct"

async def query(user_query: str, system_prompt: str = MEDICHAT_PROMPT) -> str | None:
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
        print(f"[Llama] Error: {e}")
        return None
```

### File 4: `requirements.txt` — ADD this line at the end:
```
openai>=1.40.0