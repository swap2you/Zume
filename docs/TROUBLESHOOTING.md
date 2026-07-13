# Zume Troubleshooting

## `zume: command not found`
Activate the venv (`.\.venv\Scripts\Activate.ps1`) or call the shim directly:
`.\.venv\Scripts\zume`.

## Interview prep is "Blocked"
The screening decision is Do-Not-Proceed. This is intentional. To proceed
anyway, pass `--override --override-reason "<reason>"`. The reason is recorded
in the candidate JSON, status history, SQLite, and focus sheet.

## Experience shows as "unknown"
The resume had no clear total-experience statement, or the claims conflicted.
This routes to a conditional manual review — it is not an automatic rejection.
Confirm the candidate's total experience manually.

## Score looks "low" compared to before
The percentage is now **resume evidence coverage**. A bare skills-list mention
earns low credit by design; project and quantified evidence earn more. A lower
number reflects weaker resume evidence, not a competency verdict.

## LibreOffice render is skipped
LibreOffice (`soffice`) is not installed. Structural validation still runs.
Install it in an elevated shell (`choco install libreoffice-fresh -y`) and
re-run `zume validate --candidate <folder>` to enable rendered-PDF checks.
See `reports/DOCX_RENDER_VALIDATION.md`.

## `UnicodeEncodeError` in the console
Use a UTF-8 capable terminal (Windows Terminal) or set
`$env:PYTHONUTF8 = "1"` before running. Generated DOCX/MD files are always
UTF-8.

## `zume db check` reports failures
Run `zume db backup` first, then investigate. Integrity or foreign-key failures
usually mean the database file was edited or truncated externally; restore from
a validated backup.

## Duplicate candidate warning
`zume db check` lists candidates sharing a source hash or display name. This is
informational — resolve by archiving or deleting the duplicate.

## Git shows candidate files as changes
They should be ignored. Run `git status --short`; if a candidate path appears,
stop and fix `.gitignore`. Never commit `candidates/`, `input/`, `output/`, or
`data/`.

## Coverage gate fails
The threshold is 80% (`fail_under` in `pyproject.toml`). Add tests for the code
you changed rather than lowering the threshold.
