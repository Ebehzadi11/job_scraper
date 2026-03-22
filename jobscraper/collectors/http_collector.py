"""
HTTP-based collector using HTTPX.

For pages that don't require JavaScript rendering.
"""

import time
from typing import Optional

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from jobscraper.collectors.base import BaseCollector, CollectorResult
from jobscraper.config import settings


class HTTPCollector(BaseCollector):
    """
    Collector that uses HTTPX for simple HTTP requests.

    Best for:
    - Static HTML pages
    - API endpoints
    - Pages that don't require JavaScript
    """

    def __init__(
        self,
        user_agent: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        follow_redirects: bool = True,
    ):
        self.user_agent = user_agent or settings.user_agent
        self.timeout = timeout_seconds or settings.request_timeout_seconds
        self.follow_redirects = follow_redirects
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers={
                    "User-Agent": self.user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                },
                timeout=httpx.Timeout(self.timeout),
                follow_redirects=self.follow_redirects,
            )
        return self._client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        reraise=True,
    )
    async def _fetch_with_retry(self, url: str) -> httpx.Response:
        """Fetch URL with retries."""
        client = await self._get_client()
        return await client.get(url)

    async def fetch(self, url: str) -> CollectorResult:
        """
        Fetch HTML content from a URL using HTTPX.

        Args:
            url: The URL to fetch

        Returns:
            CollectorResult with HTML content and metadata
        """
        start_time = time.perf_counter()

        try:
            response = await self._fetch_with_retry(url)
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)

            html = response.text
            content_length = len(html.encode("utf-8"))

            return CollectorResult(
                html=html,
                url=url,
                final_url=str(response.url),
                status_code=response.status_code,
                content_length=content_length,
                elapsed_ms=elapsed_ms,
                success=response.is_success,
                error=None if response.is_success else f"HTTP {response.status_code}",
            )

        except httpx.TimeoutException as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return CollectorResult(
                html="",
                url=url,
                final_url=url,
                status_code=0,
                content_length=0,
                elapsed_ms=elapsed_ms,
                success=False,
                error=f"Timeout: {str(e)}",
            )

        except httpx.NetworkError as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return CollectorResult(
                html="",
                url=url,
                final_url=url,
                status_code=0,
                content_length=0,
                elapsed_ms=elapsed_ms,
                success=False,
                error=f"Network error: {str(e)}",
            )

        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return CollectorResult(
                html="",
                url=url,
                final_url=url,
                status_code=0,
                content_length=0,
                elapsed_ms=elapsed_ms,
                success=False,
                error=f"Unexpected error: {str(e)}",
            )

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
