# Zume Operating Guide (LEGACY / v1 — historical only)

> This file documents the retired v1 four-command workflow and numbered
> candidate folders. It is kept for historical reference only. The current
> workflow is the two-command `intake` / `finalize` model — see
> `docs/ZUME_DAILY_USE_GUIDE.md`.

## Install

```powershell
cd C:\Development\Workspace\Zume
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]" -c constraints.txt
.\.venv\Scripts\Activate.ps1
```

## 1. Screen a resume (retired)

```powershell
zume filter-resume --input input\Candidate.pdf
zume filter-resume --text-file input\pasted.txt --name "Candidate Name"
```

Output: standardized resume, ATS screening, recruiter feedback, and
`screening.json`.

## 2. Interview prep, gated (retired)

```powershell
zume interview-prep --candidate "Candidate Name"
zume interview-prep --candidate "Candidate Name" --override `
    --override-reason "Reason recorded"
```

## 3. Schedule (retired)

```powershell
zume schedule-interview --candidate "Candidate Name" `
    --details "Date: 2026-07-20`nTime: 10:00 AM ET`nDuration: 90 minutes`nInterviewers: Panel"
```

## 4. Feedback (retired)

```powershell
zume interview-feedback --candidate "Candidate Name" --notes input\notes.txt --leadership
```

The v1 flow wrote into numbered subfolders (`00-source`, `01-screening`,
`02-schedule`, `03-interview-prep`, `04-interview`, `05-feedback`,
`06-communications`) and promoted validated DOCX files into a `99-final` folder.
These commands are now deprecated and hidden; they never create new v1 folders.
