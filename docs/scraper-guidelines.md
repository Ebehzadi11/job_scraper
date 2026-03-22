# Scraper Guidelines

General rules, patterns, and best practices for the job scraper pipeline.

## Core Principles

1. **Be a good citizen** - Respect robots.txt, rate limits, and server resources
2. **Fail gracefully** - Log errors, continue processing other items
3. **Data quality first** - Validate and normalize all extracted data
4. **Idempotent operations** - Re-running should not create duplicates

## Architecture

### Pipeline Flow

```
Company Source (YAML)
       │
       ▼
   Collector (HTTP/Playwright)
       │
       ▼
   Extractor (ATS-specific)
       │
       ▼
   Normalizer (clean/standardize)
       │
       ▼
   Deduplicator (content hash)
       │
       ▼
   Persistence (SQLite/Supabase)
```

### When to Use Each Collector

| Collector | Use When |
|-----------|----------|
| HTTP (httpx) | Static HTML, fast, low resource |
| Playwright | JavaScript-rendered, dynamic content, SPAs |

**Default to HTTP** unless:
- Page is blank or incomplete with HTTP
- Content loads via JavaScript
- ATS is known to require JS (e.g., Ashby)

## Extraction Patterns

### Extractor Selection Order

1. **Greenhouse** - `greenhouse.io` in URL
2. **Lever** - `lever.co` in URL
3. **Ashby** - `ashbyhq.com` in URL
4. **Generic** - Fallback heuristics

### Detection Best Practices

```python
def can_handle(self, url: str, html: str) -> bool:
    # 1. Check URL first (fast, reliable)
    if "greenhouse.io" in url.lower():
        return True

    # 2. Fall back to HTML markers (slower, more robust)
    if "grnhse" in html.lower():
        return True

    return False
```

### Extraction Strategy

1. **Try structured data first** - JSON-LD, embedded JSON, APIs
2. **Fall back to semantic HTML** - Known class names, IDs
3. **Last resort: heuristics** - Link patterns, text matching

## Data Quality Rules

### Required Fields

Every job posting MUST have:
- `job_title` - Non-empty, > 3 characters
- `canonical_job_url` - Valid absolute URL
- `source_name` - Company identifier
- `source_type` - ATS type

### Field Normalization

| Field | Rules |
|-------|-------|
| `job_title` | Trim whitespace, collapse spaces |
| `location_text` | Normalize "Remote", "San Francisco, CA" format |
| `employment_type` | Map to: `full_time`, `part_time`, `contract`, `internship` |
| `department` | Title case, trim |

### URL Handling

```python
# Always make URLs absolute
job_url = urljoin(source_url, relative_href)

# Remove tracking parameters
job_url = remove_utm_params(job_url)

# Normalize trailing slashes
job_url = job_url.rstrip("/")
```

## Deduplication

### Content Hashing

Jobs are deduplicated by content hash:

```python
hash_input = f"{company}|{title}|{location}|{description[:500]}"
content_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
```

### What Triggers a New Version

- Title change
- Location change
- Significant description change (>20% diff)

### What Does NOT Trigger a New Version

- Whitespace changes
- Minor punctuation
- Reordered sections

## Error Handling

### Retry Strategy

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=1, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError))
)
async def fetch_page(url: str) -> str:
    ...
```

### Error Categories

| Category | Action |
|----------|--------|
| Network timeout | Retry with backoff |
| 404 Not Found | Log, skip, mark source as potentially stale |
| 403 Forbidden | Switch to Playwright, check rate limiting |
| 5xx Server Error | Retry with backoff |
| Parse error | Log warning, continue with partial data |

### Logging Standards

```python
# Info: Normal operations
logger.info(f"Scraped {len(jobs)} jobs from {company}")

# Warning: Recoverable issues
logger.warning(f"No jobs found for {company}, page may have changed")

# Error: Failures requiring attention
logger.error(f"Failed to parse {url}: {e}", exc_info=True)
```

## Rate Limiting

### Default Limits

- **Per domain**: 1 request/second
- **Concurrent**: 4 domains max
- **Playwright**: 2 concurrent browsers

### Respectful Scraping

```python
# Add random jitter
await asyncio.sleep(1 + random.uniform(0, 0.5))

# Honor Retry-After headers
if response.status_code == 429:
    retry_after = int(response.headers.get("Retry-After", 60))
    await asyncio.sleep(retry_after)
```

## Testing Requirements

### Unit Tests Required For

- [ ] Each extractor's `can_handle()` method
- [ ] Job list extraction with sample HTML
- [ ] Job detail extraction
- [ ] Edge cases (empty page, malformed HTML)

### Test Data

Store sample HTML in `tests/fixtures/`:
```
tests/
├── fixtures/
│   ├── greenhouse_list.html
│   ├── greenhouse_detail.html
│   ├── lever_list.html
│   └── ...
└── test_extractors.py
```

## Adding New Sources

### Company YAML Format

```yaml
sources:
  - name: company-slug        # URL-safe identifier
    display_name: Company Inc # Human-readable name
    url: https://...          # Careers page URL
    ats: greenhouse           # ATS type
    collector: http           # http or playwright
    enabled: true             # Toggle scraping
```

### Validation Checklist

Before adding a new source:
- [ ] Verify ATS type detection works
- [ ] Test with HTTP collector first
- [ ] Check if jobs extract correctly
- [ ] Verify job detail pages parse
- [ ] Add to `sources/companies.yaml`

## Anti-Patterns

### Do NOT

- Hard-code selectors without fallbacks
- Assume HTML structure is stable
- Skip error handling for "simple" pages
- Store raw HTML without compression
- Ignore robots.txt or rate limits
- Create extractors for single companies

### Do

- Use multiple selector strategies
- Log extraction failures with context
- Compress stored HTML (gzip)
- Add delays between requests
- Create extractors for ATS platforms, not individual companies
