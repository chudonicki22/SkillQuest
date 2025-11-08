from aiogram import Router, F
from aiogram.types import Message
from data.db import get_or_create_user, ensure_referral_code

router = Router()

@router.message(F.text == "/referral")
async def cmd_referral(message: Message):
    user = await get_or_create_user(message.from_user)
    code = await ensure_referral_code(message.from_user.id)
    await message.answer(
        "🤝 Пригласите друзей и получите бонусные очки!\n"
        f"Ваш код: <code>{code}</code>\n"
        "Друг вводит: /start <код>"
    )
