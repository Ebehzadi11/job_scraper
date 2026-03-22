"""
Lever ATS extractor.

Lever job boards typically have URLs like:
- jobs.lever.co/{company}
- {company}.lever.co

HTML structure patterns:
- Job postings in div.posting
- Team/department groupings
- Location and work type badges
"""

from typing import Optional
from selectolax.parser import HTMLParser

from jobscraper.extractors.base import BaseExtractor
from jobscraper.schemas import JobPostingIn
from jobscraper.utils.urls import extract_job_id_from_url


class LeverExtractor(BaseExtractor):
    """Extractor for Lever ATS job boards."""

    name = "lever"
    source_type = "lever"

    def can_handle(self, url: str, html: str) -> bool:
        """Check if URL is a Lever careers page."""
        url_lower = url.lower()

        # URL patterns
        if "lever.co" in url_lower:
            return True

        # HTML patterns - Lever-specific classes
        if "lever" in html.lower():
            if "posting-category" in html or "posting-title" in html:
                return True

        return False

    def extract_job_list(
        self,
        company_name: str,
        source_url: str,
        html: str,
    ) -> list[JobPostingIn]:
        """
        Extract job listings from Lever careers page.

        Lever HTML typically has:
        - Postings grouped by team in .postings-group
        - Individual postings as .posting divs
        - Categories (team, location, commitment) in .posting-categories
        """
        jobs: list[JobPostingIn] = []
        parser = HTMLParser(html)

        # Pattern 1: Grouped postings
        groups = parser.css(".postings-group")

        if groups:
            for group in groups:
                # Get team/department from group title
                team_header = group.css_first(".posting-category-title, .large-category-header")
                department = self._clean_text(team_header.text()) if team_header else None

                # Get postings in this group
                postings = group.css(".posting")
                for posting in postings:
                    job = self._parse_posting(
                        posting,
                        company_name,
                        source_url,
                        department,
                    )
                    if job:
                        jobs.append(job)

        # Pattern 2: Flat list of postings
        if not jobs:
            postings = parser.css(".posting")
            for posting in postings:
                job = self._parse_posting(
                    posting,
                    company_name,
                    source_url,
                    None,
                )
                if job:
                    jobs.append(job)

        # Pattern 3: Simple link structure
        if not jobs:
            links = parser.css('a[href*="lever.co"]')
            seen_urls = set()

            for link in links:
                href = link.attributes.get("href", "")
                if not href or href in seen_urls:
                    continue
                if "/apply" in href or "/jobs" not in href:
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

    def _parse_posting(
        self,
        node,
        company_name: str,
        source_url: str,
        department: Optional[str],
    ) -> Optional[JobPostingIn]:
        """Parse a single Lever posting element."""
        # Find job title and link
        title_link = node.css_first(".posting-title a, a.posting-title, h5 a")
        if not title_link:
            # Try alternate structure
            link = node.css_first("a[href]")
            if not link:
                return None
            title_link = link

        href = title_link.attributes.get("href", "")
        if not href:
            return None

        # Get job title
        title_el = node.css_first(".posting-title h5, .posting-name, h5")
        title = self._clean_text(title_el.text()) if title_el else self._clean_text(title_link.text())
        if not title:
            return None

        # Build absolute URL
        job_url = self._make_absolute_url(source_url, href)
        external_id = extract_job_id_from_url(job_url)

        # Extract categories (location, team, commitment)
        location: Optional[str] = None
        team: Optional[str] = None
        commitment: Optional[str] = None

        categories = node.css(".posting-categories span, .posting-category")
        for cat in categories:
            cat_text = self._clean_text(cat.text())
            if not cat_text:
                continue

            # Classify category by class or content
            classes = cat.attributes.get("class", "")

            if "location" in classes:
                location = cat_text
            elif "team" in classes or "department" in classes:
                team = cat_text
            elif "commitment" in classes or "workplaceType" in classes:
                commitment = cat_text
            else:
                # Heuristic: if looks like location, treat as location
                if any(loc in cat_text.lower() for loc in ["remote", "san francisco", "new york", "london"]):
                    location = cat_text
                elif department is None and team is None:
                    team = cat_text

        # Use extracted or passed department
        final_department = department or team

        return JobPostingIn(
            source_name=company_name,
            source_type=self.source_type,
            source_url=source_url,
            canonical_job_url=job_url,
            company_name=company_name,
            external_job_id=external_id,
            job_title=title,
            department=final_department,
            team=team,
            location_text=location,
            employment_type=self._normalize_commitment(commitment),
        )

    def _normalize_commitment(self, commitment: Optional[str]) -> Optional[str]:
        """Normalize commitment/employment type."""
        if not commitment:
            return None

        commitment_lower = commitment.lower()

        if "full" in commitment_lower:
            return "full_time"
        elif "part" in commitment_lower:
            return "part_time"
        elif "contract" in commitment_lower:
            return "contract"
        elif "intern" in commitment_lower:
            return "internship"

        return None

    def extract_job_details(
        self,
        job: JobPostingIn,
        html: str,
    ) -> JobPostingIn:
        """
        Extract full details from a Lever job detail page.

        Lever job pages typically have:
        - Job title in h2.posting-headline
        - Categories below title
        - Description sections in .section
        """
        parser = HTMLParser(html)

        # Get all content sections
        sections = parser.css(".section, .section-wrapper")
        all_content = []

        for section in sections:
            content = self._clean_text(section.text())
            if content:
                all_content.append(content)

        if all_content:
            job.full_description_text = "\n\n".join(all_content)

        # Try to get location from posting categories if not set
        if not job.location_text:
            location_el = parser.css_first(".location, .posting-categories .workplaceTypes")
            if location_el:
                job.location_text = self._clean_text(location_el.text())

        return job
