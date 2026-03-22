"""
Extractor registry for routing URLs to appropriate extractors.

Provides a central place to register extractors and resolve
the best extractor for a given URL/HTML combination.
"""

from typing import Optional

from jobscraper.extractors.base import BaseExtractor
from jobscraper.extractors.greenhouse import GreenhouseExtractor
from jobscraper.extractors.lever import LeverExtractor
from jobscraper.extractors.ashby import AshbyExtractor
from jobscraper.extractors.generic_careers import GenericCareersExtractor


class ExtractorRegistry:
    """
    Registry for managing and selecting extractors.

    Extractors are tried in priority order based on their specificity.
    More specific extractors (Greenhouse, Lever, Ashby) are tried before
    the generic fallback extractor.
    """

    def __init__(self):
        self._extractors: list[BaseExtractor] = []
        self._fallback: Optional[BaseExtractor] = None

        # Register default extractors
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register the default set of extractors."""
        # Specific ATS extractors (highest priority)
        self.register(GreenhouseExtractor())
        self.register(LeverExtractor())
        self.register(AshbyExtractor())

        # Generic fallback (lowest priority)
        self._fallback = GenericCareersExtractor()

    def register(self, extractor: BaseExtractor) -> None:
        """
        Register an extractor.

        Args:
            extractor: The extractor instance to register
        """
        self._extractors.append(extractor)

    def resolve(self, url: str, html: str) -> BaseExtractor:
        """
        Resolve the best extractor for a URL/HTML combination.

        Tries each registered extractor in order, returning the first
        one that can handle the content. Falls back to generic extractor.

        Args:
            url: The URL of the page
            html: The HTML content

        Returns:
            The best matching extractor
        """
        for extractor in self._extractors:
            if extractor.can_handle(url, html):
                return extractor

        # Return fallback (generic) extractor
        if self._fallback:
            return self._fallback

        # This shouldn't happen, but just in case
        return GenericCareersExtractor()

    def resolve_by_source_type(self, source_type: str) -> BaseExtractor:
        """
        Get an extractor by source type name.

        Args:
            source_type: The source type (greenhouse, lever, ashby, generic)

        Returns:
            The matching extractor
        """
        source_type_lower = source_type.lower()

        for extractor in self._extractors:
            if extractor.source_type == source_type_lower:
                return extractor

        if self._fallback and self._fallback.source_type == source_type_lower:
            return self._fallback

        return self._fallback or GenericCareersExtractor()

    def list_extractors(self) -> list[str]:
        """List all registered extractor names."""
        names = [e.name for e in self._extractors]
        if self._fallback:
            names.append(self._fallback.name)
        return names


# Global registry instance
_registry: Optional[ExtractorRegistry] = None


def get_registry() -> ExtractorRegistry:
    """Get the global extractor registry."""
    global _registry
    if _registry is None:
        _registry = ExtractorRegistry()
    return _registry


def resolve_extractor(url: str, html: str) -> BaseExtractor:
    """
    Convenience function to resolve an extractor.

    Args:
        url: The URL of the page
        html: The HTML content

    Returns:
        The best matching extractor
    """
    return get_registry().resolve(url, html)


def resolve_extractor_by_type(source_type: str) -> BaseExtractor:
    """
    Convenience function to get extractor by source type.

    Args:
        source_type: The source type name

    Returns:
        The matching extractor
    """
    return get_registry().resolve_by_source_type(source_type)
