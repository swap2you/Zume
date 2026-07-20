# Zume 1.0 — Clean-Room Independent Validator Prompt

## Your role

You are the release validator, not the implementation agent.

You did not build this branch. Do not trust commit messages, builder summaries,
coverage claims, reports, or screenshots as proof. Reproduce evidence.

## Inputs

- Repository: `C:\Development\Workspace\Zume`
- Release branch/SHA: supplied by the builder
- Acceptance contract: `02_ACCEPTANCE_MATRIX.md`
- Baseline: `bdbfbc71b2a129e53fec2dd9ba741e759028d875`

Do not read the builder chat. Reports may be used only to identify claims to
retest.

## Independence setup

1. Create a new Git worktree or clean clone at a separate path.
2. Verify the target SHA.
3. Create a fresh Python environment.
4. Use `npm ci` in a fresh frontend environment.
5. Do not reuse builder databases, candidates, indexes, `node_modules`, venvs,
   audio, lab workspaces, or generated screenshots.
6. Do not load live secrets during the main validation.
7. Use mocks/offline mode first.
8. Use a live OpenAI smoke only after all offline gates, and only when safely
   configured.

## Validation procedure

### 1. Diff and architecture review

- Compare baseline to target.
- Confirm no rewrite of core hiring behavior without justification.
- Verify new modules are bounded.
- Verify source-of-truth and generated-data boundaries.
- Search for duplicate business logic in UI/API.
- Search for hidden legacy write paths.
- Search for hardcoded secrets/model names/absolute private paths.

### 2. Full clean build

Run every documented Python and frontend gate.
Record exact commands, versions, exit codes, test counts, coverage, duration,
and failures.

### 3. Existing hiring regressions

Create fresh fictional inputs for:

- strong Senior SDET;
- weak/sub-minimum candidate;
- unknown/conflicting experience;
- mobile-heavy candidate;
- performance-heavy candidate;
- AI QA candidate;
- automation architect;
- QA manager.

For each appropriate profile:

- run intake;
- inspect selection;
- verify folder contract;
- verify deliverable count;
- render DOCX;
- inspect first, middle, and last pages;
- verify no answer leakage;
- verify schedule semantics;
- verify rerun/rotation/override/reopen/export behavior.

Finalize with:

- complete strong notes;
- complete weak notes;
- Java-only notes;
- no recognizable assessment;
- all technical areas but no independence evidence.

### 4. Library audit

Compute:

- total records;
- counts by domain/level/priority/frequency/status;
- exercises by domain/level;
- missing fields;
- duplicates and near duplicates;
- unresolved sources;
- stale records;
- priority distribution;
- answer lengths;
- follow-up completeness.

Independently sample:

- all P0 questions when feasible;
- otherwise a statistically meaningful sample plus every P0 source;
- at least 10 questions per domain;
- at least 3 exercises per Tier A domain;
- all current AI questions or a sufficiently large current-AI sample.

For each sampled item check technical correctness against the cited source.

### 5. UI and accessibility

Launch production mode.

Validate every screen and main workflow with Playwright.
Capture screenshots at desktop and tablet widths.
Check:

- clipping/overlap;
- empty states;
- loading/errors;
- keyboard;
- focus;
- labels;
- contrast;
- long content;
- code editor resizing;
- citation links;
- candidate/interviewer markings.

### 6. Ask Zume

Offline:

- retrieve library answers;
- verify citations;
- verify no fabricated source;
- verify no key required.

Mocked provider:

- current web question;
- conflicting sources;
- timeout;
- rate limit;
- provider error;
- prompt injection in retrieved content;
- candidate PII payload prohibition.

Live smoke, only when configured:

- one non-sensitive question;
- no candidate data;
- record only success/failure, latency, configured model alias, and citation
  presence.

### 7. Audio

- browser read-aloud;
- controls;
- queue;
- offline state;
- mocked OpenAI TTS;
- AI voice disclosure;
- cache deletion;
- no secret in client;
- realtime disabled state.

### 8. Labs

- SQL success/failure/reset/timeout;
- API allowlist and blocked external URL;
- Java compile/pass/fail/timeout/infinite loop;
- Docker network disabled;
- filesystem/mount checks;
- cleanup;
- Selenium profile when Docker/browser prerequisites exist.

Never execute untrusted lab code directly on the host.

### 9. Security and privacy

- tracked secret/PII scans;
- frontend-bundle scan;
- Git ignore probes;
- path traversal;
- localhost binding;
- no unexpected telemetry;
- no `C:\AarohanSecrets` copy or log;
- no candidate data in AI payloads;
- release zip scan.

### 10. Central CI

- identify PR and workflow run;
- confirm every matrix job;
- inspect failed/skipped steps;
- do not infer green from local tests.

## Report

Create:
`reports/V1_CLEAN_ROOM_VALIDATION.md`

For every acceptance row include:

- verdict: PASS / FAIL / NOT VERIFIED;
- evidence;
- command/test/screenshot;
- severity;
- required correction.

End with exactly one release verdict:

- `READY FOR HUMAN UI REVIEW`
- `NOT READY — CORRECTIONS REQUIRED`
- `NOT VERIFIED — ENVIRONMENT/PERMISSION BLOCKER`

Do not merge, tag, or modify production data.
