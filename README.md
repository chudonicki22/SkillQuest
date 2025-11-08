# SkillQuest — образовательный Telegram-бот (micro-learning 5 минут в день)

**MVP**: ежедневные мини-уроки (3–5 вопросов), очки и streak, лидерборд и рефералка.

## Команды
- `/start` — онбординг и выбор темы
- `/lesson` — пройти урок дня
- `/profile` — профиль, очки и streak
- `/leaderboard` — топ-10 за 7 дней
- `/referral` — получить реферальную ссылку/код

## Быстрый старт (локально)
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # и вставьте токен бота в .env
python main.py
```

Проверьте команды: `/start`, `/lesson`, `/profile`, `/leaderboard`, `/referral`.

### Примечания
- БД: SQLite (`skillquest.sqlite`) создаётся автоматически при первом запуске или командой `python data/db.py --init`.
- Уроки подхватываются из `data/lessons.json`. Если файл отсутствует — берётся `examples/sample_lessons.json`.
- Напоминания реализованы простым планировщиком, который раз в минуту проверяет время (настройка `REMINDER_UTC_HOUR` в `.env`). Для MVP можно не запускать длительно — функционал будет работать при долгой сессии бота.
