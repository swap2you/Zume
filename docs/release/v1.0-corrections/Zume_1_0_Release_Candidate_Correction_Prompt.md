# Zume 1.0 Release Candidate — Final Correction Prompt

## Role

You are correcting the existing Zume 1.0 release candidate. You are not
redesigning it.

Work in:

- Repository: `C:\Development\Workspace\Zume`
- Branch: `release/zume-1.0`
- Starting SHA: `2dcde4bd189d8c11cfbd560193383a1a17012166`
- Draft PR: `#1`

Read:

- `Zume_1_0_Independent_Release_Audit.md`
- `docs/release/v1.0/02_ACCEPTANCE_MATRIX.md`
- existing V1 reports

Do not merge to `main`. Do not tag `v1.0.0`.

## Fixed architecture

Preserve:

- existing Python hiring engine;
- `zume intake` and `zume finalize`;
- three candidate folders;
- seven canonical deliverables;
- 180-minute interview;
- 20-minute knockout;
- FastAPI localhost server;
- React/TypeScript/Vite UI;
- YAML source-of-truth library;
- SQLite FTS;
- provider interfaces;
- local/offline-first behavior.

Do not add microservices, cloud hosting, accounts, Kubernetes, Electron, or a
new database.

## Phase 0 — Reproduce every audit finding

Before editing, add failing tests for:

1. Library search response contract.
2. P0-P3 priority filter.
3. Practice data comes from library.
4. Lab UI uses available backend runner names.
5. Ask UI renders citations/source mode.
6. Unconfirmed schedule subject.
7. Mobile/performance/AI resume domain aliases.
8. Published records cannot use generic repeated answer templates.
9. Java metadata mismatches in `java-b2` and `java-b3`.
10. SQL query timeout and write denial.
11. API lab rejects wrong localhost ports and redirects.
12. Java timeout forces container cleanup.
13. Playwright fails when server is unavailable rather than skipping.
14. Browser speech controls exist and are operable.

Record the initial failures in:
`reports/V1_CORRECTION_BASELINE.md`

## Phase 1 — Quarantine count-driven filler

### 1.1 Publication rules

Change the seed/research pipeline so generated content defaults to:

```yaml
status: draft
review_status: unreviewed
quality_origin: generated_proposal
```

Only records meeting all editorial gates may be `published`.

Add fields or an equivalent audited mechanism:

```yaml
quality_origin: hand_authored | researched | generated_proposal
review_status: unreviewed | reviewed | rejected
reviewed_at: YYYY-MM-DD | null
review_notes: []
```

Selection, search defaults, statistics, and coverage must distinguish:

- published/reviewed;
- draft/unreviewed;
- retired/rejected.

Do not report draft records as completed interview coverage.

### 1.2 Preserve safe fallback

The previously validated curated question/exercise library remains available as
a fallback. A real candidate package must never be filled with generic draft
content merely to meet a count.

### 1.3 Remove generic published content

The following patterns are not acceptable as published answers:

- `should be applied to a stated outcome, observable evidence...`
- `Start by naming the decision that ... supports...`
- identical strong/weak signals across unrelated domains;
- identical follow-up answers across unrelated domains;
- generic exercises that only substitute a concept name.

Quarantine existing records that match these fingerprints until rewritten and
reviewed.

## Phase 2 — Build a genuinely researched library

Use the strongest available reasoning model for authoring and a separate
critic pass. Use official/primary documentation. Do not copy interview banks.

Work domain by domain. For each record:

- concept-specific question;
- concise answer;
- full recommended answer;
- concrete examples where appropriate;
- meaningful follow-up and answer;
- domain-specific strong/weak signals;
- domain-specific mistakes/red flags;
- role mapping;
- P0-P3 priority;
- realistic frequency;
- specific source locator;
- verification date;
- freshness;
- review status.

### 2.1 Quality gates

Add deterministic checks for:

- duplicate question fingerprints;
- duplicate answer fingerprints;
- repeated paragraph rate;
- generic-template phrases;
- subdomain/question/tag consistency;
- question-answer concept overlap;
- source URL and source ID resolution;
- source locator specificity;
- P0/P1 review status;
- P0/P1 follow-up depth;
- current-content freshness;
- answer length bounds;
- executable exercise completeness;
- candidate-answer leakage.

