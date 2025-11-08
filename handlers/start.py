from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from data.db import get_or_create_user, set_theme
from services.lessons import THEMES

router = Router()

def theme_keyboard():
    buttons = [[KeyboardButton(text=theme)] for theme in THEMES]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    await get_or_create_user(message.from_user)
    await message.answer(
        "👋 Добро пожаловать в <b>SkillQuest</b>!\n"
        "Это мини-уроки на 5 минут в день: отвечай на вопросы, копи очки и попадай в лидерборд.\n\n"
        "Выберите тему для обучения:",
        reply_markup=theme_keyboard()
    )

@router.message(F.text.in_(THEMES))
async def choose_theme(message: Message):
    await set_theme(message.from_user.id, message.text)
    await message.answer(
        f"Отлично! Тема установлена: <b>{message.text}</b>.\n"
        "Набери /lesson чтобы пройти урок дня."
    )
