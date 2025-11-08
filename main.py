import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from handlers.start import router as start_router
from handlers.lesson import router as lesson_router
from handlers.profile import router as profile_router
from handlers.leaderboard import router as leaderboard_router
from handlers.referral import router as referral_router
from services.reminders import start_reminder_loop

async def main():
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(start_router)
    dp.include_router(lesson_router)
    dp.include_router(profile_router)
    dp.include_router(leaderboard_router)
    dp.include_router(referral_router)

    # Фоновая задача ежедневных напоминаний
    asyncio.create_task(start_reminder_loop(bot))

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
