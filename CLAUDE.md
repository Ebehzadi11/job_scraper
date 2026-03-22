# Job Scraper

Full-stack job scraping platform: React dashboard + Python scraper pipeline.

## Quick Links

| Topic | Documentation |
|-------|---------------|
| Scraper rules & patterns | [docs/scraper-guidelines.md](docs/scraper-guidelines.md) |
| Frontend (React) | [docs/frontend.md](docs/frontend.md) |
| Extractors overview | [docs/extractors/README.md](docs/extractors/README.md) |
| Greenhouse extractor | [docs/extractors/greenhouse.md](docs/extractors/greenhouse.md) |
| Lever extractor | [docs/extractors/lever.md](docs/extractors/lever.md) |
| Ashby extractor | [docs/extractors/ashby.md](docs/extractors/ashby.md) |
| Generic extractor | [docs/extractors/generic.md](docs/extractors/generic.md) |

## Architecture

```
src/                    React dashboard (TypeScript)
        ↓
    Supabase            PostgreSQL + real-time
        ↓
jobscraper/             Python scraper (CLI)
```

## Project Layout

```
├── src/                      # React frontend
│   ├── components/ui/        # shadcn/ui (don't modify)
│   ├── components/scraper/   # Dashboard components
│   └── lib/supabase.ts       # Supabase client
│
├── jobscraper/               # Python scraper
│   ├── extractors/           # ATS parsers (greenhouse, lever, ashby, generic)
│   ├── collectors/           # HTTP + Playwright fetchers
│   ├── pipelines/            # Orchestration
│   └── services/             # Persistence, deduplication
│
├── sources/companies.yaml    # Scraping targets
├── tests/                    # Python tests
└── docs/                     # Detailed documentation
```

## Essential Commands

### Frontend
```bash
npm run dev              # Dev server
npm run build            # Production build
```

### Python Scraper
```bash
pip install -e ".[dev]"  # Install
playwright install       # Browser setup

python -m jobscraper.cli discover      # Run discovery
python -m jobscraper.cli scrape <name> # Single company
pytest                                  # Run tests
```

## Environment Setup

Copy `.env.example` → `.env`:
```
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
SUPABASE_PROJECT_ID=xxx
```

## Key Concepts

### Extractor Selection
Greenhouse → Lever → Ashby → Generic (fallback)

### Collector Choice
- **HTTP**: Default, fast, static pages
- **Playwright**: JavaScript-rendered, SPAs

### Data Flow
```
Company YAML → Collector → Extractor → Normalizer → Deduplicator → DB
```

## Path Aliases

- `@/*` → `./src/*` (frontend)

## When Adding Features

| Task | Read First |
|------|------------|
| New extractor | [docs/extractors/README.md](docs/extractors/README.md), [docs/scraper-guidelines.md](docs/scraper-guidelines.md) |
| Scraper changes | [docs/scraper-guidelines.md](docs/scraper-guidelines.md) |
| Dashboard UI | [docs/frontend.md](docs/frontend.md) |
| New company source | [docs/scraper-guidelines.md](docs/scraper-guidelines.md) → "Adding New Sources" |
