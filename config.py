import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))
    REMINDER_UTC_HOUR: int = int(os.getenv("REMINDER_UTC_HOUR", "9"))

settings = Settings()
