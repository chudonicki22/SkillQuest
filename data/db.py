import os
import aiosqlite
import argparse
import json
from datetime import datetime, timezone, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "skillquest.sqlite")
LESSONS_JSON = os.path.join(os.path.dirname(__file__), "lessons.json")
SAMPLE_JSON = os.path.join(os.path.dirname(__file__), "..", "examples", "sample_lessons.json")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                theme TEXT,
                score INTEGER DEFAULT 0,
                streak INTEGER DEFAULT 0,
                last_lesson_date TEXT,
                referral_code TEXT,
                referred_by TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                theme TEXT,
                content TEXT
            );
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                lesson_id INTEGER,
                correct INTEGER,
                points INTEGER,
                timestamp TEXT DEFAULT (datetime('now'))
            );
            """
        )
        await db.commit()

async def get_or_create_user(user) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE id=?", (user.id,))
        row = await cur.fetchone()
        await cur.close()
        if row:
            return dict(row)
        await db.execute("INSERT INTO users (id, username) VALUES (?, ?)", (user.id, user.username))
        await db.commit()
        return {"id": user.id, "username": user.username, "theme": None, "score": 0, "streak": 0}

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE id=?", (user_id,))
        row = await cur.fetchone()
        await cur.close()
        return dict(row) if row else None

async def set_theme(user_id: int, theme: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET theme=? WHERE id=?", (theme, user_id))
        await db.commit()

async def ensure_referral_code(user_id: int) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT referral_code FROM users WHERE id=?", (user_id,))
        row = await cur.fetchone()
        await cur.close()
        if row and row["referral_code"]:
            return row["referral_code"]
        code = f"RQ{user_id}"
        await db.execute("UPDATE users SET referral_code=? WHERE id=?", (code, user_id))
        await db.commit()
        return code

async def record_answer(user_id: int, lesson_id: int, correct: int, points: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO answers (user_id, lesson_id, correct, points) VALUES (?, ?, ?, ?)",
            (user_id, lesson_id, correct, points)
        )
        await db.commit()

# === GLOBAL Daily Lesson ===
async def get_or_create_global_lesson_for_date(day):
    """
    Создаёт (или возвращает существующий) общий урок на дату `day` с theme='GLOBAL'.
    Контент выбирается из lessons.json (или fallback), случайным образом.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT id FROM lessons WHERE date=? AND theme='GLOBAL'", (day.isoformat(),))
        row = await cur.fetchone()
        await cur.close()
        if row:
            return row["id"]

        path = LESSONS_JSON if os.path.exists(LESSONS_JSON) else SAMPLE_JSON
        with open(path, "r", encoding="utf-8") as f:
            pool = json.load(f)

        # Берём любой набор вопросов (при желании можно фильтровать по theme)
        chosen = random.choice(pool) if pool else {"questions": []}
        content = json.dumps(chosen, ensure_ascii=False)

        await db.execute(
            "INSERT INTO lessons (date, theme, content) VALUES (?, 'GLOBAL', ?)",
            (day.isoformat(), content)
        )
        await db.commit()

        cur = await db.execute("SELECT last_insert_rowid() AS id")
        row = await cur.fetchone()
        await cur.close()
        return row["id"]

# === Метрики и лидерборд ===

async def get_user_week_points(user_id: int) -> int:
    since = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        # Считаем очки как correct * 10, чтобы не зависеть от столбца points
        cur = await db.execute(
            "SELECT COALESCE(SUM(correct)*10, 0) AS s FROM answers WHERE user_id=? AND timestamp >= ?",
            (user_id, since)
        )
        row = await cur.fetchone()
        await cur.close()
        return int(row["s"] or 0)

async def get_leaderboard_week(limit: int = 10):
    since = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            """
            SELECT u.id, u.username, COALESCE(SUM(a.correct)*10, 0) AS week_points
            FROM users u
            LEFT JOIN answers a ON a.user_id = u.id AND a.timestamp >= ?
            GROUP BY u.id, u.username
            ORDER BY week_points DESC
            LIMIT ?
            """,
            (since, limit)
        )
        rows = await cur.fetchall()
        await cur.close()
        return [dict(r) for r in rows]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true")
    args = parser.parse_args()
    if args.init:
        import asyncio
        asyncio.run(init_db())
        print("DB initialized:", DB_PATH)

