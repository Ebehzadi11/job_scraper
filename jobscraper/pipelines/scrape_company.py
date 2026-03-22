"""
Single company scraping pipeline.

This is the main pipeline for scraping a single company's careers page.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Optional

from jobscraper.collectors import HTTPCollector, PlaywrightCollector, CollectorResult
from jobscraper.config import settings
from jobscraper.db import get_session
from jobscraper.extractors.base import BaseExtractor
from jobscraper.logging import get_logger, ScrapeLogger
from jobscraper.registry import resolve_extractor, resolve_extractor_by_type
from jobscraper.schemas import JobPostingIn
from jobscraper.services.normalization import normalize_job_posting
from jobscraper.services.persistence import (
    upsert_job_posting,
    create_scrape_run,
    complete_scrape_run,
    mark_jobs_inactive,
)
from jobscraper.services.raw_storage import save_raw_html


@dataclass
class ScrapeResult:
    """Result of a company scrape operation."""

    company_name: str
    careers_url: str
    success: bool
    jobs_found: int = 0
    jobs_inserted: int = 0
    jobs_updated: int = 0
    duration_ms: int = 0
    error: Optional[str] = None
    jobs: list[JobPostingIn] = field(default_factory=list)


async def scrape_company(
    company_name: str,
    careers_url: str,
    source_type: Optional[str] = None,
    use_browser: bool = False,
    fetch_details: bool = True,
    max_detail_pages: int = 50,
    logger: Optional[ScrapeLogger] = None,
) -> ScrapeResult:
    """
    Scrape jobs from a company's careers page.

    This pipeline:
    1. Fetches HTML from the careers page
    2. Saves raw HTML for debugging
    3. Resolves the appropriate extractor
    4. Extracts job listings
    5. Optionally fetches job detail pages
    6. Parses sections, tools/skills, and semantic signals
    7. Normalizes and persists job records

    Args:
        company_name: Company name
        careers_url: URL of careers page
        source_type: Optional ATS type (auto-detected if not provided)
        use_browser: Use Playwright instead of HTTP
        fetch_details: Fetch individual job detail pages
        max_detail_pages: Maximum detail pages to fetch
        logger: Optional logger instance

    Returns:
        ScrapeResult with job data and statistics
    """
    start_time = time.perf_counter()
    log = logger or get_logger(company_name)

    result = ScrapeResult(
        company_name=company_name,
        careers_url=careers_url,
        success=False,
    )

    # Create collector
    collector_type = "playwright" if use_browser else "http"
    log.info("[CONFIG]", f"Using {collector_type} collector")

    try:
        # Step 1: Fetch HTML
        log.info("[FETCH]", f"Fetching {careers_url}")

        collector = PlaywrightCollector() if use_browser else HTTPCollector()

        try:
            fetch_result: CollectorResult = await collector.fetch(careers_url)
        finally:
            await collector.close()

        if not fetch_result.success:
            log.error("[FETCH]", f"Failed: {fetch_result.error}")
            result.error = fetch_result.error
            result.duration_ms = int((time.perf_counter() - start_time) * 1000)
            return result

        log.success(
            "[FETCH]",
            f"Retrieved {fetch_result.size_kb:.1f}KB in {fetch_result.elapsed_ms}ms",
        )

        # Step 2: Save raw HTML
        raw_path = save_raw_html(fetch_result.html, company_name, careers_url)
        log.info("[PERSIST]", f"Saved raw HTML to {raw_path.name}")

        # Step 3: Resolve extractor
        if source_type:
            extractor = resolve_extractor_by_type(source_type)
            log.info("[EXTRACT]", f"Using {extractor.name} extractor (specified)")
        else:
            extractor = resolve_extractor(careers_url, fetch_result.html)
            log.info("[EXTRACT]", f"Resolved extractor: {extractor.name}")

        # Step 4: Extract job listings
        jobs = extractor.extract_job_list(
            company_name=company_name,
            source_url=careers_url,
            html=fetch_result.html,
        )

        log.success("[EXTRACT]", f"Found {len(jobs)} job listings")
        result.jobs_found = len(jobs)

        if not jobs:
            result.success = True
            result.duration_ms = int((time.perf_counter() - start_time) * 1000)
            return result

        # Step 5: Fetch detail pages (optional)
        if fetch_details and len(jobs) <= max_detail_pages:
            jobs = await _fetch_job_details(
                jobs=jobs,
                extractor=extractor,
                use_browser=use_browser,
                company_name=company_name,
                logger=log,
            )

        # Step 6: Normalize and enrich jobs
        log.info("[NORMALIZE]", f"Normalizing {len(jobs)} jobs")
        normalized_jobs = []
        for job in jobs:
            normalized = normalize_job_posting(job)
            normalized.raw_html_path = str(raw_path)
            normalized_jobs.append(normalized)

        # Step 7: Persist to database
        log.info("[PERSIST]", f"Saving {len(normalized_jobs)} jobs to database")

        session = get_session()
        scrape_run = create_scrape_run(
            session=session,
            company_name=company_name,
            careers_url=careers_url,
            source_type=extractor.source_type,
            collector_type=collector_type,
        )

        inserted = 0
        updated = 0
        seen_urls = set()

        for job in normalized_jobs:
            try:
                job_record, is_new, was_updated = upsert_job_posting(session, job)

                if is_new:
                    inserted += 1
                elif was_updated:
                    updated += 1

                if job.canonical_job_url:
                    seen_urls.add(job.canonical_job_url)

            except Exception as e:
                log.warn("[PERSIST]", f"Failed to save job '{job.job_title}': {e}")

        # Mark jobs not seen as inactive
        inactive_count = mark_jobs_inactive(session, company_name, seen_urls)
        if inactive_count > 0:
            log.info("[DEDUPE]", f"Marked {inactive_count} jobs as inactive")

        # Complete scrape run
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        complete_scrape_run(
            session=session,
            run=scrape_run,
            status="success",
            jobs_found=len(jobs),
            jobs_inserted=inserted,
            jobs_updated=updated,
            duration_ms=duration_ms,
        )

        log.success(
            "[PERSIST]",
            f"Saved {len(normalized_jobs)} jobs ({inserted} new, {updated} updated)",
        )

        result.success = True
        result.jobs_found = len(jobs)
        result.jobs_inserted = inserted
        result.jobs_updated = updated
        result.duration_ms = duration_ms
        result.jobs = normalized_jobs

        return result

    except Exception as e:
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        log.error("[EXTRACT]", f"Pipeline error: {str(e)}")

        result.error = str(e)
        result.duration_ms = duration_ms
        return result


async def _fetch_job_details(
    jobs: list[JobPostingIn],
    extractor: BaseExtractor,
    use_browser: bool,
    company_name: str,
    logger: ScrapeLogger,
    max_concurrent: int = 4,
) -> list[JobPostingIn]:
    """
    Fetch details for each job posting.

    Args:
        jobs: List of jobs with basic info
        extractor: Extractor to use
        use_browser: Whether to use Playwright
        company_name: Company name for logging
        logger: Logger instance
        max_concurrent: Maximum concurrent requests

    Returns:
        List of jobs with full details
    """
    jobs_with_urls = [j for j in jobs if j.canonical_job_url]

    if not jobs_with_urls:
        return jobs

    logger.info("[FETCH]", f"Fetching {len(jobs_with_urls)} job detail pages")

    semaphore = asyncio.Semaphore(max_concurrent)
    collector = PlaywrightCollector() if use_browser else HTTPCollector()

    async def fetch_detail(job: JobPostingIn) -> JobPostingIn:
        async with semaphore:
            try:
                result = await collector.fetch(job.canonical_job_url)
                if result.success:
                    # Save raw HTML
                    save_raw_html(
                        result.html,
                        company_name,
                        job.canonical_job_url,
                    )
                    # Extract details
                    return extractor.extract_job_details(job, result.html)
            except Exception as e:
                logger.warn(
                    "[FETCH]",
                    f"Failed to fetch details for '{job.job_title}': {e}",
                )
            return job

    try:
        enriched_jobs = await asyncio.gather(*[fetch_detail(j) for j in jobs_with_urls])
    finally:
        await collector.close()

    # Merge enriched jobs with those that had no URL
    jobs_without_urls = [j for j in jobs if not j.canonical_job_url]
    return list(enriched_jobs) + jobs_without_urls
