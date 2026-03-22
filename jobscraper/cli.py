"""
Command-line interface for the job scraper.

Uses Typer for a modern CLI experience.
"""

import asyncio
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from jobscraper import __version__

app = typer.Typer(
    name="jobscraper",
    help="Production-grade job scraper for AI automation analysis",
    add_completion=False,
)

console = Console()


@app.command()
def initdb(
    drop: bool = typer.Option(False, "--drop", help="Drop existing tables first"),
):
    """
    Initialize the database.

    Creates all necessary tables for storing job data.
    """
    from jobscraper.db import init_db, drop_all_tables
    from jobscraper.config import settings
    from jobscraper.logging import get_logger

    logger = get_logger()

    # Ensure directories exist
    settings.ensure_directories()

    if drop:
        logger.warn("[INIT]", "Dropping existing tables")
        drop_all_tables()

    logger.info("[INIT]", "Creating database tables")
    init_db()
    logger.success("[INIT]", f"Database initialized at {settings.database_url}")


@app.command("scrape-company")
def scrape_company_cmd(
    company: str = typer.Option(..., "--company", "-c", help="Company name"),
    url: str = typer.Option(..., "--url", "-u", help="Careers page URL"),
    browser: bool = typer.Option(False, "--browser", "-b", help="Use Playwright browser"),
    source_type: Optional[str] = typer.Option(
        None,
        "--type",
        "-t",
        help="ATS type (greenhouse, lever, ashby, generic)",
    ),
    no_details: bool = typer.Option(
        False,
        "--no-details",
        help="Skip fetching individual job detail pages",
    ),
):
    """
    Scrape jobs from a single company's careers page.

    Example:
        jobscraper scrape-company --company "Stripe" --url "https://boards.greenhouse.io/stripe"
    """
    from jobscraper.db import init_db
    from jobscraper.config import settings
    from jobscraper.pipelines.scrape_company import scrape_company
    from jobscraper.logging import get_logger

    logger = get_logger()

    # Initialize
    settings.ensure_directories()
    init_db()

    logger.info("[INIT]", f"Scraping {company}")

    # Run scrape
    result = asyncio.run(
        scrape_company(
            company_name=company,
            careers_url=url,
            source_type=source_type,
            use_browser=browser,
            fetch_details=not no_details,
        )
    )

    # Print result
    if result.success:
        console.print()
        console.print(f"[green]Scrape completed successfully[/green]")
        console.print(f"  Jobs found: {result.jobs_found}")
        console.print(f"  Jobs inserted: {result.jobs_inserted}")
        console.print(f"  Jobs updated: {result.jobs_updated}")
        console.print(f"  Duration: {result.duration_ms / 1000:.1f}s")
    else:
        console.print()
        console.print(f"[red]Scrape failed: {result.error}[/red]")
        raise typer.Exit(1)


@app.command("scrape-all")
def scrape_all_cmd(
    concurrency: int = typer.Option(
        0,
        "--concurrency",
        "-j",
        help="Maximum concurrent scrapes (0 = use config)",
    ),
    no_details: bool = typer.Option(
        False,
        "--no-details",
        help="Skip fetching individual job detail pages",
    ),
):
    """
    Scrape all enabled companies from configuration.

    Reads companies from sources/companies.yaml and scrapes each one.
    """
    from jobscraper.db import init_db
    from jobscraper.config import settings
    from jobscraper.pipelines.scrape_all import scrape_all
    from jobscraper.logging import get_logger

    logger = get_logger()

    # Initialize
    settings.ensure_directories()
    init_db()

    logger.info("[INIT]", "Starting batch scrape of all companies")

    # Run scrape
    result = asyncio.run(
        scrape_all(
            max_concurrent=concurrency,
            fetch_details=not no_details,
        )
    )

    # Exit code based on results
    if result.failed > 0:
        raise typer.Exit(1)


