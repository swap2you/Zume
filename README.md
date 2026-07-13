# Zume

Zume is a lightweight, local-first Senior SDET hiring operations toolkit. It turns resumes, interview schedule screenshots, and interview notes into structured screening, interview, feedback, and communication artifacts.

## Local path
`C:\Development\Workspace\Zume`

## Setup

```powershell
cd C:\Development\Workspace\Zume
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

For a reproducible install pinned to verified versions, add the constraints
file (`pyproject.toml` stays the source of truth):

```powershell
.\.venv\Scripts\python -m pip install -e ".[dev]" -c constraints.txt
```

The `zume` command is then available at `.venv\Scripts\zume` (or plainly as
`zume` after activating the venv with `.\.venv\Scripts\Activate.ps1`).

## Core triggers
- `Filter Resume – Automation Hiring`
- `Interview Prep – Automation Hiring`
- `Schedule Interview – Automation Hiring`
- `Interview Feedback – Automation Hiring`

## Usage

Place input files in `input/` (or reference any path). Every workflow writes
into `candidates/LastName_FirstName_YYYY-MM-DD/` and promotes validated DOCX
files to that folder's `99-final/`.

```powershell
# 1. Screen a resume (PDF, DOCX or TXT; --text-file for pasted text)
zume filter-resume --input input\Rohan_N.pdf
zume filter-resume --text-file input\pasted-resume.txt --name "Rohan N"

# 2. Build the interview kit (focus sheet, 3-hour guide, scorecard, exercises)
zume interview-prep --candidate "Rohan N"

# 3. Record the schedule (screenshot metadata + confirmed details)
zume schedule-interview --candidate "Rohan N" --image input\rohan_interview.png `
    --details "Date: 2026-07-20`nTime: 10:00 AM ET`nDuration: 90 minutes"

# 4. Turn interviewer notes into the evaluation package
zume interview-feedback --candidate "Rohan N" --notes input\notes.txt --leadership

# Natural-language trigger mapping
zume run --trigger "Filter Resume – Automation Hiring" --input input\Rohan_N.pdf

# Fictional end-to-end sample and validation
zume demo
zume validate --candidate Mehta_Aarav_2026-07-13
```

### Screening terminology (important)

The screening percentage is **resume evidence coverage**, not a competency
score. It measures how strongly the resume evidences each mandatory skill
(quantified > project > responsibility > skills-list mention). It does **not**
establish technical competency — that is verified only through live assessment.
The experience gate reports an explicit state: `passed`, `failed`, or `unknown`
(unknown/conflicting experience routes to a conditional manual review rather
than an automatic rejection).

### Workflow gate and override

`interview-prep` will not silently prepare a rejected candidate:

```powershell
# Blocked for a Do-Not-Proceed decision unless intentionally overridden:
zume interview-prep --candidate "Rohan N" --override `
    --override-reason "Hiring manager requested a courtesy screen"
```

The override reason is recorded in the candidate JSON, status history, SQLite,
and the generated focus sheet. Interview prep also emits two exercise artifacts:
an **interviewer** pack (with reference solutions) and a **candidate** sheet
(tasks only — never solutions).

### Candidate privacy lifecycle

```powershell
zume candidate list
zume candidate export  --candidate "Rohan N"            # zip into git-ignored output/
zume candidate archive --candidate "Rohan N"            # move under candidates/_archive
zume candidate delete  --candidate "Rohan N"            # preview only (no --confirm)
zume candidate delete  --candidate "Rohan N" --confirm  # folder + all DB rows (transactional)
```

Retention is documented in `config/privacy.yaml`. Zume never auto-deletes data.

### Database and security utilities

```powershell
zume db check          # schema version, integrity, foreign keys, duplicates
zume db backup         # validated online backup into git-ignored data/
zume scan-secrets      # scan tracked text files for secrets and PII
```

## Outputs by workflow

| Workflow | Folder | Artifacts |
|----------|--------|-----------|
| Screening | `01-screening` | Standardized Resume, ATS Screening, Recruiter Feedback (DOCX + MD draft) |
| Interview prep | `03-interview-prep` | Focus Sheet, Full Interview Guide, Scorecard, Exercise Pack |
| Schedule | `02-schedule` | Interview Schedule DOCX, join/reschedule/cancel/no-show drafts (MD) |
| Feedback | `05-feedback` | Final Evaluation, Completed Scorecard, Recruiter/Leadership Feedback (DOCX + MD) |

Copy-ready communication drafts land in `06-communications`. Searchable
metadata (candidates, screenings, scores, status history, artifacts) is indexed
in `data/zume.db` (SQLite, git-ignored).

## Build with Cursor
Open `.cursor/prompts/00_MASTER_BUILD_PROMPT.md` in Cursor Agent mode and run it from the repository root.

## Documentation
- `docs/OPERATING_GUIDE.md` — day-to-day operator workflows and commands.
- `docs/ARCHITECTURE.md` — modules, data flow, and storage design.
- `docs/PRIVACY.md` — privacy model, ignore rules, and lifecycle commands.
- `docs/TROUBLESHOOTING.md` — common issues and fixes.
- `.cursor/prompts/` — task prompts (00–09), each with objective, inputs,
  privacy boundary, allowed files, validation commands, stop conditions,
  required report, and git restrictions.
- `reports/` — audit, risk assessment, render validation, and hardening reports.

## Privacy
The current repository must be private before any real candidate material is
used (see `reports/PUBLIC_REPOSITORY_RISK_ASSESSMENT.md`). Candidate files,
generated outputs, screenshots, `General Docs/`, backups, and the production
SQLite database must remain git-ignored. Run `zume scan-secrets` and
`git status --short` before every commit. CI uses only fictional data and never
uploads candidate folders.
