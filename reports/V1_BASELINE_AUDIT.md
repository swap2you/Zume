# Zume 1.0 — Baseline Audit

Date: 2026-07-15
Builder start commit: `bdbfbc71b2a129e53fec2dd9ba741e759028d875`
Release branch: `release/zume-1.0` (created from that SHA)

## Toolchain

| Tool | Status |
|------|--------|
| Python | 3.13.5 (requires-python >=3.11) |
| Node | v20.11.1 |
| npm | 10.2.4 |
| Docker | 29.5.3 |
| GitHub CLI (`gh`) | 2.95.0 |
| Microsoft Office / Word | Present under Program Files |
| LibreOffice (`soffice`) | Not required for baseline; Word COM available for render QA |

## Privacy / working tree at start

- Working tree clean on baseline SHA before Phase 0 edits.
- Candidate/private/output paths remain Git-ignored.
- No values from `C:\AarohanSecrets` were inspected, printed, or copied.

## Existing library (pre-expansion)

| Library | Count |
|---------|------:|
| Interview questions (`config/interview-question-library.yaml`) | 99 across 12 areas |
| Exercises (`config/exercise-library.yaml`) | 22 across 7 areas |

Per-area question counts: java 9, selenium 9, testng 9, cucumber 9, rest_assured 9,
sql_oracle 9, framework_design 9, cicd 9, debugging 9, appium 6, browserstack 6,
performance 6.

## GitHub Actions (central CI)

- Workflow `CI` is **active** (id `312630898`).
- Triggers: `push`/`pull_request` to `main`, plus `workflow_dispatch`.
- Latest run on lockdown commit `bdbfbc7`: **failure**
  - Run: https://github.com/swap2you/Zume/actions/runs/29300715399
  - Root cause: `pipeline._read_arg` treated long note strings as paths; Linux
    raised `OSError: [Errno 36] File name too long` instead of treating them as
    literal text. Downstream coverage fell to 79.85%.
- Prior successful runs exist on earlier main commits (simplify / harden).

Phase 0 corrective action for this baseline defect is recorded in
`reports/CI_VISIBILITY_AND_LOCKDOWN.md` and implemented as a guarded `_read_arg`
plus schedule-subject correction.

## Invariants confirmed at baseline

- Canonical commands: `zume intake`, `zume finalize`
- Candidate contract: `source/`, `_internal/`, `deliverables/`
- Maximum seven deliverables; no `99-final` / user-visible `__vN` creation paths
- 180-minute agenda / 20-minute knockout

## Phase 0-only existing-behavior correction

Unconfirmed join email subject must be
`Proposed Interview Schedule – <candidate>` (body already used “Proposing”).
Confirmed schedules keep `Interview Confirmation – <candidate>`.

## V1.0 builder evidence index (2026-07-15)

Phase 0 committed at `20ec43b9b8794dc1aee539318c771186ec881e99`. Full builder
reports (phases 1–12 evidence in working tree; not clean-room proof):

| Report | Path |
|--------|------|
| Implementation | `reports/V1_IMPLEMENTATION_REPORT.md` |
| Library coverage | `reports/V1_LIBRARY_COVERAGE_REPORT.md` |
| UI visual QA | `reports/V1_UI_VISUAL_QA.md` |
| Security & privacy | `reports/V1_SECURITY_AND_PRIVACY_REPORT.md` |
| Lab sandbox | `reports/V1_LAB_SANDBOX_REPORT.md` |
| Clean-room (NOT RUN) | `reports/V1_CLEAN_ROOM_VALIDATION.md` |
| Release readiness | `reports/V1_RELEASE_READINESS.md` |

Acceptance contract: `docs/release/v1.0/02_ACCEPTANCE_MATRIX.md`
