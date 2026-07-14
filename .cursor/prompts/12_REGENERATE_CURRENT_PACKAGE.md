# Regenerate the Current Package (Idempotent)

## Objective
Re-run intake for an existing candidate to refresh deliverables without changing
the assigned exercises, schedule, or status history.

## Inputs
An existing candidate reference. The same resume/schedule already on file.

## Privacy boundary
All real data stays under git-ignored paths. Never paste candidate content into
chat, logs, or reports.

## Files allowed to change
Only git-ignored candidate output.

## Validation commands
```
zume intake --resume input\<resume> --schedule-details "<same details>"
zume validate --candidate "<ref>"
```

## Stop conditions
A normal rerun MUST be idempotent: same assigned exercises, same visible
filenames, no new `__vN` files, and no duplicated status events. Only re-assign
exercises when explicitly requested:
```
zume intake ... --rotate-exercises --rotation-reason "<reason>"
```

## Required final report
Confirmation that the deliverable set is unchanged in count (<= 7), exercises are
preserved (or rotated with the recorded reason), and no versioned files exist.

## Git restrictions
Never stage or commit candidate data. Do not push.
