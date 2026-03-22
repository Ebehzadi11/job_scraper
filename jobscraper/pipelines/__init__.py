"""
Scraping pipelines.

Pipelines orchestrate the scraping process:
- Discover sources from configuration
- Scrape individual companies
- Scrape all configured companies
"""

from jobscraper.pipelines.discover import load_sources, get_enabled_sources
from jobscraper.pipelines.scrape_company import scrape_company, ScrapeResult
from jobscraper.pipelines.scrape_all import scrape_all

__all__ = [
    "load_sources",
    "get_enabled_sources",
    "scrape_company",
    "ScrapeResult",
    "scrape_all",
]
