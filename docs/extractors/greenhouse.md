# Greenhouse Extractor

## Overview
Greenhouse is one of the most popular ATS platforms. Job boards are typically hosted on `boards.greenhouse.io` or custom subdomains.

## URL Patterns

```
boards.greenhouse.io/{company}
boards.greenhouse.io/{company}/jobs/{job_id}
{company}.greenhouse.io
```

## Detection Logic

**URL-based:**
- Contains `greenhouse.io`

**HTML-based:**
- Contains `id="content"` with greenhouse markers
- Contains `grnhse` class prefixes

## HTML Structure Patterns

### Pattern 1: Section-Based Layout (Most Common)
```html
<section class="level-0" department_id="123">
  <h2>Engineering</h2>
  <div class="opening">
    <a href="/jobs/123">Software Engineer</a>
    <span class="location">San Francisco, CA</span>
  </div>
</section>
```

### Pattern 2: Flat Opening List
```html
<div class="opening">
  <a href="/jobs/123">Software Engineer</a>
</div>
```

### Pattern 3: Simple Links
```html
<a href="/jobs/123">Software Engineer</a>
```

## Selectors Used

| Element | Selectors |
|---------|-----------|
| Sections | `section.level-0`, `div.level-0`, `section[department_id]` |
| Department | `h2`, `h3`, `.department-name` |
| Openings | `div.opening`, `tr.opening`, `li.opening` |
| Job Link | `a` within opening |
| Location | `.location`, `span.location`, `.job-location` |

## Job Detail Page

```html
<div id="content">
  <h1>Software Engineer</h1>
  <div class="location">San Francisco, CA</div>
  <div class="department">Engineering</div>
  <div class="content">
    <!-- Full job description -->
  </div>
</div>
```

## Known Issues

1. **Dynamic loading**: Some Greenhouse boards load jobs via JavaScript
   - Solution: Use Playwright collector

2. **Custom styling**: Companies may override default classes
   - Solution: Fall back to link-based extraction

3. **Pagination**: Large job boards may paginate
   - TODO: Implement pagination handling

## Edge Cases

- Jobs without department groupings
- Custom domain masking (company uses own domain)
- Multiple locations per job

## Improvement Opportunities

- [ ] Handle `?gh_jid=` query parameter format
- [ ] Extract salary information when present
- [ ] Parse "Apply by" deadline dates
- [ ] Handle embedded application forms
- [ ] Detect and skip closed positions

## Test Cases

See `tests/test_extractors.py` for test coverage.

## Learnings Log

<!-- Add discoveries here as you encounter new patterns -->

### 2024-XX-XX
- Initial implementation with 3 extraction patterns
