"""
Base extractor interface.
"""

from abc import ABC, abstractmethod
from typing import Optional

from jobscraper.schemas import JobPostingIn


class BaseExtractor(ABC):
    """
    Abstract base class for job listing extractors.

    Extractors parse HTML from career pages and extract structured job data.
    Each ATS platform has its own extractor implementation.
    """

    # Extractor identifier
    name: str = "base"

    # Source type for this extractor
    source_type: str = "generic"

    @abstractmethod
    def can_handle(self, url: str, html: str) -> bool:
        """
        Check if this extractor can handle the given URL/HTML.

        Args:
            url: The URL of the page
            html: The HTML content

        Returns:
            True if this extractor can parse the content
        """
        pass

    @abstractmethod
    def extract_job_list(
        self,
        company_name: str,
        source_url: str,
        html: str,
    ) -> list[JobPostingIn]:
        """
        Extract job listings from a careers page.

        This extracts basic job information from the listing page.
        For full details, use extract_job_details on individual job pages.

        Args:
            company_name: Name of the company
            source_url: URL of the careers page
            html: HTML content of the page

        Returns:
            List of JobPostingIn objects with basic information
        """
        pass

    def extract_job_details(
        self,
        job: JobPostingIn,
        html: str,
    ) -> JobPostingIn:
        """
        Extract full details from a job detail page.

        Override this method to parse individual job pages.
        Default implementation returns the job unchanged.

        Args:
            job: JobPostingIn with basic info from listing
            html: HTML content of the job detail page

        Returns:
            JobPostingIn with additional details filled in
        """
        return job

    def _make_absolute_url(self, base_url: str, relative_url: str) -> str:
        """Helper to make URLs absolute."""
        from jobscraper.utils.urls import make_absolute_url
        return make_absolute_url(base_url, relative_url)

    def _clean_text(self, text: Optional[str]) -> Optional[str]:
        """Helper to clean text content."""
        if not text:
            return None
        from jobscraper.utils.text import clean_text
        return clean_text(text)
