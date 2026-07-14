# Zume Final Lockdown — Validation Report

- **Date:** 2026-07-13
- **Branch:** main
- **Baseline commit:** `0d3fea90499889b4d66adf19782cb8b789aa1f4e`
- **OS / Python:** Windows 11 (10.0.26200) · Python 3.13.5
- **Environment:** fresh `.venv-lock` — `pip install -e ".[dev]" -c constraints.txt`
  (plus `.[win]` → `pywin32` for the Word-rendered visual QA re-run). No new
  project dependency was added.

This pass applied only the ten narrow corrective/release-locking changes from the
lockdown prompt. The application was not redesigned; the three-folder candidate
contract and the seven canonical deliverables are unchanged.

## Gate results (fresh `.venv-lock`, this session)

| Gate | Command | Result |
|------|---------|--------|
| Byte-compile | `python -m compileall src` | PASS (rc 0) |
| Lint | `ruff check .` | PASS (all checks passed, rc 0) |
| Types | `mypy src` | PASS (22 files, no issues, rc 0) |
| Tests + coverage | `pytest -q --cov=zume --cov-fail-under=80` | **154 passed**, coverage **80.41%** (rc 0) |
| Package build | `python -m build` | PASS — `zume-0.1.0.tar.gz` + `zume-0.1.0-py3-none-any.whl` |
| Demo | `zume demo` | PASS — intake (INTERVIEW_SCHEDULED) → finalize (SELECTED) |
| Candidate validation (no render) | `zume validate --candidate Mehta_Aarav_2026-07-13` | 52 passed, 1 warning (render backend absent), 0 errors |
| Candidate validation (Word render) | same, with `.[win]` installed | **85 passed, 0 warnings, 0 errors** |
| DB reliability | `zume db check` | PASS — schema v2, integrity + FKs OK, no duplicates |
| Secret / PII scan | `zume scan-secrets` | PASS — no secrets or PII in tracked text/DOCX |
| Git privacy | `git status --porcelain -uall` filtered | No `candidates/ input/ output/ private/ data/ "General Docs/"` entries |

## Corrective changes (by prompt section)

### 1. v2 is the only documented workflow
- `README.md` rewritten around `zume intake` / `zume finalize`; points first to
  `CURSOR_START_HERE.md`, `docs/ZUME_DAILY_USE_GUIDE.md`,
  `docs/ZUME_TROUBLESHOOTING_GUIDE.md`. No current-workflow references to the old
  four commands, numbered folders, `99-final`, automatic `__vN`, or a 90-minute
  interview remain.
- `AGENTS.md` makes `intake`/`finalize` canonical and states legacy commands must
  not create candidate records.
- `docs/OPERATING_GUIDE.md` and `docs/TROUBLESHOOTING.md` are now short redirects
  to the current guides; the historical v1 content was moved to
  `docs/reference/legacy/OPERATING_GUIDE_v1.md` and `TROUBLESHOOTING_v1.md`. There
  are no longer two competing operating guides.

### 2. Legacy CLI commands locked away from the old folder model
- `filter-resume`, `interview-prep`, `schedule-interview`, `interview-feedback`
  and the natural-language `run` trigger are now `hidden=True`.
