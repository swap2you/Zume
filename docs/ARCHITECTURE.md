# Zume Architecture

Zume is a local-first, CLI-only Python toolkit. There is no web app, GUI, cloud
service, or authentication layer.

## Modules (`src/zume/`)

| Module | Responsibility |
|--------|----------------|
| `cli.py` | Typer entry point; wires workflows and sub-apps (`candidate`, `db`). |
| `config.py` | Loads YAML config (triggers, hiring standard, theme, exercises, privacy). |
| `models.py` | Pydantic models and enums (evidence, decision, experience state, schedule). |
| `ingest.py` | Text extraction (PDF/DOCX/TXT), name and experience analysis, image metadata. |
| `screening.py` | Evidence typing, resume evidence coverage, experience gate, decision. |
| `exercises.py` | Exercise parsing, fingerprinting, rotation-aware selection. |
| `interview.py` | Interview kit, focus sheet, guide, scorecard, interviewer/candidate packs. |
| `scheduling.py` | Schedule parsing, timezone/date/time validation, communication drafts. |
| `feedback.py` | Interview-notes evaluation, independence observations, feedback docs. |
| `documents.py` | Branded DOCX engine (headers, footers, page numbers, banners, tables). |
| `storage.py` | SQLite index: schema versioning, migrations, FK, indexes, backup, integrity. |
| `validation.py` | DOCX structural validation, candidate folder checks, privacy checks, render. |
| `security.py` | Secret/PII scanning over git-tracked text files. |
| `providers/` | Deterministic default provider (no mandatory AI dependency). |

## Data flow

```
resume ──ingest──▶ ResumeProfile ──screening──▶ ScreeningResult ──▶ DOCX + JSON
                                                     │
                                                     ▼ (decision gate)
                                        interview-prep ──exercises(rotation)──▶ kit
                                                     │
schedule details ──scheduling(validate)──▶ ScheduleRecord ──▶ DOCX + drafts
                                                     │
interviewer notes ──feedback──▶ FeedbackResult ──▶ DOCX + drafts
```

## Storage design

- Source files stay in candidate folders; SQLite (`data/zume.db`) is a
  searchable **index**, not a document store.
- `PRAGMA foreign_keys = ON`; schema version tracked via `PRAGMA user_version`
  with idempotent migrations.
- Indexes on candidate display name, status, created date, and source hash.
- Rotation state lives in `exercise_usage` and `candidate_exercises`.
- Deletion is transactional and cascades across all child tables.

## Candidate folder contract

`candidates/LastName_FirstName_YYYY-MM-DD/` with staged subfolders
(`00-source` … `06-communications`, `99-final`). Validated DOCX files are
promoted to `99-final/`. Writes are atomic and content-hash versioned.

## Configuration (`config/`)

`triggers.yaml`, `hiring-standard.yaml` (weights, minimum experience, evidence
scoring), `statuses.yaml`, `document-theme.yaml`, `exercise-library.yaml`
(interviewer-only), `privacy.yaml` (retention).
