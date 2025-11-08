from aiogram import Router, F
from aiogram.types import Message
from data.db import get_leaderboard_week

router = Router()

@router.message(F.text == "/leaderboard")
async def cmd_leaderboard(message: Message):
    top = await get_leaderboard_week(limit=10)
    if not top:
        await message.answer("Рейтинг пуст. Пройдите первый урок!")
        return
    lines = []
    for i, row in enumerate(top, start=1):
        name = row["username"] or f"id{row['id']}"
        lines.append(f"{i}. {name} — {row['week_points']}")
    await message.answer("🏆 <b>Лидерборд (7 дней)</b>\n" + "\n".join(lines))
