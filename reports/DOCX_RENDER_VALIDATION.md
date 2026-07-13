# DOCX Render Validation

Date: 2026-07-13
Environment: Windows 10.0.26200, Python 3.13.5

## Summary

| Check | Result |
|-------|--------|
| Structural validation (python-docx) of all fictional-demo DOCX | **PASS** — 154 checks, 0 errors, 1 warning |
| LibreOffice availability | **NOT AVAILABLE** on this machine |
| Automated PDF render + rendered-content inspection | **SKIPPED** (LibreOffice unavailable) |

This report does **not** claim full visual validation. Structural validation
confirms the document XML (headings, header, footer, page-number field, expected
sections, tables, no unfilled placeholders), but that is not the same as
confirming the rendered page. The honest status of rendered-PDF validation is
**skipped**, with the exact reason below.

## Why render validation was skipped

LibreOffice (`soffice`) is not installed and could not be installed
automatically in this environment:

- `winget` is not available on this machine.
- `choco install libreoffice-fresh` failed with
  `System.UnauthorizedAccessException: Access to the path
  'C:\ProgramData\chocolatey\lib-bad' is denied` — Chocolatey requires an
  elevated (administrator) shell, which is not available to the agent.

No admin rights were available to install a system package, and downloading a
portable build was out of scope for an unattended run. Rather than fake a render
result, this step is recorded as skipped.

## What WAS validated (structural, via python-docx)

`zume validate --candidate Mehta_Aarav_2026-07-13` produced **154 passed, 0
errors, 1 warning** (the single warning is the LibreOffice-not-installed notice).

The 13 final fictional-demo documents each passed:

- heading hierarchy present;
- Zume header present;
- confidentiality footer present;
- page-number field present;
- all expected sections present (where a section contract exists);
- no unfilled `[Placeholder]` tokens.

Final documents validated:

1. ATS_Screening.docx
2. Candidate_Exercise_Sheet.docx (candidate copy — no reference solutions)
3. Candidate_Focus_Sheet.docx
4. Completed_Scorecard.docx
5. Exercise_Pack.docx (interviewer copy)
6. Final_Evaluation.docx
7. Full_Interview_Guide.docx
8. Interview_Schedule.docx
9. Leadership_Feedback.docx
10. Recruiter_Feedback_Post_Interview.docx
11. Recruiter_Feedback.docx
12. Scorecard.docx
13. Standardized_Resume.docx

## Render code readiness

`src/zume/validation.py::render_docx` is implemented to perform a real
rendered-content inspection as soon as LibreOffice is present. When `soffice`
is found it will:

- convert each final DOCX to PDF and confirm the conversion succeeds;
- confirm page count is nonzero and the document is not empty;
- warn on a blank trailing page;
- extract PDF text and confirm the Zume header and confidentiality footer text
  render;
- confirm expected section headings appear in the extracted PDF text.

To enable it, install LibreOffice (in an elevated shell:
`choco install libreoffice-fresh -y`) and re-run
`zume validate --candidate <folder>` (rendering is on by default; `--no-render`
disables it).

## Manual visual-inspection checklist (until render is enabled)

Open each final DOCX in Word/LibreOffice and confirm:

- [ ] The Zume header appears on every page (top-right).
- [ ] The confidentiality footer and page number appear on every page.
- [ ] Color-coded banners also carry a text label (accessibility: color + text).
- [ ] Tables are not clipped and repeat header rows across page breaks.
- [ ] No blank trailing page.
- [ ] Interviewer documents (Full_Interview_Guide, Exercise_Pack) contain the
      "CONFIDENTIAL — interviewer only" banner.
- [ ] Candidate_Exercise_Sheet.docx contains NO reference solutions or scoring.
- [ ] ATS_Screening.docx shows the "evidence coverage is not a competency score"
      disclaimer.

## Known limitation

Rendered-PDF validation is unverified in this environment. Treat the DOCX
outputs as structurally correct but visually unverified until LibreOffice is
installed and the render step is run, or the checklist above is completed
manually.
