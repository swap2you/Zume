# Final Simplification — Validation Report (Phase 18)

- **Date:** 2026-07-13
- **Branch:** main
- **Baseline commit:** `4fd87e7d008b02bb2a816da71a7e4e287e4af00b`
- **OS / Python:** Windows 11 (10.0.26200) · Python 3.13.5
- **Environment:** fresh `.venv-final` — `pip install -e ".[dev]" -c constraints.txt`
  (plus `.[win]` → `pywin32` for Word COM rendering)

## Gate results (reproduced this session)

| Gate | Command | Result |
|------|---------|--------|
| Byte-compile | `python -m compileall src` | PASS (rc 0) |
| Lint | `ruff check .` | PASS (all checks passed) |
| Types | `mypy src` | PASS (22 files, no issues) |
| Tests + coverage | `pytest -q --cov=zume --cov-fail-under=80` | **126 passed**, coverage **80.77%** |
| Demo | `zume demo` | PASS — intake then finalize, status SELECTED |
| Candidate validation | `zume validate --candidate <demo>` | **85 passed, 0 warnings, 0 errors** (Word-rendered) |
| Rendered visual QA | 7 deliverables → PDF via Word COM | PASS (see `FINAL_DOCUMENT_VISUAL_QA.md`) |
| Privacy / security | `pytest tests/test_privacy.py tests/test_security.py` | PASS |
| Package build | `python -m build` | PASS — `zume-0.1.0` sdist + wheel |
| Git privacy | `git status --porcelain -uall` | No `candidates/ input/ output/ private/ data/ General Docs/` entries |

## Invariants verified

- **Contract (Phase 2):** new candidates use `source/ _internal/ deliverables/`;
  `candidate.json` lives under `_internal/`. No `99-final/` folder is created.
- **Deliverable count (Phase 3):** demo produces exactly 7 user-facing DOCX
  (`01_Screening_Summary` … `07_Post_Interview_Communications`); validation enforces
  ≤ 7 and no `__vN` versioned files.
- **Operating model (Phase 4):** `interview-plan.json` agenda totals **180 minutes**;
  first segment is the **20-minute knockout**; final close is a fixed 5 minutes.
- **Question library (Phase 5):** loads and passes the depth contract — core areas
  have ≥ 3 basic/intermediate/advanced; every question and follow-up has a
  recommended answer.
- **Exercise preservation (Phase 6):** a normal rerun keeps the same assigned
  exercises and status history; rotation requires `--rotate-exercises`
  + `--rotation-reason`.
- **Commands (Phase 7):** `zume intake` and `zume finalize` orchestrate the full
  pre- and post-interview flows.
- **Wait-for-notes (Phase 8):** intake never writes `feedback.json`,
  `06_Final_Interview_Evaluation.docx` or `07_Post_Interview_Communications.docx`;
  status stays `READY_FOR_INTERVIEW` / `INTERVIEW_SCHEDULED`.
- **Schedule controls (Phase 9):** non-180-minute durations and ambiguous timezones
  (bare `ET`/`CT`/…) are flagged and require confirmation.
- **Cursor-first (Phase 10/11):** `CURSOR_START_HERE.md`, `.cursor/rules`, prompts
  10–13, and the daily-use / troubleshooting guides (Markdown + DOCX) are present.
- **General Docs cleanup (Phase 12):** classified and moved (never deleted);
  see `GENERAL_DOCS_CLEANUP_REPORT.md`. Only the PII-free job description was
  promoted to tracked reference material.
- **Visual QA (Phase 13):** real rendered-PDF checks via Word; fixed bracketed level
  labels that tripped placeholder detection and a stale legacy `99-final/` folder.
- **Export (Phase 14):** deliverables-only by default; `--include-source` /
  `--include-internal` are opt-in.
- **Idempotency + cleanup (Phase 15):** reruns are stable; `zume candidate cleanup`
  removes `__vN` / `99-final` after preview.
- **Tests (Phase 16):** new suites `test_question_library`, `test_agenda`,
  `test_simplification`, `test_cli`, `test_feedback_and_schedule_docs`.
- **CI (Phase 17):** `workflow_dispatch` added; v2-aware candidate discovery, a
  simplification-invariants gate, and a "no candidate data tracked" gate added.

## Coverage note

Total coverage is **80.77%** (branch + statement) against an 80% CI gate. The
remaining gaps are in legacy CLI trigger shims and render code paths that only run
with a live word processor; these are exercised on developer Windows machines but
skipped (with an explicit warning) where no renderer is installed.

## Method note

All results above were reproduced in this session from a clean virtual environment.
Earlier reports were not reused as evidence of current behavior.
