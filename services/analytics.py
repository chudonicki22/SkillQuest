import json
import os
from datetime import datetime, timezone

LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "events.log")

async def log_event(user_id: int, event: str, value: str = ""):
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "event": event,
        "value": value,
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
