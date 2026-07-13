# Independent Repository Audit

Date: 2026-07-13
Auditor: independent reproduction pass (not a copy of the prior report)
Repository: `https://github.com/swap2you/Zume`
Branch: `main`
HEAD at audit start: `53bfc291c9134890b9751f7ac7a155df1a9f177d`

## Environment

| Item | Value |
|------|-------|
| Operating system | Microsoft Windows 10.0.26200.8655 |
| Python | 3.13.5 |
| Virtual environment | **Fresh** `.venv-audit` created for this audit (not the pre-existing `.venv`) |
| Install command | `.venv-audit\Scripts\python -m pip install -e ".[dev]"` |
| Install result | Success. Notable resolved versions: pydantic 2.13.4, typer 0.26.8, python-docx 1.2.0, pytest 9.1.1, ruff 0.15.21, mypy 2.3.0, coverage 7.15.1 |

> Note: `pyproject.toml` uses lower-bound version specifiers, so a fresh install
> today resolves newer dependency versions than the prior session. All gates
> still pass on these newer versions.

## Reproduction of the documented gates

The claims below are compared against `reports/FINAL_VALIDATION_REPORT.md` and
`reports/IMPLEMENTATION_PLAN.md`.

| Gate | Command | Claimed | Reproduced result | Status |
|------|---------|---------|-------------------|--------|
| 1. Byte-compile | `python -m compileall src` | Pass | Exit 0 | **Reproduced** |
| 2. Tests | `pytest -q` | 36 passed | 36 passed | **Reproduced** |
| 2c. Coverage | `pytest --cov=zume` | (not previously reported) | 87% total | **Reproduced** (new measurement) |
| 3. Lint | `ruff check .` | Pass | "All checks passed!" | **Reproduced** |
| 4. Types | `mypy src` | Pass, 16 files | "no issues found in 16 source files" | **Reproduced** |
| 5. Demo | `zume demo` | Pass, 4 workflows | Exit 0, all 4 workflows, screening Proceed / feedback Proceed→SELECTED | **Reproduced** |
| 6. Folder validation | `zume validate --candidate Mehta_Aarav_2026-07-13` | 144 passed, 1 warning, 0 errors | **306 passed**, 1 warning, 0 errors | **Partially reproduced** (see below) |
| 7. Git privacy | `git check-ignore` | All ignored | All ignored | **Reproduced** |
| 8. DOCX structural re-open | part of gate 6 | Pass | Pass (0 errors) | **Reproduced** |
| 9. LibreOffice render | `soffice` lookup | Warning (not installed) | Warning (not installed at audit start) | **Reproduced** (see Phase 12 for follow-up) |

## Differences between claimed and reproduced results

1. **Validation count 144 → 306 (Partially reproduced).**
   The validator walks every `*.docx` under the candidate folder. Because
   `zume demo` had already been run in a prior session and was run again during
   this audit, the versioning logic produced archived duplicates
   (`*__v1.docx`, `*__v2.docx`) in each stage folder. The validator inspects
   those too, so the passed-check count grew from 144 to 306. **Zero errors in
   both cases**, so the quality signal is unchanged, but the raw count in the
   prior report is not stable across repeated demo runs. This is a real
   observation about the report's reproducibility, not a functional defect.

2. **Newer dependency versions.** The prior report ran against the versions
   present in `.venv`; a clean install resolves newer majors (e.g. pytest 9,
   mypy 2, ruff 0.15). All gates still pass, but the prior report did not pin
   versions, so exact reproduction of the dependency set is not possible. This
   is addressed in Phase 9 (reproducible dependency management).

## Defects and weaknesses identified during inspection

These feed the hardening phases that follow.

1. **Experience-gate contradiction (Phase 2).** In `src/zume/screening.py`,
   `screen_resume` sets `gate_passed = False` when experience is unreadable, and
   `decide()` returns `DO_NOT_PROCEED` whenever `gate_passed` is false. The
   inline comment says unknown experience should be "a risk, not an automatic
   reject", but the code rejects it anyway. Missing/unknown experience is
   therefore treated identically to sub-minimum experience. **Confirmed bug.**

2. **Misleading score terminology (Phase 3).** The weighted keyword-evidence
   percentage is labeled "Screening score" / "Weighted evidence score" and
   shown alongside the decision, implying measured competence. It only measures
   resume keyword coverage.

3. **Keyword-only evidence over-credits (Phase 4).** A single skills-list
   mention yields full "explicit" credit, identical to project or ownership
   evidence. No evidence typing, confidence, recency or ownership signal.

4. **No workflow gate on interview-prep (Phase 5).** `run_interview_prep` builds
   a full kit regardless of screening decision; a `DO_NOT_PROCEED` candidate can
   silently proceed to interview preparation.

5. **Exercise library exposes answers with no rotation controls (Phase 6).**
   Reference solutions are emitted; there is no active/retired status, rotation,
   usage tracking, difficulty, or candidate/interviewer separation of material.

6. **No candidate lifecycle commands (Phase 7).** No export/archive/delete/purge;
   deletion of DB rows is not possible through the CLI.

7. **Thin database layer (Phase 8).** No schema version, migrations, foreign-key
   enforcement (`PRAGMA foreign_keys` is off by default in sqlite3), integrity
   check, backup, or indexes.

8. **Scheduling lacks validation (Phase 13).** No timezone capture, no rejection
   of past dates / impossible times / non-positive duration, and no per-field
   source/confidence.

9. **Minor hygiene.** A `.coverage` file produced by `pytest --cov` is not
   git-ignored; `*.egg-info/` is ignored but `.venv-audit` relies on the venv's
   own generated `.gitignore`. Both are tightened in Phase 11.

## Conclusion

The prior build reproduces cleanly on a fresh environment: all functional gates
pass with zero errors. The main caveats are (a) the validation *count* is not
stable across repeated demo runs, and (b) dependencies were unpinned. The
inspection confirmed the experience-gate bug called out in the hardening brief
and surfaced the additional weaknesses listed above, all of which are addressed
in Phases 2–14.
