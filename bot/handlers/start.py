from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я бот для транскрибации и суммаризации голосовых сообщений.\n\n"
        "Отправьте или перешлите мне голосовое сообщение или видеокружочек, "
        "и я переведу речь в текст и кратко изложу суть.\n\n"
        "Используйте /help для подробностей."
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Как пользоваться ботом:\n\n"
        "1. Отправьте или перешлите голосовое сообщение\n"
        "2. Или отправьте видеокружочек\n\n"
        "Бот автоматически:\n"
        "- Распознает речь в тексте\n"
        "- Если текст длинный — кратко изложит суть"
    )
