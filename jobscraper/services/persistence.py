"""
Persistence service for job postings.

Handles database operations for job postings including upserts.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session, select

from jobscraper.db import get_session
from jobscraper.models import JobPosting, ScrapeRun
from jobscraper.schemas import JobPostingIn
from jobscraper.services.dedupe import is_duplicate, has_content_changed


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


def upsert_job_posting(
    session: Session,
    job_in: JobPostingIn,
) -> tuple[JobPosting, bool, bool]:
    """
    Upsert a job posting.

    Creates a new record or updates an existing one based on:
    1. canonical_job_url (if present)
    2. source_type + external_job_id
    3. source_url as fallback

    Args:
        session: Database session
        job_in: JobPostingIn with job data

    Returns:
        Tuple of (JobPosting, is_new, was_updated)
    """
    # Check for existing record
    is_dup, existing = is_duplicate(
        session,
        job_in.source_type,
        job_in.company_name,
        job_in.canonical_job_url,
        job_in.external_job_id,
    )

    now = utc_now()

    if existing:
        # Update existing record
        was_updated = False

        # Check if content changed
        if job_in.page_hash and has_content_changed(existing.page_hash, job_in.page_hash):
            was_updated = True

        # Update fields
        for field, value in job_in.model_dump(exclude_unset=True).items():
            if value is not None and hasattr(existing, field):
                setattr(existing, field, value)

        # Update timestamps
        existing.last_seen_timestamp = now
        existing.updated_at = now
        existing.scrape_timestamp = now
        existing.is_active = True

        session.add(existing)
        session.commit()
        session.refresh(existing)

        return existing, False, was_updated

    else:
        # Create new record
        job_data = job_in.model_dump()
        job_data["first_seen_timestamp"] = now
        job_data["last_seen_timestamp"] = now
        job_data["scrape_timestamp"] = now
        job_data["created_at"] = now
        job_data["updated_at"] = now
        job_data["is_active"] = True

        job = JobPosting(**job_data)
        session.add(job)
        session.commit()
        session.refresh(job)

        return job, True, False


def get_job_by_url(session: Session, url: str) -> Optional[JobPosting]:
    """
    Get a job posting by its canonical URL.

    Args:
        session: Database session
        url: Canonical job URL

    Returns:
        JobPosting or None
    """
    statement = select(JobPosting).where(JobPosting.canonical_job_url == url)
    return session.exec(statement).first()


def get_job_by_id(session: Session, job_id: int) -> Optional[JobPosting]:
    """
    Get a job posting by ID.

    Args:
        session: Database session
        job_id: Job ID

    Returns:
        JobPosting or None
    """
    return session.get(JobPosting, job_id)


def mark_jobs_inactive(
    session: Session,
    company_name: str,
    seen_urls: set[str],
) -> int:
    """
    Mark jobs as inactive if they weren't seen in the latest scrape.

    Args:
        session: Database session
        company_name: Company name
        seen_urls: Set of job URLs that were seen

    Returns:
        Number of jobs marked inactive
    """
    statement = select(JobPosting).where(
        JobPosting.company_name == company_name,
        JobPosting.is_active == True,
    )

    jobs = session.exec(statement).all()
    marked_inactive = 0

    for job in jobs:
        if job.canonical_job_url and job.canonical_job_url not in seen_urls:
            job.is_active = False
            job.posting_status = "inactive"
            job.updated_at = utc_now()
            session.add(job)
            marked_inactive += 1

    session.commit()
    return marked_inactive


def get_jobs_for_company(
    session: Session,
    company_name: str,
    active_only: bool = True,
    limit: int = 1000,
) -> list[JobPosting]:
    """
    Get all jobs for a company.

    Args:
        session: Database session
        company_name: Company name
        active_only: Only return active jobs
        limit: Maximum number of jobs to return

    Returns:
        List of JobPosting objects
    """
    statement = select(JobPosting).where(JobPosting.company_name == company_name)

    if active_only:
        statement = statement.where(JobPosting.is_active == True)

    statement = statement.limit(limit)

    return list(session.exec(statement).all())


def get_all_jobs(
    session: Session,
    active_only: bool = True,
    limit: int = 1000,
) -> list[JobPosting]:
    """
    Get all jobs.

    Args:
        session: Database session
        active_only: Only return active jobs
        limit: Maximum number of jobs to return

    Returns:
        List of JobPosting objects
    """
    statement = select(JobPosting)

    if active_only:
        statement = statement.where(JobPosting.is_active == True)

    statement = statement.limit(limit)

    return list(session.exec(statement).all())


def create_scrape_run(
    session: Session,
    company_name: str,
    careers_url: str,
    source_type: str,
    collector_type: str,
) -> ScrapeRun:
    """
    Create a new scrape run record.

    Args:
        session: Database session
        company_name: Company name
        careers_url: Careers URL
        source_type: ATS type
        collector_type: Collector type (http or playwright)

    Returns:
        ScrapeRun record
    """
    run = ScrapeRun(
        company_name=company_name,
        careers_url=careers_url,
        source_type=source_type,
        collector_type=collector_type,
        status="running",
        started_at=utc_now(),
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def complete_scrape_run(
    session: Session,
    run: ScrapeRun,
    status: str,
    jobs_found: int = 0,
    jobs_inserted: int = 0,
    jobs_updated: int = 0,
    duration_ms: int = 0,
    error_message: Optional[str] = None,
) -> ScrapeRun:
    """
    Complete a scrape run record.

    Args:
        session: Database session
        run: ScrapeRun to update
        status: Final status
        jobs_found: Number of jobs found
        jobs_inserted: Number of new jobs inserted
        jobs_updated: Number of jobs updated
        duration_ms: Duration in milliseconds
        error_message: Optional error message

    Returns:
        Updated ScrapeRun
    """
    run.status = status
    run.jobs_found = jobs_found
    run.jobs_inserted = jobs_inserted
    run.jobs_updated = jobs_updated
    run.duration_ms = duration_ms
    run.error_message = error_message
    run.completed_at = utc_now()

    session.add(run)
    session.commit()
    session.refresh(run)
    return run
