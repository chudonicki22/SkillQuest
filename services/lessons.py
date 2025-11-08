import json
import os
import aiosqlite

# Доступные темы обучения (для онбординга и будущих категорий)
THEMES = ["English", "Finance", "General"]

# Пути к источникам вопросов
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "lessons.json")
FALLBACK_PATH = os.path.join(os.path.dirname(__file__), "..", "examples", "sample_lessons.json")

# === Загрузка пула вопросов ===
async def _load_repo():
    """
    Загружает общий репозиторий уроков из lessons.json
    (если отсутствует — берёт из examples/sample_lessons.json)
    """
    path = DATA_PATH if os.path.exists(DATA_PATH) else FALLBACK_PATH
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# === Получение вопросов текущего урока ===
async def get_daily_questions(lesson_id: int, start: int = 0, end: int | None = None):
    """
    Возвращает список вопросов для урока по его ID.
    """
    async with aiosqlite.connect(os.path.join(os.path.dirname(__file__), "..", "skillquest.sqlite")) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT content FROM lessons WHERE id=?", (lesson_id,))
        row = await cur.fetchone()
        await cur.close()

        if not row:
            return []

        content = json.loads(row["content"])
        questions = content.get("questions", [])
        return questions[start:end]

# === Проверка ответа пользователя ===
async def validate_answer(question_id: int, chosen_index: int):
    """
    Проверяет выбранный пользователем ответ, возвращает:
    (is_correct, question_data, total_questions, current_position)
    где question_data содержит lesson_id, options и answer.
    """
    DB_PATH = os.path.join(os.path.dirname(__file__), "..", "skillquest.sqlite")

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT id, content FROM lessons")
        rows = await cur.fetchall()
        await cur.close()

        for row in rows:
            content = json.loads(row["content"])
            questions = content.get("questions", [])
            for pos, q in enumerate(questions):
                if q["id"] == question_id:
                    is_corr = (chosen_index == q["answer"])
                    return is_corr, {
                        "lesson_id": row["id"],
                        "options": q["options"],
                        "answer": q["answer"]  # добавлено для корректного вывода правильного ответа
                    }, len(questions), pos

    # если вопрос не найден
    return False, {"lesson_id": None, "options": [], "answer": None}, 0, 0
