"""
Base collector interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class CollectorResult:
    """Result from a collector fetch operation."""

    html: str
    url: str
    final_url: str  # After redirects
    status_code: int
    content_length: int
    elapsed_ms: int
    success: bool
    error: Optional[str] = None

    @property
    def size_kb(self) -> float:
        """Content size in kilobytes."""
        return self.content_length / 1024


class BaseCollector(ABC):
    """
    Abstract base class for HTML collectors.

    Collectors are responsible for fetching HTML content from URLs.
    Different implementations handle different scenarios (simple HTTP vs browser).
    """

    @abstractmethod
    async def fetch(self, url: str) -> CollectorResult:
        """
        Fetch HTML content from a URL.

        Args:
            url: The URL to fetch

        Returns:
            CollectorResult with HTML content and metadata
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Clean up resources."""
        pass

    async def __aenter__(self):
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()
