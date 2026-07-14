# Zume Troubleshooting (LEGACY / v1 — historical only)

> Retired troubleshooting for the v1 four-command workflow. Kept for historical
> reference only. See `docs/ZUME_TROUBLESHOOTING_GUIDE.md` for the current guide.

## `zume: command not found`
Activate the venv (`.\.venv\Scripts\Activate.ps1`) or call the shim directly:
`.\.venv\Scripts\zume`.

## Interview prep is "Blocked" (retired)
The screening decision is Do-Not-Proceed. To proceed anyway, pass
`--override --override-reason "<reason>"`.

## LibreOffice render is skipped
LibreOffice (`soffice`) is not installed. Structural validation still runs.
Install it and re-run `zume validate`.

## Git shows candidate files as changes
They should be ignored. Run `git status --short`; if a candidate path appears,
stop and fix `.gitignore`. Never commit `candidates/`, `input/`, `output/`, or
`data/`.
