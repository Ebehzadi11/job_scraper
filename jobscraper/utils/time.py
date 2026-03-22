"""
Time and date utilities.
"""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


def format_timestamp(dt: datetime | None) -> str:
    """Format datetime as ISO 8601 string."""
    if dt is None:
        return ""
    return dt.isoformat()


def format_duration_ms(duration_ms: int) -> str:
    """
    Format duration in milliseconds as human-readable string.

    Examples:
        150 -> "150ms"
        1500 -> "1.5s"
        65000 -> "1m 5s"
    """
    if duration_ms < 1000:
        return f"{duration_ms}ms"

    seconds = duration_ms / 1000

    if seconds < 60:
        return f"{seconds:.1f}s"

    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)

    if remaining_seconds == 0:
        return f"{minutes}m"

    return f"{minutes}m {remaining_seconds}s"


def format_relative_time(dt: datetime) -> str:
    """
    Format datetime as relative time string.

    Examples:
        "just now"
        "5 minutes ago"
        "2 hours ago"
        "yesterday"
    """
    now = utc_now()

    # Ensure both are timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    diff = now - dt
    seconds = diff.total_seconds()

    if seconds < 60:
        return "just now"

    minutes = seconds / 60
    if minutes < 60:
        mins = int(minutes)
        return f"{mins} minute{'s' if mins != 1 else ''} ago"

    hours = minutes / 60
    if hours < 24:
        hrs = int(hours)
        return f"{hrs} hour{'s' if hrs != 1 else ''} ago"

    days = hours / 24
    if days < 2:
        return "yesterday"

    if days < 7:
        d = int(days)
        return f"{d} day{'s' if d != 1 else ''} ago"

    weeks = days / 7
    if weeks < 4:
        w = int(weeks)
        return f"{w} week{'s' if w != 1 else ''} ago"

    months = days / 30
    if months < 12:
        m = int(months)
        return f"{m} month{'s' if m != 1 else ''} ago"

    years = days / 365
    y = int(years)
    return f"{y} year{'s' if y != 1 else ''} ago"


def parse_iso_timestamp(timestamp_str: str) -> datetime | None:
    """Parse an ISO 8601 timestamp string."""
    if not timestamp_str:
        return None

    try:
        # Handle various ISO formats
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return dt
    except ValueError:
        return None
