"""
Semantic signal parser for automation analysis.

Extracts heuristic signals that indicate automation potential:
- Remote type (remote, hybrid, onsite)
- Employment type (full-time, part-time, contract)
- Seniority level
- Years of experience
- Customer-facing indicators
- Judgment/decision-making intensity
- Repetition/routine indicators
- Compliance sensitivity
- Physical world dependency
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class SemanticSignals:
    """Extracted semantic signals for automation analysis."""

    # Basic job attributes
    remote_type: Optional[str] = None  # remote, hybrid, onsite, unknown
    employment_type: Optional[str] = None  # full_time, part_time, contract, etc.
    seniority_level: Optional[str] = None  # intern, entry, mid, senior, etc.
    years_experience: Optional[int] = None
    education_requirement: Optional[str] = None

    # Role classification
    normalized_role_family: Optional[str] = None  # engineering, sales, marketing, etc.

    # Automation analysis scores (0-100)
    customer_facing_score: Optional[int] = None
    communication_intensity: Optional[int] = None
    judgment_intensity: Optional[int] = None
    repetition_intensity: Optional[int] = None

    # Risk indicators
    compliance_sensitivity: Optional[str] = None  # none, low, medium, high
    physical_world_dependency: Optional[str] = None  # none, minimal, moderate, high

    # Languages
    language_requirements: Optional[list[str]] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "remote_type": self.remote_type,
            "employment_type": self.employment_type,
            "seniority_level": self.seniority_level,
            "years_experience": self.years_experience,
            "education_requirement": self.education_requirement,
            "normalized_role_family": self.normalized_role_family,
            "customer_facing_score": self.customer_facing_score,
            "communication_intensity": self.communication_intensity,
            "judgment_intensity": self.judgment_intensity,
            "repetition_intensity": self.repetition_intensity,
            "compliance_sensitivity": self.compliance_sensitivity,
            "physical_world_dependency": self.physical_world_dependency,
            "language_requirements": self.language_requirements,
        }


class SemanticSignalParser:
    """
    Parser for extracting semantic signals from job descriptions.

    Uses keyword matching and heuristics to infer automation-relevant signals.
    """

    # Remote type patterns
    REMOTE_PATTERNS = {
        "remote": [
            r"\bfully remote\b",
            r"\b100% remote\b",
            r"\bremote[- ]first\b",
            r"\bwork from home\b",
            r"\bwork from anywhere\b",
            r"\bremote position\b",
            r"\bremote role\b",
        ],
        "hybrid": [
            r"\bhybrid\b",
            r"\bflexible.*office\b",
            r"\b\d+ days.*office\b",
            r"\bpartially remote\b",
        ],
        "onsite": [
            r"\bon[- ]?site\b",
            r"\bin[- ]?office\b",
            r"\bmust be located\b",
            r"\brequires presence\b",
            r"\bno remote\b",
        ],
    }

    # Employment type patterns
    EMPLOYMENT_PATTERNS = {
        "full_time": [r"\bfull[- ]?time\b", r"\bpermanent\b", r"\bfte\b"],
        "part_time": [r"\bpart[- ]?time\b"],
        "contract": [r"\bcontract\b", r"\bfreelance\b", r"\bconsultant\b", r"\b1099\b"],
        "internship": [r"\bintern\b", r"\binternship\b", r"\bco-?op\b"],
        "temporary": [r"\btemporary\b", r"\btemp\b", r"\bseasonal\b"],
    }

    # Seniority patterns
    SENIORITY_PATTERNS = {
        "intern": [r"\bintern\b"],
        "entry": [r"\bentry[- ]?level\b", r"\bjunior\b", r"\bgraduate\b", r"\bnew grad\b"],
        "mid": [r"\bmid[- ]?level\b", r"\b2-5 years\b", r"\b3-5 years\b"],
        "senior": [r"\bsenior\b", r"\bsr\.?\b", r"\b5\+ years\b", r"\b7\+ years\b"],
        "staff": [r"\bstaff\b", r"\bprincipal\b"],
        "lead": [r"\blead\b", r"\btech lead\b", r"\bteam lead\b"],
        "manager": [r"\bmanager\b", r"\bmanaging\b"],
        "director": [r"\bdirector\b"],
        "vp": [r"\bvice president\b", r"\bvp\b"],
        "c_level": [r"\bcto\b", r"\bceo\b", r"\bcfo\b", r"\bcoo\b", r"\bchief\b"],
    }

    # Role family patterns
    ROLE_FAMILY_PATTERNS = {
        "engineering": [
            r"\bengineer\b", r"\bdeveloper\b", r"\bswe\b", r"\bsde\b",
            r"\bprogrammer\b", r"\barchitect\b", r"\bdevops\b", r"\bsre\b",
        ],
        "data": [
            r"\bdata scientist\b", r"\bdata analyst\b", r"\bdata engineer\b",
            r"\bmachine learning\b", r"\bml engineer\b", r"\bai\b",
        ],
        "design": [
            r"\bdesigner\b", r"\bux\b", r"\bui\b", r"\bproduct design\b",
            r"\bgraphic design\b", r"\bvisual design\b",
        ],
        "product": [
            r"\bproduct manager\b", r"\bpm\b", r"\bproduct owner\b",
        ],
        "sales": [
            r"\bsales\b", r"\baccount executive\b", r"\bae\b", r"\bbdr\b",
            r"\bsdr\b", r"\bbusiness development\b",
        ],
        "marketing": [
            r"\bmarketing\b", r"\bgrowth\b", r"\bcontent\b", r"\bseo\b",
            r"\bsocial media\b", r"\bbrand\b",
        ],
        "customer_success": [
            r"\bcustomer success\b", r"\bcustomer support\b", r"\bsupport engineer\b",
            r"\bcustomer service\b", r"\bsolutions engineer\b",
        ],
        "operations": [
            r"\boperations\b", r"\bops\b", r"\boffice manager\b",
            r"\badministrative\b", r"\bexecutive assistant\b",
        ],
        "finance": [
            r"\bfinance\b", r"\baccounting\b", r"\baccountant\b",
            r"\bcontroller\b", r"\bfp&a\b",
        ],
        "hr": [
            r"\bhuman resources\b", r"\bhr\b", r"\brecruiter\b",
            r"\btalent\b", r"\bpeople\b",
        ],
        "legal": [
            r"\blegal\b", r"\blawyer\b", r"\battorney\b", r"\bcounsel\b",
            r"\bcompliance\b",
        ],
    }

    # Customer-facing indicators
    CUSTOMER_FACING_KEYWORDS = [
        "customer", "client", "stakeholder", "user", "partner",
        "external", "customer-facing", "client-facing",
        "presentation", "demo", "meeting", "call",
    ]

    # Communication intensity indicators
    COMMUNICATION_KEYWORDS = [
        "communicate", "communication", "collaborate", "collaboration",
        "cross-functional", "stakeholder", "presentation", "writing",
        "documentation", "meeting", "verbal", "written",
    ]

    # Judgment/decision intensity indicators
    JUDGMENT_KEYWORDS = [
        "decision", "judgment", "evaluate", "assess", "analyze",
        "strategy", "strategic", "critical thinking", "problem solving",
        "ambiguous", "uncertainty", "complex", "nuanced",
    ]

    # Repetition/routine indicators
    REPETITION_KEYWORDS = [
        "routine", "repetitive", "standard", "process", "procedure",
        "daily", "weekly", "recurring", "consistent", "systematic",
        "checklist", "template", "automated", "manual",
    ]

    # Compliance sensitivity indicators
    COMPLIANCE_KEYWORDS = {
        "high": ["hipaa", "pci", "sox", "gdpr", "ferpa", "sec", "finra", "regulated"],
        "medium": ["compliance", "audit", "legal", "privacy", "security"],
        "low": ["policy", "standard", "guideline"],
    }

    # Physical world dependency indicators
    PHYSICAL_KEYWORDS = [
        "on-site", "office", "physical", "hardware", "manufacturing",
        "warehouse", "logistics", "field", "travel", "in-person",
    ]

    def parse(self, text: str, title: str = "") -> SemanticSignals:
        """
        Extract semantic signals from job description.

        Args:
            text: Full job description text
            title: Job title (optional, helps with role classification)

        Returns:
            SemanticSignals with extracted values
        """
        if not text:
            return SemanticSignals()

        text_lower = text.lower()
        title_lower = title.lower() if title else ""
        combined = f"{title_lower} {text_lower}"

        signals = SemanticSignals()

        # Extract basic attributes
        signals.remote_type = self._extract_pattern_match(
            combined, self.REMOTE_PATTERNS, default="unknown"
        )
        signals.employment_type = self._extract_pattern_match(
            combined, self.EMPLOYMENT_PATTERNS
        )
        signals.seniority_level = self._extract_pattern_match(
            combined, self.SENIORITY_PATTERNS
        )
        signals.years_experience = self._extract_years_experience(text_lower)
        signals.education_requirement = self._extract_education(text_lower)

        # Extract role family (prefer title, fall back to text)
        signals.normalized_role_family = self._extract_pattern_match(
            title_lower, self.ROLE_FAMILY_PATTERNS
        ) or self._extract_pattern_match(text_lower, self.ROLE_FAMILY_PATTERNS)

        # Calculate intensity scores
        signals.customer_facing_score = self._calculate_keyword_score(
            text_lower, self.CUSTOMER_FACING_KEYWORDS
        )
        signals.communication_intensity = self._calculate_keyword_score(
            text_lower, self.COMMUNICATION_KEYWORDS
        )
        signals.judgment_intensity = self._calculate_keyword_score(
            text_lower, self.JUDGMENT_KEYWORDS
        )
        signals.repetition_intensity = self._calculate_keyword_score(
            text_lower, self.REPETITION_KEYWORDS
        )

        # Extract risk indicators
        signals.compliance_sensitivity = self._extract_compliance_level(text_lower)
        signals.physical_world_dependency = self._extract_physical_dependency(text_lower)

        # Extract language requirements
        signals.language_requirements = self._extract_languages(text_lower)

        return signals

    def _extract_pattern_match(
        self,
        text: str,
        patterns: dict[str, list[str]],
        default: Optional[str] = None,
    ) -> Optional[str]:
        """Find first matching pattern category."""
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, text, re.IGNORECASE):
                    return category
        return default

    def _extract_years_experience(self, text: str) -> Optional[int]:
        """Extract years of experience requirement."""
        # Pattern: X+ years
        match = re.search(r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience)?", text)
        if match:
            return int(match.group(1))

        # Pattern: X-Y years (take lower bound)
        match = re.search(r"(\d+)\s*[-–]\s*\d+\s*(?:years?|yrs?)", text)
        if match:
            return int(match.group(1))

        return None

    def _extract_education(self, text: str) -> Optional[str]:
        """Extract education requirement."""
        if re.search(r"\bph\.?d\b|\bdoctorate\b", text):
            return "phd"
        elif re.search(r"\bmaster'?s?\b|\bmba\b|\bms\b|\bma\b", text):
            return "masters"
        elif re.search(r"\bbachelor'?s?\b|\bbs\b|\bba\b|\bundergr", text):
            return "bachelors"
        elif re.search(r"\bassociate'?s?\b", text):
            return "associates"
        elif re.search(r"\bhigh school\b|\bged\b", text):
            return "high_school"
        return None

    def _calculate_keyword_score(
        self,
        text: str,
        keywords: list[str],
        max_score: int = 100,
    ) -> int:
        """Calculate score based on keyword presence and frequency."""
        if not text:
            return 0

        count = 0
        for keyword in keywords:
            count += len(re.findall(rf"\b{re.escape(keyword)}\b", text))

        # Normalize to 0-100 scale
        # More than 10 mentions = max score
        normalized = min(count * 10, max_score)
        return normalized

    def _extract_compliance_level(self, text: str) -> Optional[str]:
        """Extract compliance sensitivity level."""
        for level in ["high", "medium", "low"]:
            for keyword in self.COMPLIANCE_KEYWORDS.get(level, []):
                if keyword in text:
                    return level
        return "none"

    def _extract_physical_dependency(self, text: str) -> Optional[str]:
        """Extract physical world dependency level."""
        count = 0
        for keyword in self.PHYSICAL_KEYWORDS:
            if keyword in text:
                count += 1

        if count >= 3:
            return "high"
        elif count >= 2:
            return "moderate"
        elif count >= 1:
            return "minimal"
        return "none"

    def _extract_languages(self, text: str) -> list[str]:
        """Extract required languages."""
        languages = []

        language_patterns = {
            "english": r"\benglish\b",
            "spanish": r"\bspanish\b",
            "french": r"\bfrench\b",
            "german": r"\bgerman\b",
            "mandarin": r"\bmandarin\b|\bchinese\b",
            "japanese": r"\bjapanese\b",
            "korean": r"\bkorean\b",
            "portuguese": r"\bportuguese\b",
            "arabic": r"\barabic\b",
            "hindi": r"\bhindi\b",
        }

        for lang, pattern in language_patterns.items():
            if re.search(pattern, text):
                languages.append(lang)

        return languages


# Global parser instance
_parser: Optional[SemanticSignalParser] = None


def get_semantic_parser() -> SemanticSignalParser:
    """Get the global semantic signal parser."""
    global _parser
    if _parser is None:
        _parser = SemanticSignalParser()
    return _parser


def parse_semantic_signals(text: str, title: str = "") -> SemanticSignals:
    """Convenience function to parse semantic signals."""
    return get_semantic_parser().parse(text, title)
