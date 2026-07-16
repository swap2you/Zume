# Zume Question Library — Final Cursor Startup Prompt

## Repository

- Path: `C:\Development\Workspace\Zume`
- Branch: `release/zume-1.0`
- Start from the latest pushed tip.
- Keep PR #1 draft.
- Do not merge or tag.

## Mission

Replace the current Question Library and weak generated content with a
database-driven, reviewed, high-signal interview-preparation experience.

Use:

- `01_QUESTION_LIBRARY_UI_SPEC.md`
- `02_QUESTION_LIBRARY_TAXONOMY.yaml`
- `03_GOLD_CORE_QUESTION_CATALOG.yaml`

These files are binding.

Do not ask routine implementation questions. Work in small commits and validate
each phase.

## Non-negotiable preservation

Do not break:

- `zume intake`;
- `zume finalize`;
- three candidate folders;
- seven canonical deliverables;
- 180-minute interview;
- 20-minute knockout;
- finalized-candidate rerun protection;
- sparse-note decision protection;
- local-first privacy;
- draft versus reviewed separation.

## Phase 0 — Reproduce the current failures

Add tests proving:

- default Library request currently fails or returns no meaningful results;
- empty numeric filters are omitted;
- API errors do not become zero results;
- Home counts distinguish reviewed and draft;
- existing semantic templates are detected;
- citations resolve to absolute source URLs;
- role-specific plans are not all identical;
- natural-language search has a fallback;
- push and PR builds produce deterministic ZIP bytes.

Record:
`reports/QUESTION_LIBRARY_CORRECTION_BASELINE.md`

## Phase 1 — Taxonomy and facets

Import `02_QUESTION_LIBRARY_TAXONOMY.yaml` into the canonical knowledge taxonomy
without creating duplicate competing taxonomies.

Implement:

`GET /api/knowledge/facets?mode=reviewed|draft|gaps`

The response must be generated from actual records and contain option counts.

Frontend dropdowns must use this API.

Do not hardcode:

- domains;
- subdomains;
- priorities;
- roles;
- frequencies;
- question types.

Omit every empty query parameter.

## Phase 2 — Rebuild the Library UI

Implement every requirement in `01_QUESTION_LIBRARY_UI_SPEC.md`.

The visual target is:

- prominent search;
- compact database-driven dropdown filters;
- active chips;
- reviewed/draft/gap modes;
- meaningful result cards;
- expandable answers;
- scoring guidance;
- follow-ups;
- valid citations;
- preparation controls;
- responsive tablet layout.

Remove the current row of blank categorical text inputs.

Do not show draft totals as reviewed content.

## Phase 3 — Build the gold core

Read existing interview guides and question libraries already used by Zume and
the project. Preserve high-quality material when it meets the new standard.

Use `03_GOLD_CORE_QUESTION_CATALOG.yaml` as the required high-signal blueprint.

For every blueprint record:

1. Expand it into the complete Zume question schema.
2. Write a concise answer.
3. Write a complete recommended answer.
4. Add a concrete example or code/query example where appropriate.
5. Add strong signals, weak signals, red flags and common mistakes.
6. Add the supplied follow-up and a complete recommended answer.
7. Add an independence question where appropriate.
8. Map correct role tracks.
9. Assign realistic priority/frequency.
10. Cite official or primary sources with:
    - source ID;
    - source name;
    - absolute HTTPS URL;
    - specific locator;
    - verification date.
11. Run an independent critic.
12. Publish only after the critic passes.

Do not convert a question to a generic template merely to expand counts.

## Phase 4 — Content-quality enforcement

The publication gate must detect:

- concept-substitution templates;
- normalized repeated questions;
- normalized repeated answers;
- repeated signals, mistakes and follow-ups;
- metadata/question mismatch;
- invalid role mapping;
- weak or missing source locators;
- relative/empty source URLs;
- generic executable exercises;
- missing starter files/tests;
- stale P0/P1 content;
- unreviewed published content.

Add:

```text
zume knowledge content-quality
zume knowledge review-report
```

The report must show:

