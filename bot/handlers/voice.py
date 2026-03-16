import asyncio
import logging
import os
import subprocess
import tempfile

from aiogram import Router, F
from aiogram.types import Message

from bot.services.transcriber import Transcriber
from bot.services.summarizer import Summarizer

router = Router()
logger = logging.getLogger(__name__)

SUMMARY_THRESHOLD = 100
TG_MSG_LIMIT = 4096
TRUNCATION_SUFFIX = "\n\n[...транскрипция обрезана]"


def _extract_audio(video_path: str, audio_path: str) -> None:
    result = subprocess.run(
        ["ffmpeg", "-i", video_path, "-vn", "-acodec", "pcm_s16le", audio_path, "-y"],
        capture_output=True,
    )
    if result.returncode != 0:
        logger.error("ffmpeg failed (code %d): %s", result.returncode, result.stderr.decode(errors="replace"))
        result.check_returncode()


def _build_result_with_summary(text: str, summary: str) -> str:
    footer = f"\n\nСуть:\n{summary}"
    header = "Транскрипция:\n"
    available = TG_MSG_LIMIT - len(header) - len(footer) - len(TRUNCATION_SUFFIX)

    if len(header) + len(text) + len(footer) <= TG_MSG_LIMIT:
        return f"{header}{text}{footer}"

    truncated = text[:available] + TRUNCATION_SUFFIX
    return f"{header}{truncated}{footer}"


async def _send_result(status: Message, original: Message, result: str) -> None:
    if len(result) <= TG_MSG_LIMIT:
        await status.edit_text(result)
        return

    # Split into chunks for very long messages (no summary case)
    await status.delete()
    for i in range(0, len(result), TG_MSG_LIMIT):
        await original.answer(result[i : i + TG_MSG_LIMIT])


@router.message(F.voice)
@router.message(F.video_note)
async def handle_voice(message: Message, transcriber: Transcriber, summarizer: Summarizer) -> None:
    status = await message.answer("Транскрибирую...")
    tmp_files: list[str] = []

    try:
        if message.voice:
            file_id = message.voice.file_id
            suffix = ".ogg"
        else:
            file_id = message.video_note.file_id
            suffix = ".mp4"

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.close()
        tmp_files.append(tmp.name)

        await message.bot.download(file_id, destination=tmp.name)

        audio_path = tmp.name
        if message.video_note:
            wav_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            wav_tmp.close()
            tmp_files.append(wav_tmp.name)
            await asyncio.to_thread(_extract_audio, tmp.name, wav_tmp.name)
            audio_path = wav_tmp.name

        text = await asyncio.to_thread(transcriber.transcribe, audio_path)

        if len(text) >= SUMMARY_THRESHOLD:
            await status.edit_text("Суммаризирую...")
            summary = await summarizer.summarize(text)
            result = _build_result_with_summary(text, summary)
        else:
            result = f"Транскрипция:\n{text}"

        await _send_result(status, message, result)

    except Exception:
        logger.exception("Error processing voice message")
        await status.edit_text("Произошла ошибка при обработке.")

    finally:
        for path in tmp_files:
            try:
                os.unlink(path)
            except OSError:
                pass
