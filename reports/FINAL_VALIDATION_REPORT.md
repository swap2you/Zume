# Zume Final Validation Report

Date: 2026-07-13
Environment: Windows 11, Python 3.13.5, virtualenv at `.venv`
All commands were run from the repository root `C:\Development\Workspace\Zume`.

## Gate results

| # | Gate | Command | Result |
|---|------|---------|--------|
| 1 | Byte-compile | `.venv\Scripts\python -m compileall src` | PASS (exit 0) |
| 2 | Test suite | `.venv\Scripts\python -m pytest -q` | PASS — 36 passed, 0 failed |
| 3 | Lint | `.venv\Scripts\python -m ruff check .` | PASS — "All checks passed!" |
| 4 | Types | `.venv\Scripts\python -m mypy src` | PASS — "no issues found in 16 source files" |
| 5 | End-to-end demo | `.venv\Scripts\zume demo` | PASS — all 4 workflows completed |
| 6 | Folder validation | `.venv\Scripts\zume validate --candidate Mehta_Aarav_2026-07-13` | PASS — 144 passed, 1 warning, 0 errors (exit 0) |
| 7 | Git privacy review | `git status --short` + `git check-ignore -v` | PASS (details below) |
| 8 | DOCX structural re-open | part of gate 6: every generated DOCX opened with python-docx | PASS |
| 9 | LibreOffice render | `soffice` lookup | WARNING — LibreOffice is not installed on this machine, so PDF render verification was skipped. The validator records this explicitly instead of silently passing. |
| 10 | This report | `reports/FINAL_VALIDATION_REPORT.md` | Written |

## Demo run detail (gate 5)

`zume demo` processed the fictional candidate `examples/fictional-candidate/`
through all four workflows:

1. Filter Resume — Decision: Proceed (score 100%), folder
   `candidates/Mehta_Aarav_2026-07-13` created with the full folder contract.
2. Interview Prep — kit generated with 6 exercises (Appium included because the
   fictional resume mentions Appium/BrowserStack).
3. Schedule Interview — details confirmed from `schedule.txt`
   (2026-07-20, 10:00 AM ET, 90 minutes); status moved to INTERVIEW_SCHEDULED.
4. Interview Feedback — Decision: Proceed (score 85%), status SELECTED,
   leadership feedback generated.

## Folder validation detail (gate 6/8)

`zume validate` opened every generated DOCX with python-docx and verified for
each: heading hierarchy, Zume header, confidentiality footer, page-number
field, expected sections (per document type) and absence of unfilled
placeholders. It also verified the eight contract subfolders, `candidate.json`
JSON validity, and git ignore rules. Result: 144 passed, 0 errors.

The single warning is the LibreOffice render skip (gate 9). To enable render
verification, install LibreOffice; the validator picks up `soffice`
automatically from PATH or the default install location.

## Git privacy review (gate 7)

`git check-ignore -v` proves the sensitive paths are excluded:

```
.gitignore:14:candidates/**   candidates/Mehta_Aarav_2026-07-13/candidate.json
.gitignore:13:General Docs/   General Docs/Vikas Sharma.docx
.gitignore:20:data/*.db       data/zume.db
```

Also ignored: `input/**`, `output/**`, `*.pdf`, `*.png`, `*.jpg`, `.env`,
`.venv/`. The `General Docs/` folder containing real candidate material was
added to `.gitignore` before any git activity. `git status` shows only source
code, config, docs, prompts and tests as trackable content.

## Trigger mapping check

`zume run --trigger "Filter Resume - Automation Hiring"` executed the screening
workflow (hyphen and en-dash variants both accepted). An unknown trigger fails
with exit code 2 and lists the four known triggers.

## Known limitations

- LibreOffice is not installed, so DOCX-to-PDF render verification is skipped
  with an explicit warning (see gate 9).
- Schedule screenshots are used for reliable metadata only (file name, size,
  EXIF capture time). Actual date/time must be supplied or confirmed via
  `--details`; OCR is deliberately not performed silently.
- No model API is configured; the deterministic template provider is used for
  all generation (this is the designed fallback and requires no key).

## Exact user steps

See README.md "Usage" for the four trigger commands, input locations
(`input/`, or any path) and output locations (`candidates/<Folder>/…`,
final validated copies in `99-final/`).
