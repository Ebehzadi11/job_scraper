"""Tests for normalization service."""

import pytest

from jobscraper.schemas import JobPostingIn
from jobscraper.services.normalization import normalize_job_posting


class TestNormalization:
    """Tests for job posting normalization."""

    def test_basic_normalization(self):
        """Basic normalization adds page hash."""
        job = JobPostingIn(
            source_name="Stripe",
            source_type="greenhouse",
            source_url="https://boards.greenhouse.io/stripe",
            company_name="Stripe",
            job_title="Software Engineer",
            full_description_text="We are looking for an engineer.",
        )

        normalized = normalize_job_posting(job)

        assert normalized.page_hash is not None
        assert len(normalized.page_hash) == 64  # SHA-256

    def test_section_extraction(self):
        """Normalization extracts sections."""
        job = JobPostingIn(
            source_name="Stripe",
            source_type="greenhouse",
            source_url="https://boards.greenhouse.io/stripe",
            company_name="Stripe",
            job_title="Software Engineer",
            full_description_text="""
            Responsibilities:
            - Build features
            - Write tests

            Requirements:
            - 5+ years experience
            - Python expertise
            """,
        )

        normalized = normalize_job_posting(job)

        assert normalized.responsibilities_text is not None
        assert "Build features" in normalized.responsibilities_text
        assert normalized.requirements_text is not None
        assert "5+ years" in normalized.requirements_text

    def test_tools_extraction(self):
        """Normalization extracts tools mentioned."""
        job = JobPostingIn(
            source_name="Stripe",
            source_type="greenhouse",
            source_url="https://boards.greenhouse.io/stripe",
            company_name="Stripe",
            job_title="Software Engineer",
            full_description_text="""
            Requirements:
            - Experience with Python and JavaScript
            - Knowledge of Docker and Kubernetes
            - Familiarity with AWS
            """,
        )

        normalized = normalize_job_posting(job)

        assert normalized.tools_mentioned is not None
        # Check for some expected tools
        tools_lower = [t.lower() for t in normalized.tools_mentioned]
        assert "python" in tools_lower
        assert "docker" in tools_lower

    def test_semantic_signals(self):
        """Normalization extracts semantic signals."""
        job = JobPostingIn(
            source_name="Stripe",
            source_type="greenhouse",
            source_url="https://boards.greenhouse.io/stripe",
            company_name="Stripe",
            job_title="Senior Software Engineer",
            full_description_text="""
            This is a remote position. We are looking for a senior engineer
            with 7+ years of experience. You will work closely with customers
            and make strategic decisions about our platform.
            """,
        )

        normalized = normalize_job_posting(job)

        # Should detect remote
        assert normalized.remote_type == "remote"
        # Should detect senior level
        assert normalized.seniority_level == "senior"
        # Should detect years of experience
        assert normalized.years_experience_required == 7

    def test_preserves_existing_values(self):
        """Normalization preserves existing values."""
        job = JobPostingIn(
            source_name="Stripe",
            source_type="greenhouse",
            source_url="https://boards.greenhouse.io/stripe",
            company_name="Stripe",
            job_title="Software Engineer",
            location_text="San Francisco",
            remote_type="hybrid",  # Already set
            full_description_text="Remote position available.",
        )

        normalized = normalize_job_posting(job)

        # Should preserve existing value
        assert normalized.remote_type == "hybrid"
        assert normalized.location_text == "San Francisco"