- On invocation they print a deprecation notice and either delegate to the v2
  path where unambiguous (`filter-resume` → `intake`, `interview-feedback` →
  `finalize`, `run`'s filter/feedback triggers likewise) or refuse
  (`interview-prep`, `schedule-interview`, and the prep/schedule triggers) with a
  non-zero exit. None create a v1 candidate folder.
- The v1 orchestration functions and the only `99-final`/`__vN` write paths
  (`_promote_if_valid`, `_finish`, `run_filter_resume`, `run_interview_prep`,
  `run_schedule_interview`, `run_interview_feedback`) were removed. Legacy
  folder read/migration/cleanup functions are retained.
- Test `test_lockdown.py::test_intake_only_creates_three_folder_contract` proves
  the candidate-creation entry point produces only `source/`, `_internal/`,
  `deliverables/` and never `99-final` or a user-visible `__vN`.

### 3. Finalized candidates protected from accidental intake reruns
- `run_intake` stops when the candidate is in a terminal state (`INTERVIEWED`,
  `SELECTED`, `REJECTED`, `SECOND_ROUND`). A `--reopen` with a required
  `--reopen-reason` is the only exception; it records the reason, preserves
  `06_Final_Interview_Evaluation.docx` and `07_Post_Interview_Communications.docx`
  by default, and never resets the final status to ready/scheduled.
- Tests: intake→finalize→intake blocked; a blocked rerun leaves all deliverables
  byte-for-byte unchanged; reopen without a reason blocked; a deliberate reopen
  records the reason and preserves final artifacts.

### 4. Export no longer replaces the workflow status
- `zume candidate export` records an `EXPORTED` history event via
  `candidate.record_event` without changing the hiring workflow `status`.
- Test proves: intake → export → status stays `READY_FOR_INTERVIEW`/
  `INTERVIEW_SCHEDULED` → finalize still succeeds → final status reflects the
  interview decision, not `EXPORTED`.

### 5. Incomplete interview notes cannot yield a final selection
- `feedback.evaluate_notes` adds an evidence-completeness gate: a `SELECTED`
  requires assessable evidence for Java, Selenium, REST Assured/API, SQL/Oracle,
  and independent explanation/modification. When any is missing it does not invent
  scores, lists the missing areas, sets a manual-review/second-round state, and
  uses the recommendation *"Incomplete interview evidence — manual review required
  before a final hiring decision."* A low-confidence independence result or an
  explicitly failed mandatory area can still produce Do Not Proceed.
- `FeedbackResult` now carries `assessed_areas`, `missing_areas` and
  `decision_permitted`; the final evaluation distinguishes assessed vs missing
  areas, the calculated score, and whether a final decision was permitted.
- Six tests cover: Java-only, Java+Selenium only, all four areas but no
  independence, complete strong notes, complete weak notes, and no recognizable
  assessment.

### 6. Complete recommended answers for every exercise question
- `Exercise`/`ExerciseSelection` gained `requirement_change_recommended_answer`,
  `debugging_recommended_answer`; independence questions are now objects
  (`question` + `recommended_answer`). `config/exercise-library.yaml` was extended
  for every exercise. `validate_exercise_answers` enforces non-empty values for
  every active exercise; `test_exercises.py` asserts the contract.
- The interviewer guide now renders task, expected reasoning, reference solution,
  requirement-change follow-up + answer, debugging follow-up + answer, each
  independence question + answer, rubric and red flags. The candidate exercise
  sheet remains tasks-only (verified by tests).

### 7. Timezone in schedule communications
- `scheduling._when` now always renders date, time **and** timezone; drafts
  include the meeting platform where available. Unconfirmed schedules are prefixed
  with an explicit "DRAFT — schedule is NOT confirmed" marker and never say
  "Confirming the interview". Tests check the join/reschedule/cancel/no-show
  drafts include the timezone and never present an unconfirmed schedule as
  confirmed.

### 8. Tracked DOCX text scanned for PII
- `security.scan_repository` now extracts paragraph and table text from
  git-tracked `.docx` files using the already-installed `python-docx` and scans it
  with the existing email/phone/secret patterns, reporting only the finding kind
  and document path (never the matched value). Ignored candidate/private files are
  still skipped. A fictional-DOCX fixture test proves detection.

### 9. Documentation-consistency test
- `tests/test_docs_consistency.py` fails if any of `README.md`, `AGENTS.md`,
  `CURSOR_START_HERE.md`, `docs/ZUME_DAILY_USE_GUIDE.md`, or
  `docs/ZUME_TROUBLESHOOTING_GUIDE.md` contains a forbidden legacy phrase
  (`99-final`, `Duration: 90 minutes`, 90-minute, the numbered workflow folders,
  or the retired `zume filter-resume/interview-prep/schedule-interview/
  interview-feedback` invocations). Legacy files under `docs/reference/legacy/`
  are intentionally excluded.

## Targeted regression scenarios

| # | Scenario | Result |
|---|----------|--------|
| 1 | Strong intake | PASS (full package, status ready/scheduled) |
| 2 | Export before finalize | PASS (status preserved, event recorded) |
| 3 | Finalize | PASS (SELECTED on complete strong notes) |
| 4 | Accidental intake after finalization | PASS (blocked; deliverables unchanged) |
| 5 | Sparse / incomplete notes | PASS (manual-review, never SELECTED) |
| 6 | Complete strong notes | PASS (selection permitted) |
| 7 | Schedule comms with IANA timezone | PASS (timezone in every draft) |
| 8 | Direct invocation of each legacy command | PASS (deprecated; no v1 folder) |
| 9 | Candidate-shareable sheet answer/secret scan | PASS (tasks only) |
| 10 | Tracked DOCX PII scan | PASS (detects planted PII in a fixture) |

## Document render results

- With Microsoft Word available (`.[win]`), all seven deliverables render to PDF
  and `zume validate` reports **85 passed, 0 warnings, 0 errors**.
- In a pure `.[dev]` environment with no LibreOffice or Word, `zume validate`
  runs all structural checks and emits an explicit warning that render
  verification was skipped (52 passed, 1 warning, 0 errors). It never silently
  passes as if rendered.

## Remaining limitations

- Render verification requires a real word processor (LibreOffice or Word/COM);
  otherwise it is skipped with a warning. `validation.py` render paths therefore
  stay uncovered where no renderer is installed.
- The evidence-completeness gate is a deterministic heuristic over interviewer
  notes; it enforces area coverage but does not judge answer correctness — a human
  still owns the final hiring decision.

## Git

- One focused commit prepared after all gates passed. Nothing under
  `candidates/`, `input/`, `output/`, `private/`, or `data/` was staged.
- **Not pushed.** No release tag created.
