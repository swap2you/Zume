# Zume

Zume is a lightweight, local-first Senior SDET hiring operations toolkit. It
turns a resume and interviewer notes into a small, consistent set of interview
documents. Zume is driven primarily from **Cursor**, using two commands:
`zume intake` (before the interview) and `zume finalize` (after the interview).

## Start here

- **[`CURSOR_START_HERE.md`](CURSOR_START_HERE.md)** — how to run Zume from Cursor.
- **[`docs/ZUME_DAILY_USE_GUIDE.md`](docs/ZUME_DAILY_USE_GUIDE.md)** — day-to-day use for non-developers.
- **[`docs/ZUME_TROUBLESHOOTING_GUIDE.md`](docs/ZUME_TROUBLESHOOTING_GUIDE.md)** — common issues and fixes.

## Local path
`C:\Development\Workspace\Zume`

## Setup

```powershell
cd C:\Development\Workspace\Zume
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]" -c constraints.txt
```

The `zume` command is then available at `.venv\Scripts\zume` (or plainly as
`zume` after activating the venv with `.\.venv\Scripts\Activate.ps1`).

## The two-command workflow

Zume uses exactly two operational commands:

```powershell
# 1. Before the interview — screen the resume and build the full package, then STOP.
zume intake --resume input\Candidate.pdf
zume intake --text-file input\pasted-resume.txt --name "Candidate Name"
zume intake --resume input\Candidate.pdf `
    --schedule-details "Date: 2026-07-20`nTime: 10:00 AM`nTimezone: America/New_York`nDuration: 180 minutes"

# 2. After the interview — turn interviewer notes into the final evaluation.
zume finalize --candidate "Candidate Name" --notes input\notes.txt --leadership
```

`intake` never produces interview feedback; it stops and waits for real
interviewer notes. `finalize` runs only after those notes exist.

The standard interview is **180 minutes** with a **20-minute knockout round**.

### Candidate folder contract

Every candidate folder contains exactly three subfolders:

- `source/` — the original resume (and any schedule screenshot).
- `_internal/` — working JSON and interviewer notes (never shared).
- `deliverables/` — the final, user-facing DOCX files.

There is no separate legacy final-copy folder and there are no user-visible
versioned (`__vN`) files. At most seven canonical deliverables exist:

| # | Deliverable | Audience |
|---|-------------|----------|
| 01 | `01_Screening_Summary.docx` | interviewer |
| 02 | `02_Three_Hour_Interview_Guide.docx` | interviewer (answers + solutions) |
| 03 | `03_Interview_Scorecard.docx` | interviewer |
| 04 | `04_Candidate_Exercise_Sheet.docx` | **candidate-shareable** (tasks only) |
| 05 | `05_Schedule_and_Communications.docx` | interviewer |
| 06 | `06_Final_Interview_Evaluation.docx` | interviewer (after `finalize`) |
| 07 | `07_Post_Interview_Communications.docx` | interviewer (after `finalize`) |

### Guards worth knowing

- **Do-Not-Proceed:** `intake` builds only the screening summary unless you pass
  `--override --override-reason "<reason>"`.
- **Finalized candidates:** re-running `intake` on an interviewed/selected/
  rejected candidate is blocked. Use `--reopen --reopen-reason "<reason>"` to
  regenerate the pre-interview package; final documents are preserved.
- **Export:** `zume candidate export` is deliverables-only by default and records
  an export event **without** changing the hiring workflow status.
- **Incomplete notes:** `finalize` will not produce a "Selected" from partial
  notes; it lists the missing mandatory areas and routes to manual review.

### Screening terminology (important)

The screening percentage is **resume evidence coverage**, not a competency
score. It measures how strongly the resume evidences each mandatory skill
(quantified > project > responsibility > skills-list mention). It does **not**
establish technical competency — that is verified only through live assessment.
The experience gate reports an explicit state: `passed`, `failed`, or `unknown`.

## Lifecycle, database and security utilities

```powershell
zume candidate list
zume candidate export  --candidate "Candidate Name"     # deliverables-only zip into output/
zume candidate migrate --candidate "Candidate Name" --preview   # legacy folder -> v2
zume candidate cleanup --candidate "Candidate Name" --preview   # remove redundant copies
zume candidate archive --candidate "Candidate Name"
zume candidate delete  --candidate "Candidate Name" --confirm

zume db check          # schema version, integrity, foreign keys, duplicates
zume db backup         # validated online backup into git-ignored data/
zume scan-secrets      # scan tracked text AND DOCX files for secrets and PII
```

Retention is documented in `config/privacy.yaml`. Zume never auto-deletes data.

## Fictional sample and validation

```powershell
zume demo
zume validate --candidate Mehta_Aarav_2026-07-13
```

## Documentation

- `docs/ARCHITECTURE.md` — modules, data flow, and storage design.
- `docs/PRIVACY.md` — privacy model, ignore rules, and lifecycle commands.
- `docs/reference/legacy/` — historical notes on the retired v1 workflow.
- `reports/` — audit, risk assessment, render validation, and lockdown reports.

## Privacy

The repository must be private before any real candidate material is used.
Candidate files, generated outputs, screenshots, backups, and the production
SQLite database remain git-ignored. Run `zume scan-secrets` and
`git status --short` before every commit. CI uses only fictional data and never
uploads candidate folders.
