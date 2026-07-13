# Process Candidate Safely (Privacy-First)

## Objective
Process a real candidate end to end while guaranteeing no candidate data is ever
committed.

## Inputs
A real resume/screenshot/notes placed under `input/` (git-ignored).

## Privacy boundary
All real data stays under git-ignored paths (`input/`, `candidates/`, `output/`,
`data/`). Run `zume scan-secrets` and `git status` before finishing. Never paste
real candidate text into chat, logs, or reports.

## Files allowed to change
Only git-ignored candidate output. No source or config changes.

## Validation commands
```
zume filter-resume --input input\<file>
zume interview-prep --candidate "<ref>"
zume schedule-interview --candidate "<ref>" --details "<confirmed>"
zume interview-feedback --candidate "<ref>" --notes input\<notes>
zume validate --candidate "<ref>"
git status --short        # must show no candidate files
zume scan-secrets
```

## Stop conditions
Stop immediately if `git status` shows any candidate file as tracked/staged, or
if the screening decision is Do-Not-Proceed (unless an override with reason is
intended).

## Required final report
Decision, generated paths (folder-relative), and confirmation that git status is
clean of candidate data.

## Git restrictions
Never stage or commit anything under `candidates/`, `input/`, `output/`, or
`data/`. Do not push.
