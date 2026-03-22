# Extractors

ATS-specific extractors for parsing job listings from career pages.

## Overview

Each extractor handles a specific ATS (Applicant Tracking System) platform. The registry tries extractors in order until one matches.

## Extractor Comparison

| Extractor | URL Pattern | Collector | Reliability | Notes |
|-----------|-------------|-----------|-------------|-------|
| [Greenhouse](greenhouse.md) | `greenhouse.io` | HTTP | High | Most common ATS |
| [Lever](lever.md) | `lever.co` | HTTP | High | Clean HTML structure |
| [Ashby](ashby.md) | `ashbyhq.com` | Playwright | Medium | Requires JS, JSON extraction |
| [Generic](generic.md) | Fallback | Either | Low | Heuristic-based |

## Selection Logic

```
URL/HTML Input
      │
      ▼
┌─────────────────┐
│  Greenhouse?    │──Yes──▶ GreenhouseExtractor
└────────┬────────┘
         │ No
         ▼
┌─────────────────┐
│    Lever?       │──Yes──▶ LeverExtractor
└────────┬────────┘
         │ No
         ▼
┌─────────────────┐
│    Ashby?       │──Yes──▶ AshbyExtractor
└────────┬────────┘
         │ No
         ▼
┌─────────────────┐
│  Careers page?  │──Yes──▶ GenericExtractor
└────────┬────────┘
         │ No
         ▼
    Skip / Error
```

## Extractor Interface

All extractors inherit from `BaseExtractor` and implement:

```python
class BaseExtractor:
    name: str           # Identifier (e.g., "greenhouse")
    source_type: str    # ATS type for records

    def can_handle(self, url: str, html: str) -> bool:
        """Return True if this extractor can parse the page."""
        ...

    def extract_job_list(
        self,
        company_name: str,
        source_url: str,
        html: str,
    ) -> list[JobPostingIn]:
        """Extract job listings from a careers page."""
        ...

    def extract_job_details(
        self,
        job: JobPostingIn,
        html: str,
    ) -> JobPostingIn:
        """Enrich job with full description from detail page."""
        ...
```

## Adding a New Extractor

1. **Identify the ATS** - Look for patterns in URL/HTML
2. **Create extractor file**: `jobscraper/extractors/{name}.py`
3. **Implement interface** - `can_handle`, `extract_job_list`, `extract_job_details`
4. **Register** in `jobscraper/extractors/__init__.py`
5. **Add tests** in `tests/test_extractors.py`
6. **Document** in `docs/extractors/{name}.md`

## Documentation Template

Each extractor doc should include:

- URL patterns
- Detection logic
- HTML/JSON structure patterns
- Selectors used (table format)
- Known issues
- Edge cases
- Improvement opportunities
- Learnings log

## Quick Reference

### Common Selectors by ATS

| ATS | Job Container | Title | Location | Department |
|-----|---------------|-------|----------|------------|
| Greenhouse | `.opening` | `a` text | `.location` | Section `h2` |
| Lever | `.posting` | `.posting-title h5` | `.location` span | `.posting-category-title` |
| Ashby | JSON or `[data-testid*="job"]` | `title` field | `location` field | `department` field |
| Generic | `[class*='job']` | `h1-h5` or link | `[class*='location']` | `[class*='department']` |

### Extraction Strategies by ATS

| ATS | Primary Strategy | Fallback |
|-----|------------------|----------|
| Greenhouse | Section-based HTML | Flat list, link scan |
| Lever | Grouped postings | Flat postings, link scan |
| Ashby | `__NEXT_DATA__` JSON | HTML parsing |
| Generic | Container selectors | Link heuristics, Schema.org |

## Individual Extractor Docs

- **[Greenhouse](greenhouse.md)** - Standard HTML patterns, section-based layout
- **[Lever](lever.md)** - Category classification, employment normalization
- **[Ashby](ashby.md)** - JSON-first approach, Next.js handling
- **[Generic](generic.md)** - Multi-strategy heuristics, Schema.org support
