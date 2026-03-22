"""
Ashby ATS extractor.

Ashby job boards typically have URLs like:
- jobs.ashbyhq.com/{company}
- {company}.ashbyhq.com

HTML structure patterns:
- Job postings often loaded dynamically (may need Playwright)
- JSON data embedded in script tags
- React-based rendering
"""

import json
import re
from typing import Optional, Any
from selectolax.parser import HTMLParser

from jobscraper.extractors.base import BaseExtractor
from jobscraper.schemas import JobPostingIn
from jobscraper.utils.urls import extract_job_id_from_url


class AshbyExtractor(BaseExtractor):
    """Extractor for Ashby ATS job boards."""

    name = "ashby"
    source_type = "ashby"

    def can_handle(self, url: str, html: str) -> bool:
        """Check if URL is an Ashby careers page."""
        url_lower = url.lower()

        # URL patterns
        if "ashbyhq.com" in url_lower or "ashby" in url_lower:
            return True

        # HTML patterns - Ashby-specific
        if "ashby" in html.lower():
            if "__NEXT_DATA__" in html or "ashby-job" in html:
                return True

        return False

    def extract_job_list(
        self,
        company_name: str,
        source_url: str,
        html: str,
    ) -> list[JobPostingIn]:
        """
        Extract job listings from Ashby careers page.

        Ashby often embeds job data as JSON in __NEXT_DATA__ or similar.
        Falls back to HTML parsing if JSON not found.
        """
        jobs: list[JobPostingIn] = []

        # Try to extract from embedded JSON first
        json_jobs = self._extract_from_json(html, company_name, source_url)
        if json_jobs:
            return json_jobs

        # Fall back to HTML parsing
        parser = HTMLParser(html)

        # Pattern 1: Job cards/list items
        job_elements = parser.css(
            '[data-testid*="job"], .job-posting, .ashby-job-posting, '
            '[class*="JobPosting"], [class*="job-card"], article[class*="job"]'
        )

        if job_elements:
            for element in job_elements:
                job = self._parse_job_element(element, company_name, source_url)
                if job:
                    jobs.append(job)

        # Pattern 2: Simple links to job pages
        if not jobs:
            links = parser.css('a[href*="/jobs/"], a[href*="/job/"], a[href*="ashby"]')
            seen_urls = set()

            for link in links:
                href = link.attributes.get("href", "")
                if not href or href in seen_urls:
                    continue
                if "/apply" in href:
                    continue

                seen_urls.add(href)
                title = self._clean_text(link.text())
                if not title or len(title) < 3:
                    continue

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

        return jobs

    def _extract_from_json(
        self,
        html: str,
        company_name: str,
        source_url: str,
    ) -> list[JobPostingIn]:
        """Try to extract job data from embedded JSON."""
        jobs: list[JobPostingIn] = []

        # Look for __NEXT_DATA__ (Next.js)
        next_data_match = re.search(
            r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.+?)</script>',
            html,
            re.DOTALL,
        )

        if next_data_match:
            try:
                data = json.loads(next_data_match.group(1))
                jobs = self._parse_next_data(data, company_name, source_url)
                if jobs:
                    return jobs
            except json.JSONDecodeError:
                pass

        # Look for other embedded JSON patterns
        json_match = re.search(
            r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
            html,
            re.DOTALL,
        )

        if json_match:
            try:
                data = json.loads(json_match.group(1))
                jobs = self._parse_initial_state(data, company_name, source_url)
            except json.JSONDecodeError:
                pass

        return jobs

    def _parse_next_data(
        self,
        data: dict,
        company_name: str,
        source_url: str,
    ) -> list[JobPostingIn]:
        """Parse Next.js __NEXT_DATA__ structure."""
        jobs: list[JobPostingIn] = []

        # Navigate common paths where jobs might be
        props = data.get("props", {})
        page_props = props.get("pageProps", {})

        # Try different possible locations for job data
        job_data = (
            page_props.get("jobs", [])
            or page_props.get("jobPostings", [])
            or page_props.get("openings", [])
            or self._find_jobs_in_dict(page_props)
        )

        if isinstance(job_data, list):
            for item in job_data:
                job = self._parse_job_dict(item, company_name, source_url)
                if job:
                    jobs.append(job)

        return jobs

    def _parse_initial_state(
        self,
        data: dict,
        company_name: str,
        source_url: str,
    ) -> list[JobPostingIn]:
        """Parse __INITIAL_STATE__ structure."""
        jobs: list[JobPostingIn] = []
        job_data = self._find_jobs_in_dict(data)

        if isinstance(job_data, list):
            for item in job_data:
                job = self._parse_job_dict(item, company_name, source_url)
                if job:
                    jobs.append(job)

        return jobs

    def _find_jobs_in_dict(self, data: Any, depth: int = 0) -> list:
        """Recursively find job arrays in nested dict."""
        if depth > 5:  # Limit recursion
            return []

        if isinstance(data, list) and len(data) > 0:
            # Check if this looks like a job list
            if isinstance(data[0], dict):
                first = data[0]
                if any(key in first for key in ["title", "name", "jobTitle", "position"]):
                    return data

        if isinstance(data, dict):
            for key, value in data.items():
                if key.lower() in ["jobs", "jobpostings", "openings", "positions"]:
                    if isinstance(value, list):
                        return value

                result = self._find_jobs_in_dict(value, depth + 1)
                if result:
                    return result

        return []

    def _parse_job_dict(
        self,
        item: dict,
        company_name: str,
        source_url: str,
    ) -> Optional[JobPostingIn]:
        """Parse a job dict from JSON data."""
        if not isinstance(item, dict):
            return None

        # Get title
        title = (
            item.get("title")
            or item.get("name")
            or item.get("jobTitle")
            or item.get("position")
        )
        if not title:
            return None

        # Get URL
        job_url = item.get("url") or item.get("link") or item.get("applyUrl")
        if job_url:
            job_url = self._make_absolute_url(source_url, job_url)
        else:
            # Try to construct URL from ID
            job_id = item.get("id") or item.get("jobId")
            if job_id:
                job_url = f"{source_url.rstrip('/')}/jobs/{job_id}"

        external_id = (
            item.get("id")
            or item.get("jobId")
            or item.get("externalId")
            or extract_job_id_from_url(job_url or "")
        )

        # Get other fields
        department = item.get("department") or item.get("team") or item.get("departmentName")
        location = item.get("location") or item.get("locationName") or item.get("office")

        if isinstance(location, dict):
            location = location.get("name") or location.get("city")

        return JobPostingIn(
            source_name=company_name,
            source_type=self.source_type,
            source_url=source_url,
            canonical_job_url=job_url,
            company_name=company_name,
            external_job_id=str(external_id) if external_id else None,
            job_title=title,
            department=department,
            location_text=location,
        )

    def _parse_job_element(
        self,
        node,
        company_name: str,
        source_url: str,
    ) -> Optional[JobPostingIn]:
        """Parse a job element from HTML."""
        # Find link
        link = node.css_first("a[href]")
        if not link:
            return None

        href = link.attributes.get("href", "")
        if not href:
            return None

        # Get title
        title_el = node.css_first("h2, h3, h4, [class*='title'], [class*='name']")
        title = self._clean_text(title_el.text()) if title_el else self._clean_text(link.text())
        if not title:
            return None

        job_url = self._make_absolute_url(source_url, href)
        external_id = extract_job_id_from_url(job_url)

        # Get location
        location_el = node.css_first("[class*='location'], [class*='Location']")
        location = self._clean_text(location_el.text()) if location_el else None

        # Get department
        dept_el = node.css_first("[class*='department'], [class*='team']")
        department = self._clean_text(dept_el.text()) if dept_el else None

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

    def extract_job_details(
        self,
        job: JobPostingIn,
        html: str,
    ) -> JobPostingIn:
        """Extract full details from an Ashby job detail page."""
        parser = HTMLParser(html)

        # Get full description
        content = parser.css_first(
            ".job-description, [class*='description'], article, main, #content"
        )
        if content:
            job.full_description_text = self._clean_text(content.text())

        return job
