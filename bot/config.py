from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str
    xai_api_key: str
    groq_api_key: str


def load_config() -> Config:
    token = getenv("TELEGRAM_BOT_TOKEN", "").strip()
    xai_api_key = getenv("XAI_API_KEY", "").strip()
    groq_api_key = getenv("GROQ_API_KEY", "").strip()

    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set")
    if not xai_api_key:
        raise ValueError("XAI_API_KEY is not set")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is not set")

    return Config(
        telegram_bot_token=token,
        xai_api_key=xai_api_key,
        groq_api_key=groq_api_key,
    )
