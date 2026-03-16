import logging

import httpx

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Ты — помощник для краткого изложения. "
    "Тебе дан текст из голосового сообщения. "
    "Изложи основную суть в 2-3 предложениях. "
    "Будь кратким и точным. "
    "Отвечай на том же языке, на котором написан текст."
)

API_URL = "https://api.groq.com/openai/v1/chat/completions"


class Summarizer:
    def __init__(self, api_key: str) -> None:
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

    async def summarize(self, text: str) -> str:
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
        }

        try:
            response = await self.client.post(API_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            choices = data.get("choices")
            if not choices:
                logger.error("API returned empty choices: %s", data)
                return "Не удалось суммаризировать текст."
            return choices[0]["message"]["content"]
        except Exception:
            logger.exception("Summarization API error")
            return "Не удалось суммаризировать текст."

    async def close(self) -> None:
        await self.client.aclose()
