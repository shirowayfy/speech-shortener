from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str
    xai_api_key: str
    whisper_model: str


def load_config() -> Config:
    token = getenv("TELEGRAM_BOT_TOKEN", "").strip()
    api_key = getenv("XAI_API_KEY", "").strip()
    whisper_model = getenv("WHISPER_MODEL", "base").strip()

    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set")
    if not api_key:
        raise ValueError("XAI_API_KEY is not set")

    return Config(
        telegram_bot_token=token,
        xai_api_key=api_key,
        whisper_model=whisper_model,
    )
