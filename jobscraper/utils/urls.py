"""
URL manipulation utilities.
"""

import re
from urllib.parse import urljoin, urlparse, urlunparse


def normalize_url(url: str) -> str:
    """
    Normalize a URL by:
    - Lowercasing the scheme and host
    - Removing trailing slashes
    - Removing default ports
    - Sorting query parameters
    """
    if not url:
        return ""

    parsed = urlparse(url.strip())

    # Lowercase scheme and netloc
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    # Remove default ports
    if netloc.endswith(":80") and scheme == "http":
        netloc = netloc[:-3]
    elif netloc.endswith(":443") and scheme == "https":
        netloc = netloc[:-4]

    # Remove trailing slash from path (unless it's just "/")
    path = parsed.path.rstrip("/") if parsed.path != "/" else parsed.path

    # Reconstruct URL
    normalized = urlunparse((
        scheme,
        netloc,
        path,
        parsed.params,
        parsed.query,
        "",  # Remove fragment
    ))

    return normalized


def make_absolute_url(base_url: str, relative_url: str) -> str:
    """
    Convert a relative URL to an absolute URL.

    Args:
        base_url: The base URL to resolve against
        relative_url: The relative URL to convert

    Returns:
        Absolute URL string
    """
    if not relative_url:
        return base_url

    # Already absolute
    if relative_url.startswith(("http://", "https://")):
        return relative_url

    return urljoin(base_url, relative_url)


def extract_domain(url: str) -> str:
    """
    Extract the domain from a URL.

    Examples:
        https://boards.greenhouse.io/stripe -> boards.greenhouse.io
        https://www.example.com/path -> www.example.com
    """
    if not url:
        return ""

    parsed = urlparse(url)
    return parsed.netloc.lower()


def extract_base_domain(url: str) -> str:
    """
    Extract the base domain (without subdomains) from a URL.

    Examples:
        https://boards.greenhouse.io/stripe -> greenhouse.io
        https://www.example.com/path -> example.com
    """
    domain = extract_domain(url)
    if not domain:
        return ""

    parts = domain.split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return domain


def is_greenhouse_url(url: str) -> bool:
    """Check if URL is a Greenhouse careers page."""
    domain = extract_domain(url)
    return "greenhouse.io" in domain


def is_lever_url(url: str) -> bool:
    """Check if URL is a Lever careers page."""
    domain = extract_domain(url)
    return "lever.co" in domain or "jobs.lever.co" in domain


def is_ashby_url(url: str) -> bool:
    """Check if URL is an Ashby careers page."""
    domain = extract_domain(url)
    return "ashbyhq.com" in domain or "jobs.ashbyhq.com" in domain


def extract_job_id_from_url(url: str) -> str | None:
    """
    Attempt to extract a job ID from a URL.

    Works with common patterns:
    - /jobs/12345
    - /jobs/12345-job-title
    - ?gh_jid=12345
    """
    if not url:
        return None

    # Try query parameter patterns
    import re
    from urllib.parse import parse_qs

    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)

    # Greenhouse pattern
    if "gh_jid" in query_params:
        return query_params["gh_jid"][0]

    # Path-based patterns
    path = parsed.path

    # Pattern: /jobs/12345 or /jobs/12345-title
    job_match = re.search(r"/jobs?/(\d+)", path)
    if job_match:
        return job_match.group(1)

    # Pattern: /positions/uuid
    uuid_match = re.search(
        r"/(?:positions?|jobs?)/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})",
        path,
        re.IGNORECASE,
    )
    if uuid_match:
        return uuid_match.group(1)

    # Last path segment as fallback
    segments = [s for s in path.split("/") if s]
    if segments:
        return segments[-1]

    return None
