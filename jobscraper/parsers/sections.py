"""
Section parser for job descriptions.

Splits job description text into semantic sections:
- Responsibilities / What you'll do
- Requirements / Qualifications
- Preferred qualifications
- Benefits / What we offer
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class JobSections:
    """Extracted sections from a job description."""

    responsibilities: Optional[str] = None
    requirements: Optional[str] = None
    preferred_qualifications: Optional[str] = None
    benefits: Optional[str] = None
    remaining_text: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "responsibilities": self.responsibilities,
            "requirements": self.requirements,
            "preferred_qualifications": self.preferred_qualifications,
            "benefits": self.benefits,
        }


class SectionParser:
    """
    Parser for extracting sections from job descriptions.

    Uses heuristic heading detection to split text into semantic sections.
    Handles various heading formats and naming conventions.
    """

    # Heading patterns for each section type
    RESPONSIBILITY_PATTERNS = [
        r"responsibilities",
        r"what you'?ll do",
        r"what you will do",
        r"your role",
        r"the role",
        r"job duties",
        r"duties",
        r"key responsibilities",
        r"role responsibilities",
        r"day to day",
        r"in this role,? you will",
        r"as a .+?,? you will",
    ]

    REQUIREMENT_PATTERNS = [
        r"requirements",
        r"qualifications",
        r"what you'?ll need",
        r"what you need",
        r"who you are",
        r"about you",
        r"required skills",
        r"required experience",
        r"must have",
        r"minimum qualifications",
        r"basic qualifications",
        r"you should have",
        r"we'?re looking for",
    ]

    PREFERRED_PATTERNS = [
        r"preferred qualifications",
        r"preferred experience",
        r"nice to have",
        r"bonus points",
        r"plus points",
        r"it'?s a plus if",
        r"ideally you",
        r"preferred skills",
        r"additional qualifications",
        r"desired qualifications",
        r"what sets you apart",
    ]

    BENEFITS_PATTERNS = [
        r"benefits",
        r"perks",
        r"what we offer",
        r"why join us",
        r"why .+\?$",
        r"compensation",
        r"total rewards",
        r"our offer",
        r"we provide",
        r"you'?ll get",
        r"you will receive",
    ]

    def __init__(self):
        # Compile patterns for efficiency
        self._responsibility_re = self._compile_patterns(self.RESPONSIBILITY_PATTERNS)
        self._requirement_re = self._compile_patterns(self.REQUIREMENT_PATTERNS)
        self._preferred_re = self._compile_patterns(self.PREFERRED_PATTERNS)
        self._benefits_re = self._compile_patterns(self.BENEFITS_PATTERNS)

    def _compile_patterns(self, patterns: list[str]) -> re.Pattern:
        """Compile multiple patterns into a single regex."""
        combined = "|".join(f"({p})" for p in patterns)
        return re.compile(combined, re.IGNORECASE)

    def parse(self, text: str) -> JobSections:
        """
        Parse job description text into sections.

        Args:
            text: Full job description text

        Returns:
            JobSections with extracted content
        """
        if not text:
            return JobSections()

        # Find all section headings and their positions
        sections = self._find_sections(text)

        # Extract content for each section
        result = JobSections()

        for section_type, start, end in sections:
            content = text[start:end].strip()
            # Remove the heading from content
            content = self._remove_heading(content)

            if section_type == "responsibilities":
                result.responsibilities = content
            elif section_type == "requirements":
                result.requirements = content
            elif section_type == "preferred":
                result.preferred_qualifications = content
            elif section_type == "benefits":
                result.benefits = content

        return result

    def _find_sections(self, text: str) -> list[tuple[str, int, int]]:
        """
        Find all sections in the text.

        Returns:
            List of (section_type, start_pos, end_pos) tuples
        """
        # Find all potential headings
        headings = []

        for match in self._responsibility_re.finditer(text):
            if self._is_likely_heading(text, match.start()):
                headings.append(("responsibilities", match.start()))

        for match in self._requirement_re.finditer(text):
            if self._is_likely_heading(text, match.start()):
                headings.append(("requirements", match.start()))

        for match in self._preferred_re.finditer(text):
            if self._is_likely_heading(text, match.start()):
                headings.append(("preferred", match.start()))

        for match in self._benefits_re.finditer(text):
            if self._is_likely_heading(text, match.start()):
                headings.append(("benefits", match.start()))

        # Sort by position
        headings.sort(key=lambda x: x[1])

        # Convert to sections with end positions
        sections = []
        for i, (section_type, start) in enumerate(headings):
            if i + 1 < len(headings):
                end = headings[i + 1][1]
            else:
                end = len(text)
            sections.append((section_type, start, end))

        return sections

    def _is_likely_heading(self, text: str, pos: int) -> bool:
        """
        Check if the match at position is likely a heading.

        Headings are typically:
        - At the start of a line
        - Followed by a colon or newline
        - In title case or all caps
        """
        # Check if at start of line
        if pos > 0 and text[pos - 1] not in "\n\r":
            # Check if preceded only by whitespace on this line
            line_start = text.rfind("\n", 0, pos) + 1
            prefix = text[line_start:pos]
            if prefix.strip():
                return False

        # Find the end of the potential heading
        end = pos
        while end < len(text) and text[end] not in "\n\r:":
            end += 1

        # Check if too long (headings are usually short)
        if end - pos > 100:
            return False

        return True

    def _remove_heading(self, content: str) -> str:
        """Remove the heading line from content."""
        lines = content.split("\n")
        if lines:
            # Remove first line if it looks like a heading
            first_line = lines[0].strip()
            if len(first_line) < 100 and (":" in first_line or first_line.endswith("?")):
                lines = lines[1:]
        return "\n".join(lines).strip()


# Global parser instance
_parser: Optional[SectionParser] = None


def get_section_parser() -> SectionParser:
    """Get the global section parser."""
    global _parser
    if _parser is None:
        _parser = SectionParser()
    return _parser


def parse_sections(text: str) -> JobSections:
    """Convenience function to parse sections."""
    return get_section_parser().parse(text)