Add an independent model critic command that writes findings but cannot publish:

```text
zume knowledge critique --domain <domain> --output reports/...
```

A separate promotion command may publish only clean reviewed proposals:

```text
zume knowledge promote --proposal <path> --review-file <path>
```

No direct model-to-published path.

### 2.2 Coverage contract

Retain the original domain targets, but report two numbers:

- reviewed published coverage;
- draft proposal coverage.

Do not claim zero gaps until reviewed published records meet the target.

### 2.3 Representative mandatory content

At minimum, hand-review all P0/P1 records for:

- Java
- Selenium
- TestNG
- Cucumber
- API/OpenAPI
- REST Assured
- Postman/Newman
- SQL/Oracle
- framework architecture
- debugging/reliability
- Git/Maven
- CI/CD
- Appium/mobile
- performance/APM
- leadership/management
- solution architecture
- LLM engineering
- agentic AI/MCP
- AI for QA
- AI governance

### 2.4 Exercises

Every published executable exercise must have real domain-specific:

- task;
- starter content;
- reference solution;
- tests/assertions;
- scoring rubric;
- hints;
- change request;
- debugging variant;
- independence questions;
- runner compatibility.

An exercise with `runner_type: java/sql/api/selenium` must run or test against
that provider. Concept-only whiteboard scenarios must use `runner_type: none`
and must not be presented as executable.

## Phase 3 — Correct candidate-specific selection

Create one canonical domain alias registry and use it everywhere.

Required mappings include:

- Appium/mobile → `mobile-appium`
- JMeter/Gatling/k6/performance/APM → `performance-observability`
- LLM/OpenAI/RAG/generative AI → `llm-engineering`
- agent/MCP/tool calling → `agentic-ai`
- Postman/Newman → `postman-newman`

Selection reasons must be truthful:

```text
mandatory-core
resume-claimed
missing-evidence
risk-validation
role-aligned
specialty-depth
rotation
```

Do not label a mandatory question as resume-aligned unless the resume matched it.

Integrate reviewed expanded exercises into candidate packages or explicitly use
the validated legacy exercises. Persist both selected question and exercise IDs.
Preserve rerun behavior.

Add synthetic profile tests for:

- strong Senior SDET;
- conditional/unknown evidence;
- weak candidate;
- mobile specialist;
- performance specialist;
- AI QA engineer;
- automation architect;
- QA manager/leader.

Inspect generated interviewer guides and candidate sheets for every profile.

## Phase 4 — Complete the web workspace

### 4.1 Shared typed API contract

Use generated OpenAPI TypeScript types or one small shared contract layer.
Eliminate response-key drift.

### 4.2 Question Library

Implement:

- full-text search;
- domain;
- subdomain;
- level;
- P0/P1/P2/P3;
- frequency;
- role;
- tags;
- freshness;
- question type;
- published/reviewed status;
- pagination.

Question details show:

- concise answer;
- full recommended answer;
- deep dive;
- key points;
- follow-ups and answers;
- strong/weak signals;
- mistakes/red flags;
- source citations;
- last verified/freshness;
- bookmark.

### 4.3 Practice

Use live library records. Add:

- study-set filters;
- next;
- previous;
- random;
- reveal/hide;
- self-rating;
- bookmark;
- progress;
- read aloud;
- persisted local state;
- empty/error states.

### 4.4 Candidate Intake

Support safe PDF, DOCX, and TXT upload through a typed multipart endpoint that
reuses existing ingestion. Also allow pasted text.

Never expose arbitrary host paths to the browser.

### 4.5 Candidate Finalize

List only candidates eligible for finalization. Show status and an evidence
checklist. Submit notes through the existing pipeline and show missing areas,
decision permission, deliverables, and next action.

### 4.6 Interview Builder

Render the plan as sections and timeline, not raw JSON. Show each selected
record, reason, level, priority, and time. Show the total and knockout segment.

### 4.7 Exercise Lab

