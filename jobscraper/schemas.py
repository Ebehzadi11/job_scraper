"""
Pydantic schemas for data validation and serialization.

These schemas define the input/output contracts for the pipeline:
Job Posting -> Job Tasks -> Task Automation Scores -> Job Automation Summary
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# ============================================================
# Job Posting Schemas
# ============================================================


class JobPostingIn(BaseModel):
    """Input schema for creating/updating a job posting."""

    model_config = ConfigDict(extra="ignore")

    # Source identification
    source_name: str
    source_type: str
    source_url: str
    canonical_job_url: Optional[str] = None
    company_name: str
    external_job_id: Optional[str] = None

    # Status
    posting_status: str = "active"
    raw_html_path: Optional[str] = None
    page_hash: Optional[str] = None

    # Core identity
    job_title: str
    department: Optional[str] = None
    team: Optional[str] = None
    location_text: Optional[str] = None
    remote_type: Optional[str] = None
    employment_type: Optional[str] = None
    seniority_level: Optional[str] = None

    # Salary
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None

    # Content
    full_description_text: Optional[str] = None
    responsibilities_text: Optional[str] = None
    requirements_text: Optional[str] = None
    preferred_qualifications_text: Optional[str] = None
    benefits_text: Optional[str] = None

    # Extracted data
    tools_mentioned: Optional[list[str]] = None
    skills_mentioned: Optional[list[str]] = None
    certifications_mentioned: Optional[list[str]] = None
    education_requirements: Optional[str] = None
    years_experience_required: Optional[int] = None

    # Semantic fields
    normalized_role_family: Optional[str] = None
    normalized_sub_role: Optional[str] = None
    normalized_industry: Optional[str] = None

    # Analysis signals
    customer_facing_score: Optional[int] = None
    communication_intensity: Optional[int] = None
    judgment_intensity: Optional[int] = None
    repetition_intensity: Optional[int] = None
    tool_dependency_signals: Optional[list[str]] = None
    compliance_sensitivity: Optional[str] = None
    physical_world_dependency: Optional[str] = None
    language_requirements: Optional[list[str]] = None


class JobPostingOut(BaseModel):
    """Output schema for job posting responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    source_name: str
    source_type: str
    source_url: str
    canonical_job_url: Optional[str]
    company_name: str
    external_job_id: Optional[str]

    scrape_timestamp: datetime
    first_seen_timestamp: datetime
    last_seen_timestamp: datetime
    posting_status: str

    job_title: str
    department: Optional[str]
    team: Optional[str]
    location_text: Optional[str]
    remote_type: Optional[str]
    employment_type: Optional[str]
    seniority_level: Optional[str]

    salary_min: Optional[float]
    salary_max: Optional[float]
    salary_currency: Optional[str]

    full_description_text: Optional[str]
    responsibilities_text: Optional[str]
    requirements_text: Optional[str]
    preferred_qualifications_text: Optional[str]
    benefits_text: Optional[str]

    tools_mentioned: Optional[list[str]]
    skills_mentioned: Optional[list[str]]
    certifications_mentioned: Optional[list[str]]
    education_requirements: Optional[str]
    years_experience_required: Optional[int]

    normalized_role_family: Optional[str]
    customer_facing_score: Optional[int]
    judgment_intensity: Optional[int]
    repetition_intensity: Optional[int]

    is_active: bool
    created_at: datetime
    updated_at: datetime


# ============================================================
# Job Task Schemas (Future)
# ============================================================


class JobTaskIn(BaseModel):
    """Input schema for creating a job task."""

    model_config = ConfigDict(extra="ignore")

    job_posting_id: int
    task_text: str
    task_category: Optional[str] = None
    task_sequence: int = 0

    input_structure: Optional[str] = None
    output_structure: Optional[str] = None
    requires_judgment: Optional[str] = None
    requires_human_interaction: Optional[str] = None
    requires_physical: bool = False
    requires_real_time: bool = False
    compliance_sensitive: bool = False

    tools_required: Optional[list[str]] = None
    skills_required: Optional[list[str]] = None

    extracted_by: Optional[str] = None
    confidence_score: Optional[float] = None


