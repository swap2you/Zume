# Zume 1.0 — Clean-Room Validation (Independent Validator)

Date: 2026-07-15  
Status: **NOT RUN** — awaiting independent validator  
Prepared by: Builder (stub only; **do not treat as PASS**)

> The builder **did not** perform clean-room validation and **must not** claim
> clean-room PASS. This file records required inputs and procedure for the
> independent agent. The validator will replace or supersede this stub with
> per-row PASS / FAIL / NOT VERIFIED verdicts.

## Release verdict (builder)

**NOT RUN — INDEPENDENT VALIDATION REQUIRED**

No release verdict is issued. Production release is **not** complete.

## Exact inputs for the independent validator

| Input | Value |
|-------|-------|
| Repository path | `C:\Development\Workspace\Zume` |
| Release branch | `release/zume-1.0` |
| Phase 0 commit (builder HEAD at report time) | `20ec43b9b8794dc1aee539318c771186ec881e99` |
| Baseline commit | `bdbfbc71b2a129e53fec2dd9ba741e759028d875` |
| Acceptance contract | `docs/release/v1.0/02_ACCEPTANCE_MATRIX.md` |
| Validator procedure | `docs/release/v1.0/05_CLEAN_ROOM_VALIDATOR_PROMPT.md` |
| Release runbook | `docs/release/v1.0/06_RELEASE_RUNBOOK.md` |
| Windows release zip | `releases/Zume-v1.0.0-Windows.zip` |
| Zip SHA-256 | `07b8f7eaae762771e6be8b851bbdd5e996a5378cddc34c275ea84bd2d73b789e` |

### Builder reports (claims to retest — not evidence)

The validator must **not** use these as proof. They identify what to reproduce:

- `reports/V1_IMPLEMENTATION_REPORT.md`
- `reports/V1_LIBRARY_COVERAGE_REPORT.md`
- `reports/V1_UI_VISUAL_QA.md`
- `reports/V1_SECURITY_AND_PRIVACY_REPORT.md`
- `reports/V1_LAB_SANDBOX_REPORT.md`
- `reports/V1_RELEASE_READINESS.md`
- `reports/V1_BASELINE_AUDIT.md`
- `reports/CI_VISIBILITY_AND_LOCKDOWN.md`

### Screenshots (builder-captured — validator must recapture)

```text
reports/screenshots/home.png
reports/screenshots/home-tablet.png
reports/screenshots/library.png
reports/screenshots/practice.png
reports/screenshots/interview-builder.png
reports/screenshots/intake.png
reports/screenshots/finalize.png
reports/screenshots/lab.png
reports/screenshots/ask.png
reports/screenshots/settings.png
```

## Independence setup (required)

1. New Git worktree or clean clone at a **separate path** (not builder cwd).
2. Verify target SHA on `release/zume-1.0` (post-push; may differ from `20ec43b`
   after phase commits land).
3. Fresh Python venv and `npm ci` — no reuse of builder `node_modules`, venv,
   `data/zume.db`, `data/knowledge-fts.sqlite`, candidates, or screenshots.
4. Do **not** read the builder chat.
5. Do **not** load live secrets for main validation; mocks/offline first.
6. Live OpenAI smoke only after offline gates, only if doctor reports configured
   **without printing any key**.

## Validation procedure checklist

The validator must execute all sections in
`docs/release/v1.0/05_CLEAN_ROOM_VALIDATOR_PROMPT.md`:

1. Diff and architecture review (baseline → target)
2. Full clean build (Python + frontend gates)
3. Hiring regressions (synthetic profiles: strong, weak, unknown, mobile,
   performance, AI QA, architect, manager)
4. Library audit (counts, sampling, source correctness, near-duplicates)
5. UI and accessibility (Playwright, desktop + tablet, keyboard/focus/contrast)
6. Ask Zume (offline, mocked provider, optional live smoke)
7. Audio (browser TTS, controls, cache, no client secret)
8. Labs (SQL, API allowlist, Java Docker, Selenium optional, escape tests)
9. Security and privacy (scans, zip, traversal, localhost, no AarohanSecrets leak)
10. Central CI (PR + workflow runs — do not infer green from local tests)

## Acceptance matrix

For **every row** in `docs/release/v1.0/02_ACCEPTANCE_MATRIX.md` (sections A–J),
the validator must record:

- Verdict: **PASS** / **FAIL** / **NOT VERIFIED**
- Evidence (command, test, screenshot, file path)
- Severity (if FAIL)
- Required correction (if FAIL)

## Expected final verdict (validator chooses one)

Exactly one of:

- `READY FOR HUMAN UI REVIEW`
- `NOT READY — CORRECTIONS REQUIRED`
- `NOT VERIFIED — ENVIRONMENT/PERMISSION BLOCKER`

The builder issues **no** verdict above.

## Post-validator sequence

1. Human/Cowork screen review per `docs/release/v1.0/06_RELEASE_RUNBOOK.md`
2. Central CI green on draft PR
3. Merge + tag `v1.0.0` only after clean-room + human review + CI

## Related

- `docs/release/v1.0/00_READ_ME_FIRST.md`
- `reports/V1_RELEASE_READINESS.md`

## Exact inputs for independent clean-room validator

- Repository path: `C:\Development\Workspace\Zume`
- Branch: `release/zume-1.0`
- SHA: `bb61ceb65efe49fd3917366477303aea48d330d5`
- Contracts: `docs/release/v1.0/02_ACCEPTANCE_MATRIX.md` and `docs/release/v1.0/05_CLEAN_ROOM_VALIDATOR_PROMPT.md`
- Do not reuse builder chat history or trust builder reports as evidence
