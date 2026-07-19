# Zume Full Browser Validation — Cowork Prompt

## Environment gate (do this first)

Before validation, prove this server is the requested build:

1. `GET /api/health` must show `review_mode=true` and header `X-Zume-Review-Mode: 1`.
2. `GET /api/knowledge/facets?mode=reviewed` must return 200 and the current gold-core reviewed count (66 questions / 4 exercises unless deliberately changed).
3. `GET /api/candidates` must be empty.
4. `GET /api/build-info` must record `git_sha`, digests, and reviewed counts.
5. Stop and report **ENVIRONMENT MISMATCH** if any check fails.
6. Do not validate a stale process.

Preferred startup:

```text
zume review serve --port 8787 --no-open --reset
```

## Role

Act as an independent product, UI, API and data validator.

Do not trust builder reports. Use the running application and inspect the
browser, network requests, console, API responses, generated files and database
content.

## Input

Local URL:

`http://127.0.0.1:8787/`

Review mode must use fictional data only under `data/review-workspace`.

## Rules

- Do not use real candidate data.
- Do not reveal or inspect secret values.
- Do not modify `main`.
- Do not merge or tag.
- Capture screenshots only after meaningful content loads.
- A heading being visible is not proof that a feature works.

## Validate every route

### Overview

- Health is online.
- Reviewed, draft, exercise, domain and gap counts are labeled correctly.
- No blank metric.
- Quick links work.
- Review-mode banner appears.

### Candidate intake

- Paste fictional resume.
- Upload fictional TXT, DOCX and PDF.
- Validate unsupported file rejection.
- Generate package.
- Confirm decision, evidence coverage and deliverables.
- Inspect generated folder and DOCX names.
- Confirm no feedback is generated.

### Finalize interview

- Ready candidates appear in dropdown.
- Complete notes produce a permitted decision.
- Sparse notes show missing areas and prevent final selection.
- Deliverables appear.
- Finalized candidate cannot be silently reset.

### Question Library

- Reviewed mode loads nonzero records.
- Draft mode is visibly different.
- Gap mode works.
- Every categorical filter is a dropdown/check control populated by API.
- Domain changes subdomain options.
- Counts match results.
- Natural-language search works.
- P0/P1 filters are correct.
- Role filter is correct.
- Active chips and Clear All work.
- Expand a question.
- Verify concise answer, complete answer, scoring guidance, follow-ups and
  interviewer signals.
- Open every source link in a new tab and verify it is an absolute official
  source.
- Bookmark works.
- Error and empty states are distinguishable.
- No failed API call is presented as zero results.

### Practice

- Records come from reviewed Library.
- Next, previous and random.
- Reveal/hide.
- Self-rating persists.
- Bookmark.
- Read aloud play/pause/resume/stop.
- Voice/rate/mode.
- Empty/unavailable speech state.

### Interview builder

Test:

- Senior SDET
- Mobile Automation Engineer
- Performance Engineer
- AI QA Engineer
- Test Automation Architect
- QA Manager

For each:

- 180-minute total;
- 20-minute knockout where appropriate;
- role-relevant domain mix;
- truthful selection reasons;
- warning when reviewed role coverage is insufficient;
- candidate-safe exercises;
- no raw JSON as primary UI.

### Exercise lab

- SQL SELECT.
- SQL write denial.
- SQL timeout.
- API mock success.
- API external/alternate-port rejection.
- Java unavailable/available state.
- Selenium unavailable/available state.
- Monaco resizing.
- Starter exercise selection.
- Structured output and tests.

### Ask Zume

- Natural-language Selenium question.
- Local answer.
- Absolute citations.
- confidence/source mode.
- web-disabled state.
- clear history.
- provider error state.

### Settings & doctor

- Cards, not raw JSON.
- No secret value/prefix/suffix.
- cache/history clearing.
- provider and Docker states accurate.

## Browser engineering validation

For every route:

- desktop 1440×900;
- tablet 900×1200;
- keyboard-only pass;
- focus visibility;
- no horizontal overflow;
- no overlap/clipping;
- no console error;
- no failed request;
- no 4xx/5xx;
- loading/error/empty/success states;
- long content wrapping;
- valid accessible names.

## Backend/data validation

Cross-check UI against:

- `/api/knowledge/facets`
- `/api/knowledge/questions`
- `/api/knowledge/stats`
- `/api/knowledge/gaps`
- `/api/interview/preview`
- `/api/labs`
- `/api/doctor`

Verify displayed counts equal API counts.

Inspect a sample of at least:

- every P0 reviewed question;
- 10 questions per reviewed domain where available;
- all reviewed exercises;
- all role-policy configurations.

## Package validation

Run the release build twice.

- Compare SHA-256.
- Extract and compare file lists/content.
- Scan for secrets, PII, runtime data and candidate data.
- Start the extracted package and repeat health + Library smoke.

## Output

Create:

`reports/COWORK_FULL_VALIDATION.md`

For every item record:

- PASS / FAIL / NOT VERIFIED;
- screenshot;
- route;
- browser action;
- API request and status;
- expected versus actual;
- severity;
- exact correction.

End with exactly one:

- `READY FOR HUMAN UI REVIEW`
- `NOT READY — CORRECTIONS REQUIRED`
- `NOT VERIFIED — ENVIRONMENT BLOCKER`
