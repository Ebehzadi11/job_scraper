"""
Source discovery from configuration.

Loads company sources from YAML configuration.
"""

from pathlib import Path
from typing import Optional

import yaml

from jobscraper.config import settings
from jobscraper.schemas import CompanySource


def load_sources(config_path: Optional[Path] = None) -> list[CompanySource]:
    """
    Load company sources from YAML configuration.

    Args:
        config_path: Path to YAML file (defaults to settings.companies_yaml_path)

    Returns:
        List of CompanySource objects
    """
    path = config_path or settings.companies_yaml_path

    if not path.exists():
        return []

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    if not data or "companies" not in data:
        return []

    sources = []
    for company_data in data["companies"]:
        try:
            source = CompanySource(**company_data)
            sources.append(source)
        except Exception as e:
            # Log and skip invalid entries
            print(f"Warning: Invalid company entry: {company_data}. Error: {e}")

    return sources


def get_enabled_sources(config_path: Optional[Path] = None) -> list[CompanySource]:
    """
    Get only enabled company sources.

    Args:
        config_path: Path to YAML file

    Returns:
        List of enabled CompanySource objects
    """
    sources = load_sources(config_path)
    return [s for s in sources if s.enabled]


def get_source_by_name(
    company_name: str,
    config_path: Optional[Path] = None,
) -> Optional[CompanySource]:
    """
    Get a company source by name.

    Args:
        company_name: Company name to find
        config_path: Path to YAML file

    Returns:
        CompanySource or None
    """
    sources = load_sources(config_path)
    for source in sources:
        if source.company_name.lower() == company_name.lower():
            return source
    return None


def validate_sources(config_path: Optional[Path] = None) -> list[str]:
    """
    Validate company sources configuration.

    Args:
        config_path: Path to YAML file

    Returns:
        List of validation error messages
    """
    errors = []
    sources = load_sources(config_path)

    seen_names = set()
    seen_urls = set()

    for source in sources:
        # Check for duplicate names
        name_lower = source.company_name.lower()
        if name_lower in seen_names:
            errors.append(f"Duplicate company name: {source.company_name}")
        seen_names.add(name_lower)

        # Check for duplicate URLs
        if source.careers_url in seen_urls:
            errors.append(f"Duplicate URL: {source.careers_url}")
        seen_urls.add(source.careers_url)

        # Check URL format
        if not source.careers_url.startswith(("http://", "https://")):
            errors.append(f"Invalid URL for {source.company_name}: {source.careers_url}")

        # Check source type
        valid_types = ["greenhouse", "lever", "ashby", "generic"]
        if source.source_type not in valid_types:
            errors.append(
                f"Invalid source_type for {source.company_name}: {source.source_type}"
            )

    return errors
