# Zume 1.0 — Exact Cowork UAT Prompt for Current Review Build

You are the independent UAT validator for Zume. Validate the running application
through the browser, network, API, stored review data, and generated files.

## Fixed target

- URL: `http://127.0.0.1:8787/`
- Repository: `C:\Development\Workspace\Zume`
- Branch: `release/zume-1.0`
- Required SHA: `a3fc50308fd71dc2cb4b1ad8b6e2365d1ce7267f`
- Expected current reviewed corpus: 66 questions / 4 exercises
- Expected mode: fictional review workspace
- PR: #1 must remain draft, unmerged, and untagged

Do not trust an earlier browser tab or server process.

## Mandatory environment proof

Before doing any UAT, call and record:

1. `GET /api/health`
2. `GET /api/build-info`
3. `GET /api/candidates`
4. `GET /api/knowledge/facets?mode=reviewed`
5. `GET /api/knowledge/facets?mode=draft`
6. `GET /api/knowledge/gaps`

The environment is valid only when:

- HTTP 200 for every endpoint;
- `review_mode=true`;
- build SHA is exactly `a3fc50308fd71dc2cb4b1ad8b6e2365d1ce7267f`;
- reviewed questions = 66;
- reviewed exercises = 4;
- candidate list is initially empty;
- review-mode/noindex headers are present;
- the browser visibly shows `Review mode — fictional data`.

Stop immediately and report:

`NOT VERIFIED — ENVIRONMENT MISMATCH`

when any precondition fails. Do not continue against a stale server.

## Browser instrumentation

Open developer tools or equivalent instrumentation.

For the entire UAT:

- fail on uncaught JavaScript errors;
- record console errors and warnings;
- record every failed network request;
- record every unexpected API 4xx/5xx;
- record route, request, response status, and correlation/request ID;
- do not accept a heading being visible as proof of functionality.

## 1. Overview

Validate:

- health status;
- build SHA/version;
- review banner;
- reviewed question count;
- draft question count;
- reviewed exercise count;
- domain count;
- gap count;
- no blank metric;
- no real candidate names;
- quick actions navigate correctly;
- counts match API responses exactly.

## 2. Candidate intake

Use only fictional resumes.

Test:

- pasted resume text;
- TXT upload;
- DOCX upload;
- PDF upload;
- unsupported extension;
- empty submission;
- malformed document.

For each valid input:

- verify screening decision;
- verify evidence coverage;
- verify warning messages;
- verify candidate folder is under the review workspace;
- verify exactly `source`, `_internal`, and `deliverables`;
- verify expected canonical DOCX names;
- verify no final feedback documents are produced during intake;
- verify no file is written to the ordinary candidate root.

## 3. Finalize interview

Test a fictional ready candidate.

Sparse notes:

- missing areas listed;
- manual review/second round;
- `decision_permitted=false`;
- no false SELECTED result.

Complete strong notes:

- permitted decision;
- final documents generated;
- document names correct;
- candidate folder contract preserved.

Also validate:

- finalized candidate cannot be silently reset;
- reopen requires a reason;
- export does not change workflow status.

## 4. Question Library — current 66-question gold core

### Modes

Validate independently:

- Reviewed Library;
- Draft Research;
- Coverage & Gaps.

The three modes must not display identical data.

### Facets

Validate database-driven dropdowns:

- Domain;
- Subdomain;
- Level;
- Priority;
- Role track;
- Frequency;
- Question type;
- Source family;
- Freshness;
- Tags.

Checks:

- options come from `/api/knowledge/facets`;
- each option has a count;
- selecting Domain changes Subdomain;
- empty query parameters are omitted;
- active chips work;
- Clear All works;
- result totals match API;
- a failed API displays an error and Retry, not zero results.

### Search

Search:

`What is an explicit wait in Selenium?`

Require:

- relevant Selenium results;
- result count changes;
- strict search/fallback behavior is transparent enough to diagnose;
- no unrelated first result.

Also test:

- `HashMap mutable key`
- `REST API idempotency`
- `Oracle latest row`
- `agent tool permission`
- gibberish/no-match query.

### Question detail

Open representative P0, P1, basic, intermediate, and advanced records.

Verify:

