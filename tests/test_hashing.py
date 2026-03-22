"""Tests for hashing utilities."""

import pytest

from jobscraper.utils.hashing import (
    compute_content_hash,
    compute_url_hash,
    compute_job_dedupe_key,
)


class TestContentHash:
    """Tests for compute_content_hash."""

    def test_empty_content(self):
        """Empty content returns empty string."""
        assert compute_content_hash("") == ""
        assert compute_content_hash(None) == ""

    def test_consistent_hash(self):
        """Same content produces same hash."""
        content = "Hello, World!"
        hash1 = compute_content_hash(content)
        hash2 = compute_content_hash(content)
        assert hash1 == hash2

    def test_whitespace_normalization(self):
        """Whitespace is normalized before hashing."""
        hash1 = compute_content_hash("hello   world")
        hash2 = compute_content_hash("hello world")
        assert hash1 == hash2

    def test_case_insensitive(self):
        """Hash is case-insensitive."""
        hash1 = compute_content_hash("Hello World")
        hash2 = compute_content_hash("hello world")
        assert hash1 == hash2

    def test_different_content_different_hash(self):
        """Different content produces different hash."""
        hash1 = compute_content_hash("hello")
        hash2 = compute_content_hash("world")
        assert hash1 != hash2


class TestUrlHash:
    """Tests for compute_url_hash."""

    def test_empty_url(self):
        """Empty URL returns empty string."""
        assert compute_url_hash("") == ""

    def test_consistent_hash(self):
        """Same URL produces same hash."""
        url = "https://example.com/jobs"
        hash1 = compute_url_hash(url)
        hash2 = compute_url_hash(url)
        assert hash1 == hash2

    def test_truncated_hash(self):
        """Hash is truncated to 16 characters."""
        url = "https://example.com/jobs"
        hash_val = compute_url_hash(url)
        assert len(hash_val) == 16


class TestJobDedupeKey:
    """Tests for compute_job_dedupe_key."""

    def test_basic_dedupe_key(self):
        """Basic dedupe key is computed."""
        key = compute_job_dedupe_key(
            source_type="greenhouse",
            company_name="Stripe",
            job_title="Software Engineer",
        )
        assert key
        assert len(key) == 64  # SHA-256 hex

    def test_location_affects_key(self):
        """Location changes the dedupe key."""
        key1 = compute_job_dedupe_key(
            source_type="greenhouse",
            company_name="Stripe",
            job_title="Software Engineer",
            location="San Francisco",
        )
        key2 = compute_job_dedupe_key(
            source_type="greenhouse",
            company_name="Stripe",
            job_title="Software Engineer",
            location="New York",
        )
        assert key1 != key2

    def test_case_insensitive(self):
        """Dedupe key is case-insensitive."""
        key1 = compute_job_dedupe_key(
            source_type="Greenhouse",
            company_name="STRIPE",
            job_title="Software Engineer",
        )
        key2 = compute_job_dedupe_key(
            source_type="greenhouse",
            company_name="stripe",
            job_title="software engineer",
        )
        assert key1 == key2
