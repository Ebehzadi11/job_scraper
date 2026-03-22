"""
Configuration management using pydantic-settings.

Loads configuration from environment variables and .env files.
"""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="jobscraper", description="Application name")

    # Database
    database_url: str = Field(
        default="sqlite:///./data/jobscraper.db",
        description="SQLAlchemy database URL",
    )

    # HTTP Settings
    user_agent: str = Field(
        default="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        description="User-Agent header for HTTP requests",
    )
    request_timeout_seconds: int = Field(
        default=30,
        description="Timeout for HTTP requests in seconds",
    )

    # Playwright Settings
    playwright_headless: bool = Field(
        default=True,
        description="Run Playwright in headless mode",
    )

    # Concurrency
    max_concurrency: int = Field(
        default=4,
        description="Maximum concurrent scrape operations",
    )

    # Storage Paths
    raw_html_dir: Path = Field(
        default=Path("./data/raw"),
        description="Directory for raw HTML snapshots",
    )
    export_dir: Path = Field(
        default=Path("./data/exports"),
        description="Directory for data exports",
    )
    companies_yaml_path: Path = Field(
        default=Path("./sources/companies.yaml"),
        description="Path to companies YAML configuration",
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.raw_html_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)

        # Ensure database directory exists
        db_path = self.database_url.replace("sqlite:///", "")
        if db_path.startswith("./"):
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
