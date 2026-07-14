# Troubleshoot a Candidate

## Objective
Diagnose a problem with a candidate package (bad extraction, wrong name, schedule
mismatch, missing documents, git leakage) without guessing.

## Inputs
The candidate reference and a description of the symptom.

## Privacy boundary
Never print real candidate content into chat, logs, or reports. Refer to files
by path only.

## Files allowed to change
Only git-ignored candidate output, unless the user explicitly switches to
development mode to fix a bug.

## Validation commands
```
zume validate --candidate "<ref>"        # structural + render checks
zume db check
zume scan-secrets
git status --short
zume candidate cleanup --candidate "<ref>" --preview
```

## Stop conditions
Stop and ask the user before deleting anything, before migrating a legacy folder
with `--apply`, or if any candidate file appears tracked by Git.

## Required final report
The identified cause, the exact corrective command run (or recommended), the
expected result, and whether the issue is resolved. See
`docs/ZUME_TROUBLESHOOTING_GUIDE.md` for the symptom catalogue.

## Git restrictions
Never stage or commit candidate data. Do not push.
