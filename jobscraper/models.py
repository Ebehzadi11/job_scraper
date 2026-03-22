"""
SQLModel database models.

Defines the core data models for:
1. JobPosting - Scraped and normalized job data
2. JobTask - Extracted tasks from job descriptions (future)
3. TaskAutomationScore - Automation scores per task (future)
4. JobAutomationSummary - Aggregated automation analysis (future)
"""

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel, Column, JSON


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class JobPosting(SQLModel, table=True):
    """
    Core job posting model.

    Contains all scraped data plus normalized fields for automation analysis.
    This schema is designed to support downstream task decomposition and
    automation scoring.
    """

    __tablename__ = "job_postings"

    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Source identification
    source_name: str = Field(index=True, description="Name of the source (e.g., company name)")
    source_type: str = Field(index=True, description="ATS type: greenhouse, lever, ashby, generic")
    source_url: str = Field(description="Original careers page URL")
    canonical_job_url: Optional[str] = Field(
        default=None, unique=True, index=True, description="Canonical URL for this specific job"
    )
    company_name: str = Field(index=True, description="Company name")
    external_job_id: Optional[str] = Field(default=None, index=True, description="External job ID from ATS")

    # Timestamps
    scrape_timestamp: datetime = Field(default_factory=utc_now, description="When this record was scraped")
    first_seen_timestamp: datetime = Field(default_factory=utc_now, description="First time we saw this job")
    last_seen_timestamp: datetime = Field(default_factory=utc_now, description="Last time we saw this job")

    # Status and tracking
    posting_status: str = Field(default="active", description="active, inactive, pending")
    raw_html_path: Optional[str] = Field(default=None, description="Path to stored raw HTML")
    page_hash: Optional[str] = Field(default=None, index=True, description="Hash of page content for change detection")

    # Core identity fields
    job_title: str = Field(description="Job title")
    department: Optional[str] = Field(default=None, description="Department or team")
    team: Optional[str] = Field(default=None, description="Specific team within department")
    location_text: Optional[str] = Field(default=None, description="Location as displayed")
    remote_type: Optional[str] = Field(default=None, description="remote, hybrid, onsite, unknown")
    employment_type: Optional[str] = Field(default=None, description="full_time, part_time, contract, etc.")
    seniority_level: Optional[str] = Field(default=None, description="intern, entry, mid, senior, staff, etc.")

    # Salary information
    salary_min: Optional[float] = Field(default=None, description="Minimum salary")
    salary_max: Optional[float] = Field(default=None, description="Maximum salary")
    salary_currency: Optional[str] = Field(default=None, description="Currency code (USD, EUR, etc.)")

    # Full content fields - critical for task decomposition
    full_description_text: Optional[str] = Field(default=None, description="Complete job description text")
    responsibilities_text: Optional[str] = Field(default=None, description="Extracted responsibilities section")
    requirements_text: Optional[str] = Field(default=None, description="Extracted requirements section")
    preferred_qualifications_text: Optional[str] = Field(
        default=None, description="Extracted preferred qualifications"
    )
    benefits_text: Optional[str] = Field(default=None, description="Extracted benefits section")

    # Extracted structured data (stored as JSON)
    tools_mentioned: Optional[list] = Field(default=None, sa_column=Column(JSON), description="Tools mentioned")
    skills_mentioned: Optional[list] = Field(default=None, sa_column=Column(JSON), description="Skills mentioned")
    certifications_mentioned: Optional[list] = Field(
        default=None, sa_column=Column(JSON), description="Certifications mentioned"
    )
    education_requirements: Optional[str] = Field(default=None, description="Education requirements text")
    years_experience_required: Optional[int] = Field(default=None, description="Years of experience required")

    # Semantic/normalized fields for automation analysis
    normalized_role_family: Optional[str] = Field(
        default=None, description="Normalized role family (engineering, sales, etc.)"
    )
    normalized_sub_role: Optional[str] = Field(default=None, description="Normalized sub-role")
    normalized_industry: Optional[str] = Field(default=None, description="Industry classification")

    # Automation analysis signals (heuristic scores 0-100)
    customer_facing_score: Optional[int] = Field(
        default=None, description="How customer-facing is this role (0-100)"
    )
    communication_intensity: Optional[int] = Field(
        default=None, description="Communication requirements intensity (0-100)"
    )
    judgment_intensity: Optional[int] = Field(
        default=None, description="Judgment/decision-making requirements (0-100)"
    )
    repetition_intensity: Optional[int] = Field(
        default=None, description="How repetitive are the tasks (0-100)"
    )
    tool_dependency_signals: Optional[list] = Field(
        default=None, sa_column=Column(JSON), description="Tool dependency signals"
    )
    compliance_sensitivity: Optional[str] = Field(default=None, description="Compliance risk level")
    physical_world_dependency: Optional[str] = Field(default=None, description="Physical dependency level")
    language_requirements: Optional[list] = Field(
        default=None, sa_column=Column(JSON), description="Language requirements"
    )

    # Operational fields
    is_active: bool = Field(default=True, index=True, description="Is posting currently active")
    created_at: datetime = Field(default_factory=utc_now, description="Record creation time")
    updated_at: datetime = Field(default_factory=utc_now, description="Record last update time")


