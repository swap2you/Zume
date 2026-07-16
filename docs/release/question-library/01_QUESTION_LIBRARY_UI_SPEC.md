# Zume Question Library — Final UI and Product Specification

## 1. Product purpose

The Question Library has two uses:

1. **Interview preparation**
   - Study questions and answers by skill, level, role and importance.
   - Listen to questions and answers.
   - Bookmark, rate and build study sets.

2. **Interview operations**
   - Inspect the reviewed questions Zume may select for candidate packages.
   - Understand why a question is important.
   - Review scoring guidance, follow-ups and source provenance.

The screen must not look like a database query form.

## 2. Information architecture

Use three top-level modes:

- **Reviewed Library** — default
- **Draft Research** — clearly marked, never used in candidate packages
- **Coverage & Gaps**

A reviewer must never confuse draft quantity with reviewed quality.

## 3. Header

Display:

- Page title: `Question Library`
- Subtitle: `Reviewed interview questions, answer guidance, exercises and sources`
- Summary badges:
  - `Reviewed questions`
  - `Reviewed exercises`
  - `Covered domains`
  - `Open gaps`
- Last library validation date
- Validation status:
  - green `Validated`
  - amber `Warnings`
  - red `Blocked`

Do not display total draft + published records as a single “library questions”
number.

## 4. Search and filters

### 4.1 Search bar

One prominent search field:

`Search questions, answers, tools, scenarios or tags`

Behavior:

- 300 ms debounce;
- natural-language search;
- stop-word removal;
- strict match followed by ranked fallback;
- clear button;
- search history stored locally;
- keyboard shortcut `/`;
- API errors shown as errors, never as zero results.

### 4.2 Primary filters

Use dropdowns populated by the API facet endpoint:

- Domain
- Subdomain
- Level
- Priority
- Role track

Rules:

- Subdomain is disabled until a domain is selected.
- Subdomain values update when Domain changes.
- Every option displays a reviewed-record count:
  `Java (18)`.
- Only values that exist in the current selected mode are shown.
- `All` is the default.

### 4.3 Secondary filters

Place under `More filters`:

- Frequency
- Question type
- Experience range
- Source family
- Freshness status
- Tags
- Has exercise
- Has follow-ups
- Has code example
- Last verified date

These are also dropdowns or checkboxes. Do not use blank free-text inputs for
categorical values.

### 4.4 Active filter chips

Below filters show removable chips:

`Java ×` `Advanced ×` `P0 ×` `Senior SDET ×`

Include `Clear all`.

### 4.5 Sorting

Dropdown:

- Recommended
- Priority: P0 → P3
- Most frequently asked
- Recently verified
- Basic → advanced
- Advanced → basic
- Domain A → Z

## 5. Results header

Display:

- `18 reviewed questions`
- Page number and total pages
- `List` / `Compact` view switch
- `Build study set`
- `Export selected` only for reviewed content

When no records match:

- state why;
- list active filters;
- suggest removing the most restrictive filter;
- provide `Clear filters`;
- do not show a blank page.

When the API fails:

- red error banner;
- correlation/request ID;
- Retry;
- never replace it with “0 results”.

## 6. Question card

Collapsed card contains:

- Priority badge
- Level badge
- Domain / subdomain
- Frequency
- Role badges
- Question
- Estimated interview time
- Last verified date
- Bookmark
- `Open details`

Example:

```text
P0 · Intermediate
Java / Collections
Very common · Senior SDET · Lead SDET

A mutable object is used as a HashMap key. Explain why lookups can fail after
the object changes and how you would redesign the key.

4 minutes · Verified 2026-07-10
```

## 7. Expanded question details

Tabs:

### Interview answer

- concise answer;
- complete recommended answer;
- key points;
- concrete example;
- common mistakes;
- current versus legacy behavior when relevant.

### Interviewer guidance

