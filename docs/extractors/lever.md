# Lever Extractor

## Overview
Lever is a popular ATS with clean, consistent HTML structure. Job boards are hosted on `jobs.lever.co`.

## URL Patterns

```
jobs.lever.co/{company}
jobs.lever.co/{company}/{job_id}
{company}.lever.co
```

## Detection Logic

**URL-based:**
- Contains `lever.co`

**HTML-based:**
- Contains `posting-category` class
- Contains `posting-title` class

## HTML Structure Patterns

### Pattern 1: Grouped Postings (Most Common)
```html
<div class="postings-group">
  <div class="posting-category-title">Engineering</div>
  <div class="posting">
    <a class="posting-title" href="/company/job-id">
      <h5>Software Engineer</h5>
    </a>
    <div class="posting-categories">
      <span class="location">San Francisco</span>
      <span class="commitment">Full-time</span>
    </div>
  </div>
</div>
```

### Pattern 2: Flat Posting List
```html
<div class="posting">
  <a class="posting-title" href="/company/job-id">
    <h5>Software Engineer</h5>
  </a>
</div>
```

## Selectors Used

| Element | Selectors |
|---------|-----------|
| Groups | `.postings-group` |
| Team Header | `.posting-category-title`, `.large-category-header` |
| Postings | `.posting` |
| Title Link | `.posting-title a`, `a.posting-title`, `h5 a` |
| Title Text | `.posting-title h5`, `.posting-name`, `h5` |
| Categories | `.posting-categories span`, `.posting-category` |
| Location | Category with `location` class |
| Team | Category with `team` or `department` class |
| Commitment | Category with `commitment` or `workplaceType` class |

## Job Detail Page

```html
<div class="posting-headline">
  <h2>Software Engineer</h2>
  <div class="posting-categories">
    <span class="location">San Francisco</span>
    <span class="workplaceTypes">Remote</span>
  </div>
</div>
<div class="section">
  <h3>About the Role</h3>
  <p>...</p>
</div>
```

## Category Classification

The extractor classifies posting categories by:
1. **Class name**: `location`, `team`, `commitment`
2. **Content heuristics**: If text contains "remote", "San Francisco", etc.

## Employment Type Normalization

| Lever Value | Normalized |
|-------------|------------|
| Full-time, Full time | `full_time` |
| Part-time, Part time | `part_time` |
| Contract | `contract` |
| Intern, Internship | `internship` |

## Known Issues

1. **Workplace type vs location**: Remote/Hybrid sometimes appears as location
   - Solution: Check `workplaceType` class specifically

2. **Missing department**: Some postings lack team categorization
   - Solution: Use group header as fallback

## Edge Cases

- Jobs with multiple locations
- Hybrid workplace types
- Custom commitment types

## Improvement Opportunities

- [ ] Handle workplace type (remote/hybrid/onsite) separately from location
- [ ] Extract salary ranges when disclosed
- [ ] Parse experience level requirements
- [ ] Handle multi-location postings
- [ ] Detect internal vs external postings

## Test Cases

See `tests/test_extractors.py` for test coverage.

## Learnings Log

<!-- Add discoveries here as you encounter new patterns -->

### 2024-XX-XX
- Initial implementation with grouped and flat patterns
- Added commitment normalization
