# Rotate Interview Exercises

## Objective
Rotate the active exercise set so the same primary exercise is not repeatedly
assigned, and retire over-exposed exercises.

## Inputs
`config/exercise-library.yaml` and the SQLite `exercise_usage` /
`candidate_exercises` tables.

## Privacy boundary
No candidate PII is required. Reference solutions remain interviewer-only.

## Files allowed to change
`config/exercise-library.yaml` (status/rotation metadata) and tests.

## Validation commands
```
zume db check
pytest -q tests/test_exercises.py
zume demo
```

## Stop conditions
Keep at least three active variants per core area (Java, Selenium, REST Assured,
SQL/Oracle, Framework design, Debugging). Do not retire an exercise if doing so
drops an area below three active variants.

## Required final report
Which exercises were retired/activated/added and the resulting active counts per
core area.

## Git restrictions
Commit only when explicitly authorized. Do not push.
