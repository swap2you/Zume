# Zume — Master Build Prompt for Cursor

You are the principal engineer responsible for completing Zume end to end inside this repository. Work autonomously, but remain inside the repository and do not push to GitHub.

## Product boundary
Build a lightweight local-first Python CLI and document-generation workspace. Do not build a web application, desktop GUI, background service, authentication system, or unnecessary infrastructure.

## User goal
The user provides one or more of: a resume PDF/DOCX/TXT, pasted resume text, an interview schedule screenshot, or interview notes. Zume creates a candidate folder, evaluates the resume against the configured Senior SDET standard, generates polished Word documents, stores searchable metadata in SQLite, and produces copy-ready communication drafts.

## Exact triggers
1. `Filter Resume – Automation Hiring`
2. `Interview Prep – Automation Hiring`
3. `Schedule Interview – Automation Hiring`
4. `Interview Feedback – Automation Hiring`

## Required behavior
- Accept file paths and pasted text.
- Use a deterministic candidate folder contract.
- Create a candidate.json audit record.
- Generate all user-facing reports as DOCX.
- Generate optional Markdown communication drafts for easy copying.
- Keep real candidate data ignored by Git.
- Never invent experience; distinguish explicit evidence, inferred evidence and missing evidence.
- Record possible external-assistance concerns as neutral observations, never as a cheating accusation.
- Support a templated/manual fallback when no model API is configured.

## Required modules
- `src/zume/cli.py`
- `src/zume/models.py`
- `src/zume/ingest.py`
- `src/zume/candidate.py`
- `src/zume/screening.py`
- `src/zume/interview.py`
- `src/zume/scheduling.py`
- `src/zume/feedback.py`
- `src/zume/documents.py`
- `src/zume/storage.py`
- `src/zume/validation.py`
- `src/zume/providers/base.py` and a deterministic template provider

## CLI commands
Implement:
- `zume filter-resume --input <path> [--text-file <path>]`
- `zume interview-prep --candidate <name-or-folder>`
- `zume schedule-interview --candidate <name-or-folder> --image <path>`
- `zume interview-feedback --candidate <name-or-folder> --notes <path-or-text>`
- `zume validate --candidate <name-or-folder>`
- `zume demo`

Also implement `zume run --trigger "..."` to map the exact natural-language trigger to the appropriate workflow.

## Candidate folder
Use `LastName_FirstName_YYYY-MM-DD` and create:
- `00-source`
- `01-screening`
- `02-schedule`
- `03-interview-prep`
- `04-interview`
- `05-feedback`
- `06-communications`
- `99-final`
- `candidate.json`

All writes must be staged to a temporary file and atomically replaced. Never overwrite a source file. Version regenerated outputs when content changes.

## DOCX requirements
Use `python-docx`. All final documents need:
- Zume header and confidentiality footer
- Page numbers
- Strong heading hierarchy
- Color-coded banners using both text labels and color
- Readable short paragraphs and spacing
- Alternating table rows and repeated headers where possible
- Decision, risks and actions visually separated
- No clipped tables or orphan headings

Implement structural validation for headings, header/footer, expected sections and empty placeholders. If LibreOffice is installed, render final DOCX files to PDF/PNG and verify output exists. If it is unavailable, write an explicit validation warning.

## Screening workflow
Generate:
- Standardized resume DOCX
- ATS screening DOCX
- Recruiter feedback DOCX and Markdown
- Decision: Proceed / Conditional Technical Screen / Do Not Proceed
- Evidence matrix for mandatory and good-to-have skills
- Risks, inconsistencies and candidate-specific validation questions

## Interview workflow
Generate:
- Candidate focus sheet
- Full 3-hour interview guide
- Scorecard
- Selected exercise pack
- Exact questions, expected answers, reference solutions, red flags and follow-up modifications
- Candidate-specific resume validation

Prioritize Java, Selenium, TestNG/Cucumber, REST Assured, Oracle SQL, framework ownership, CI/CD and independent debugging. Include Appium, BrowserStack and performance testing when the resume supports them.

## Scheduling workflow
Extract schedule details from screenshot only when reliable. Prefer image metadata and built-in vision/provider capability. OCR must be optional, single-pass and never silently trusted. Allow the user to confirm/edit extracted details. Generate schedule DOCX and copy-ready join, reschedule, cancel and no-show drafts.

## Feedback workflow
Accept conversational notes. Generate:
- Final evaluation DOCX
- Completed scorecard
- Recruiter feedback DOCX/Markdown
- Leadership feedback DOCX/Markdown when requested
- Status update

Use neutral evidence language. For independence concerns, record observations such as pauses, audible device activity, solution-quality shifts, inability to explain, inability to modify and resulting confidence.

## Database
Use SQLite for metadata and status history only. Required tables: candidates, source_files, screenings, interviews, scores, communications, status_history and artifacts. Store relative paths, hashes and timestamps.

## Tests
Create unit and integration tests for:
- Trigger mapping
- Candidate naming and folder creation
- Resume text extraction
- Scoring gates
- Decision rules
- DOCX generation and structural checks
- Atomic writes and versioning
- Privacy ignore checks
- Fictional end-to-end demo

## Validation gates
Do not declare completion until all are executed:
1. `python -m compileall src`
2. `pytest -q`
3. `ruff check .`
4. `mypy src` when practical
5. `zume demo`
6. `zume validate --candidate <demo folder>`
7. Git status review proving real candidate paths are ignored
8. Open every generated DOCX with python-docx and verify required structures
9. Render DOCX through LibreOffice if available
10. Create `reports/FINAL_VALIDATION_REPORT.md` with exact commands and results

## Work sequence
1. Inspect repository and docs.
2. Write `reports/IMPLEMENTATION_PLAN.md`.
3. Implement models/config/folder contract.
4. Implement document engine and tests.
5. Implement screening.
6. Implement interview prep.
7. Implement scheduling.
8. Implement feedback.
9. Implement SQLite/index/search.
10. Run demo and validation.
11. Fix every failure.
12. Produce final report.

## Final response
Report what was built, exact commands to use, where inputs go, where outputs appear, validation results, git/privacy status, and remaining optional enhancements. Do not say “complete” if any required gate was skipped.
