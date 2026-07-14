# Finalize After the Interview

## Objective
After the interview has happened, use the interviewer's notes to generate the
final evaluation and post-interview communications.

## Inputs
Interview notes (text or a file under `input/`). The candidate must already have
a pre-interview package (status `READY_FOR_INTERVIEW` or `INTERVIEW_SCHEDULED`).

## Privacy boundary
Real notes stay under git-ignored paths. Never paste candidate content into
chat, logs, or reports.

## Files allowed to change
Only git-ignored candidate output. No source, config, test, or doc changes.

## Validation commands
```
zume finalize --candidate "<ref>" --notes input\<notes> [--leadership]
zume validate --candidate "<ref>"
git status --short        # must show no candidate files
```

## Stop conditions
Do not run finalize unless the user has explicitly stated the interview is
complete and provided non-empty notes. Blocked if the candidate is not in a
ready/scheduled state.

## Required final report
Final decision and status, the two new deliverable filenames, and confirmation
that git status shows no candidate data.

## Git restrictions
Never stage or commit candidate data. Do not push.
