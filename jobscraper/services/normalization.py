"""
Normalization service for job postings.

Normalizes sparse extractor output into complete JobPostingIn shapes.
"""

from typing import Optional

from jobscraper.schemas import JobPostingIn
from jobscraper.parsers.sections import parse_sections
from jobscraper.parsers.tools_skills import parse_tools_skills
from jobscraper.parsers.semantic_signals import parse_semantic_signals
from jobscraper.utils.hashing import compute_content_hash


def normalize_job_posting(
    job: JobPostingIn,
    full_html: Optional[str] = None,
) -> JobPostingIn:
    """
    Normalize and enrich a job posting with parsed data.

    Takes a sparse JobPostingIn from an extractor and enriches it with:
    - Section parsing (responsibilities, requirements, etc.)
    - Tools and skills extraction
    - Semantic signals for automation analysis
    - Content hash for change detection

    Args:
        job: JobPostingIn with basic data from extractor
        full_html: Optional HTML for hash computation

    Returns:
        Enriched JobPostingIn
    """
    # Compute content hash if we have the full description
    if job.full_description_text and not job.page_hash:
        job.page_hash = compute_content_hash(job.full_description_text)
    elif full_html and not job.page_hash:
        job.page_hash = compute_content_hash(full_html)

    # Parse sections from full description
    if job.full_description_text:
        sections = parse_sections(job.full_description_text)

        if sections.responsibilities and not job.responsibilities_text:
            job.responsibilities_text = sections.responsibilities
        if sections.requirements and not job.requirements_text:
            job.requirements_text = sections.requirements
        if sections.preferred_qualifications and not job.preferred_qualifications_text:
            job.preferred_qualifications_text = sections.preferred_qualifications
        if sections.benefits and not job.benefits_text:
            job.benefits_text = sections.benefits

    # Extract tools and skills
    text_to_parse = job.full_description_text or ""
    if job.requirements_text:
        text_to_parse += "\n" + job.requirements_text
    if job.responsibilities_text:
        text_to_parse += "\n" + job.responsibilities_text

    if text_to_parse:
        extracted = parse_tools_skills(text_to_parse)

        if extracted.tools and not job.tools_mentioned:
            job.tools_mentioned = extracted.tools
        if extracted.skills and not job.skills_mentioned:
            job.skills_mentioned = extracted.skills
        if extracted.certifications and not job.certifications_mentioned:
            job.certifications_mentioned = extracted.certifications

    # Extract semantic signals
    if text_to_parse or job.job_title:
        signals = parse_semantic_signals(text_to_parse, job.job_title)

        if signals.remote_type and not job.remote_type:
            job.remote_type = signals.remote_type
        if signals.employment_type and not job.employment_type:
            job.employment_type = signals.employment_type
        if signals.seniority_level and not job.seniority_level:
            job.seniority_level = signals.seniority_level
        if signals.years_experience and not job.years_experience_required:
            job.years_experience_required = signals.years_experience
        if signals.education_requirement and not job.education_requirements:
            job.education_requirements = signals.education_requirement
        if signals.normalized_role_family and not job.normalized_role_family:
            job.normalized_role_family = signals.normalized_role_family

        # Set analysis scores
        if signals.customer_facing_score is not None:
            job.customer_facing_score = signals.customer_facing_score
        if signals.communication_intensity is not None:
            job.communication_intensity = signals.communication_intensity
        if signals.judgment_intensity is not None:
            job.judgment_intensity = signals.judgment_intensity
        if signals.repetition_intensity is not None:
            job.repetition_intensity = signals.repetition_intensity

        if signals.compliance_sensitivity:
            job.compliance_sensitivity = signals.compliance_sensitivity
        if signals.physical_world_dependency:
            job.physical_world_dependency = signals.physical_world_dependency
        if signals.language_requirements:
            job.language_requirements = signals.language_requirements

    return job


def normalize_location(location: Optional[str]) -> Optional[str]:
    """
    Normalize location text.

    Standardizes common location formats.
    """
    if not location:
        return None

    # Basic cleanup
    location = location.strip()

    # Remove common prefixes
    prefixes = ["Location:", "Location", "Office:", "Based in:"]
    for prefix in prefixes:
        if location.lower().startswith(prefix.lower()):
            location = location[len(prefix):].strip()

    return location if location else None


def normalize_department(department: Optional[str]) -> Optional[str]:
    """
    Normalize department/team name.
    """
    if not department:
        return None

    # Basic cleanup
    department = department.strip()

    # Remove common prefixes
    prefixes = ["Department:", "Team:", "Group:"]
    for prefix in prefixes:
        if department.lower().startswith(prefix.lower()):
            department = department[len(prefix):].strip()

    return department if department else None


def merge_job_postings(
    existing: JobPostingIn,
    new: JobPostingIn,
) -> JobPostingIn:
    """
    Merge a new job posting with an existing one.

    Preserves existing data while updating with new information.
    Used for incremental updates when re-scraping.

    Args:
        existing: Existing job posting
        new: New job posting with potentially updated data

    Returns:
        Merged job posting
    """
    # Create a copy of existing
    merged = existing.model_copy()

    # Update fields that are set in new posting
    for field in new.model_fields:
        new_value = getattr(new, field)
        if new_value is not None:
            setattr(merged, field, new_value)

    return merged
