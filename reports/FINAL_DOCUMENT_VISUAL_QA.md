# Final Document Visual QA (Phase 13)

- **Date:** 2026-07-13
- **OS / Python:** Windows 11 (10.0.26200) · Python 3.13.5 · `.venv-final`
- **Render backend used:** Microsoft Word via COM (`win32com`, `pywin32==312`)
- **Fallback order:** LibreOffice (`soffice`) → Microsoft Word (COM) → structural-only
  with an explicit warning. Render was **not** skipped in this environment.
- **Sample:** fictional demo candidate `Mehta_Aarav_2026-07-13`
  (git-ignored; no real PII).

## Method

Each deliverable is rendered to PDF by the real word processor, then the PDF is
inspected with `pypdf` for: non-zero pages, extractable text, header/footer
presence, expected headings, unresolved `[Placeholder]` tokens, blank last page,
and sparse trailing pages (`detect_sparse_trailing_page`). Structural DOCX checks
(heading hierarchy, header/footer, page numbers, section completeness, no `__vN`,
≤ 7 deliverables) run first and independently of the render backend.

## Results — rendered PDF per deliverable

| # | Deliverable | Pages | Header | Footer | Headings | Placeholders |
|---|-------------|:-----:|:------:|:------:|:--------:|:------------:|
| 01 | `01_Screening_Summary.docx` | 3 | ✓ | ✓ | ✓ | none |
| 02 | `02_Three_Hour_Interview_Guide.docx` | 27 | ✓ | ✓ | ✓ | none |
| 03 | `03_Interview_Scorecard.docx` | 2 | ✓ | ✓ | n/a | none |
| 04 | `04_Candidate_Exercise_Sheet.docx` | 1 | ✓ | ✓ | ✓ | none |
| 05 | `05_Schedule_and_Communications.docx` | 2 | ✓ | ✓ | ✓ | none |
| 06 | `06_Final_Interview_Evaluation.docx` | 2 | ✓ | ✓ | n/a | none |
| 07 | `07_Post_Interview_Communications.docx` | 1 | ✓ | ✓ | ✓ | none |

**`zume validate --candidate Mehta_Aarav_2026-07-13`: 85 passed, 0 warnings, 0 errors.**

## Layout issues found and fixed

1. **False-positive placeholder warnings.** The interviewer guide rendered
   difficulty levels as bracketed tags (`[Basic]`, `[Intermediate]`, `[Advanced]`),
   which the `[Placeholder]` detector correctly flagged as suspicious. Fixed by
   rendering levels as plain labels (`Basic — <question>`,
   `<area> / <level> — <question>`) so genuine unfilled placeholders remain
   detectable. Re-render: 0 placeholder warnings.
2. **Stale `99-final` folder in reused demo folder.** An earlier (pre-simplification)
   demo run had left a legacy `99-final/` directory in the date-named demo folder,
   which the v2 invariant check flagged. Resolved by regenerating the package
   cleanly; the current pipeline never creates `99-final/` or `__vN` files.
3. **Table row splitting / orphan lines.** `documents.py` now marks table rows as
   "cannot split across pages" (`_prevent_row_split`) and uses explicit
   `page_break()` before large appendices (reserve questions), preventing rows and
   headings from being orphaned at page boundaries.

## Sparse / blank page checks

- No deliverable produced a blank final page.
- `detect_sparse_trailing_page` reported no sparse trailing pages across all seven
  documents. The 27-page interviewer guide is content-dense (full agenda, 20-minute
  knockout with recommended answers, basic/intermediate/advanced questions per area
  with reference solutions, exercises, and a reserve-question appendix).

## Reproduction

```
zume demo
zume validate --candidate Mehta_Aarav_2026-07-13
```

On a machine without Word or LibreOffice, `zume validate` runs all structural
checks and emits an explicit warning that render verification was skipped; it never
silently passes as if the documents were rendered.
