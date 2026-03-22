"""
Generic careers page extractor.

Fallback extractor for company career pages that don't use a known ATS.
Uses heuristics to find job listings.
"""

from typing import Optional
from selectolax.parser import HTMLParser

from jobscraper.extractors.base import BaseExtractor
from jobscraper.schemas import JobPostingIn
from jobscraper.utils.urls import extract_job_id_from_url


class GenericCareersExtractor(BaseExtractor):
    """
    Generic extractor for career pages without a specific ATS.

    Uses heuristics to identify job listings based on common patterns.
    Less reliable than ATS-specific extractors but provides broad coverage.
    """

    name = "generic"
    source_type = "generic"

    # Common selectors for job listings
    JOB_SELECTORS = [
        ".job-listing",
        ".job-card",
        ".job-item",
        ".job-post",
        ".career-item",
        ".position-item",
        ".opening",
        "article.job",
        "li.job",
        "div[class*='job']",
        "div[class*='career']",
        "div[class*='position']",
        "div[class*='opening']",
        "tr.job",
        "tr[class*='position']",
    ]

    # Common selectors for job links
    LINK_SELECTORS = [
        'a[href*="job"]',
        'a[href*="career"]',
        'a[href*="position"]',
        'a[href*="opening"]',
        'a[href*="apply"]',
    ]

    def can_handle(self, url: str, html: str) -> bool:
        """
        Generic extractor can handle any URL.

        This should be used as a fallback when no specific extractor matches.
        """
        # Check if this looks like a careers page
        url_lower = url.lower()
        html_lower = html.lower()

        careers_indicators = [
            "career" in url_lower,
            "jobs" in url_lower,
            "careers" in html_lower,
            "job openings" in html_lower,
            "open positions" in html_lower,
            "join our team" in html_lower,
            "we're hiring" in html_lower,
        ]

        return any(careers_indicators)

    def extract_job_list(
        self,
        company_name: str,
        source_url: str,
        html: str,
    ) -> list[JobPostingIn]:
        """
        Extract job listings using heuristics.

        Tries multiple strategies:
        1. Known job container selectors
        2. Links with job-related patterns
        3. Schema.org JobPosting markup
        """
        jobs: list[JobPostingIn] = []
        parser = HTMLParser(html)

        # Strategy 1: Try known job container selectors
        for selector in self.JOB_SELECTORS:
            elements = parser.css(selector)
            if elements and len(elements) >= 1:
                for element in elements:
                    job = self._parse_job_container(element, company_name, source_url)
                    if job:
                        jobs.append(job)

            if len(jobs) >= 3:
                # Found enough jobs, use this pattern
                break

        # Strategy 2: Look for job links
        if len(jobs) < 3:
            seen_urls = set()

            for selector in self.LINK_SELECTORS:
                links = parser.css(selector)

                for link in links:
                    href = link.attributes.get("href", "")
                    if not href or href in seen_urls:
                        continue
                    if href.startswith("#") or "javascript:" in href:
                        continue

                    # Filter out non-job links
                    if self._is_likely_job_link(href, link):
                        seen_urls.add(href)
                        title = self._clean_text(link.text())

                        if title and len(title) > 3:
                            job_url = self._make_absolute_url(source_url, href)
                            external_id = extract_job_id_from_url(job_url)

                            jobs.append(
                                JobPostingIn(
                                    source_name=company_name,
                                    source_type=self.source_type,
                                    source_url=source_url,
                                    canonical_job_url=job_url,
                                    company_name=company_name,
                                    external_job_id=external_id,
                                    job_title=title,
                                )
                            )

        # Strategy 3: Look for Schema.org markup
        if len(jobs) < 3:
            schema_jobs = self._extract_schema_jobs(parser, company_name, source_url)
            if schema_jobs:
                jobs.extend(schema_jobs)

        # Deduplicate by URL
        seen = set()
        unique_jobs = []
        for job in jobs:
            key = job.canonical_job_url or job.job_title
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)

        return unique_jobs

    def _parse_job_container(
        self,
        node,
        company_name: str,
        source_url: str,
    ) -> Optional[JobPostingIn]:
        """Parse a job container element."""
        # Find link
        link = node.css_first("a[href]")
        if not link:
            return None

        href = link.attributes.get("href", "")
        if not href or href.startswith("#"):
            return None

        # Get title - try multiple patterns
        title: Optional[str] = None

        # Pattern 1: Heading element
        heading = node.css_first("h1, h2, h3, h4, h5")
        if heading:
            title = self._clean_text(heading.text())

        # Pattern 2: Title class
        if not title:
            title_el = node.css_first("[class*='title'], [class*='name']")
            if title_el:
                title = self._clean_text(title_el.text())

        # Pattern 3: Link text
        if not title:
            title = self._clean_text(link.text())

        if not title or len(title) < 3:
            return None

        job_url = self._make_absolute_url(source_url, href)
        external_id = extract_job_id_from_url(job_url)

        # Try to find location
        location: Optional[str] = None
        location_el = node.css_first("[class*='location'], [class*='Location']")
        if location_el:
            location = self._clean_text(location_el.text())

        # Try to find department
        department: Optional[str] = None
        dept_el = node.css_first("[class*='department'], [class*='team'], [class*='category']")
        if dept_el:
            department = self._clean_text(dept_el.text())

        return JobPostingIn(
            source_name=company_name,
            source_type=self.source_type,
            source_url=source_url,
            canonical_job_url=job_url,
            company_name=company_name,
            external_job_id=external_id,
            job_title=title,
            department=department,
            location_text=location,
        )

    def _is_likely_job_link(self, href: str, link) -> bool:
        """Check if a link is likely to be a job link."""
        href_lower = href.lower()
        text = (link.text() or "").lower()

        # Positive indicators
        positive = [
            "/job" in href_lower,
            "/career" in href_lower,
            "/position" in href_lower,
            "/opening" in href_lower,
            "/apply" in href_lower,
            "engineer" in text,
            "manager" in text,
            "designer" in text,
            "analyst" in text,
            "developer" in text,
        ]

        # Negative indicators (navigation/utility links)
        negative = [
            "about" in href_lower,
            "contact" in href_lower,
            "privacy" in href_lower,
            "terms" in href_lower,
            "login" in href_lower,
            "sign" in href_lower,
            len(text.split()) > 15,  # Too long to be a job title
        ]

        return any(positive) and not any(negative)

    def _extract_schema_jobs(
        self,
        parser: HTMLParser,
        company_name: str,
        source_url: str,
    ) -> list[JobPostingIn]:
        """Extract jobs from Schema.org JobPosting markup."""
        import json

        jobs: list[JobPostingIn] = []

        # Look for JSON-LD
        scripts = parser.css('script[type="application/ld+json"]')

        for script in scripts:
            try:
                data = json.loads(script.text())

                # Handle single object or array
                items = [data] if isinstance(data, dict) else data

                for item in items:
                    if not isinstance(item, dict):
                        continue

                    item_type = item.get("@type", "")
                    if item_type != "JobPosting":
                        continue

                    title = item.get("title", "")
                    if not title:
                        continue

                    job_url = item.get("url") or item.get("sameAs")
                    if job_url:
                        job_url = self._make_absolute_url(source_url, job_url)

                    location = None
                    job_location = item.get("jobLocation", {})
                    if isinstance(job_location, dict):
                        address = job_location.get("address", {})
                        if isinstance(address, dict):
                            location = address.get("addressLocality")

                    jobs.append(
                        JobPostingIn(
                            source_name=company_name,
                            source_type=self.source_type,
                            source_url=source_url,
                            canonical_job_url=job_url,
                            company_name=company_name,
                            job_title=title,
                            location_text=location,
                        )
                    )

            except (json.JSONDecodeError, TypeError):
                continue

        return jobs

    def extract_job_details(
        self,
        job: JobPostingIn,
        html: str,
    ) -> JobPostingIn:
        """Extract full details from a generic job detail page."""
        parser = HTMLParser(html)

        # Try common content selectors
        content_selectors = [
            "article",
            ".job-description",
            ".job-content",
            ".job-details",
            "#job-description",
            "main",
            ".content",
        ]

        for selector in content_selectors:
            content = parser.css_first(selector)
            if content:
                text = self._clean_text(content.text())
                if text and len(text) > 100:
                    job.full_description_text = text
                    break

        return job
