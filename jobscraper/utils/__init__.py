"""
Utility modules for the job scraper.
"""

from jobscraper.utils.hashing import compute_content_hash, compute_url_hash
from jobscraper.utils.urls import normalize_url, make_absolute_url, extract_domain
from jobscraper.utils.text import clean_text, extract_text_content, truncate_text
from jobscraper.utils.files import safe_filename, ensure_directory
from jobscraper.utils.time import utc_now, format_duration_ms

__all__ = [
    "compute_content_hash",
    "compute_url_hash",
    "normalize_url",
    "make_absolute_url",
    "extract_domain",
    "clean_text",
    "extract_text_content",
    "truncate_text",
    "safe_filename",
    "ensure_directory",
    "utc_now",
    "format_duration_ms",
]
