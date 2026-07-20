# Cowork Validation Inputs

## Preferred local startup

```text
zume review serve --port 8787 --no-open --reset
```

- Local URL: http://127.0.0.1:8787/
- Banner must read: `Review mode — fictional data`
- Uses `data/review-workspace` (fictional). Never point at real `candidates/`.
- OpenAI live and Docker labs disabled by default.
- Reset: `zume review reset`
- Prove identity: `GET /api/build-info`

## Pre-flight (stop on ENVIRONMENT MISMATCH)

1. `review_mode=true` and `X-Zume-Review-Mode: 1`
2. `/api/candidates` → `items: []`
3. `/api/knowledge/facets?mode=reviewed` → 66 questions, 4 exercises
4. `/api/knowledge/gaps` → 200
5. Selenium natural-language search returns hits

## Binding documents

- `docs/release/question-library/01_QUESTION_LIBRARY_UI_SPEC.md`
- `docs/release/question-library/02_QUESTION_LIBRARY_TAXONOMY.yaml`
- `docs/release/question-library/03_GOLD_CORE_QUESTION_CATALOG.yaml`
- `docs/release/question-library/05_COWORK_VALIDATION_PROMPT.md`

## Expected Library smoke

1. Open `/library` — Reviewed mode shows nonzero records immediately.
2. Domain dropdown options come from `/api/knowledge/facets?mode=reviewed`.
3. Selecting a domain enables Subdomain with dependent options.
4. Expand a P0 card — concise + recommended answers, scoring anchors, follow-ups.
5. Sources tab — every link is `https://…` (not a locator string).
6. Draft mode banner states drafts never enter candidate packages.
7. Natural-language search: `What is an explicit wait in Selenium?`

## Builder smoke

Preview Senior SDET, Mobile Automation Engineer, Performance Engineer,
AI QA Engineer, Test Automation Architect, QA Manager — confirm distinct
knockouts and coverage warnings when applicable.

## Independent validator prompt

Use `docs/release/question-library/05_COWORK_VALIDATION_PROMPT.md` (includes
environment gate). Preserve any prior stale report as
`reports/COWORK_FULL_VALIDATION_STALE_ENV.md`.
