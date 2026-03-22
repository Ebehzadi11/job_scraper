"""
Raw HTML storage service.

Saves raw HTML snapshots for debugging and reprocessing.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from jobscraper.config import settings
from jobscraper.utils.files import safe_filename, ensure_directory
from jobscraper.utils.hashing import compute_url_hash


def get_raw_html_path(
    company_name: str,
    url: str,
    timestamp: Optional[datetime] = None,
) -> Path:
    """
    Generate a deterministic path for raw HTML storage.

    Structure: {raw_html_dir}/{company}/{url_hash}_{timestamp}.html

    Args:
        company_name: Company name
        url: Source URL
        timestamp: Optional timestamp (defaults to now)

    Returns:
        Path object for the HTML file
    """
    ts = timestamp or datetime.now()
    ts_str = ts.strftime("%Y%m%d_%H%M%S")

    # Create safe directory name from company
    company_dir = safe_filename(company_name.lower())

    # Create filename from URL hash and timestamp
    url_hash = compute_url_hash(url)
    filename = f"{url_hash}_{ts_str}.html"

    return settings.raw_html_dir / company_dir / filename


def save_raw_html(
    html: str,
    company_name: str,
    url: str,
    timestamp: Optional[datetime] = None,
) -> Path:
    """
    Save raw HTML to disk.

    Args:
        html: HTML content to save
        company_name: Company name
        url: Source URL
        timestamp: Optional timestamp

    Returns:
        Path where HTML was saved
    """
    filepath = get_raw_html_path(company_name, url, timestamp)

    # Ensure directory exists
    ensure_directory(filepath.parent)

    # Write HTML
    filepath.write_text(html, encoding="utf-8")

    return filepath


def load_raw_html(filepath: Path) -> Optional[str]:
    """
    Load raw HTML from disk.

    Args:
        filepath: Path to HTML file

    Returns:
        HTML content or None if file doesn't exist
    """
    if filepath.exists():
        return filepath.read_text(encoding="utf-8")
    return None


def list_raw_html_files(
    company_name: Optional[str] = None,
    limit: int = 100,
) -> list[Path]:
    """
    List stored raw HTML files.

    Args:
        company_name: Optional filter by company
        limit: Maximum files to return

    Returns:
        List of file paths, newest first
    """
    if company_name:
        search_dir = settings.raw_html_dir / safe_filename(company_name.lower())
    else:
        search_dir = settings.raw_html_dir

    if not search_dir.exists():
        return []

    # Get all HTML files
    files = list(search_dir.rglob("*.html"))

    # Sort by modification time, newest first
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    return files[:limit]


def cleanup_old_html(
    company_name: Optional[str] = None,
    keep_count: int = 10,
) -> int:
    """
    Clean up old HTML files, keeping only the most recent.

    Args:
        company_name: Optional filter by company
        keep_count: Number of files to keep per company

    Returns:
        Number of files deleted
    """
    deleted = 0

    if company_name:
        companies = [safe_filename(company_name.lower())]
    else:
        if not settings.raw_html_dir.exists():
            return 0
        companies = [d.name for d in settings.raw_html_dir.iterdir() if d.is_dir()]

    for company in companies:
        company_dir = settings.raw_html_dir / company
        if not company_dir.exists():
            continue

        files = list(company_dir.glob("*.html"))
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        # Delete files beyond keep_count
        for f in files[keep_count:]:
            f.unlink()
            deleted += 1

    return deleted
