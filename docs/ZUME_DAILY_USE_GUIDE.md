# Zume Daily Use Guide

This guide is for everyday use in Cursor. You do not need to be a developer and
you do not need to memorize commands.

## One-time setup

- Install Python 3.11+ and open this repository folder in Cursor.
- In a terminal, create and activate a virtual environment, then install Zume:
- `python -m venv .venv`
- `.\.venv\Scripts\Activate.ps1`
- `pip install -e ".[dev]" -c constraints.txt`
- You only do this once per machine.

## Start Cursor in the correct repository

- Open the folder that contains `pyproject.toml` and this `docs/` folder.
- Confirm the terminal prompt shows the Zume repository path.

## Attach the candidate materials

- Attach the resume as PDF, DOCX, or TXT.
- Optionally attach a schedule screenshot or paste a few schedule lines such as
  Date, Time, Timezone, Duration, Interviewers, and Meeting.

## The one-line intake instruction

Send exactly:

> Process this candidate in Zume. Generate the pre-interview package and stop before feedback.

## What Cursor does automatically

- Extracts and screens the resume.
- Produces the screening summary.
- If the decision is Proceed or Conditional, builds the interviewer guide, the
  scorecard, and the candidate-shareable exercise sheet.
- Processes the schedule if you provided one.
- Validates every document and exports a clean deliverables-only ZIP.
- Sets the status to ready and STOPS. No feedback is generated yet.

## How to read the screening decision

- Proceed: resume evidence is strong; still verify depth live.
- Conditional: proceed with a stricter live technical screen.
- Do Not Proceed: only the screening summary is produced unless you request an
  override with a written reason.
- The percentage is resume evidence coverage, not a competency score.

## What files are created

- `01_Screening_Summary.docx`
- `02_Three_Hour_Interview_Guide.docx`
- `03_Interview_Scorecard.docx`
- `04_Candidate_Exercise_Sheet.docx`
- `05_Schedule_and_Communications.docx` (only if a schedule was provided)
- `06_Final_Interview_Evaluation.docx` (after the interview)
- `07_Post_Interview_Communications.docx` (after the interview)

## What to share and what not to share

- Share ONLY `04_Candidate_Exercise_Sheet.docx` with a candidate.
- Everything else is interviewer-only and contains answers, rubrics, or
  reference solutions.

## When the candidate is rejected or conditional

- Do Not Proceed: send the screening message; archive the candidate.
- Conditional: schedule the interview and run a strict live screen focused on the
  listed risks.

## On interview day

- Open the interviewer guide and the scorecard.
- Run the 20-minute knockout round first; follow the knockout decision rule.
- Keep each agenda segment within its minutes; the interview totals 180 minutes.

## The exact post-interview instruction

Paste or attach your notes, then send exactly:

> The interview is complete. Use these notes to finalize the candidate.

## Export, archive, and delete

- Export a clean package: `zume candidate export --candidate "<ref>"`.
- Archive: `zume candidate archive --candidate "<ref>"`.
- Delete (permanent): `zume candidate delete --candidate "<ref>" --confirm`.

## One-page quick reference

- Intake: attach resume, say "Process this candidate in Zume. Generate the
  pre-interview package and stop before feedback."
- Finalize: attach notes, say "The interview is complete. Use these notes to
  finalize the candidate."
- Share only the candidate exercise sheet.
- Standard interview length is 180 minutes.
- Candidate data is never committed to Git.
