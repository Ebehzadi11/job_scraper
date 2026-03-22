"""
Hashing utilities for content deduplication and change detection.
"""

import hashlib
import re


def compute_content_hash(content: str) -> str:
    """
    Compute a stable hash of content for change detection.

    Normalizes content before hashing:
    - Strips whitespace
    - Normalizes line endings
    - Lowercases

    Args:
        content: The content to hash

    Returns:
        SHA-256 hash as hex string
    """
    if not content:
        return ""

    # Normalize content
    normalized = content.strip().lower()
    normalized = re.sub(r"\s+", " ", normalized)  # Collapse whitespace
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")

    # Compute hash
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def compute_url_hash(url: str) -> str:
    """
    Compute a hash of a URL for use as an identifier.

    Args:
        url: The URL to hash

    Returns:
        SHA-256 hash as hex string (first 16 chars for brevity)
    """
    if not url:
        return ""

    normalized = url.strip().lower()
    full_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return full_hash[:16]


def compute_job_dedupe_key(
    source_type: str,
    company_name: str,
    job_title: str,
    location: str | None = None,
) -> str:
    """
    Compute a deduplication key for a job posting.

    Used when canonical URL is not available.

    Args:
        source_type: ATS type (greenhouse, lever, etc.)
        company_name: Company name
        job_title: Job title
        location: Optional location

    Returns:
        SHA-256 hash as hex string
    """
    parts = [
        source_type.lower().strip(),
        company_name.lower().strip(),
        job_title.lower().strip(),
    ]

    if location:
        parts.append(location.lower().strip())

    combined = "|".join(parts)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def compute_file_hash(filepath: str) -> str:
    """
    Compute SHA-256 hash of a file.

    Args:
        filepath: Path to the file

    Returns:
        SHA-256 hash as hex string
    """
    sha256 = hashlib.sha256()

    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()