@app.command("list-sources")
def list_sources():
    """
    List configured company sources.
    """
    from jobscraper.pipelines.discover import load_sources

    sources = load_sources()

    if not sources:
        console.print("[yellow]No sources configured[/yellow]")
        return

    table = Table(title="Configured Sources")
    table.add_column("Company", style="cyan")
    table.add_column("URL")
    table.add_column("Type", style="magenta")
    table.add_column("Browser", style="yellow")
    table.add_column("Enabled", style="green")

    for source in sources:
        table.add_row(
            source.company_name,
            source.careers_url[:50] + "..." if len(source.careers_url) > 50 else source.careers_url,
            source.source_type,
            "Yes" if source.use_browser else "No",
            "Yes" if source.enabled else "No",
        )

    console.print(table)


@app.command("list-jobs")
def list_jobs(
    company: Optional[str] = typer.Option(None, "--company", "-c", help="Filter by company"),
    active: bool = typer.Option(True, "--active/--all", help="Only show active jobs"),
    limit: int = typer.Option(50, "--limit", "-n", help="Maximum jobs to show"),
):
    """
    List jobs from the database.
    """
    from jobscraper.db import init_db, get_session
    from jobscraper.services.persistence import get_jobs_for_company, get_all_jobs

    init_db()
    session = get_session()

    if company:
        jobs = get_jobs_for_company(session, company, active_only=active, limit=limit)
    else:
        jobs = get_all_jobs(session, active_only=active, limit=limit)

    if not jobs:
        console.print("[yellow]No jobs found[/yellow]")
        return

    table = Table(title=f"Jobs ({len(jobs)} shown)")
    table.add_column("ID", style="dim")
    table.add_column("Title", style="cyan")
    table.add_column("Company", style="magenta")
    table.add_column("Location")
    table.add_column("Type", style="yellow")
    table.add_column("Active", style="green")

    for job in jobs:
        table.add_row(
            str(job.id),
            job.job_title[:40] + "..." if len(job.job_title) > 40 else job.job_title,
            job.company_name,
            (job.location_text or "")[:25],
            job.source_type,
            "Yes" if job.is_active else "No",
        )

    console.print(table)


@app.command("stats")
def show_stats():
    """
    Show database statistics.
    """
    from sqlmodel import select, func

    from jobscraper.db import init_db, get_session
    from jobscraper.models import JobPosting, ScrapeRun

    init_db()
    session = get_session()

    # Job stats
    total_jobs = session.exec(select(func.count(JobPosting.id))).one()
    active_jobs = session.exec(
        select(func.count(JobPosting.id)).where(JobPosting.is_active == True)
    ).one()
    companies = session.exec(
        select(func.count(func.distinct(JobPosting.company_name)))
    ).one()

    # Scrape run stats
    total_runs = session.exec(select(func.count(ScrapeRun.id))).one()
    successful_runs = session.exec(
        select(func.count(ScrapeRun.id)).where(ScrapeRun.status == "success")
    ).one()

    console.print()
    console.print("[bold]Database Statistics[/bold]")
    console.print()
    console.print(f"  Total jobs:     {total_jobs}")
    console.print(f"  Active jobs:    {active_jobs}")
    console.print(f"  Companies:      {companies}")
    console.print()
    console.print(f"  Total scrapes:  {total_runs}")
    console.print(f"  Successful:     {successful_runs}")
    console.print()


@app.command("validate")
def validate_sources():
    """
    Validate sources configuration.
    """
    from jobscraper.pipelines.discover import validate_sources as _validate

    errors = _validate()

    if errors:
        console.print("[red]Validation errors:[/red]")
        for error in errors:
            console.print(f"  - {error}")
        raise typer.Exit(1)
    else:
        console.print("[green]Configuration is valid[/green]")


@app.command("version")
def version():
    """
    Show version information.
    """
    console.print(f"jobscraper v{__version__}")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
