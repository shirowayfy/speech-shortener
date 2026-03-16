import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.config import load_config
from bot.handlers import start, voice
from bot.services.transcriber import Transcriber
from bot.services.summarizer import Summarizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    config = load_config()

    logger.info("Loading Whisper model '%s'...", config.whisper_model)
    transcriber = Transcriber(config.whisper_model)
    summarizer = Summarizer(config.xai_api_key)
    logger.info("Whisper model loaded.")

    bot = Bot(token=config.telegram_bot_token)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(voice.router)

    dp["transcriber"] = transcriber
    dp["summarizer"] = summarizer

    logger.info("Bot starting...")
    try:
        await dp.start_polling(bot, allowed_updates=["message"])
    finally:
        await summarizer.close()


if __name__ == "__main__":
    asyncio.run(main())
