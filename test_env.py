import os
from dotenv import load_dotenv

print("👀 Тест .env — начало")

env_loaded = load_dotenv()
print("✅ load_dotenv():", env_loaded)

print("📂 Текущая директория:", os.getcwd())
print("📄 Файлы:", os.listdir())

token = os.getenv("BOT_TOKEN")
print("🔍 BOT_TOKEN:", token if token else "❌ Не найден!")

print("✅ Тест завершён.")
