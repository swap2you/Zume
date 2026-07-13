# Add or Rotate Interview Exercises

## Objective
Add new interview exercise variants to `config/exercise-library.yaml` for a
requested area without duplicating existing tasks.

## Inputs
The target skill area and desired difficulty, plus the existing library.

## Privacy boundary
No candidate data is involved. Reference solutions are interviewer-only and must
never be written into candidate-facing output.

## Files allowed to change
`config/exercise-library.yaml`, `tests/test_exercises.py`, and documentation.

## Validation commands
```
pytest -q tests/test_exercises.py
ruff check .
zume demo
```

## Stop conditions
Stop if a new task duplicates an existing `variant_family` fingerprint, or if an
exercise is missing any required field (task, requirement-change follow-up,
debugging follow-up, expected reasoning, reference solution, scoring rubric,
red flags, independence questions).

## Required final report
A short summary of added exercise IDs, their variant families, and status.

## Git restrictions
Do not push. Commit only when explicitly authorized.