class JobTaskOut(BaseModel):
    """Output schema for job task responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    job_posting_id: int
    task_text: str
    task_category: Optional[str]
    task_sequence: int

    input_structure: Optional[str]
    output_structure: Optional[str]
    requires_judgment: Optional[str]
    requires_human_interaction: Optional[str]
    requires_physical: bool
    requires_real_time: bool
    compliance_sensitive: bool

    tools_required: Optional[list[str]]
    skills_required: Optional[list[str]]

    extracted_by: Optional[str]
    confidence_score: Optional[float]
    created_at: datetime


# ============================================================
# Task Automation Score Schemas (Future)
# ============================================================


class TaskAutomationScoreIn(BaseModel):
    """Input schema for task automation scoring."""

    model_config = ConfigDict(extra="ignore")

    job_task_id: int

    overall_automation_score: int = Field(ge=0, le=100)
    ai_feasibility_score: int = Field(ge=0, le=100)
    data_availability_score: int = Field(ge=0, le=100)
    integration_complexity_score: int = Field(ge=0, le=100)

    error_impact_score: int = Field(ge=0, le=100)
    compliance_risk_score: int = Field(ge=0, le=100)
    human_oversight_need: int = Field(ge=0, le=100)

    automation_category: Optional[str] = None
    recommended_approach: Optional[str] = None
    blockers: Optional[list[str]] = None

    scored_by: Optional[str] = None
    model_version: Optional[str] = None


class TaskAutomationScoreOut(BaseModel):
    """Output schema for task automation score responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    job_task_id: int

    overall_automation_score: int
    ai_feasibility_score: int
    data_availability_score: int
    integration_complexity_score: int

    error_impact_score: int
    compliance_risk_score: int
    human_oversight_need: int

    automation_category: Optional[str]
    recommended_approach: Optional[str]
    blockers: Optional[list[str]]

    scored_by: Optional[str]
    model_version: Optional[str]
    created_at: datetime


# ============================================================
# Job Automation Summary Schemas (Future)
# ============================================================


class JobAutomationSummaryIn(BaseModel):
    """Input schema for job automation summary."""

    model_config = ConfigDict(extra="ignore")

    job_posting_id: int

    overall_automation_potential: int = Field(ge=0, le=100)
    tasks_fully_automatable_pct: float = Field(ge=0, le=100)
    tasks_partially_automatable_pct: float = Field(ge=0, le=100)
    tasks_not_automatable_pct: float = Field(ge=0, le=100)

    total_tasks_identified: int
    tasks_analyzed: int

    automation_category: str
    primary_blockers: Optional[list[str]] = None
    automation_opportunities: Optional[list[str]] = None

    recommended_ai_tools: Optional[list[str]] = None
    implementation_complexity: Optional[str] = None
    estimated_time_savings_pct: Optional[float] = None

    analysis_version: Optional[str] = None


class JobAutomationSummaryOut(BaseModel):
    """Output schema for job automation summary responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    job_posting_id: int

    overall_automation_potential: int
    tasks_fully_automatable_pct: float
    tasks_partially_automatable_pct: float
    tasks_not_automatable_pct: float

    total_tasks_identified: int
    tasks_analyzed: int

    automation_category: str
    primary_blockers: Optional[list[str]]
    automation_opportunities: Optional[list[str]]

    recommended_ai_tools: Optional[list[str]]
    implementation_complexity: Optional[str]
    estimated_time_savings_pct: Optional[float]

    analysis_version: Optional[str]
    created_at: datetime
    updated_at: datetime


# ============================================================
# Scrape Run Schemas
# ============================================================


class ScrapeRunIn(BaseModel):
    """Input schema for recording a scrape run."""

    company_name: str
    careers_url: str
    source_type: str
    collector_type: str
    status: str = "running"


class ScrapeRunOut(BaseModel):
    """Output schema for scrape run responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    company_name: str
    careers_url: str
    source_type: str
    collector_type: str

    status: str
    jobs_found: int
    jobs_inserted: int
    jobs_updated: int
    duration_ms: int

    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]


# ============================================================
# Company Source Schema
# ============================================================


class CompanySource(BaseModel):
    """Schema for company source configuration from YAML."""

    company_name: str
    careers_url: str
    source_type: str
    use_browser: bool = False
    enabled: bool = True
