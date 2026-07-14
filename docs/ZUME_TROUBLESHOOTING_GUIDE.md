# Zume Troubleshooting Guide

Each item lists the symptom, the corrective action, the expected result, and when
to stop rather than guessing.

## Cursor cannot see the attachment

- Re-attach the file and confirm it is saved under `input/`.
- Expected: the file path is visible before you send the instruction.
- Stop if the file is empty or zero bytes; obtain a fresh copy.

## Resume text extraction is empty or garbled

- Ensure the PDF is text-based, not a scanned image; try a DOCX or TXT export.
- Expected: the screening summary shows a real resume summary.
- Stop and request a better source file if extraction stays empty.

## Candidate name is parsed incorrectly

- Re-run intake with `--name "First Last"`.
- Expected: the candidate folder and documents use the corrected name.

## Experience is unknown or conflicting

- This routes to a conditional manual review; it is not an automatic rejection.
- Confirm the candidate's total experience manually before deciding.

## Candidate already exists

- Re-running intake for the same name/date is idempotent and updates in place.
- Expected: the same folder, same assigned exercises, no duplicate files.

## Interview prep is blocked

- The decision is Do-Not-Proceed. To proceed anyway, re-run with
  `--override --override-reason "<reason>"`. The reason is recorded.

## Schedule image is ambiguous

- Screenshots are never trusted silently. Provide the details as text via
  `--schedule-details` (Date, Time, Timezone, Duration, ...).

## Schedule duration is not three hours

- The standard is 180 minutes. A different duration is flagged as a mismatch.
- Confirm a 180-minute schedule or intentionally generate a shortened plan.
- Stop and confirm with the recruiter before relying on a mismatched schedule.

## Timezone is ambiguous

- Bare `ET`/`CT`/`MT`/`PT` are flagged. Record an IANA zone such as
  `America/New_York` and re-run.

## Package contains duplicate or versioned files

- Run `zume candidate cleanup --candidate "<ref>" --preview` then `--apply`.
- Expected: no `__vN` files and no `99-final` folder remain.

## Rerun changed exercises

- Normal reruns preserve exercises. If they changed, you likely passed
  `--rotate-exercises`. Omit it to keep the assignment.

## Missing recommended answer

- Every guide question and follow-up must have an answer. If one is missing,
  the question library is invalid — run `pytest tests/test_question_library.py`.

## Document has blank or sparse pages

- Validation warns on sparse trailing pages. Re-run `zume validate` and review
  the flagged document; regenerate after fixing content.

## Word or LibreOffice render failure

- Structural validation still runs. Install LibreOffice
  (`choco install libreoffice-fresh -y`) to enable rendered-PDF checks.

## CLI command not found

- Activate the venv (`.\.venv\Scripts\Activate.ps1`) or call the shim directly:
  `.\.venv\Scripts\zume`.

## Virtual environment problem

- Recreate it: delete `.venv`, then `python -m venv .venv` and
  `pip install -e ".[dev]" -c constraints.txt`.

## Database integrity failure

- Run `zume db backup` first, then `zume db check`. Restore from a validated
  backup if integrity or foreign-key checks fail.

## Candidate files appear in Git

- Stop immediately. Run `git status --short`; nothing under `candidates/`,
  `input/`, `output/`, or `data/` should ever appear. Fix `.gitignore` before
  continuing.

## Export ZIP is too large or contains internal files

- The default export is deliverables-only. Do not pass `--include-internal`
  unless you specifically need an audit bundle.

## How to restore from backup

- Locate the validated backup under `data/`, then open it to confirm before
  replacing the working database.

## How to run a complete health check

- `zume validate --candidate "<ref>"`, `zume db check`, `zume scan-secrets`,
  and `git status --short` together confirm document, database, secret, and
  privacy health.
