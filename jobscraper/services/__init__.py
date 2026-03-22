"""
Services for data processing and persistence.

Services handle:
- Raw HTML storage
- Data normalization
- Deduplication
- Database persistence
"""

from jobscraper.services.raw_storage import save_raw_html, get_raw_html_path
from jobscraper.services.normalization import normalize_job_posting
from jobscraper.services.dedupe import compute_dedupe_key, is_duplicate
from jobscraper.services.persistence import upsert_job_posting, get_job_by_url

__all__ = [
    "save_raw_html",
    "get_raw_html_path",
    "normalize_job_posting",
    "compute_dedupe_key",
    "is_duplicate",
    "upsert_job_posting",
    "get_job_by_url",
]
