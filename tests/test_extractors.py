"""Tests for extractors."""

import pytest

from jobscraper.extractors.greenhouse import GreenhouseExtractor
from jobscraper.extractors.lever import LeverExtractor
from jobscraper.extractors.ashby import AshbyExtractor
from jobscraper.extractors.generic_careers import GenericCareersExtractor
from jobscraper.registry import resolve_extractor


class TestExtractorMatching:
    """Tests for extractor can_handle methods."""

    def test_greenhouse_url_match(self):
        """Greenhouse extractor matches greenhouse.io URLs."""
        extractor = GreenhouseExtractor()
        assert extractor.can_handle("https://boards.greenhouse.io/stripe", "")
        assert extractor.can_handle("https://stripe.greenhouse.io", "")

    def test_lever_url_match(self):
        """Lever extractor matches lever.co URLs."""
        extractor = LeverExtractor()
        assert extractor.can_handle("https://jobs.lever.co/company", "")
        assert extractor.can_handle("https://company.lever.co", "")

    def test_ashby_url_match(self):
        """Ashby extractor matches ashbyhq.com URLs."""
        extractor = AshbyExtractor()
        assert extractor.can_handle("https://jobs.ashbyhq.com/company", "")

    def test_generic_fallback(self):
        """Generic extractor handles career pages."""
        extractor = GenericCareersExtractor()
        assert extractor.can_handle("https://example.com/careers", "")
        assert extractor.can_handle("https://example.com/jobs", "")


class TestRegistryResolution:
    """Tests for registry extractor resolution."""

    def test_resolve_greenhouse(self):
        """Registry resolves Greenhouse URLs."""
        extractor = resolve_extractor("https://boards.greenhouse.io/stripe", "")
        assert extractor.name == "greenhouse"

    def test_resolve_lever(self):
        """Registry resolves Lever URLs."""
        extractor = resolve_extractor("https://jobs.lever.co/company", "")
        assert extractor.name == "lever"

    def test_resolve_ashby(self):
        """Registry resolves Ashby URLs."""
        extractor = resolve_extractor("https://jobs.ashbyhq.com/company", "")
        assert extractor.name == "ashby"

    def test_resolve_generic_fallback(self):
        """Registry falls back to generic for unknown URLs."""
        extractor = resolve_extractor(
            "https://example.com/careers",
            "<html><body>careers</body></html>",
        )
        assert extractor.name == "generic"


class TestGreenhouseExtractor:
    """Tests for Greenhouse extractor."""

    def test_extract_job_list_basic(self):
        """Extract jobs from basic Greenhouse HTML."""
        html = """
        <html>
        <body>
            <section class="level-0">
                <h2>Engineering</h2>
                <div class="opening">
                    <a href="/stripe/jobs/123">Software Engineer</a>
                    <span class="location">San Francisco</span>
                </div>
                <div class="opening">
                    <a href="/stripe/jobs/456">Backend Engineer</a>
                    <span class="location">Remote</span>
                </div>
            </section>
        </body>
        </html>
        """
        extractor = GreenhouseExtractor()
        jobs = extractor.extract_job_list(
            company_name="Stripe",
            source_url="https://boards.greenhouse.io/stripe",
            html=html,
        )

        assert len(jobs) == 2
        assert jobs[0].job_title == "Software Engineer"
        assert jobs[0].department == "Engineering"
        assert jobs[1].job_title == "Backend Engineer"


class TestLeverExtractor:
    """Tests for Lever extractor."""

    def test_extract_job_list_basic(self):
        """Extract jobs from basic Lever HTML."""
        html = """
        <html>
        <body>
            <div class="postings-group">
                <div class="posting-category-title">Engineering</div>
                <div class="posting">
                    <a href="https://jobs.lever.co/company/abc" class="posting-title">
                        <h5>Software Engineer</h5>
                    </a>
                    <span class="posting-categories">
                        <span class="location">San Francisco</span>
                        <span class="commitment">Full-time</span>
                    </span>
                </div>
            </div>
        </body>
        </html>
        """
        extractor = LeverExtractor()
        jobs = extractor.extract_job_list(
            company_name="Company",
            source_url="https://jobs.lever.co/company",
            html=html,
        )

        assert len(jobs) == 1
        assert jobs[0].job_title == "Software Engineer"
        assert jobs[0].department == "Engineering"
