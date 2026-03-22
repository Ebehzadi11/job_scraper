"""
Tools and skills extractor.

Extracts mentions of:
- Software tools and platforms
- Technical skills
- Certifications
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ExtractedToolsSkills:
    """Extracted tools, skills, and certifications."""

    tools: list[str]
    skills: list[str]
    certifications: list[str]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "tools": self.tools,
            "skills": self.skills,
            "certifications": self.certifications,
        }


class ToolsSkillsParser:
    """
    Parser for extracting tools, skills, and certifications from job text.

    Uses keyword dictionaries and pattern matching.
    Does not use LLM - purely heuristic-based.
    """

    # Common software tools and platforms
    TOOLS = {
        # Programming languages (also tools)
        "python", "javascript", "typescript", "java", "c++", "c#", "ruby", "go",
        "golang", "rust", "scala", "kotlin", "swift", "php", "perl", "r",
        # Cloud platforms
        "aws", "amazon web services", "gcp", "google cloud", "azure", "heroku",
        "digitalocean", "cloudflare",
        # Databases
        "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch",
        "dynamodb", "cassandra", "oracle", "sql server", "sqlite", "neo4j",
        # DevOps / Infrastructure
        "docker", "kubernetes", "k8s", "terraform", "ansible", "jenkins",
        "circleci", "github actions", "gitlab ci", "travis ci", "datadog",
        "prometheus", "grafana", "splunk", "new relic", "pagerduty",
        # Frameworks
        "react", "angular", "vue", "next.js", "nextjs", "node.js", "nodejs",
        "express", "django", "flask", "fastapi", "spring", "rails", "laravel",
        "svelte", "remix", "gatsby",
        # Data tools
        "spark", "hadoop", "kafka", "airflow", "dbt", "snowflake", "databricks",
        "looker", "tableau", "power bi", "metabase", "redshift", "bigquery",
        # Collaboration
        "jira", "confluence", "slack", "notion", "asana", "trello", "linear",
        "figma", "miro", "lucidchart",
        # Version control
        "git", "github", "gitlab", "bitbucket", "svn",
        # AI/ML
        "tensorflow", "pytorch", "scikit-learn", "keras", "hugging face",
        "langchain", "openai", "anthropic",
        # Others
        "salesforce", "hubspot", "zendesk", "intercom", "segment", "amplitude",
        "mixpanel", "stripe", "twilio", "sendgrid", "auth0", "okta",
    }

    # Technical skills
    SKILLS = {
        # General
        "machine learning", "deep learning", "natural language processing", "nlp",
        "computer vision", "data science", "data engineering", "data analysis",
        "artificial intelligence", "ai", "ml",
        # Software engineering
        "software development", "software engineering", "full stack", "frontend",
        "backend", "devops", "sre", "site reliability", "cloud architecture",
        "microservices", "api design", "system design", "distributed systems",
        "database design", "data modeling", "etl",
        # Security
        "cybersecurity", "security", "penetration testing", "soc", "compliance",
        "gdpr", "hipaa", "pci", "soc2",
        # Methodologies
        "agile", "scrum", "kanban", "lean", "ci/cd", "tdd", "test driven",
        "pair programming", "code review",
        # Other
        "project management", "product management", "technical writing",
        "public speaking", "leadership", "mentoring", "cross-functional",
        "stakeholder management", "customer success", "sales engineering",
        "solution architecture", "enterprise", "startup",
    }

    # Certifications
    CERTIFICATIONS = {
        # Cloud
        "aws certified", "aws solutions architect", "aws developer",
        "google cloud certified", "gcp certified", "azure certified",
        "cka", "ckad", "cks",  # Kubernetes
        # Security
        "cissp", "cism", "cisa", "ceh", "oscp", "comptia security+",
        "comptia network+", "comptia a+",
        # Project Management
        "pmp", "prince2", "csm", "psm", "safe", "itil",
        # Data
        "google analytics certified", "tableau certified", "snowflake certified",
        # Other
        "six sigma", "lean six sigma", "green belt", "black belt",
    }

    def __init__(self):
        # Pre-compile patterns
        self._tool_patterns = self._compile_keyword_patterns(self.TOOLS)
        self._skill_patterns = self._compile_keyword_patterns(self.SKILLS)
        self._cert_patterns = self._compile_keyword_patterns(self.CERTIFICATIONS)

    def _compile_keyword_patterns(self, keywords: set[str]) -> list[re.Pattern]:
        """Compile keywords into regex patterns with word boundaries."""
        patterns = []
        for keyword in keywords:
            # Escape special regex characters
            escaped = re.escape(keyword)
            # Add word boundaries
            pattern = re.compile(rf"\b{escaped}\b", re.IGNORECASE)
            patterns.append((keyword, pattern))
        return patterns

    def parse(self, text: str) -> ExtractedToolsSkills:
        """
        Extract tools, skills, and certifications from text.

        Args:
            text: Job description text

        Returns:
            ExtractedToolsSkills with found items
        """
        if not text:
            return ExtractedToolsSkills(tools=[], skills=[], certifications=[])

        text_lower = text.lower()

        tools = self._find_matches(text_lower, self._tool_patterns)
        skills = self._find_matches(text_lower, self._skill_patterns)
        certifications = self._find_matches(text_lower, self._cert_patterns)

        return ExtractedToolsSkills(
            tools=sorted(tools),
            skills=sorted(skills),
            certifications=sorted(certifications),
        )

    def _find_matches(
        self,
        text: str,
        patterns: list[tuple[str, re.Pattern]],
    ) -> list[str]:
        """Find all matches in text."""
        found = set()
        for keyword, pattern in patterns:
            if pattern.search(text):
                # Normalize to title case
                found.add(keyword.title())
        return list(found)


# Global parser instance
_parser: Optional[ToolsSkillsParser] = None


def get_tools_skills_parser() -> ToolsSkillsParser:
    """Get the global tools/skills parser."""
    global _parser
    if _parser is None:
        _parser = ToolsSkillsParser()
    return _parser


def parse_tools_skills(text: str) -> ExtractedToolsSkills:
    """Convenience function to parse tools and skills."""
    return get_tools_skills_parser().parse(text)
