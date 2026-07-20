# Question Library Correction — Phase 0 Baseline

- Baseline SHA: `fa44f8f1bc30921466deef22236025acdd3a911` (branch `release/zume-1.0`)
- Binding inputs: `docs/release/question-library/01_QUESTION_LIBRARY_UI_SPEC.md`,
  `02_QUESTION_LIBRARY_TAXONOMY.yaml`, `03_GOLD_CORE_QUESTION_CATALOG.yaml`
- Regression suites added in this phase:
  - `tests/test_question_library_phase0.py` (backend, 13 tests)
  - `apps/web/src/pages/LibraryPhase0.test.tsx` (frontend, 3 tests)

## Reproduced failures at baseline

| # | Requirement | Baseline result |
|---|---|---|
| 1 | `GET /api/knowledge/facets?mode=reviewed` exists with real option counts | FAIL — endpoint returns 404 |
| 2 | Facet counts equal question-list totals | FAIL — no facets endpoint |
| 3 | Question list exposes `request_id`, `limit`, `facets_applied`, honors `mode` | FAIL — fields missing, `mode` ignored |
| 4 | Empty query parameters tolerated by API (and omitted by UI) | FAIL — `?freshness=` returns 422 |
| 5 | Default reviewed library returns meaningful, non-template records | FAIL — all 89 "reviewed" questions are one concept-substitution template: "In {domain}, explain the purpose and failure boundary of {subdomain}…" |
| 6 | Content-quality gate detects concept-substitution templates | FAIL — gate passes the templated set |
| 7 | Citations resolve to absolute HTTPS `source_url` via `sources.yaml` | FAIL — references expose only `source_id` + locator; UI links the locator string |
| 8 | `GET /api/knowledge/gaps` available to the UI | FAIL — 404 |
| 9 | Stats expose reviewed vs draft separately | PASS (backend field existed; Home UI still shows the combined 1988 figure — frontend test fails) |
| 10 | Role-specific plans differ (Senior SDET / QA Manager / Performance Engineer) | FAIL — one identical knockout and question list for every role |
| 11 | Plan reports reviewed role-coverage honestly | FAIL — no `role_coverage` in plan |
| 12 | Natural-language search fallback ("What is an explicit wait in Selenium?") | FAIL — strict AND FTS returns nothing |
| 13 | Release ZIP bytes deterministic across rebuilds | FAIL — no deterministic packaging function; archive embeds file mtimes |

Frontend baseline failures (`LibraryPhase0.test.tsx`):

- Library API failure is rendered as "0 results" with no error banner or Retry.
- Library filters are blank free-text inputs; no facets-driven dropdowns; no
  dependent subdomain behavior.
- Home headline metric is the combined 1988 "library questions" count with no
  reviewed/draft distinction.

## Baseline library inventory

- Total question records: 1988 (1899 draft `generated_proposal`)
- Published + reviewed questions: 89 — all `hand_authored` concept-substitution
  templates; these do not meet the content standard and will be retired.
- Published + reviewed exercises: 4
- Reviewed exercise runners: sql, api, java, selenium (one each)

## Correction plan

Phases 1–12 of `docs/release/question-library/04_CURSOR_STARTUP_PROMPT.md`,
implemented in focused commits on `release/zume-1.0`, keeping PR #1 draft,
no merge, no `v1.0.0` tag.
