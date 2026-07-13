# Zume Agent Instructions

1. Keep the product local-first and CLI-based. Do not introduce a web application, GUI, or cloud service unless explicitly requested. Preserve the product name **Zume** (never rename to Zoom).
2. Treat candidate information as confidential. Never commit real candidate files or PII. Verify git ignore rules before and after every git operation; run `zume scan-secrets`.
3. Use exact evidence from the resume or interviewer notes. Do not invent experience, evidence, duration, proficiency, or recency.
4. The screening percentage is **resume evidence coverage**, not a competency score. Keep that language in all user-facing output, and keep interview performance scores separate from resume evidence scores.
5. The experience gate has explicit states (`passed`/`failed`/`unknown`). Unknown/conflicting experience is a manual-review (conditional) state, not an automatic rejection. Sub-minimum experience is Do-Not-Proceed.
6. Never expose reference solutions in candidate-facing output. Interviewer material and candidate material are separate artifacts.
7. `interview-prep` must not silently prepare a Do-Not-Proceed candidate; require `--override` with a recorded `--override-reason`.
8. Generate DOCX outputs with readable spacing, color-plus-text banners, headers, footers, and page numbers.
9. Every workflow must end in validation. Do not declare success — or production-readiness — when any gate is failed or skipped.
10. Preserve the exact trigger phrases defined in `config/triggers.yaml`.
11. Keep modules small, typed, and testable. Keep scoring rules configurable in YAML.
12. Keep `pyproject.toml` as the dependency source of truth; regenerate `constraints.txt` after intentional bumps.
13. Do not push changes unless the user explicitly authorizes it. One focused commit only after all gates pass.