Fetch `/api/labs` and expose only:

- SQL;
- API;
- Java;
- Selenium.

Load actual exercises and starter content. Use Monaco language modes correctly.
Show unavailable prerequisites, run/test output, test cases, timeout and
truncation status. Remove Python/JavaScript unless fully implemented.

### 4.8 Ask Zume

Display:

- answer;
- citations;
- source mode;
- confidence;
- model/provider status;
- offline versus web badge;
- provider errors;
- history clear control.

Make citation links visible and safe.

### 4.9 Settings and Doctor

Render structured cards and controls, not raw JSON. Include:

- provider state;
- web-search flag state;
- browser/OpenAI speech state;
- Docker lab state;
- cache/history clear actions;
- no secret values.

### 4.10 Offline assets

Remove runtime Google Fonts network import. Use system fonts or locally bundled,
license-compatible assets.

Pin explicit compatible frontend versions rather than using `"latest"`.

## Phase 5 — Implement audio

Use browser `window.speechSynthesis`.

Required controls:

- play;
- pause;
- resume;
- stop;
- rate;
- voice;
- question only;
- answer only;
- question + answer;
- queued practice set.

Add feature detection and a usable unavailable state. OpenAI TTS remains
optional and must show AI-generated disclosure.

## Phase 6 — Harden labs

### SQL

- Use a temporary SQLite database.
- Use `set_authorizer` or equivalent to deny writes, attach/detach, dangerous
  pragmas, extension loading, and filesystem-related operations.
- Use `set_progress_handler` with a real deadline.
- Limit rows and output bytes.
- Reset per run.
- Add recursive/heavy-query timeout tests.

### API

- Permit only the exact configured mock origin, initially
  `http://127.0.0.1:8765`.
- Reject alternate ports, credentials, fragments, non-HTTP schemes, IPv6
  alternatives, and redirects outside the exact origin.
- Disable redirects or revalidate every hop.
- Start/stop the bundled mock server deterministically in tests.
- Add SSRF and redirect tests.

### Java

Use a unique container name and ensure cleanup:

- `--network none`
- non-root
- `--cap-drop ALL`
- `--security-opt no-new-privileges`
- read-only root
- bounded writable temp/work directory
- memory/CPU/PID limits
- output limit
- timeout
- `docker rm -f <name>` in timeout/finally
- pinned/configurable image digest

Add compile, pass, fail, infinite-loop, fork-bomb-like, network, and cleanup
tests in a Docker-capable environment.

### Selenium

Implement an actual minimal exercise:

- bundled static training page;
- valid internal-only Compose network;
- Selenium browser;
- Java runner;
- mounted ephemeral exercise workspace;
- real compile and browser assertion;
- screenshot/log on failure;
- complete cleanup.

Do not return success merely because a compose file exists.

## Phase 7 — Correct OpenAI integration

At implementation time, verify the current official OpenAI documentation.

Use a supported server-side Responses API path with:

- structured output schema;
- actual web-search source annotation extraction;
- visible citations;
- configurable model;
- timeout;
- bounded retries for retryable failures;
- rate-limit handling;
- cancellation;
- malformed output handling;
- no-citation handling.

Never send candidate workflow data. Add payload-redaction tests.

Live credentials are optional. All tests use mocks. Do not print or copy
`C:\AarohanSecrets`.

## Phase 8 — Expand central CI

Keep the existing Python matrix and add jobs.

### Frontend job

```text
npm ci
npm run lint
npm run typecheck
npm run test
npm run build
```

### Browser job

- install Playwright browser;
- start `zume serve --no-open`;
- wait for health;
- run Playwright without conditional skip;
- test every route and primary workflow;
- run accessibility smoke;
- capture desktop and tablet screenshots;
- upload `ui-screenshots` artifact.

### Knowledge quality job

Run:

```text
zume knowledge validate
zume knowledge stats
zume knowledge gaps
zume knowledge content-quality
```

Fail when generic published content, stale P0/P1 content, source problems, or
review-status violations exist.

### Lab security job

