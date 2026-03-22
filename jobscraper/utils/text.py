"""
Text processing utilities.
"""

import re
import unicodedata
from html import unescape


def clean_text(text: str | None) -> str:
    """
    Clean and normalize text content.

    - Decodes HTML entities
    - Normalizes unicode
    - Collapses whitespace
    - Strips leading/trailing whitespace
    """
    if not text:
        return ""

    # Decode HTML entities
    text = unescape(text)

    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)

    # Replace various whitespace chars with space
    text = re.sub(r"[\t\r\f\v]+", " ", text)

    # Collapse multiple spaces
    text = re.sub(r" +", " ", text)

    # Normalize newlines (keep paragraph structure)
    text = re.sub(r"\n\s*\n", "\n\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_text_content(html: str) -> str:
    """
    Extract visible text content from HTML.

    Uses a simple regex-based approach. For complex HTML,
    use selectolax directly.
    """
    if not html:
        return ""

    # Remove script and style elements
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Clean up
    return clean_text(text)


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length, breaking at word boundaries.
    """
    if not text or len(text) <= max_length:
        return text or ""

    # Find the last space before max_length
    truncated = text[: max_length - len(suffix)]
    last_space = truncated.rfind(" ")

    if last_space > max_length // 2:
        truncated = truncated[:last_space]

    return truncated.rstrip() + suffix


def normalize_whitespace(text: str) -> str:
    """Normalize all whitespace to single spaces."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def extract_numbers(text: str) -> list[int]:
    """Extract all numbers from text."""
    if not text:
        return []
    return [int(n) for n in re.findall(r"\d+", text)]


def extract_years_experience(text: str) -> int | None:
    """
    Extract years of experience requirement from text.

    Patterns:
    - "5+ years"
    - "5-7 years"
    - "minimum 5 years"
    - "at least 3 years"
    """
    if not text:
        return None

    text_lower = text.lower()

    # Pattern: X+ years
    match = re.search(r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)?", text_lower)
    if match:
        return int(match.group(1))

    # Pattern: X-Y years (take lower bound)
    match = re.search(r"(\d+)\s*[-–]\s*\d+\s*(?:years?|yrs?)", text_lower)
    if match:
        return int(match.group(1))

    # Pattern: minimum/at least X years
    match = re.search(r"(?:minimum|at\s+least|min)\s*(\d+)\s*(?:years?|yrs?)", text_lower)
    if match:
        return int(match.group(1))

    return None


def split_into_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    if not text:
        return []

    # Simple sentence splitting
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]


def extract_bullet_points(text: str) -> list[str]:
    """
    Extract bullet points from text.

    Handles:
    - Lines starting with -, *, •, ▪, ▸
    - Numbered lists (1., 2., etc.)
    """
    if not text:
        return []

    lines = text.split("\n")
    bullets = []

    for line in lines:
        line = line.strip()
        # Match bullet patterns
        match = re.match(r"^[\-\*•▪▸◦○●]\s*(.+)$", line)
        if match:
            bullets.append(match.group(1).strip())
            continue

        # Match numbered patterns
        match = re.match(r"^\d+[.)]\s*(.+)$", line)
        if match:
            bullets.append(match.group(1).strip())

    return bullets
