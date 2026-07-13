# Harden and Validate

## Objective
Perform an independent audit and hardening pass on the existing Zume toolkit
without rebuilding it or adding web/GUI/cloud infrastructure. Preserve the name
Zume.

## Inputs
The current repository and its reports under `reports/`.

## Privacy boundary
Never add real resumes, candidate data, screenshots, notes, emails, phone
numbers, generated documents, or production databases to Git. Verify ignore
rules before and after every Git operation.

## Files allowed to change
Source under `src/`, config under `config/`, tests under `tests/`, CI under
`.github/`, docs, and `reports/`. Never candidate data.

## Validation commands
```
python -m compileall src
pytest -q --cov=zume --cov-report=term-missing
ruff check .
mypy src
python -m build
zume demo
zume validate --candidate <demo-folder>
zume db check
zume db backup
zume scan-secrets
```

## Stop conditions
Do not describe the repository as production-ready if any mandatory gate fails or
is skipped. Do not push until explicitly authorized.

## Required final report
`reports/HARDENING_FINAL_REPORT.md` with exact commands, exit codes, test
counts, coverage, files changed, privacy results, render results, limitations,
remaining risks, git status, and whether anything was committed or pushed.

## Git restrictions
One focused commit only after all gates pass. Never push without explicit
authorization.
