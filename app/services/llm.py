"""OpenRouter LLM client — OpenAI-compatible via the openai SDK."""

from openai import AsyncOpenAI
from app.config import OPENROUTER_API_KEY, OPENROUTER_MODEL

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)


async def chat(system_prompt: str, user_message: str) -> str:
    """Send a system + user message to the LLM and return the response text."""
    resp = await client.chat.completions.create(
        model=OPENROUTER_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=512,
        temperature=0.7,
    )
    return resp.choices[0].message.content or "(no response)"
