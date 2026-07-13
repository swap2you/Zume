# Validate Zume Repository

## Objective
Inspect the entire repository and run every validation gate. Do not modify
product behavior unless required to fix a failed gate.

## Inputs
The current working tree at `C:\Development\Workspace\Zume`.

## Privacy boundary
Read-only for candidate data. Never open, print, or copy anything under
`candidates/`, `input/`, `output/`, `data/*.db`, or `General Docs/`.

## Files allowed to change
`reports/REPOSITORY_AUDIT.md` only (plus minimal fixes to failed gates if
explicitly required).

## Validation commands
```
python -m compileall src
pytest -q --cov=zume --cov-report=term-missing
ruff check .
mypy src
zume demo
zume validate --candidate <demo-folder>
zume db check
zume scan-secrets
```

## Stop conditions
Stop and report if any gate fails, or if a change would alter product behavior
beyond a required fix.

## Required final report
`reports/REPOSITORY_AUDIT.md` with pass/fail evidence, coverage, privacy
findings, DOCX render findings, and prioritized fixes.

## Git restrictions
Do not stage, commit, or push. Report status only.
