# Zume Operating Guide

## Install

```powershell
cd C:\Development\Workspace\Zume
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]" -c constraints.txt
.\.venv\Scripts\Activate.ps1
```

## 1. Screen a resume

```powershell
zume filter-resume --input input\Candidate.pdf
# or paste text:
zume filter-resume --text-file input\pasted.txt --name "Candidate Name"
```

Output: standardized resume, ATS screening, recruiter feedback (DOCX + MD), and
`screening.json`. The reported percentage is **resume evidence coverage**, not a
competency score. The experience gate is reported as `passed`, `failed`, or
`unknown` (unknown → conditional manual review).

## 2. Interview prep (gated)

```powershell
zume interview-prep --candidate "Candidate Name"
```

- Proceed → full kit.
- Conditional → kit generated, unverified mandatory skills highlighted.
- Do Not Proceed → **blocked**. To proceed intentionally:

```powershell
zume interview-prep --candidate "Candidate Name" --override `
    --override-reason "Reason recorded in JSON, status, DB and focus sheet"
```

Artifacts: focus sheet, full interview guide (interviewer-only), scorecard,
interviewer exercise pack (with solutions), and a candidate exercise sheet
(tasks only). Exercises rotate to avoid reuse across candidates.

## 3. Schedule

```powershell
zume schedule-interview --candidate "Candidate Name" `
    --details "Date: 2026-07-20`nTime: 10:00 AM ET`nDuration: 90 minutes`nInterviewers: Panel"
```

Screenshots are metadata-only and untrusted until details are confirmed. The
record stays "needs confirmation" if timezone/date/time/duration checks fail.

## 4. Feedback

```powershell
zume interview-feedback --candidate "Candidate Name" --notes input\notes.txt --leadership
```

Produces the final evaluation, completed scorecard, and recruiter/leadership
drafts. Interview performance scores are separate from resume evidence coverage.

## Lifecycle, database, and security

```powershell
zume candidate list
zume candidate export  --candidate "Candidate Name"
zume candidate archive --candidate "Candidate Name"
zume candidate delete  --candidate "Candidate Name" --confirm
zume db check
zume db backup
zume scan-secrets
```

## Validation

```powershell
zume demo
zume validate --candidate <demo-folder>
```

Install LibreOffice to enable rendered-PDF checks (otherwise render is skipped
with a warning; see `reports/DOCX_RENDER_VALIDATION.md`).