Run SQL/API security tests on every platform. Run Docker Java/Selenium smoke on
an appropriate Ubuntu runner when Docker is available.

### Release job

Build the Windows release ZIP, scan its file list and extracted content for
secrets/PII/runtime data, calculate SHA-256, and upload a short-retention
`release-candidate` artifact. Do not include real candidate data.

## Phase 9 — Real visual and end-to-end QA

Playwright must test, not merely load:

- library search and P0 filter;
- answer expansion and citation;
- practice next/reveal/rate/read-aloud;
- interview builder;
- intake text and file;
- finalize selection and notes;
- SQL lab;
- API lab;
- unavailable/available Java/Selenium states;
- Ask citations;
- settings and cache clear;
- loading;
- empty;
- validation error;
- server error;
- long answer wrapping;
- tablet navigation;
- keyboard flow.

A missing server must fail the test setup. Never `test.skip` the entire suite
because the server was not started.

## Phase 10 — Regenerate release evidence

Regenerate from the final correction SHA:

- `reports/V1_IMPLEMENTATION_REPORT.md`
- `reports/V1_LIBRARY_COVERAGE_REPORT.md`
- `reports/V1_UI_VISUAL_QA.md`
- `reports/V1_SECURITY_AND_PRIVACY_REPORT.md`
- `reports/V1_LAB_SANDBOX_REPORT.md`
- `reports/V1_RELEASE_READINESS.md`
- `reports/V1_CORRECTION_REPORT.md`

Every report must contain one consistent SHA and current CI state.

Update PR #1 body/checklist. Keep it draft.

## Phase 11 — Independent validation

After all correction commits and central CI are green:

1. Push `release/zume-1.0`.
2. Do not merge.
3. Start a new Cursor chat with no builder history.
4. Use `Zume_1_0_Clean_Room_Validation_Prompt_v2.md`.
5. Create a fresh worktree or clone.
6. Download and inspect CI screenshot and release artifacts.
7. Independently sample content against sources.
8. Produce PASS/FAIL/NOT VERIFIED per acceptance item.

The required verdict before human review is:

`READY FOR HUMAN UI REVIEW`

## Required local validation

Run clean environments and record exact versions/exit codes:

```powershell
python -m venv .venv-v1-correction
.\.venv-v1-correction\Scripts\python -m pip install -e ".[dev]" -c constraints.txt
.\.venv-v1-correction\Scripts\python -m compileall src
.\.venv-v1-correction\Scripts\python -m ruff check .
.\.venv-v1-correction\Scripts\python -m mypy src
.\.venv-v1-correction\Scripts\python -m pytest -q --cov=zume --cov-fail-under=80
.\.venv-v1-correction\Scripts\python -m build
.\.venv-v1-correction\Scripts\zume knowledge validate
.\.venv-v1-correction\Scripts\zume knowledge content-quality
.\.venv-v1-correction\Scripts\zume knowledge stats
.\.venv-v1-correction\Scripts\zume knowledge gaps
.\.venv-v1-correction\Scripts\zume demo
.\.venv-v1-correction\Scripts\zume db check
.\.venv-v1-correction\Scripts\zume scan-secrets
```

```powershell
cd apps\web
npm ci
npm run lint
npm run typecheck
npm run test
npm run build
npm run test:e2e
```

Also run Docker lab validation when Docker is present.

## Git rules

- Use focused correction commits.
- Do not rewrite or squash existing phase history during correction.
- Do not force-push.
- Do not merge PR #1.
- Do not tag.
- Do not commit candidates, generated runtime data, secrets, venvs, node_modules,
  audio, chat history, lab workspaces, or release staging.
- Screenshots may be tracked only when fictional and privacy-scanned.
- Release ZIP should be a CI artifact, not source-controlled.

## Final response

Return:

1. correction commit list;
2. final SHA;
3. published reviewed versus draft counts;
4. content-quality findings and resolutions;
5. UI feature evidence;
6. lab security evidence;
7. AI/audio status;
8. local gates;
9. central CI run IDs;
10. artifact names/checksums;
11. clean-room input SHA;
12. known limitations;
13. confirmation PR remains draft and no merge/tag occurred.
