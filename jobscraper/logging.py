"""
Logging configuration and utilities.

Provides structured logging with prefixes matching the UI expectations.
"""

import sys
from datetime import datetime, timezone
from typing import Literal

from rich.console import Console
from rich.text import Text

from jobscraper.config import settings

# Console for rich output
console = Console()

# Log level type
LogLevel = Literal["INFO", "WARN", "ERROR", "SUCCESS"]

# Log prefix type
LogPrefix = Literal[
    "[FETCH]",
    "[EXTRACT]",
    "[PERSIST]",
    "[DEDUPE]",
    "[INIT]",
    "[CONFIG]",
    "[RETRY]",
    "[PARSE]",
    "[NORMALIZE]",
]

# Color mapping for log levels
LEVEL_COLORS = {
    "INFO": "blue",
    "WARN": "yellow",
    "ERROR": "red",
    "SUCCESS": "green",
}

# Color mapping for prefixes
PREFIX_COLORS = {
    "[FETCH]": "cyan",
    "[EXTRACT]": "magenta",
    "[PERSIST]": "green",
    "[DEDUPE]": "yellow",
    "[INIT]": "blue",
    "[CONFIG]": "dim",
    "[RETRY]": "yellow",
    "[PARSE]": "magenta",
    "[NORMALIZE]": "cyan",
}


class ScrapeLogger:
    """Structured logger for scrape operations."""

    def __init__(self, company: str | None = None):
        self.company = company
        self.logs: list[dict] = []

    def _log(
        self,
        level: LogLevel,
        prefix: LogPrefix,
        message: str,
        company: str | None = None,
    ) -> dict:
        """Internal logging method."""
        timestamp = datetime.now(timezone.utc).isoformat()
        effective_company = company or self.company

        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "prefix": prefix,
            "message": message,
            "company": effective_company,
        }

        self.logs.append(log_entry)
        self._print_log(log_entry)

        return log_entry

    def _print_log(self, entry: dict) -> None:
        """Print log entry to console with colors."""
        ts = datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

        text = Text()
        text.append(f"{ts} ", style="dim")
        text.append(entry["level"].ljust(7), style=LEVEL_COLORS.get(entry["level"], "white"))
        text.append(entry["prefix"].ljust(12), style=PREFIX_COLORS.get(entry["prefix"], "white"))

        if entry.get("company"):
            text.append(f"[{entry['company']}] ", style="bold")

        text.append(entry["message"])

        console.print(text)

    def info(self, prefix: LogPrefix, message: str, company: str | None = None) -> dict:
        """Log an info message."""
        return self._log("INFO", prefix, message, company)

    def warn(self, prefix: LogPrefix, message: str, company: str | None = None) -> dict:
        """Log a warning message."""
        return self._log("WARN", prefix, message, company)

    def error(self, prefix: LogPrefix, message: str, company: str | None = None) -> dict:
        """Log an error message."""
        return self._log("ERROR", prefix, message, company)

    def success(self, prefix: LogPrefix, message: str, company: str | None = None) -> dict:
        """Log a success message."""
        return self._log("SUCCESS", prefix, message, company)

    def get_logs(self) -> list[dict]:
        """Return all logged entries."""
        return self.logs.copy()

    def clear(self) -> None:
        """Clear the log buffer."""
        self.logs.clear()


# Global logger instance
logger = ScrapeLogger()


def get_logger(company: str | None = None) -> ScrapeLogger:
    """Get a logger instance, optionally scoped to a company."""
    if company:
        return ScrapeLogger(company=company)
    return logger