- question;
- concise answer;
- complete recommended answer;
- key points;
- examples/code where appropriate;
- common mistakes;
- strong signals;
- weak signals;
- red flags;
- scoring anchors;
- follow-up question and answer;
- source name;
- absolute HTTPS source URL;
- locator;
- verified/freshness date;
- bookmark;
- read aloud.

Open each sampled source link and confirm it is not a relative Zume link.

### Content quality sample

Independently inspect all 66 reviewed questions.

For each record mark:

- technically specific or vague;
- answer matches question;
- level plausible;
- priority plausible;
- role mapping plausible;
- no semantic template repetition;
- source supports the claim;
- follow-up is deeper, not a paraphrase.

Any materially vague or templated reviewed record is a UAT defect.

## 5. Practice session

Validate:

- uses reviewed library data;
- filter-built study set;
- next/previous/random;
- reveal/hide;
- self-rating persistence;
- bookmark persistence;
- progress;
- speech play/pause/resume/stop;
- voice and rate;
- question/answer/both modes;
- empty and unavailable speech states.

## 6. Interview builder

Test:

- Senior SDET;
- Mobile Automation Engineer;
- Performance Engineer;
- AI QA Engineer;
- Test Automation Architect;
- QA Manager.

For each role verify through UI and `/api/interview/preview`:

- policy ID;
- 180-minute agenda;
- knockout duration and applicability;
- role-specific knockout domains;
- role-specific depth domains;
- truthful selection reason;
- exercises;
- reviewed-coverage warning;
- selected IDs persist on rerun.

Required distinctions:

- Mobile includes Appium/mobile.
- Performance includes performance-observability.
- AI QA includes AI quality, LLM, or agentic AI.
- Architect includes framework/solution architecture.
- QA Manager is not given the unchanged Senior SDET Java/Selenium knockout.

## 7. Exercise lab

Validate through UI and API:

SQL:

- SELECT succeeds;
- write denied;
- dangerous operation denied;
- recursive/heavy query times out;
- output limit;
- reset.

API:

- bundled mock success;
- alternate localhost port blocked;
- public URL blocked;
- redirect escape blocked.

Java/Selenium:

- validate capability/unavailable state;
- when Docker is available, run real compile/browser checks;
- otherwise mark only those live executions NOT VERIFIED.

## 8. Ask Zume

Test natural-language questions.

Require:

- local answer;
- relevant record retrieval;
- absolute source citations;
- confidence;
- source mode;
- offline status;
- clear history;
- provider-error state;
- no candidate data in the request payload.

## 9. Settings and doctor

Validate:

- structured cards;
- build SHA;
- corpus digest;
- provider state;
- Docker state;
- no key value, prefix, or suffix;
- clear chat/audio/cache actions;
- review workspace path or state without exposing private data.

## 10. Responsive and accessibility pass

Test every route at:

- 1440×900;
- 1280×800;
- 900×1200;
- 768×1024.

Validate:

- no overlapping filters;
- no clipped labels;
- no horizontal overflow;
- no control collision;
- no hidden buttons;
- reasonable tab order;
- visible focus;
- keyboard-only navigation;
- accessible names;
- screen-reader status for loading/errors/counts;
- long questions and answers wrap correctly.

Capture screenshots after meaningful data loads, not blank states.

## 11. Package validation

Build the Windows package twice.

Require:

- identical SHA-256;
- identical file list;
- no secret;
- no PII;
- no real candidate;
- no virtual environment;
- no node_modules;
- no runtime cache;
- extracted package starts;
- extracted package reports the same build SHA and corpus digest;
- extracted Library smoke passes.

## Report

Create a new file:

`reports/COWORK_UAT_A3FC503.md`

Do not overwrite earlier stale-environment reports.

For every check record:

- PASS / FAIL / NOT VERIFIED;
- route;
- browser action;
- API request/status;
- expected;
- actual;
- screenshot;
- severity;
- exact correction.

End with exactly one verdict:

- `READY FOR HUMAN UI REVIEW`
- `NOT READY — CORRECTIONS REQUIRED`
- `NOT VERIFIED — ENVIRONMENT MISMATCH`
- `NOT VERIFIED — ENVIRONMENT CAPABILITY BLOCKER`

Do not merge PR #1 and do not create a release tag.
