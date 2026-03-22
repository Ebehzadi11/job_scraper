# Job Scraper

A full-stack job scraping platform with a React dashboard and Python scraper pipeline that aggregates job postings from various company career pages.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                        │
│  src/                                                           │
│  ├── components/ui/       # shadcn/ui components                │
│  ├── components/scraper/  # Dashboard components                │
│  ├── lib/supabase.ts      # Supabase client                     │
│  └── types/               # TypeScript types                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Supabase (Backend)                         │
│  - PostgreSQL database                                          │
│  - Real-time subscriptions                                      │
│  - Row-level security                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Python Scraper (jobscraper/)                 │
│  ├── extractors/    # ATS-specific parsers                      │
│  ├── collectors/    # HTTP/Playwright fetchers                  │
│  ├── pipelines/     # Orchestration                             │
│  └── services/      # Persistence, deduplication                │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

### Frontend
- **Framework**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS + shadcn/ui (new-york style)
- **UI Components**: Radix UI primitives
- **Charts**: Recharts
- **Routing**: React Router v6
- **Forms**: React Hook Form + Zod

### Backend
- **Database**: Supabase (PostgreSQL)
- **Scraper**: Python 3.11+
- **HTTP Client**: httpx (async)
- **Browser Automation**: Playwright
- **HTML Parsing**: selectolax
- **CLI**: Typer + Rich

## Project Structure

```
job_scraper/
├── src/                      # React frontend
│   ├── components/
│   │   ├── ui/               # shadcn/ui (don't modify)
│   │   └── scraper/          # Dashboard components
│   ├── lib/
│   │   └── supabase.ts       # Supabase client
│   └── types/
│       └── supabase.ts       # Generated DB types
│
├── jobscraper/               # Python scraper package
│   ├── cli.py                # CLI entry point
│   ├── config.py             # Settings (pydantic-settings)
│   ├── schemas.py            # Pydantic models
│   ├── models.py             # SQLModel ORM models
│   ├── extractors/           # ATS-specific extractors
│   │   ├── greenhouse.py
│   │   ├── lever.py
│   │   ├── ashby.py
│   │   └── generic_careers.py
│   ├── collectors/           # Page fetchers
│   │   ├── http_collector.py
│   │   └── playwright_collector.py
│   ├── pipelines/            # Orchestration
│   │   ├── discover.py       # Find new jobs
│   │   ├── scrape_company.py # Single company
│   │   └── scrape_all.py     # All companies
│   ├── services/             # Business logic
│   │   ├── persistence.py    # DB operations
│   │   ├── dedupe.py         # Deduplication
│   │   └── normalization.py  # Text normalization
│   ├── parsers/              # Content parsing
│   │   ├── sections.py       # Job description sections
│   │   └── tools_skills.py   # Extract tools/skills
│   └── utils/                # Helpers
│       ├── hashing.py        # Content hashing
│       ├── urls.py           # URL utilities
│       └── text.py           # Text cleaning
│
├── tests/                    # Python tests
├── sources/                  # Company configs
│   └── companies.yaml
├── docs/                     # Documentation
│   └── extractors/           # Extractor learnings
└── data/                     # Local data (gitignored)
    ├── raw/                  # Raw HTML cache
    ├── exports/              # CSV/JSON exports
    └── jobscraper.db         # SQLite database
```

## Development Commands

### Frontend
```bash
npm run dev          # Start dev server
npm run build        # Type check + build
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Python Scraper
```bash
# Install dependencies
pip install -e ".[dev]"
playwright install

# CLI commands
python -m jobscraper.cli discover          # Discover jobs from all sources
python -m jobscraper.cli scrape <company>  # Scrape specific company
python -m jobscraper.cli export            # Export to CSV/JSON

# Run tests
pytest
pytest tests/test_extractors.py -v
```

## Key Types

### Frontend (TypeScript)
- `Company` - Source configuration
- `JobPosting` - Job listing data
- `ScrapeLog` - Pipeline logs
- `PipelineStats` - Dashboard stats

### Backend (Python)
- `JobPostingIn` - Input schema for job data
- `JobPostingDB` - SQLModel for persistence
- `CompanySource` - Company configuration
- `ATSType` - Enum: greenhouse, lever, ashby, generic
- `CollectorType` - Enum: http, playwright

## Extractor Architecture

Each ATS extractor implements:
1. `can_handle(url, html)` - Detect if page matches this ATS
2. `extract_job_list(...)` - Parse job listings from careers page
3. `extract_job_details(...)` - Parse full job description

**Extractor selection order:**
1. Greenhouse (boards.greenhouse.io)
2. Lever (jobs.lever.co)
3. Ashby (jobs.ashbyhq.com)
4. Generic (fallback heuristics)

See `docs/extractors/` for detailed patterns and learnings.

## Design System (Frontend)

- **Dark theme**: Background `#0F1117`, text `#F8F7F4`
- **Font**: Monospace throughout
- **Accent colors**: Amber (primary), Teal (success), Slate (borders)

## Adding New Extractors

1. Create `jobscraper/extractors/{ats_name}.py`
2. Inherit from `BaseExtractor`
3. Implement `can_handle`, `extract_job_list`, `extract_job_details`
4. Register in `jobscraper/extractors/__init__.py`
5. Add tests in `tests/test_extractors.py`
6. Document patterns in `docs/extractors/{ats_name}.md`

## Environment Variables

Copy `.env.example` to `.env` and configure:
- `VITE_SUPABASE_URL` - Supabase project URL
- `VITE_SUPABASE_ANON_KEY` - Supabase anon key
- `SUPABASE_PROJECT_ID` - For type generation
- `COMPANIES_YAML_PATH` - Path to company sources

## Path Aliases

- `@/*` maps to `./src/*` (frontend)
