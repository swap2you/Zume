# Zume Hardening — Final Validation Report

- **Date:** 2026-07-13
- **Repository:** https://github.com/swap2you/Zume
- **Branch:** main
- **Baseline commit (pre-commit HEAD):** `53bfc291c9134890b9751f7ac7a155df1a9f177d`
- **OS:** Microsoft Windows 11 Pro (10.0.26200)
- **Python:** 3.13.5
- **Fresh environment:** `.venv-final` (created for this validation), installed with `pip install -e ".[dev]" -c constraints.txt`

## Scope
Independent audit and hardening pass across Phases 1–15. The application was
not rebuilt; it remains a local-first Python CLI. Product name **Zume**
preserved throughout.

## Validation gates (fresh environment)

| # | Gate | Command | Exit | Result |
|---|------|---------|------|--------|
| 1 | Clean install | `python -m venv .venv-final` + `pip install -e ".[dev]" -c constraints.txt` | 0 | PASS — reproducible from pinned constraints |
| 2 | Compile | `python -m compileall src` | 0 | PASS |
| 3 | Tests | `pytest -q` | 0 | PASS — 83 passed |
| 4 | Coverage threshold | `pytest --cov=zume --cov-fail-under=80` | 0 | PASS — **80.55%** (threshold 80%) |
| 5 | Lint | `ruff check .` | 0 | PASS — All checks passed |
| 6 | Types | `mypy src` | 0 | PASS — no issues in 18 source files |
| 7 | Package build | `python -m build` | 0 | PASS — `zume-0.1.0.tar.gz` + `-py3-none-any.whl` |
| 8 | Demo | `zume demo` | 0 | PASS — fictional candidate generated |
| 9 | Candidate validation | `zume validate --candidate Mehta_Aarav_2026-07-13` | 0 | PASS — 294 checks passed, 1 WARN (LibreOffice absent) |
| 10 | DB check | `zume db check` | 0 | PASS — schema v2, integrity + FK OK, no duplicates |
| 11 | DB backup + restore validation | `zume db backup` | 0 | PASS — backup written and re-opened/validated |
| 12 | Candidate export | `zume candidate export` | 0 | PASS — `output/..._package.zip` created |
| 13 | Candidate archive | `zume candidate archive` | 0 | PASS — moved to `candidates/_archive/` |
| 14 | Candidate delete (fictional) | `zume candidate delete --confirm` | 0 | PASS — folder + DB rows removed; preview shown without `--confirm` |
| 15 | Privacy-ignore verification | `git check-ignore` on pdf/docx/db/env/png/jpg/General Docs | 0 | PASS — all sensitive types ignored |
| 16 | Secret scan | `zume scan-secrets` | 0 | PASS — no secrets or PII in tracked files |
| 17 | Git status review | `git status --short` | 0 | PASS — only intended source/doc/config/test files |
| 18 | LibreOffice render | n/a | — | SKIPPED — `soffice` not installed (no admin rights). See `reports/DOCX_RENDER_VALIDATION.md` |
| 19 | CI YAML validation | `python -c "yaml.safe_load(...)"` on `.github/workflows/ci.yml` | 0 | PASS — valid YAML |
| 20 | Staged-file review | `git diff --cached --name-only` + PII grep on staged diff | 0 | PASS — 47 files, no PII/secret matches |

## Test counts
- 83 tests passed, 0 failed, 1 warning.
- New test modules: `test_experience.py`, `test_exercises.py`, `test_interview_gate.py`,
  `test_lifecycle.py`, `test_database.py`, `test_scheduling.py`, `test_security.py`.

## Coverage
- Total: **80.55%** (branch coverage enabled, `fail_under = 80`).
- Lowest module: `validation.py` at 57% (render-path branches are only exercised
  when LibreOffice is present — see limitations).

## Files changed (47 staged)
- **Prompts:** `00`–`04` restructured to the 8-section contract; new `05`–`09`.
- **CI:** `.github/workflows/ci.yml` (Windows + Ubuntu, Python 3.11 & 3.13).
- **Config:** `exercise-library.yaml`, `hiring-standard.yaml` (evidence scoring),
  new `privacy.yaml`; `constraints.txt`; `pyproject.toml` (coverage config).
- **Source:** `models.py`, `screening.py`, `ingest.py`, `interview.py`,
  `scheduling.py`, `storage.py`, `validation.py`, `candidate.py`, `cli.py`,
  `config.py`; new `exercises.py`, `security.py`.
- **Tests:** 7 new modules + `test_screening.py`, `test_documents.py` updated.
- **Docs:** `README.md`, `AGENTS.md`, `.gitignore`; new `docs/ARCHITECTURE.md`,
  `docs/OPERATING_GUIDE.md`, `docs/PRIVACY.md`, `docs/TROUBLESHOOTING.md`.
- **Reports:** `INDEPENDENT_REPOSITORY_AUDIT.md`,
  `PUBLIC_REPOSITORY_RISK_ASSESSMENT.md`, `DOCX_RENDER_VALIDATION.md`,
  this report.

## Database migration details
- Schema version constant introduced; current version **2**.
- Migration v1 → v2 adds `override_reason` to the `interviews` table
  (idempotent, column-existence guarded).
- `PRAGMA foreign_keys = ON` enforced at connection.
- Indexes added for candidate name, status, date, and source hash.
- New tables: `exercise_usage`, `candidate_exercises`.
- `db check` runs `PRAGMA integrity_check`, foreign-key check, and duplicate
  detection; `db backup` writes a copy and re-opens it to validate.

## Privacy results
- `zume scan-secrets`: no secrets or PII in tracked files.
- Ignore rules confirmed for `.pdf`, `.png`, `.jpg`, `.docx`, `.env`,
  `*.sqlite*`, `candidates/`, `data/`, `output/`, `input/`, `General Docs/`.
- Staged diff scanned for emails, phone numbers, AWS keys, and private keys —
  no matches.
- Only fictional fixtures are tracked.

## DOCX render results
- Structural validation via `python-docx` passed for all generated documents.
- Rendered-PDF validation (page count, headings-in-text, header/footer,
  page-number fields) is implemented in `validation.py` but **skipped** because
  LibreOffice/`soffice` is not installed and cannot be installed without admin
  rights in this environment. A manual visual-inspection checklist is provided
  in `reports/DOCX_RENDER_VALIDATION.md`.

## Known limitations
- No automated visual DOCX→PDF render performed (LibreOffice unavailable).
- `validation.py` render branches are under-covered for the same reason.
- Deterministic evidence extraction is heuristic; it never invents evidence but
  can under-credit unusually formatted resumes.

## Remaining risks
- **The GitHub repository is public.** It exposes hiring standards, scoring
  rules, exercises, and reference solutions. Recommendation: make it private.
  See `reports/PUBLIC_REPOSITORY_RISK_ASSESSMENT.md`. This cannot be changed
  automatically and requires owner action.

## Git status
- 47 files staged; working tree otherwise clean (ignored artifacts hidden).
- No sensitive or generated files staged.

## Commit / push status
- **Committed:** see commit SHA reported in the chat response.
- **Pushed:** NO — awaiting explicit user authorization.

## Production-ready statement
One mandatory gate (LibreOffice visual render, Phase 12/Gate 18) was **skipped**
due to environment constraints. Therefore this repository is **not** declared
fully production-ready; all other gates passed.
