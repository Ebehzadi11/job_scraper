"""
Greenhouse ATS extractor.

Greenhouse job boards typically have URLs like:
- boards.greenhouse.io/{company}
- {company}.greenhouse.io

HTML structure patterns:
- Job listings in divs with class "opening"
- Job links with data-mapped attributes
- Department groupings
"""

from typing import Optional
from selectolax.parser import HTMLParser

from jobscraper.extractors.base import BaseExtractor
from jobscraper.schemas import JobPostingIn
from jobscraper.utils.urls import extract_job_id_from_url


class GreenhouseExtractor(BaseExtractor):
    """Extractor for Greenhouse ATS job boards."""

    name = "greenhouse"
    source_type = "greenhouse"

    def can_handle(self, url: str, html: str) -> bool:
        """Check if URL is a Greenhouse careers page."""
        url_lower = url.lower()

        # URL patterns
        if "greenhouse.io" in url_lower:
            return True

        # HTML patterns - check for Greenhouse-specific elements
        if "greenhouse" in html.lower():
            if 'id="content"' in html or "grnhse" in html.lower():
                return True

        return False

    def extract_job_list(
        self,
        company_name: str,
        source_url: str,
        html: str,
    ) -> list[JobPostingIn]:
        """
        Extract job listings from Greenhouse careers page.

        Greenhouse HTML typically has:
        - Section headers for departments
        - Job openings as divs with class "opening"
        - Links containing job URLs
        """
        jobs: list[JobPostingIn] = []
        parser = HTMLParser(html)

        # Track current department from section headers
        current_department: Optional[str] = None

        # Pattern 1: Standard Greenhouse board layout
        # Departments are in section headers, jobs are in .opening divs
        sections = parser.css("section.level-0, div.level-0, section[department_id]")

        if sections:
            for section in sections:
                # Get department from section header
                dept_header = section.css_first("h2, h3, .department-name")
                if dept_header:
                    current_department = self._clean_text(dept_header.text())

                # Get job openings in this section
                openings = section.css("div.opening, tr.opening, li.opening")
                for opening in openings:
                    job = self._parse_opening(
                        opening,
                        company_name,
                        source_url,
                        current_department,
                    )
                    if job:
                        jobs.append(job)

        # Pattern 2: Flat list of openings
        if not jobs:
            openings = parser.css("div.opening, tr.opening, li.opening")
            for opening in openings:
                # Try to find department from parent or nearby elements
                parent = opening.parent
                if parent:
                    dept_header = parent.css_first("h2, h3")
                    if dept_header:
                        current_department = self._clean_text(dept_header.text())

                job = self._parse_opening(
                    opening,
                    company_name,
                    source_url,
                    current_department,
                )
                if job:
                    jobs.append(job)

        # Pattern 3: Simple anchor links
        if not jobs:
            links = parser.css('a[href*="/jobs/"], a[href*="/job/"]')
            for link in links:
                href = link.attributes.get("href", "")
                if not href or "#" in href:
                    continue

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

    def _parse_opening(
        self,
        node,
        company_name: str,
        source_url: str,
        department: Optional[str],
    ) -> Optional[JobPostingIn]:
        """Parse a single job opening element."""
        # Find the job link
        link = node.css_first("a")
        if not link:
            return None

        href = link.attributes.get("href", "")
        if not href:
            return None

        # Get job title
        title = self._clean_text(link.text())
        if not title:
            return None

        # Build absolute URL
        job_url = self._make_absolute_url(source_url, href)

        # Extract job ID
        external_id = extract_job_id_from_url(job_url)

        # Try to find location
        location: Optional[str] = None
        location_el = node.css_first(".location, span.location, .job-location")
        if location_el:
            location = self._clean_text(location_el.text())

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
        """
        Extract full details from a Greenhouse job detail page.

        Greenhouse job pages typically have:
        - Job title in h1
        - Location in .location
        - Content in #content or .content
        """
        parser = HTMLParser(html)

        # Get full description
        content = parser.css_first("#content, .content, article, main")
        if content:
            job.full_description_text = self._clean_text(content.text())

        # Get location if not already set
        if not job.location_text:
            location_el = parser.css_first(".location, [class*='location']")
            if location_el:
                job.location_text = self._clean_text(location_el.text())

        # Get department if not already set
        if not job.department:
            dept_el = parser.css_first(".department, [class*='department']")
            if dept_el:
                job.department = self._clean_text(dept_el.text())

        return job