- reviewed published count;
- draft proposal count;
- domains covered;
- gaps;
- normalized duplicate clusters;
- role coverage;
- source/freshness status.

## Phase 5 — Role-specific policies

Create explicit role-family policies:

- Senior SDET
- Lead SDET / QE Lead
- Mobile Automation Engineer
- Performance Engineer
- AI QA / AI Test Engineer
- Test Automation Architect
- QA Manager / QE Manager

Each policy defines:

- mandatory core;
- role depth;
- knockout applicability;
- exercises;
- leadership/architecture weighting;
- insufficient-reviewed-content behavior.

Do not give QA Manager, Performance Engineer and AI QA Engineer the same
Java/Selenium knockout.

When reviewed coverage is insufficient, show a clear warning and do not pretend
the plan is role-complete.

## Phase 6 — Sources and search

Resolve every reference through `knowledge/sources.yaml`.

API returns:

```json
{
  "source_id": "...",
  "source_name": "...",
  "source_url": "https://...",
  "locator": "...",
  "last_verified": "..."
}
```

Frontend uses only `source_url` as the link.

Improve FTS:

- stop-word removal;
- strict search;
- reduced-keyword fallback;
- OR/ranked fallback;
- typo-tolerant domain/tag matching where safe.

Add natural-language test:

`What is an explicit wait in Selenium?`

## Phase 7 — Improve all screens consistently

Do not redesign the product, but bring every route to the same quality level.

Validate and correct:

- Overview
- Candidate intake
- Finalize interview
- Question Library
- Practice session
- Interview builder
- Exercise lab
- Ask Zume
- Settings & doctor

For each:

- loading state;
- API error;
- validation error;
- empty state;
- success state;
- keyboard behavior;
- tablet behavior;
- no misleading counts;
- no raw JSON as the main presentation;
- valid links;
- no console errors.

## Phase 8 — Cowork/local validation mode

Add:

```text
zume review serve --port 8787
```

Behavior:

- localhost only by default;
- fictional/demo data root;
- no real candidate data;
- OpenAI live disabled unless explicitly enabled;
- Docker labs disabled by default;
- banner: `Review mode — fictional data`;
- noindex headers;
- request and console logging suitable for validation;
- one command to reset review data.

Do not make the application publicly reachable automatically.

## Phase 9 — End-to-end tests

Playwright must validate meaningful outcomes, not headings.

Required:

- default reviewed Library loads records;
- every dropdown option comes from facets;
- domain changes subdomains;
- result counts match;
- answers expand;
- citations are absolute;
- Practice uses actual records;
- Intake file and text;
- Finalize sparse/complete notes;
- Builder role policies;
- SQL/API lab;
- Ask natural-language retrieval;
- Settings clear actions;
- review mode banner;
- every route desktop + tablet;
- fail on console error, failed request and 4xx/5xx;
- screenshots after meaningful data loads.

## Phase 10 — Deterministic package

Build release twice and require identical SHA-256.

Normalize:

- entry ordering;
- timestamps;
- path separators;
- file permissions;
- compression settings.

## Phase 11 — Reports

Create:

- `reports/QUESTION_LIBRARY_IMPLEMENTATION.md`
- `reports/QUESTION_LIBRARY_CONTENT_REVIEW.md`
- `reports/QUESTION_LIBRARY_UI_QA.md`
- `reports/ROLE_POLICY_VALIDATION.md`
- `reports/COWORK_VALIDATION_INPUTS.md`
- updated release-readiness report.

Report actual gaps. Do not state that the library is complete.

## Phase 12 — Git and completion

- Focused commits.
- Push release branch.
- Keep PR #1 draft.
- Run complete central CI.
- Upload meaningful desktop/tablet screenshots.
- Upload deterministic release candidate.
- Do not merge.
- Do not tag.

Return:

1. commit list;
2. final SHA;
3. reviewed/draft/gap counts;
4. role coverage;
5. content-quality results;
6. UI screenshots;
7. Playwright results;
8. deterministic ZIP checksum;
9. Cowork local review command;
10. exact clean-room inputs.