- why this question is asked;
- strong signals;
- weak signals;
- red flags;
- scoring anchors:
  - 0 — no answer
  - 1 — superficial
  - 2 — workable
  - 3 — strong
  - 4 — expert/application depth
- knockout relevance;
- independence check.

### Follow-ups

Every follow-up shows:

- question;
- recommended answer;
- what capability it tests;
- difficulty increase.

### Sources

Every citation displays:

- source name;
- absolute HTTPS source link;
- source locator;
- verified date;
- freshness state.

Never use a locator string as the URL.

### Practice

- reveal/hide answer;
- self-rating;
- read aloud;
- previous/next;
- add to study set;
- add related exercise.

## 8. Exercise cards

Show:

- task;
- runner type;
- starter files;
- time box;
- prerequisites;
- hints;
- candidate-safe task;
- interviewer-only solution;
- tests;
- scoring rubric;
- change request;
- debugging variant;
- independence questions.

Executable exercises are displayed as executable only when their configured
runner is available.

## 9. Dropdown data contract

Add:

`GET /api/knowledge/facets?mode=reviewed`

Response:

```json
{
  "mode": "reviewed",
  "counts": {
    "questions": 0,
    "exercises": 0,
    "domains": 0,
    "gaps": 0
  },
  "domains": [
    {
      "value": "java",
      "label": "Java",
      "count": 18,
      "subdomains": [
        {"value": "collections", "label": "Collections", "count": 4}
      ]
    }
  ],
  "levels": [],
  "priorities": [],
  "frequencies": [],
  "roles": [],
  "question_types": [],
  "source_families": [],
  "freshness_states": [],
  "tags": []
}
```

The frontend must never hardcode options that conflict with backend values.

## 10. Question list contract

`GET /api/knowledge/questions`

Accepted optional parameters:

- `mode`
- `q`
- `domain`
- `subdomain`
- `level`
- `priority`
- `frequency`
- `role`
- `question_type`
- `source_family`
- `freshness_state`
- `tag`
- `has_exercise`
- `has_followups`
- `has_code_example`
- `sort`
- `limit`
- `offset`

Empty parameters must be omitted.

Response:

```json
{
  "items": [],
  "total": 0,
  "offset": 0,
  "limit": 20,
  "facets_applied": {},
  "request_id": "..."
}
```

## 11. Content standard

A reviewed-published question requires:

- concept-specific wording;
- technically complete answer;
- specific examples;
- meaningful follow-up;
- domain-specific scoring signals;
- official/primary source;
- verified date;
- review evidence;
- correct role mapping;
- no repeated semantic template;
- no generic “state an invariant and collect evidence” filler.

## 12. Visual design

Replace the current large gray filter rectangle.

Desktop:

- header and metrics;
- wide search bar;
- compact two-row filter strip;
- result count;
- 65–70% result list;
- optional 30–35% sticky detail panel in split view.

Tablet:

- search first;
- filters in a collapsible drawer;
- cards full width;
- sidebar becomes top navigation or drawer.

Use consistent spacing, label alignment and control heights. Avoid six adjoining
blank text fields.

## 13. Accessibility

- labels tied to controls;
- keyboard navigation;
- visible focus;
- `aria-live` for result count and errors;
- dropdown options understandable without color;
- details tabs keyboard operable;
- minimum touch target;
- no focus trap;
- screen-reader text for priority and status.

## 14. Required acceptance tests

- Default reviewed page loads at least one record.
- No request contains `freshness=` or other empty parameters.
- Domain and subdomain dropdowns are API-driven.
- Subdomain changes with domain.
- Counts match API results.
- P0 filter returns only P0.
- Role filter returns only matching role records.
- Search natural-language fallback works.
- Expanded card displays answers and absolute source links.
- Draft mode is visibly separated and never selectable into candidate packages.
- API failure shows Retry, not zero results.
- Empty valid combination shows a meaningful empty state.
- Tablet layout has no horizontal overflow.
