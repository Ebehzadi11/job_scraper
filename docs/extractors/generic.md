# Generic Careers Extractor

## Overview
Fallback extractor for company career pages that don't use a known ATS. Uses heuristics and common patterns to find job listings.

## When Used
- Page doesn't match Greenhouse, Lever, or Ashby patterns
- URL or HTML contains career-related keywords
- Custom-built career pages

## Detection Logic

The extractor activates when any of these indicators are present:
- URL contains `career` or `jobs`
- HTML contains: `careers`, `job openings`, `open positions`, `join our team`, `we're hiring`

## Extraction Strategies

The extractor tries three strategies in order:

### Strategy 1: Job Container Selectors
Looks for elements matching common job listing patterns:

```css
.job-listing, .job-card, .job-item, .job-post
.career-item, .position-item, .opening
article.job, li.job
div[class*='job'], div[class*='career']
div[class*='position'], div[class*='opening']
tr.job, tr[class*='position']
```

### Strategy 2: Job Links
Scans for links with job-related patterns:

```css
a[href*="job"]
a[href*="career"]
a[href*="position"]
a[href*="opening"]
a[href*="apply"]
```

**Link classification heuristics:**

Positive indicators:
- URL contains `/job`, `/career`, `/position`, `/opening`, `/apply`
- Link text contains: engineer, manager, designer, analyst, developer

Negative indicators (filtered out):
- URL contains: about, contact, privacy, terms, login, sign
- Link text longer than 15 words

### Strategy 3: Schema.org Markup
Extracts from `application/ld+json` scripts with `@type: "JobPosting"`:

```json
{
  "@type": "JobPosting",
  "title": "Software Engineer",
  "url": "/jobs/123",
  "jobLocation": {
    "address": {
      "addressLocality": "San Francisco"
    }
  }
}
```

## Job Container Parsing

When a container is found, the extractor looks for:

| Element | Selectors |
|---------|-----------|
| Title | `h1`-`h5`, `[class*='title']`, `[class*='name']`, link text |
| Link | `a[href]` |
| Location | `[class*='location']` |
| Department | `[class*='department']`, `[class*='team']`, `[class*='category']` |

## Job Detail Page

Tries common content selectors:
```css
article
.job-description, .job-content, .job-details
#job-description
main, .content
```

Requires content to be >100 characters to be valid.

## Known Issues

1. **Low precision**: May capture non-job links
   - Solution: Filter by positive/negative indicators

2. **Missing metadata**: Location/department often unavailable
   - Solution: Parse from job detail pages

3. **Inconsistent structure**: Every site is different
   - Solution: Multiple fallback strategies

4. **JavaScript-rendered**: Many modern sites require JS
   - Solution: Use Playwright collector

## Edge Cases

- Single-page job listings
- Jobs embedded in iframes
- PDF job postings
- External job board links (Indeed, LinkedIn)

## Improvement Opportunities

- [ ] Learn from successful extractions per domain
- [ ] Add domain-specific selector overrides
- [ ] Detect and handle iframe-embedded job boards
- [ ] Parse structured data beyond Schema.org (RDFa, Microdata)
- [ ] Handle infinite scroll job lists
- [ ] Recognize common job title patterns for better filtering
- [ ] Track extraction success rate per domain

## When to Create a New Extractor

If you see a pattern appearing multiple times:
1. Document the URL pattern
2. Document the HTML structure
3. Create a dedicated extractor
4. Add to extractor registry

## Test Cases

See `tests/test_extractors.py` for test coverage.

## Learnings Log

<!-- Add discoveries here as you encounter new patterns -->

### 2024-XX-XX
- Initial implementation with 3-strategy approach
- Schema.org extraction for SEO-optimized pages
- Heuristic link classification

### Patterns Worth Monitoring
<!-- Track recurring patterns that might warrant dedicated extractors -->

| Domain Pattern | HTML Structure | Frequency |
|----------------|----------------|-----------|
| Example | `div.job-row > a.title` | 3 sites |
