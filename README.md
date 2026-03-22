# Job Scraper

Production-grade job scraping system for AI automation analysis.

## Overview

This system is the data foundation for an AI job automation marketplace. Unlike typical job scrapers that only collect basic listing data, this scraper is optimized for **downstream automation analysis**.

The scraper collects and normalizes enough job data so that a later analysis layer can determine:

1. **What tasks the job contains**
2. **Which tasks are automatable by AI agents**
3. **The overall automation opportunity for that role**

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATA PIPELINE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌───────────┐    ┌──────────┐    ┌──────────┐ │
│  │Collectors│───▶│ Extractors│───▶│  Parsers │───▶│ Services │ │
│  │(HTTP/    │    │(Greenhouse│    │(Sections │    │(Persist, │ │
│  │Playwright)│    │Lever/etc) │    │Tools/    │    │Normalize)│ │
│  └──────────┘    └───────────┘    │Signals)  │    └──────────┘ │
│                                   └──────────┘                  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                       SCHEMA LAYERS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌──────────┐    ┌───────────────────────┐  │
│  │ JobPosting  │───▶│ JobTask  │───▶│ TaskAutomationScore   │  │
│  │ (scraped)   │    │ (future) │    │ (future)              │  │
│  └─────────────┘    └──────────┘    └───────────────────────┘  │
│         │                                      │                │
│         └──────────────────────────────────────┘                │
│                           │                                     │
│                           ▼                                     │
│              ┌─────────────────────────┐                       │
│              │ JobAutomationSummary    │                       │
│              │ (future)                │                       │
│              └─────────────────────────┘                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Why This Scraper Collects More Data

Traditional job scrapers collect:
- Job title
- Company
- Location
- Link

**This scraper collects:**

| Category | Fields |
|----------|--------|
| **Identity** | Title, department, team, location, remote type, employment type, seniority |
| **Full Content** | Complete description, responsibilities, requirements, preferred qualifications, benefits |
| **Extracted Data** | Tools mentioned, skills mentioned, certifications, education requirements, years of experience |
| **Semantic Signals** | Customer-facing score, communication intensity, judgment intensity, repetition intensity |
| **Analysis Metadata** | Compliance sensitivity, physical world dependency, normalized role family |

This data enables future analysis to determine which parts of a job can be automated by AI.

## Installation

```bash
# Clone the repository
cd job_scraper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium
```

## Quick Start

### 1. Initialize the Database

```bash
python -m jobscraper.cli initdb
```

### 2. Scrape a Single Company

```bash
# Using HTTP collector
python -m jobscraper.cli scrape-company \
    --company "Stripe" \
    --url "https://boards.greenhouse.io/stripe"

# Using Playwright (for JavaScript-heavy pages)
python -m jobscraper.cli scrape-company \
    --company "Vercel" \
    --url "https://vercel.com/careers" \
    --browser
```

### 3. Scrape All Configured Companies

```bash
python -m jobscraper.cli scrape-all
```

### 4. View Results

```bash
# Show statistics
python -m jobscraper.cli stats

# List jobs
python -m jobscraper.cli list-jobs --limit 20

# List configured sources
python -m jobscraper.cli list-sources
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./data/jobscraper.db` | Database connection string |
| `USER_AGENT` | Chrome UA | HTTP User-Agent header |
| `REQUEST_TIMEOUT_SECONDS` | `30` | Request timeout |
| `MAX_CONCURRENCY` | `4` | Concurrent scrape operations |
| `PLAYWRIGHT_HEADLESS` | `true` | Run browser headlessly |

### Company Sources

Configure companies in `sources/companies.yaml`:

```yaml
companies:
  - company_name: Stripe
    careers_url: https://boards.greenhouse.io/stripe
    source_type: greenhouse
    use_browser: false
    enabled: true

  - company_name: Vercel
    careers_url: https://vercel.com/careers
    source_type: lever
    use_browser: true
    enabled: true
```

Supported source types:
- `greenhouse` - Greenhouse ATS
- `lever` - Lever ATS
- `ashby` - Ashby ATS
- `generic` - Generic careers pages

