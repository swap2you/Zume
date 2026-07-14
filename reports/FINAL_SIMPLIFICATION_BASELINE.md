# Final Simplification — Verified Baseline

- **Date:** 2026-07-13
- **Branch:** main
- **HEAD:** `4fd87e7d008b02bb2a816da71a7e4e287e4af00b` (matches expected baseline)
- **Remote:** `origin https://github.com/swap2you/Zume.git`
- **Working tree:** clean (only git-ignored generated artifacts present)
- **OS:** Windows 11 Pro (10.0.26200) · **Python:** 3.13.5
- **Environment:** `.venv-final` (fresh venv, `pip install -e ".[dev]" -c constraints.txt`)

## Reproduced commands and results

| Command | Result |
|---------|--------|
| `pytest -q` | **83 passed** (reproduced, not copied) |
| `zume demo` | Runs end-to-end; produces the fictional candidate package |

## Current package inventory (defect evidence)

Demo candidate `Mehta_Aarav_2026-07-13`:

- **26 DOCX files** generated (target after simplification: ≤ 7).
- **8 subfolders**: `00-source`, `01-screening`, `02-schedule`, `03-interview-prep`,
  `04-interview`, `05-feedback`, `06-communications`, **`99-final`** (to be removed
  from the new contract).
- Documents are duplicated into `99-final`, roughly doubling the file count.
- `__vN` versioned files: 0 in this fresh run, but `versioned_write_bytes` still
  creates them whenever a file is regenerated (non-idempotent reruns).

## Defects confirmed against the spec

1. Too many document types and duplication into `99-final`.
2. Workflow-numbered output folders instead of the target
   `source/_internal/deliverables` contract.
3. `versioned_write_bytes` produces user-visible `__vN` copies on regeneration.
4. Re-running `interview-prep` re-selects exercises (no assignment preservation).
5. Status history appends duplicates on rerun.
6. Interview guide is exercise-heavy; no full basic/intermediate/advanced
   question sequence per area with recommended answers.
7. No true 20-minute knockout round; no enforced 180-minute agenda.
8. Schedule duration mismatch (e.g. 90 min vs 3-hour guide) not blocked.
9. Export includes internal working files, not a clean deliverables-only package.

## Method note

Results above were reproduced in this session from a fresh virtual environment.
Prior reports (`FINAL_VALIDATION_REPORT.md`, `HARDENING_FINAL_REPORT.md`) were
**not** used as proof of current behavior.