class JobTask(SQLModel, table=True):
    """
    Extracted task from a job posting.

    Future: LLM will decompose job descriptions into discrete tasks.
    Each task can then be scored for automation potential.
    """

    __tablename__ = "job_tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    job_posting_id: int = Field(foreign_key="job_postings.id", index=True)

    # Task identification
    task_text: str = Field(description="The task description text")
    task_category: Optional[str] = Field(default=None, description="Category of task")
    task_sequence: int = Field(default=0, description="Order in which task appears")

    # Task characteristics
    input_structure: Optional[str] = Field(default=None, description="How structured inputs are")
    output_structure: Optional[str] = Field(default=None, description="How structured outputs are")
    requires_judgment: Optional[str] = Field(default=None, description="Judgment level required")
    requires_human_interaction: Optional[str] = Field(default=None, description="Human interaction level")
    requires_physical: bool = Field(default=False, description="Requires physical presence")
    requires_real_time: bool = Field(default=False, description="Requires real-time response")
    compliance_sensitive: bool = Field(default=False, description="Compliance/regulatory sensitive")

    # Tools and skills needed for this task
    tools_required: Optional[list] = Field(default=None, sa_column=Column(JSON))
    skills_required: Optional[list] = Field(default=None, sa_column=Column(JSON))

    # Metadata
    extracted_by: Optional[str] = Field(default=None, description="Method used to extract (llm, heuristic)")
    confidence_score: Optional[float] = Field(default=None, description="Extraction confidence 0-1")
    created_at: datetime = Field(default_factory=utc_now)


class TaskAutomationScore(SQLModel, table=True):
    """
    Automation score for a specific task.

    Future: Each task is scored on multiple dimensions to determine
    its automation potential.
    """

    __tablename__ = "task_automation_scores"

    id: Optional[int] = Field(default=None, primary_key=True)
    job_task_id: int = Field(foreign_key="job_tasks.id", index=True)

    # Core automation scores (0-100)
    overall_automation_score: int = Field(description="Overall automation potential 0-100")
    ai_feasibility_score: int = Field(description="How feasible with current AI 0-100")
    data_availability_score: int = Field(description="Is training data available 0-100")
    integration_complexity_score: int = Field(description="System integration difficulty 0-100")

    # Risk scores (0-100, higher = more risk)
    error_impact_score: int = Field(description="Impact of errors 0-100")
    compliance_risk_score: int = Field(description="Regulatory/compliance risk 0-100")
    human_oversight_need: int = Field(description="Need for human oversight 0-100")

    # Categorization
    automation_category: Optional[str] = Field(
        default=None, description="fully_automatable, highly_automatable, partially_automatable, etc."
    )
    recommended_approach: Optional[str] = Field(default=None, description="Recommended automation approach")
    blockers: Optional[list] = Field(default=None, sa_column=Column(JSON), description="Automation blockers")

    # Scoring metadata
    scored_by: Optional[str] = Field(default=None, description="Scoring method (rules, llm, hybrid)")
    model_version: Optional[str] = Field(default=None, description="Model version if LLM scored")
    created_at: datetime = Field(default_factory=utc_now)


class JobAutomationSummary(SQLModel, table=True):
    """
    Aggregated automation analysis for a job posting.

    Future: Combines task-level scores into an overall job automation profile.
    """

    __tablename__ = "job_automation_summaries"

    id: Optional[int] = Field(default=None, primary_key=True)
    job_posting_id: int = Field(foreign_key="job_postings.id", unique=True, index=True)

    # Aggregate scores (0-100)
    overall_automation_potential: int = Field(description="Overall job automation potential 0-100")
    tasks_fully_automatable_pct: float = Field(description="Percentage of tasks fully automatable")
    tasks_partially_automatable_pct: float = Field(description="Percentage of tasks partially automatable")
    tasks_not_automatable_pct: float = Field(description="Percentage of tasks not automatable")

    # Task breakdown
    total_tasks_identified: int = Field(description="Total tasks identified in job")
    tasks_analyzed: int = Field(description="Number of tasks analyzed")

    # Category assignments
    automation_category: str = Field(description="Overall automation category")
    primary_blockers: Optional[list] = Field(
        default=None, sa_column=Column(JSON), description="Primary automation blockers"
    )
    automation_opportunities: Optional[list] = Field(
        default=None, sa_column=Column(JSON), description="Key automation opportunities"
    )

    # AI agent recommendations
    recommended_ai_tools: Optional[list] = Field(
        default=None, sa_column=Column(JSON), description="Recommended AI tools/agents"
    )
    implementation_complexity: Optional[str] = Field(
        default=None, description="low, medium, high, very_high"
    )
    estimated_time_savings_pct: Optional[float] = Field(
        default=None, description="Estimated time savings percentage"
    )

    # Metadata
    analysis_version: Optional[str] = Field(default=None, description="Analysis pipeline version")
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ScrapeRun(SQLModel, table=True):
    """
    Record of a scrape operation.

    Tracks history of scrape runs for monitoring and debugging.
    """

    __tablename__ = "scrape_runs"

    id: Optional[int] = Field(default=None, primary_key=True)
    company_name: str = Field(index=True)
    careers_url: str
    source_type: str
    collector_type: str

    # Results
    status: str = Field(description="idle, running, success, error")
    jobs_found: int = Field(default=0)
    jobs_inserted: int = Field(default=0)
    jobs_updated: int = Field(default=0)
    duration_ms: int = Field(default=0)

    # Error tracking
    error_message: Optional[str] = Field(default=None)

    # Timestamps
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: Optional[datetime] = Field(default=None)