## CLI Commands

| Command | Description |
|---------|-------------|
| `initdb` | Initialize database tables |
| `scrape-company` | Scrape a single company |
| `scrape-all` | Scrape all enabled companies |
| `list-sources` | List configured companies |
| `list-jobs` | List jobs in database |
| `stats` | Show database statistics |
| `validate` | Validate configuration |
| `version` | Show version |

## Schema Layers

### 1. JobPosting (Implemented)

The core scraped data model. Contains:
- Source identification (URL, company, ATS type)
- Core fields (title, department, location, salary)
- Full content (description, responsibilities, requirements)
- Extracted data (tools, skills, certifications)
- Semantic signals for automation analysis

### 2. JobTask (Future)

Decomposed tasks from job descriptions:

```python
JobTask:
  - task_text: "Respond to customer support tickets"
  - task_category: "customer_service"
  - input_structure: "semi_structured"
  - output_structure: "semi_structured"
  - requires_judgment: "low"
  - requires_human_interaction: "async"
```

### 3. TaskAutomationScore (Future)

Automation potential scores per task:

```python
TaskAutomationScore:
  - overall_automation_score: 85
  - ai_feasibility_score: 90
  - error_impact_score: 20
  - automation_category: "highly_automatable"
```

### 4. JobAutomationSummary (Future)

Aggregated automation analysis:

```python
JobAutomationSummary:
  - overall_automation_potential: 65
  - tasks_fully_automatable_pct: 40
  - tasks_partially_automatable_pct: 35
  - recommended_ai_tools: ["chatbot", "email_automation"]
```

## Project Structure

```
jobscraper/
├── __init__.py
├── config.py          # Configuration (pydantic-settings)
├── cli.py             # Typer CLI
├── db.py              # Database setup
├── models.py          # SQLModel database models
├── schemas.py         # Pydantic schemas
├── registry.py        # Extractor registry
├── enums.py           # Enumeration types
├── logging.py         # Structured logging
├── utils/             # Utility functions
│   ├── urls.py        # URL manipulation
│   ├── hashing.py     # Content hashing
│   ├── text.py        # Text processing
│   ├── files.py       # File operations
│   └── time.py        # Time utilities
├── collectors/        # HTML collection
│   ├── base.py        # Base interface
│   ├── http_collector.py      # HTTPX-based
│   └── playwright_collector.py # Browser-based
├── extractors/        # Job extraction
│   ├── base.py        # Base interface
│   ├── greenhouse.py  # Greenhouse ATS
│   ├── lever.py       # Lever ATS
│   ├── ashby.py       # Ashby ATS
│   └── generic_careers.py # Generic fallback
├── parsers/           # Content parsing
│   ├── sections.py    # Section extraction
│   ├── tools_skills.py # Tools/skills extraction
│   └── semantic_signals.py # Automation signals
├── services/          # Business logic
│   ├── raw_storage.py # HTML storage
│   ├── normalization.py # Data normalization
│   ├── dedupe.py      # Deduplication
│   └── persistence.py # Database operations
└── pipelines/         # Orchestration
    ├── discover.py    # Source discovery
    ├── scrape_company.py # Single company
    └── scrape_all.py  # Batch scraping
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=jobscraper

# Run specific test file
pytest tests/test_extractors.py
```

## Next Steps

### 1. Job Detail Extraction Hardening

Current extractors focus on job listing pages. Enhance detail page parsing:
- Better section detection algorithms
- Handle more HTML structures
- Extract salary information more reliably

### 2. LLM-Based Task Decomposition

Add a pipeline stage that uses an LLM to:
- Decompose job descriptions into discrete tasks
- Classify task characteristics (input/output structure, judgment needed)
- Populate the `JobTask` table

### 3. Rules-Based Automation Scoring

Implement scoring logic that:
- Scores each task based on extracted characteristics
- Considers tool availability and integration complexity
- Aggregates into job-level automation potential
- Populates `TaskAutomationScore` and `JobAutomationSummary`

## License

MIT
