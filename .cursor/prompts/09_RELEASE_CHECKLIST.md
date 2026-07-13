# Release Checklist

## Objective
Confirm the repository is in a releasable state before tagging or sharing.

## Inputs
The current working tree.

## Privacy boundary
Confirm no candidate data is tracked. Recommend the repository be private before
any real candidate material is used.

## Files allowed to change
Version in `pyproject.toml`, `constraints.txt`, and changelog/docs only.

## Validation commands
```
python -m pip install -e ".[dev]" -c constraints.txt
python -m compileall src
pytest -q --cov=zume --cov-fail-under=80
ruff check .
mypy src
python -m build
zume demo
zume validate --candidate <demo-folder>
zume db check
zume scan-secrets
git status --short
git diff --cached --name-only
```

## Stop conditions
Do not release if any gate fails, if secrets/PII are found, or if candidate data
is staged. Do not claim production-readiness with a skipped gate.

## Required final report
A go/no-go decision with the exact gate results and any manual actions required
(e.g., make the repository private, install LibreOffice for render validation).

## Git restrictions
Tag/push only when explicitly authorized. Never force-push main.
