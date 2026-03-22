"""
Deduplication service for job postings.

Provides utilities for computing deduplication keys and checking for duplicates.
"""

from typing import Optional

from sqlmodel import Session, select

from jobscraper.models import JobPosting
from jobscraper.utils.hashing import compute_content_hash, compute_job_dedupe_key


def compute_dedupe_key(
    source_type: str,
    company_name: str,
    canonical_url: Optional[str] = None,
    external_job_id: Optional[str] = None,
    job_title: Optional[str] = None,
    location: Optional[str] = None,
) -> str:
    """
    Compute a deduplication key for a job posting.

    Priority order:
    1. Canonical URL (most reliable)
    2. source_type + external_job_id
    3. source_type + company_name + job_title + location

    Args:
        source_type: ATS type
        company_name: Company name
        canonical_url: Canonical job URL
        external_job_id: External job ID from ATS
        job_title: Job title
        location: Job location

    Returns:
        Deduplication key string
    """
    if canonical_url:
        return f"url:{compute_content_hash(canonical_url.lower())}"

    if external_job_id:
        return f"ext:{source_type}:{external_job_id}"

    if job_title:
        return f"title:{compute_job_dedupe_key(source_type, company_name, job_title, location)}"

    # Fallback - this should rarely happen
    return f"company:{compute_content_hash(f'{source_type}:{company_name}'.lower())}"


def is_duplicate(
    session: Session,
    source_type: str,
    company_name: str,
    canonical_url: Optional[str] = None,
    external_job_id: Optional[str] = None,
) -> tuple[bool, Optional[JobPosting]]:
    """
    Check if a job posting already exists.

    Args:
        session: Database session
        source_type: ATS type
        company_name: Company name
        canonical_url: Canonical job URL
        external_job_id: External job ID

    Returns:
        Tuple of (is_duplicate, existing_job)
    """
    # Check by canonical URL first (most reliable)
    if canonical_url:
        statement = select(JobPosting).where(JobPosting.canonical_job_url == canonical_url)
        result = session.exec(statement).first()
        if result:
            return True, result

    # Check by external job ID
    if external_job_id:
        statement = select(JobPosting).where(
            JobPosting.source_type == source_type,
            JobPosting.external_job_id == external_job_id,
        )
        result = session.exec(statement).first()
        if result:
            return True, result

    return False, None


def find_similar_jobs(
    session: Session,
    company_name: str,
    job_title: str,
    location: Optional[str] = None,
    threshold: float = 0.9,
) -> list[JobPosting]:
    """
    Find similar jobs based on title and location.

    This is a simple implementation. For production, consider
    using fuzzy matching or vector similarity.

    Args:
        session: Database session
        company_name: Company name
        job_title: Job title to match
        location: Optional location to match
        threshold: Similarity threshold (not used in simple implementation)

    Returns:
        List of similar job postings
    """
    # Simple exact match for now
    statement = select(JobPosting).where(
        JobPosting.company_name == company_name,
        JobPosting.job_title == job_title,
    )

    if location:
        statement = statement.where(JobPosting.location_text == location)

    return list(session.exec(statement).all())


def has_content_changed(
    existing_hash: Optional[str],
    new_hash: str,
) -> bool:
    """
    Check if content has changed based on hash comparison.

    Args:
        existing_hash: Hash of existing content
        new_hash: Hash of new content

    Returns:
        True if content has changed
    """
    if not existing_hash:
        return True

    return existing_hash != new_hash
