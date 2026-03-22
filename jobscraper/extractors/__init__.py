"""
Extractors for parsing job listings from HTML.

Each extractor knows how to parse a specific ATS platform's HTML structure.
"""

from jobscraper.extractors.base import BaseExtractor
from jobscraper.extractors.greenhouse import GreenhouseExtractor
from jobscraper.extractors.lever import LeverExtractor
from jobscraper.extractors.ashby import AshbyExtractor
from jobscraper.extractors.generic_careers import GenericCareersExtractor

__all__ = [
    "BaseExtractor",
    "GreenhouseExtractor",
    "LeverExtractor",
    "AshbyExtractor",
    "GenericCareersExtractor",
]
