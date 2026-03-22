"""
Enumeration types for the job scraper system.

These enums support both the scraping layer and future automation analysis.
"""

from enum import Enum


class SourceType(str, Enum):
    """ATS or careers page source type."""

    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    ASHBY = "ashby"
    GENERIC = "generic"


class CollectorType(str, Enum):
    """Method used to collect HTML."""

    HTTP = "http"
    PLAYWRIGHT = "playwright"


class PostingStatus(str, Enum):
    """Current status of a job posting."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class RemoteType(str, Enum):
    """Remote work arrangement type."""

    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    UNKNOWN = "unknown"


class EmploymentType(str, Enum):
    """Type of employment arrangement."""

    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    TEMPORARY = "temporary"
    UNKNOWN = "unknown"


class SeniorityLevel(str, Enum):
    """Seniority level of the role."""

    INTERN = "intern"
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    STAFF = "staff"
    PRINCIPAL = "principal"
    LEAD = "lead"
    MANAGER = "manager"
    DIRECTOR = "director"
    VP = "vp"
    C_LEVEL = "c_level"
    UNKNOWN = "unknown"


# ============================================================
# Automation Analysis Enums (for future task decomposition)
# ============================================================


class TaskCategory(str, Enum):
    """Category of task within a job role."""

    ADMINISTRATIVE = "administrative"
    ANALYTICAL = "analytical"
    COMMUNICATION = "communication"
    CREATIVE = "creative"
    CUSTOMER_SERVICE = "customer_service"
    DATA_ENTRY = "data_entry"
    DECISION_MAKING = "decision_making"
    DOCUMENTATION = "documentation"
    LEADERSHIP = "leadership"
    PHYSICAL = "physical"
    RESEARCH = "research"
    TECHNICAL = "technical"
    OTHER = "other"


class InputStructure(str, Enum):
    """How structured the task inputs are."""

    HIGHLY_STRUCTURED = "highly_structured"  # Forms, databases, APIs
    SEMI_STRUCTURED = "semi_structured"  # Emails, documents
    UNSTRUCTURED = "unstructured"  # Conversations, images, video
    MIXED = "mixed"


class OutputStructure(str, Enum):
    """How structured the task outputs are."""

    HIGHLY_STRUCTURED = "highly_structured"  # Database entries, reports
    SEMI_STRUCTURED = "semi_structured"  # Documents, summaries
    UNSTRUCTURED = "unstructured"  # Creative content, decisions
    MIXED = "mixed"


class JudgmentLevel(str, Enum):
    """Level of human judgment required."""

    NONE = "none"  # Fully rule-based
    LOW = "low"  # Simple heuristics
    MEDIUM = "medium"  # Moderate interpretation needed
    HIGH = "high"  # Significant expertise required
    CRITICAL = "critical"  # Life/safety/legal decisions


class HumanInteractionLevel(str, Enum):
    """Level of human interaction required."""

    NONE = "none"  # Fully automated
    ASYNC = "async"  # Email, messaging
    SYNC_SIMPLE = "sync_simple"  # Phone, video calls
    SYNC_COMPLEX = "sync_complex"  # Negotiations, therapy
    IN_PERSON = "in_person"  # Physical presence required


class ComplianceRisk(str, Enum):
    """Level of compliance/regulatory sensitivity."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"  # Healthcare, finance, legal
    CRITICAL = "critical"  # Life safety, national security


class PhysicalDependency(str, Enum):
    """Dependency on physical world interaction."""

    NONE = "none"  # Fully digital
    MINIMAL = "minimal"  # Occasional physical tasks
    MODERATE = "moderate"  # Regular physical components
    HIGH = "high"  # Primarily physical work
    EXCLUSIVE = "exclusive"  # Cannot be done digitally


class AutomationCategory(str, Enum):
    """Overall automation potential category."""

    FULLY_AUTOMATABLE = "fully_automatable"
    HIGHLY_AUTOMATABLE = "highly_automatable"
    PARTIALLY_AUTOMATABLE = "partially_automatable"
    AUGMENTABLE = "augmentable"  # AI assists but human leads
    NOT_AUTOMATABLE = "not_automatable"


class ScrapeStatus(str, Enum):
    """Status of a scrape operation."""

    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
