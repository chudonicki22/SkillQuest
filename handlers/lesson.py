from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime, timezone

from data.db import (
    get_or_create_user,
    record_answer,
    get_or_create_global_lesson_for_date,
)
from services.lessons import get_daily_questions, validate_answer
from services.scoring import award_points, update_streak

router = Router()


# === Клавиатура с вариантами ответов ===
def answer_kb(q_id: int, options: list[str]):
    buttons = [
        [InlineKeyboardButton(text=o, callback_data=f"ans:{q_id}:{i}")]
        for i, o in enumerate(options)
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# === Команда /lesson ===
@router.message(F.text == "/lesson")
async def cmd_lesson(message: Message):
    """Начало урока — создаёт пользователя и выдаёт первый вопрос"""
    await get_or_create_user(message.from_user)

    # Урок дня общий для всех пользователей
    today = datetime.now(timezone.utc).date()
    lesson_id = await get_or_create_global_lesson_for_date(today)

    questions = await get_daily_questions(lesson_id)
    if not questions:
        await message.answer("Сегодня уроков нет. Попробуйте позже.")
        return

    q = questions[0]
    await message.answer(
        f"📚 Урок дня (общий) — <b>{today.isoformat()}</b>\n\n"
        f"<b>Вопрос 1/{len(questions)}:</b> {q['q']}",
        reply_markup=answer_kb(q["id"], q["options"]),
    )


# === Обработка ответов ===
@router.callback_query(F.data.startswith("ans:"))
async def on_answer(cb: CallbackQuery):
    """Обрабатывает выбор варианта ответа пользователем"""
    try:
        _, q_id, idx = cb.data.split(":")
        q_id, idx = int(q_id), int(idx)
    except ValueError:
        # Неверный формат данных callback
        try:
            await cb.answer("Ошибка данных. Попробуйте снова.", show_alert=False)
        except Exception:
            pass
        return

    # Проверяем ответ
    is_correct, question, total, position = await validate_answer(q_id, idx)

    # Если вопрос уже не актуален
    if question["lesson_id"] is None:
        try:
            await cb.answer("⏳ Этот вопрос уже обработан.", show_alert=False)
        except Exception:
            pass
        return

    # Записываем результат
    await record_answer(cb.from_user.id, question["lesson_id"], 1 if is_correct else 0, 0)

    # Формируем обратную связь
    feedback = (
        "✅ Верно!"
        if is_correct
        else f"❌ Неверно. Правильный ответ: <b>{question['options'][question['answer']]}</b>"
    )

    # Следующий вопрос
    if position + 1 < total:
        next_q = await get_daily_questions(question["lesson_id"], position + 1, position + 2)
        q = next_q[0]
        try:
            await cb.message.edit_text(
                f"{feedback}\n\n<b>Вопрос {position + 2}/{total}:</b> {q['q']}"
            )
            await cb.message.edit_reply_markup(reply_markup=answer_kb(q["id"], q["options"]))
        except Exception:
            # Игнорируем, если сообщение не изменилось или Telegram не успел обработать
            pass
    else:
        # Завершение урока
        correct_count = await award_points(cb.from_user.id, question["lesson_id"])
        streak = await update_streak(cb.from_user.id)
        points = correct_count * 10

        try:
            await cb.message.edit_text(
                f"{feedback}\n\n🎉 Урок завершён!\n"
                f"Верных ответов: <b>{correct_count}</b>\n"
                f"Начислено очков: <b>{points}</b>\n"
                f"Текущий streak: <b>{streak}</b>\n\n"
                f"Посмотри /leaderboard и /profile"
            )
            await cb.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass

    # Безопасное подтверждение callback-запроса (чтобы не упасть на "too old")
    try:
        await cb.answer()
    except Exception:
        pass
