"""
Collectors for fetching HTML content.

Collectors are responsible for retrieving raw HTML from URLs.
They handle retries, timeouts, and browser automation when needed.
"""

from jobscraper.collectors.base import BaseCollector, CollectorResult
from jobscraper.collectors.http_collector import HTTPCollector
from jobscraper.collectors.playwright_collector import PlaywrightCollector

__all__ = [
    "BaseCollector",
    "CollectorResult",
    "HTTPCollector",
    "PlaywrightCollector",
]
