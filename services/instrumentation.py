"""Simple instrumentation helpers for the conversational API."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .config import settings


class InteractionLogger:
    """Writes structured interaction logs to disk for auditing."""

    def __init__(self) -> None:
        self.log_dir = settings.logs_dir / "conversations"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log_event(self, session_id: str, event_type: str, payload: Dict[str, Any]) -> None:
        record = {
            "session_id": session_id,
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
        }
        logfile = self.log_dir / f"{session_id}.jsonl"
        with logfile.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(record, ensure_ascii=False) + "\n")


interaction_logger = InteractionLogger()

