import asyncio
from datetime import datetime, timezone
import aiosqlite
import os
from aiogram import Bot
from config import settings

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "skillquest.sqlite")


async def start_reminder_loop(bot: Bot):
    """
    Фоновая задача: рассылает напоминание всем пользователям каждый день
    в час, заданный REMINDER_UTC_HOUR (по UTC).
    """
    print(f"[Reminders] Запущен фоновый цикл. Плановое время UTC: {settings.REMINDER_UTC_HOUR}:00")

    while True:
        now = datetime.now(timezone.utc)
        if now.hour == settings.REMINDER_UTC_HOUR and now.minute == 0:
            try:
                async with aiosqlite.connect(DB_PATH) as db:
                    db.row_factory = aiosqlite.Row
                    cur = await db.execute("SELECT id FROM users")
                    users = await cur.fetchall()
                    await cur.close()
                print(f"[Reminders] Отправляем уведомления {len(users)} пользователям...")

                for row in users:
                    try:
                        await bot.send_message(
                            row["id"],
                            "📚 Новый урок готов! Набери /lesson, чтобы пройти его 💪"
                        )
                        await asyncio.sleep(0.3)  # чтобы не превысить лимит Telegram
                    except Exception as e:
                        print(f"[Reminders] Ошибка отправки пользователю {row['id']}: {e}")
            except Exception as e:
                print(f"[Reminders] Ошибка цикла напоминаний: {e}")

            # ждём 61 минуту, чтобы избежать повторной отправки
            await asyncio.sleep(3660)
        else:
            await asyncio.sleep(60)
