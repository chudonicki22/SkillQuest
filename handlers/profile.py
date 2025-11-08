from aiogram import Router, F
from aiogram.types import Message
from data.db import get_user, get_user_week_points

router = Router()

@router.message(F.text == "/profile")
async def cmd_profile(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("Профиль не найден. Набери /start")
        return
    week_points = await get_user_week_points(message.from_user.id)
    await message.answer(
        "👤 <b>Профиль</b>\n"
        f"Тема: <b>{user['theme'] or '—'}</b>\n"
        f"Очки: <b>{user['score']}</b> (за 7 дней: <b>{week_points}</b>)\n"
        f"Streak: <b>{user['streak']}</b>"
    )
