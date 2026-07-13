# Zume Privacy Model

## Principles

- Local-first. Candidate data never leaves the machine and is never committed.
- The repository exposes hiring methodology (standards, exercises, answers), so
  it should be **private**. See `reports/PUBLIC_REPOSITORY_RISK_ASSESSMENT.md`.
- Zume never auto-deletes candidate data; deletion is an explicit, confirmed act.

## What is git-ignored (never committed)

- `candidates/**` (except `.gitkeep`), `input/**`, `output/**`
- `data/*.db`, `data/*.sqlite*` and all backups
- `General Docs/` (real candidate material on disk)
- `*.pdf`, `*.png`, `*.jpg`, `*.jpeg`, `*.zip`
- `.env`, `*.env`, `.env.*`
- Office temp files (`~$*.docx`), coverage/build artifacts, virtualenvs

Only the fictional sample (`examples/fictional-candidate/`) is tracked.

## Verifying privacy

```powershell
zume validate --candidate <folder>   # includes git ignore probes
zume scan-secrets                     # secrets + PII over tracked text files
git status --short                    # must show no candidate files
git diff --cached --name-only         # review before every commit
```

Automated tests enforce these guarantees: `tests/test_privacy.py` and
`tests/test_security.py` fail if sensitive paths become trackable, if generated
candidate documents are tracked, or if secrets/PII appear in tracked files.

## Candidate lifecycle

| Command | Effect |
|---------|--------|
| `zume candidate export --candidate "<ref>"` | Zip the folder into git-ignored `output/`. |
| `zume candidate archive --candidate "<ref>"` | Move the folder under `candidates/_archive`. |
| `zume candidate delete --candidate "<ref>"` | Preview what would be deleted (no deletion). |
| `zume candidate delete --candidate "<ref>" --confirm` | Delete folder + all DB rows (transactional). |

Deletion covers the candidate folder and every related SQLite row: source-file
metadata, screenings, interviews, scores, communications, status history,
artifacts, and exercise assignments.

## Retention

`config/privacy.yaml` documents `retention_days` (default 180) and keeps
`auto_purge: false`. Automatic purging is intentionally not implemented; operators
delete explicitly.

## Handling real data safely

Use `.cursor/prompts/06_PROCESS_CANDIDATE_SAFE.md`. Never paste real candidate
text into chat, logs, reports, or test fixtures. Reports must not echo candidate
file contents.
