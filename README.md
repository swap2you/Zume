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

## Privacy
The current repository must be private before any real candidate material is used. Candidate files, generated outputs, screenshots, `General Docs/` and the production SQLite database must remain git-ignored.
