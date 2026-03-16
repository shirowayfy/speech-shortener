import logging
import os

import httpx

logger = logging.getLogger(__name__)

API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

CONTENT_TYPES = {
    ".ogg": "audio/ogg",
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".mp4": "video/mp4",
}


class Transcriber:
    def __init__(self, api_key: str) -> None:
        self.client = httpx.AsyncClient(
            timeout=60.0,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    async def transcribe(self, audio_path: str) -> str:
        filename = os.path.basename(audio_path)
        ext = os.path.splitext(audio_path)[1].lower()
        content_type = CONTENT_TYPES.get(ext, "application/octet-stream")

        try:
            with open(audio_path, "rb") as f:
                response = await self.client.post(
                    API_URL,
                    files={"file": (filename, f, content_type)},
                    data={"model": "whisper-large-v3"},
                )
            response.raise_for_status()
            data = response.json()
            text = data.get("text", "").strip()
            return text if text else "Речь не распознана."
        except Exception:
            logger.exception("Groq Whisper API error")
            raise

    async def close(self) -> None:
        await self.client.aclose()
