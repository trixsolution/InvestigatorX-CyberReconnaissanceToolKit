"""
utils/logger.py
Session-based logging with timestamps and level tagging.
"""

import os
import logging
from datetime import datetime


LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")


def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def get_session_log_path() -> str:
    ensure_log_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(LOG_DIR, f"session_{ts}.log")


class SessionLogger:
    """Writes scan events to a per-session log file."""

    def __init__(self):
        ensure_log_dir()
        self.log_path = get_session_log_path()
        self._entries: list[str] = []

        logging.basicConfig(
            filename=self.log_path,
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self._logger = logging.getLogger("investigator_x")

    def info(self, msg: str):
        self._logger.info(msg)
        self._entries.append(f"[INFO] {self._ts()} {msg}")

    def warning(self, msg: str):
        self._logger.warning(msg)
        self._entries.append(f"[WARN] {self._ts()} {msg}")

    def error(self, msg: str):
        self._logger.error(msg)
        self._entries.append(f"[ERR ] {self._ts()} {msg}")

    def debug(self, msg: str):
        self._logger.debug(msg)

    def get_entries(self) -> list[str]:
        return list(self._entries)

    def get_log_path(self) -> str:
        return self.log_path

    @staticmethod
    def _ts() -> str:
        return datetime.now().strftime("%H:%M:%S")


# Global session logger instance
session_logger = SessionLogger()
