"""Tests for section parsing."""

import pytest

from jobscraper.parsers.sections import parse_sections, SectionParser


class TestSectionParser:
    """Tests for section parsing."""

    def test_parse_responsibilities(self):
        """Parse responsibilities section."""
        text = """
        About the role

        Responsibilities:
        - Build and maintain software systems
        - Collaborate with team members
        - Write clean code

        Requirements:
        - 5+ years of experience
        - Strong Python skills
        """

        sections = parse_sections(text)

        assert sections.responsibilities is not None
        assert "Build and maintain" in sections.responsibilities
        assert sections.requirements is not None
        assert "5+ years" in sections.requirements

    def test_parse_what_youll_do(self):
        """Parse 'What you'll do' heading."""
        text = """
        What you'll do:
        - Design and implement features
        - Review code

        What you'll need:
        - Experience with Python
        """

        sections = parse_sections(text)

        assert sections.responsibilities is not None
        assert "Design and implement" in sections.responsibilities

    def test_parse_benefits(self):
        """Parse benefits section."""
        text = """
        Requirements:
        - Strong communication skills

        Benefits:
        - Health insurance
        - 401k matching
        - Unlimited PTO
        """

        sections = parse_sections(text)

        assert sections.benefits is not None
        assert "Health insurance" in sections.benefits

    def test_parse_preferred_qualifications(self):
        """Parse preferred qualifications section."""
        text = """
        Requirements:
        - 3+ years experience

        Nice to have:
        - Machine learning experience
        - PhD preferred
        """

        sections = parse_sections(text)

        assert sections.preferred_qualifications is not None
        assert "Machine learning" in sections.preferred_qualifications

    def test_empty_text(self):
        """Handle empty text."""
        sections = parse_sections("")

        assert sections.responsibilities is None
        assert sections.requirements is None
        assert sections.benefits is None

    def test_no_sections(self):
        """Handle text with no section headings."""
        text = "We are looking for a great engineer to join our team."

        sections = parse_sections(text)

        # Should not crash, may or may not find sections
        assert isinstance(sections.responsibilities, (str, type(None)))
