"""Small fake logging helper for terminal-style UI panels."""

from datetime import datetime
from typing import Dict, List


class SystemLogger:
    def __init__(self, limit: int = 50) -> None:
        self.limit = max(10, min(limit, 200))
        self._entries: List[Dict[str, str]] = []

    def push(self, message: str, severity: str = "INFO", source: str = "io_scheduler") -> Dict[str, str]:
        try:
            entry = {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "severity": severity.upper(),
                "source": source,
                "message": message,
            }
            self._entries.append(entry)
            self._entries = self._entries[-self.limit :]
            return entry
        except Exception:
            return {"timestamp": "--:--:--", "severity": "INFO", "source": "system", "message": "log unavailable"}

    def bootstrap(self) -> List[Dict[str, str]]:
        try:
            if not self._entries:
                self.push("device bus synchronized")
                self.push("queue controller armed")
                self.push("scheduler telemetry online", source="kernel")
            return list(self._entries)
        except Exception:
            return []

    def entries(self) -> List[Dict[str, str]]:
        try:
            return list(self._entries)
        except Exception:
            return []
