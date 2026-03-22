# Ashby Extractor

## Overview
Ashby is a modern ATS that heavily uses React and dynamic rendering. Job boards are hosted on `jobs.ashbyhq.com`.

## URL Patterns

```
jobs.ashbyhq.com/{company}
jobs.ashbyhq.com/{company}/{job_id}
{company}.ashbyhq.com
```

## Detection Logic

**URL-based:**
- Contains `ashbyhq.com` or `ashby`

**HTML-based:**
- Contains `__NEXT_DATA__` (Next.js)
- Contains `ashby-job` class

## Extraction Strategy

Ashby requires a **JSON-first approach** because:
1. Content is rendered client-side (React/Next.js)
2. Job data is embedded in `__NEXT_DATA__` script
3. HTML parsing is unreliable without JavaScript execution

### Extraction Order
1. Try `__NEXT_DATA__` JSON extraction
2. Try `__INITIAL_STATE__` JSON extraction
3. Fall back to HTML parsing (requires Playwright)

## JSON Structure Patterns

### Pattern 1: Next.js __NEXT_DATA__
```html
<script id="__NEXT_DATA__" type="application/json">
{
  "props": {
    "pageProps": {
      "jobs": [
        {
          "id": "abc123",
          "title": "Software Engineer",
          "department": "Engineering",
          "location": {"name": "San Francisco"}
        }
      ]
    }
  }
}
</script>
```

### Pattern 2: Initial State
```html
<script>
window.__INITIAL_STATE__ = {
  "jobs": [...]
};
</script>
```

## JSON Field Mappings

| Field | Possible Keys |
|-------|---------------|
| Title | `title`, `name`, `jobTitle`, `position` |
| URL | `url`, `link`, `applyUrl` |
| ID | `id`, `jobId`, `externalId` |
| Department | `department`, `team`, `departmentName` |
| Location | `location`, `locationName`, `office` |

**Location can be:**
- String: `"San Francisco"`
- Object: `{"name": "San Francisco", "city": "SF"}`

## HTML Fallback Selectors

| Element | Selectors |
|---------|-----------|
| Job Cards | `[data-testid*="job"]`, `.job-posting`, `.ashby-job-posting` |
| Title | `h2`, `h3`, `h4`, `[class*='title']` |
| Location | `[class*='location']` |
| Department | `[class*='department']`, `[class*='team']` |

## Recursive Job Finding

The extractor includes a recursive search (`_find_jobs_in_dict`) that:
1. Searches up to 5 levels deep
2. Looks for arrays with job-like objects
3. Identifies job arrays by key names: `jobs`, `jobPostings`, `openings`, `positions`
4. Validates by checking if first item has `title`, `name`, `jobTitle`, or `position`

## Known Issues

1. **Client-side rendering**: HTML may be empty without JavaScript
   - Solution: Always use Playwright collector for Ashby

2. **Varying JSON structures**: Different Ashby configurations use different paths
   - Solution: Recursive search with multiple fallbacks

3. **Location as object**: Must handle both string and object formats
   - Solution: Check type and extract `.name` or `.city`

## Edge Cases

- Custom Next.js page structures
- Jobs loaded via API after initial render
- Nested JSON with unusual paths

## Improvement Opportunities

- [ ] Handle paginated API responses
- [ ] Extract application deadline
- [ ] Parse compensation data from JSON
- [ ] Handle multiple department assignments
- [ ] Detect job posting status (open/closed)
- [ ] Support API-based extraction (bypass HTML entirely)

## Collector Recommendation

**Always use Playwright** for Ashby boards:
```yaml
sources:
  - name: example
    url: https://jobs.ashbyhq.com/example
    ats: ashby
    collector: playwright  # Required
```

## Test Cases

See `tests/test_extractors.py` for test coverage.

## Learnings Log

<!-- Add discoveries here as you encounter new patterns -->

### 2024-XX-XX
- Initial implementation with JSON-first approach
- Added recursive job finding for varied structures
- Location field can be string or object
