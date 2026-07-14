# Start a New Candidate (Pre-Interview Package)

## Objective
Screen a resume and build the complete pre-interview package, then stop before
any feedback.

## Inputs
A resume (PDF/DOCX/TXT) and optionally schedule details, placed under `input/`
(git-ignored). Attach them in Cursor.

## Privacy boundary
All real data stays under git-ignored paths (`input/`, `candidates/`, `output/`,
`data/`). Never paste real candidate text into chat, logs, or reports.

## Files allowed to change
Only git-ignored candidate output. No source, config, test, or doc changes.

## Validation commands
```
zume intake --resume input\<resume> --schedule-details "<confirmed details or file>"
zume validate --candidate "<ref>"
git status --short        # must show no candidate files
```

## Stop conditions
Stop after the pre-interview package is generated. Do NOT generate feedback. If
the decision is Do-Not-Proceed, only the screening summary is produced unless an
override with reason is explicitly requested.

## Required final report
Screening decision, status (`READY_FOR_INTERVIEW`/`INTERVIEW_SCHEDULED`),
deliverable filenames, any schedule warnings, and the next required user action.

## Git restrictions
Never stage or commit `candidates/`, `input/`, `output/`, or `data/`. Do not push.
