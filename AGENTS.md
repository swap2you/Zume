# Zume Agent Instructions

1. Keep the product local-first and CLI-based, driven primarily from Cursor. Do not introduce a web application, GUI, or cloud service unless explicitly requested. Preserve the product name **Zume** (never rename to Zoom).
2. The canonical commands are `zume intake` (build the pre-interview package, then stop) and `zume finalize` (run only after real interviewer notes). The retired v1 commands and the natural-language `run` trigger are deprecated, hidden, and must never create a new candidate record or a legacy numbered/final-copy folder. Only migration/cleanup functions may touch existing legacy folders.
3. Candidate folders contain exactly `source/`, `_internal/`, and `deliverables/`. Never create a legacy final-copy folder or user-visible `__vN` files. There are at most seven canonical deliverables. The standard interview is 180 minutes with a 20-minute knockout round.
4. Treat candidate information as confidential. Never commit real candidate files or PII. Verify git ignore rules before and after every git operation; run `zume scan-secrets` (which scans tracked text and DOCX files).
5. Use exact evidence from the resume or interviewer notes. Do not invent experience, evidence, duration, proficiency, or recency.
6. The screening percentage is **resume evidence coverage**, not a competency score. Keep that language in all user-facing output, and keep interview performance scores separate from resume evidence scores.
7. The experience gate has explicit states (`passed`/`failed`/`unknown`). Unknown/conflicting experience is a manual-review (conditional) state, not an automatic rejection. Sub-minimum experience is Do-Not-Proceed.
8. Never expose reference solutions or recommended answers in candidate-facing output. Interviewer material and the candidate exercise sheet are separate artifacts.
9. `intake` must not silently build a full package for a Do-Not-Proceed candidate (require `--override` + `--override-reason`), must not reset a finalized candidate (require `--reopen` + `--reopen-reason`, preserving final documents), and must never generate interview feedback.
10. `finalize` must not produce a final "Selected" from incomplete interview notes; it lists missing mandatory areas and routes to manual review. Export records an event without changing the workflow status.
11. Generate DOCX outputs with readable spacing, color-plus-text banners, headers, footers, and page numbers.
12. Every workflow must end in validation. Do not declare success — or production-readiness — when any gate is failed or skipped.
13. Keep modules small, typed, and testable. Keep scoring rules and the question/exercise libraries configurable in YAML; every active exercise must carry recommended answers for its follow-ups and independence questions.
14. Keep `pyproject.toml` as the dependency source of truth; regenerate `constraints.txt` after intentional bumps. Do not add new dependencies for the lockdown pass.
15. Do not push changes unless the user explicitly authorizes it. One focused commit only after all gates pass.
