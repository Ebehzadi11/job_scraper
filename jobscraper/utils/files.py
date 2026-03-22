"""
File system utilities.
"""

import re
from datetime import datetime
from pathlib import Path


def safe_filename(name: str, max_length: int = 100) -> str:
    """
    Convert a string to a safe filename.

    - Replaces unsafe characters with underscores
    - Truncates to max_length
    - Ensures no leading/trailing dots or spaces
    """
    if not name:
        return "unnamed"

    # Replace unsafe characters
    safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)

    # Replace spaces with underscores
    safe = re.sub(r"\s+", "_", safe)

    # Remove leading/trailing dots and spaces
    safe = safe.strip(". ")

    # Collapse multiple underscores
    safe = re.sub(r"_+", "_", safe)

    # Truncate
    if len(safe) > max_length:
        safe = safe[:max_length].rstrip("_")

    return safe or "unnamed"


def ensure_directory(path: Path | str) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def generate_timestamped_filename(
    prefix: str,
    extension: str,
    timestamp: datetime | None = None,
) -> str:
    """
    Generate a filename with a timestamp.

    Args:
        prefix: Filename prefix
        extension: File extension (without dot)
        timestamp: Optional timestamp (defaults to now)

    Returns:
        Filename string like "prefix_20240115_143200.ext"
    """
    ts = timestamp or datetime.now()
    ts_str = ts.strftime("%Y%m%d_%H%M%S")
    safe_prefix = safe_filename(prefix)
    return f"{safe_prefix}_{ts_str}.{extension.lstrip('.')}"


def read_file_if_exists(path: Path | str) -> str | None:
    """
    Read a file if it exists, returning None if it doesn't.
    """
    path = Path(path)
    if path.exists() and path.is_file():
        return path.read_text(encoding="utf-8")
    return None


def get_file_size_kb(path: Path | str) -> float:
    """Get file size in kilobytes."""
    path = Path(path)
    if path.exists():
        return path.stat().st_size / 1024
    return 0.0
