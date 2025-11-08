from datetime import datetime, timezone
import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "skillquest.sqlite")

POINTS_PER_CORRECT = 10
STREAK_BONUS = 5  # при желании можно начислять дополнительно в будущем

async def award_points(user_id: int, lesson_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT COALESCE(SUM(correct),0) AS c FROM answers WHERE user_id=? AND lesson_id=?",
            (user_id, lesson_id)
        )
        row = await cur.fetchone()
        await cur.close()
        correct = int(row["c"] or 0)
        points = correct * POINTS_PER_CORRECT
        await db.execute(
            "UPDATE users SET score = score + ?, last_lesson_date = ? WHERE id = ?",
            (points, datetime.now(timezone.utc).date().isoformat(), user_id)
        )
        await db.commit()
        return correct

async def update_streak(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT last_lesson_date, streak FROM users WHERE id=?", (user_id,))
        row = await cur.fetchone()
        await cur.close()
        today = datetime.now(timezone.utc).date()
        new_streak = 1
        if row and row["last_lesson_date"]:
            prev = datetime.fromisoformat(row["last_lesson_date"]).date()
            if (today - prev).days == 1:
                new_streak = int(row["streak"] or 0) + 1
            elif (today - prev).days == 0:
                new_streak = int(row["streak"] or 0)
            else:
                new_streak = 1
        await db.execute("UPDATE users SET streak=? WHERE id=?", (new_streak, user_id))
        await db.commit()
        return new_streak

