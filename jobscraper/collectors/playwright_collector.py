"""
Playwright-based collector for JavaScript-rendered pages.

For pages that require a full browser environment.
"""

import time
from typing import Optional

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from jobscraper.collectors.base import BaseCollector, CollectorResult
from jobscraper.config import settings


class PlaywrightCollector(BaseCollector):
    """
    Collector that uses Playwright for browser-based scraping.

    Best for:
    - JavaScript-rendered pages
    - Single Page Applications (SPAs)
    - Pages requiring interaction
    - Pages with dynamic content loading
    """

    def __init__(
        self,
        headless: Optional[bool] = None,
        timeout_seconds: Optional[int] = None,
        wait_for_selector: Optional[str] = None,
        wait_for_load_state: str = "networkidle",
    ):
        self.headless = headless if headless is not None else settings.playwright_headless
        self.timeout = (timeout_seconds or settings.request_timeout_seconds) * 1000  # ms
        self.wait_for_selector = wait_for_selector
        self.wait_for_load_state = wait_for_load_state

        self._playwright = None
        self._browser = None

    async def _ensure_browser(self):
        """Ensure browser is initialized."""
        if self._browser is None:
            from playwright.async_api import async_playwright

            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless,
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _fetch_with_retry(
        self,
        url: str,
    ) -> tuple[str, str, int]:
        """
        Fetch URL with retries.

        Returns:
            Tuple of (html, final_url, status_code)
        """
        await self._ensure_browser()

        context = await self._browser.new_context(
            user_agent=settings.user_agent,
            viewport={"width": 1920, "height": 1080},
        )

        try:
            page = await context.new_page()

            # Navigate to URL
            response = await page.goto(
                url,
                timeout=self.timeout,
                wait_until="domcontentloaded",
            )

            # Wait for network to settle
            try:
                await page.wait_for_load_state(
                    self.wait_for_load_state,
                    timeout=self.timeout,
                )
            except Exception:
                # Continue even if networkidle times out
                pass

            # Wait for specific selector if provided
            if self.wait_for_selector:
                try:
                    await page.wait_for_selector(
                        self.wait_for_selector,
                        timeout=self.timeout // 2,
                    )
                except Exception:
                    # Continue even if selector not found
                    pass

            # Get final URL after redirects
            final_url = page.url

            # Get page HTML
            html = await page.content()

            # Get status code
            status_code = response.status if response else 200

            return html, final_url, status_code

        finally:
            await context.close()

    async def fetch(self, url: str) -> CollectorResult:
        """
        Fetch HTML content from a URL using Playwright.

        Args:
            url: The URL to fetch

        Returns:
            CollectorResult with HTML content and metadata
        """
        start_time = time.perf_counter()

        try:
            html, final_url, status_code = await self._fetch_with_retry(url)
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)

            content_length = len(html.encode("utf-8"))

            return CollectorResult(
                html=html,
                url=url,
                final_url=final_url,
                status_code=status_code,
                content_length=content_length,
                elapsed_ms=elapsed_ms,
                success=200 <= status_code < 400,
                error=None,
            )

        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)

            # Check for timeout
            error_str = str(e).lower()
            if "timeout" in error_str:
                error_msg = f"Timeout after {self.timeout // 1000}s"
            else:
                error_msg = f"Browser error: {str(e)}"

            return CollectorResult(
                html="",
                url=url,
                final_url=url,
                status_code=0,
                content_length=0,
                elapsed_ms=elapsed_ms,
                success=False,
                error=error_msg,
            )

    async def close(self) -> None:
        """Close browser and playwright."""
        if self._browser is not None:
            await self._browser.close()
            self._browser = None

        if self._playwright is not None:
            await self._playwright.stop()
            self._playwright = None
