"""
Scrape all configured companies.

Orchestrates scraping across all companies in the configuration.
"""

import asyncio
from dataclasses import dataclass
from typing import Optional

from rich.console import Console
from rich.table import Table

from jobscraper.logging import get_logger
from jobscraper.pipelines.discover import get_enabled_sources
from jobscraper.pipelines.scrape_company import scrape_company, ScrapeResult
from jobscraper.config import settings


@dataclass
class BatchScrapeResult:
    """Result of scraping all companies."""

    total_companies: int
    successful: int
    failed: int
    total_jobs_found: int
    total_jobs_inserted: int
    total_jobs_updated: int
    total_duration_ms: int
    results: list[ScrapeResult]


async def scrape_all(
    max_concurrent: int = 0,
    fetch_details: bool = True,
) -> BatchScrapeResult:
    """
    Scrape all enabled companies from configuration.

    Args:
        max_concurrent: Maximum concurrent company scrapes (0 = use settings)
        fetch_details: Whether to fetch individual job detail pages

    Returns:
        BatchScrapeResult with aggregated statistics
    """
    console = Console()
    logger = get_logger()

    # Load sources
    sources = get_enabled_sources()

    if not sources:
        logger.warn("[CONFIG]", "No enabled sources found in configuration")
        return BatchScrapeResult(
            total_companies=0,
            successful=0,
            failed=0,
            total_jobs_found=0,
            total_jobs_inserted=0,
            total_jobs_updated=0,
            total_duration_ms=0,
            results=[],
        )

    logger.info("[INIT]", f"Found {len(sources)} enabled companies to scrape")

    # Determine concurrency
    concurrency = max_concurrent or settings.max_concurrency
    logger.info("[CONFIG]", f"Using MAX_CONCURRENCY={concurrency}")

    # Create semaphore for rate limiting
    semaphore = asyncio.Semaphore(concurrency)

    async def scrape_with_semaphore(source) -> ScrapeResult:
        async with semaphore:
            return await scrape_company(
                company_name=source.company_name,
                careers_url=source.careers_url,
                source_type=source.source_type,
                use_browser=source.use_browser,
                fetch_details=fetch_details,
            )

    # Scrape all companies
    logger.info("[FETCH]", "Starting batch scrape")

    results = await asyncio.gather(*[scrape_with_semaphore(s) for s in sources])

    # Aggregate results
    successful = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success)
    total_jobs_found = sum(r.jobs_found for r in results)
    total_jobs_inserted = sum(r.jobs_inserted for r in results)
    total_jobs_updated = sum(r.jobs_updated for r in results)
    total_duration_ms = sum(r.duration_ms for r in results)

    batch_result = BatchScrapeResult(
        total_companies=len(sources),
        successful=successful,
        failed=failed,
        total_jobs_found=total_jobs_found,
        total_jobs_inserted=total_jobs_inserted,
        total_jobs_updated=total_jobs_updated,
        total_duration_ms=total_duration_ms,
        results=results,
    )

    # Print summary
    _print_summary(console, batch_result)

    return batch_result


def _print_summary(console: Console, result: BatchScrapeResult) -> None:
    """Print a summary table of scrape results."""
    console.print()

    # Results table
    table = Table(title="Scrape Results")
    table.add_column("Company", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Found", justify="right")
    table.add_column("New", justify="right", style="green")
    table.add_column("Updated", justify="right", style="yellow")
    table.add_column("Duration", justify="right")

    for r in result.results:
        status = "[green]OK[/green]" if r.success else f"[red]ERR[/red]"
        duration = f"{r.duration_ms / 1000:.1f}s"

        table.add_row(
            r.company_name,
            status,
            str(r.jobs_found),
            str(r.jobs_inserted),
            str(r.jobs_updated),
            duration,
        )

    console.print(table)

    # Summary stats
    console.print()
    console.print(f"[bold]Summary:[/bold]")
    console.print(f"  Companies: {result.successful}/{result.total_companies} successful")
    console.print(f"  Jobs found: {result.total_jobs_found}")
    console.print(f"  Jobs inserted: {result.total_jobs_inserted}")
    console.print(f"  Jobs updated: {result.total_jobs_updated}")
    console.print(f"  Total duration: {result.total_duration_ms / 1000:.1f}s")
    console.print()


async def scrape_companies_by_name(
    company_names: list[str],
    fetch_details: bool = True,
) -> BatchScrapeResult:
    """
    Scrape specific companies by name.

    Args:
        company_names: List of company names to scrape
        fetch_details: Whether to fetch individual job detail pages

    Returns:
        BatchScrapeResult with aggregated statistics
    """
    from jobscraper.pipelines.discover import get_source_by_name

    console = Console()
    logger = get_logger()

    sources = []
    for name in company_names:
        source = get_source_by_name(name)
        if source:
            sources.append(source)
        else:
            logger.warn("[CONFIG]", f"Company not found: {name}")

    if not sources:
        return BatchScrapeResult(
            total_companies=0,
            successful=0,
            failed=0,
            total_jobs_found=0,
            total_jobs_inserted=0,
            total_jobs_updated=0,
            total_duration_ms=0,
            results=[],
        )

    results = []
    for source in sources:
        result = await scrape_company(
            company_name=source.company_name,
            careers_url=source.careers_url,
            source_type=source.source_type,
            use_browser=source.use_browser,
            fetch_details=fetch_details,
        )
        results.append(result)

    # Aggregate
    successful = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success)
    total_jobs_found = sum(r.jobs_found for r in results)
    total_jobs_inserted = sum(r.jobs_inserted for r in results)
    total_jobs_updated = sum(r.jobs_updated for r in results)
    total_duration_ms = sum(r.duration_ms for r in results)

    batch_result = BatchScrapeResult(
        total_companies=len(sources),
        successful=successful,
        failed=failed,
        total_jobs_found=total_jobs_found,
        total_jobs_inserted=total_jobs_inserted,
        total_jobs_updated=total_jobs_updated,
        total_duration_ms=total_duration_ms,
        results=results,
    )

    _print_summary(console, batch_result)

    return batch_result
