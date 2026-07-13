# Zume Implementation Plan

Date: 2026-07-13

## Repository state at start

Starter package only: `.cursor/prompts`, `config/*.yaml`, `docs/*.docx` (blueprint,
operating guide, hiring standard, exercise library, communication templates, fictional
sample), `templates/*.docx`, `examples/fictional-candidate/*`, placeholder
`src/zume/cli.py`, one starter test. Git repo initialized locally; remote
`https://github.com/swap2you/Zume.git` is empty. No push will be performed.

## Architecture

Local-first Python 3.11+ CLI (Typer). No web app, no server, no background service.

```
src/zume/
  cli.py               Typer app: filter-resume, interview-prep, schedule-interview,
                       interview-feedback, validate, demo, run --trigger
  models.py            Pydantic models: Candidate, SourceFile, EvidenceItem,
                       ScreeningResult, ScheduleRecord, InterviewKit, FeedbackResult,
                       CommunicationDraft
  config.py            YAML config loading (hiring standard, theme, triggers,
                       statuses, exercise library)
  ingest.py            PDF (pypdf), DOCX (python-docx), TXT, pasted text; image
                       metadata via Pillow; optional OCR stays opt-in and unused
                       by default
  candidate.py         Name normalization, LastName_FirstName_YYYY-MM-DD folder
                       contract, candidate.json audit record, atomic writes,
                       content-hash based versioning
  screening.py         Evidence matrix (explicit / inferred / missing), weighted
                       scoring, gates, automatic-reject signals, decision rules
  interview.py         Candidate-specific focus sheet, 3-hour guide, scorecard,
                       exercise selection from config/exercise-library.yaml
  scheduling.py        Screenshot metadata + user-confirmed details, schedule DOCX,
                       join/reschedule/cancel/no-show drafts
  feedback.py          Notes -> calibrated evaluation, completed scorecard, neutral
                       independence observations, status update
  documents.py         Branded DOCX engine: header, confidentiality footer, page
                       numbers, heading hierarchy, color banners (label + color),
                       alternating table rows, repeated headers
  storage.py           SQLite (data/zume.db): candidates, source_files, screenings,
                       interviews, scores, communications, status_history, artifacts
  validation.py        Structural DOCX checks, folder contract checks, privacy
                       checks, optional LibreOffice render with explicit warning
  providers/base.py    Provider protocol
  providers/template.py Deterministic template provider (default, no API needed)
```

## Key contracts

- Candidate folder `candidates/LastName_FirstName_YYYY-MM-DD/` with subfolders
  `00-source`..`06-communications`, `99-final`, plus `candidate.json`.
- All writes staged to a temp file in the destination directory then `os.replace`d.
- Source files are copied into `00-source`, never modified.
- Regenerated outputs: identical content is skipped; changed content archives the
  previous file as `<stem>__v<N><ext>` before replacing.
- Evidence is always labeled explicit / inferred / missing; nothing is invented.
- Independence concerns recorded as neutral observations plus a confidence level.

## Scoring (from config/hiring-standard.yaml + docs/04)

- Gate: 8+ years overall experience.
- Weights: Java 15, Selenium 20, TestNG/Cucumber 10, REST Assured 15, SQL/Oracle 10,
  Framework 10, CI/CD 10, Ownership 10.
- Decisions: Proceed / Conditional Technical Screen / Do Not Proceed.
- Interview: 85–100 Strong, 75–84 Proceed, 68–74 Borderline, <68 Do Not Proceed,
  with a mandatory-skill override.

## Build order

1. config + models + candidate folder contract + atomic writes (tests)
2. documents engine + structural validation (tests)
3. ingest + screening (tests)
4. interview prep (tests)
5. scheduling (tests)
6. feedback (tests)
7. storage + CLI + trigger mapping + demo (tests)
8. Validation gates: compileall, pytest, ruff, mypy, `zume demo`,
   `zume validate`, git privacy review, DOCX structural re-open, LibreOffice
   render if present, FINAL_VALIDATION_REPORT.md

## Privacy

`.gitignore` excludes `candidates/**`, `input/**`, `output/**`, `data/*.db`,
images, PDFs, and the real-candidate `General Docs/` folder. Only fictional
sample data is committed.
