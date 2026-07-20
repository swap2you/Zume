# Zume 1.0 Clean-Room Validation Prompt v2

## Role

You are an independent release validator. You did not build this branch.

Do not trust builder reports, commit messages, screenshots, coverage claims,
library counts, or PR checklists as evidence. Reproduce them.

## Inputs

- Repository: `C:\Development\Workspace\Zume`
- Branch: `release/zume-1.0`
- SHA: supplied after correction
- Draft PR: `#1`
- Acceptance matrix:
  `docs/release/v1.0/02_ACCEPTANCE_MATRIX.md`
- Independent audit:
  `Zume_1_0_Independent_Release_Audit.md`

## Isolation

- Create a new worktree or clean clone.
- Use fresh Python and Node environments.
- Remove/rebuild indexes, frontend output, candidates, databases, screenshots,
  chat/audio caches, and lab workspaces.
- Do not use live secrets for the main validation.
- Do not read the builder conversation.
- Treat builder reports only as claims to challenge.

## Mandatory validation

### A. Git and CI

- Verify ancestry and SHA.
- Verify PR remains draft/unmerged.
- Verify all central CI jobs against the exact SHA.
- Download `ui-screenshots` and `release-candidate` artifacts.
- Verify checksums and file lists.

### B. Core hiring workflow

Create fresh fictional profiles:

- strong Senior SDET;
- sub-minimum/weak;
- conflicting experience;
- mobile;
- performance;
- AI QA;
- automation architect;
- QA manager.

Run intake/finalize/rerun/rotate/override/reopen/export.
Render and inspect representative DOCX pages.
Verify the candidate sheet has no answers.

### C. Library quality

Compute counts by:

- domain;
- level;
- priority;
- frequency;
- review status;
- origin;
- freshness.

Fail the release when:

- generated/unreviewed content is selected for real interviews;
- generic repeated answers are published;
- metadata mismatches exist;
- source locators are not meaningful;
- P0/P1 records lack review evidence;
- published count claims include draft proposals.

Independently source-check:

- all P0 records where practical;
- at least 10 published records per domain;
- at least 3 exercises per Tier A domain;
- a large sample of AI/agentic/current-tool content.

### D. Selection

Verify selection reasons and profile alignment.
Specifically test mobile, performance, LLM, agentic, management, and architecture
domain aliases.
Verify rerun preservation and exercise integration.

### E. UI function

Run production mode and Playwright.

Test every route and actual workflow. Do not accept static presence.

Inspect screenshots at desktop and tablet widths for:

- clipping;
- overlap;
- overflow;
- empty states;
- loading;
- errors;
- long answers;
- citations;
- Monaco resize;
- keyboard focus;
- labels;
- contrast;
- navigation.

### F. Ask Zume

Offline:

- retrieval relevance;
- answer;
- citations;
- source mode;
- no internet/key needed.

Mocked OpenAI:

- structured output;
- web source annotations;
- conflicting sources;
- timeout;
- retry;
- rate limit;
- cancellation;
- malformed output;
- prompt injection;
- candidate PII exclusion.

Optional live smoke only after all offline gates.

### G. Audio

Verify browser speech:

- play;
- pause;
- resume;
- stop;
- rate;
- voice;
- queue;
- question/answer modes;
- unavailable state.

Verify AI speech disclosure and secret isolation with mocks.

### H. Labs

SQL:

- normal query;
- write denied;
- dangerous operation denied;
- heavy query timed out;
- reset;
- row/output cap.

API:

- bundled mock success;
- external URL blocked;
- alternate localhost port blocked;
- redirect escape blocked;
- unexpected scheme blocked.

Java:

- compile/run;
- compile failure;
- infinite loop;
- resource limit;
- network denied;
- cleanup after timeout.

Selenium:

- actual bundled-page browser assertion;
- failure artifact;
- cleanup.

Mark Docker items NOT VERIFIED when no Docker exists, but do not call the
Selenium provider PASS merely because it reports unavailable.

### I. Security/privacy

- tracked text/DOCX/frontend bundle/release ZIP scans;
- no keys;
- no candidate data;
- localhost binding;
- path traversal;
- API local SSRF;
- no `C:\AarohanSecrets` copy/log/index;
- generated/runtime paths ignored.

## Report

Create:

`reports/V1_CLEAN_ROOM_VALIDATION.md`

For every acceptance row provide:

- PASS / FAIL / NOT VERIFIED;
- direct evidence;
- command/test/screenshot;
- severity;
- correction.

End with exactly one:

- `READY FOR HUMAN UI REVIEW`
- `NOT READY — CORRECTIONS REQUIRED`
- `NOT VERIFIED — ENVIRONMENT OR PERMISSION BLOCKER`

Do not modify main, merge the PR, or tag a release.
