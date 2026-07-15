# Zume 1.0 — Release Readiness (Builder)

Date: 2026-07-15  
Branch: `release/zume-1.0`  
Builder HEAD: `20ec43b9b8794dc1aee539318c771186ec881e99` (+ uncommitted phases 1–12)

## Builder release verdict

**BUILDER WORK COMPLETE — NOT READY FOR PRODUCTION RELEASE**

Local implementation and packaging evidence are in place. **Production release is
not complete.** Clean-room validation has **NOT RUN**. Human UI review must wait
until an independent validator issues `READY FOR HUMAN UI REVIEW`.

## Readiness checklist

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Descended from baseline `bdbfbc71` | **PASS** | Git ancestry |
| Hiring v2 invariants preserved | **PASS** (local) | `reports/V1_IMPLEMENTATION_REPORT.md` §A |
| Knowledge library seeded (1899 Q / 285 E) | **PASS** (local) | `reports/V1_LIBRARY_COVERAGE_REPORT.md` |
| 0 taxonomy gaps after seed | **PASS** (local) | `zume knowledge gaps` |
| Python gates (compileall, ruff, mypy, pytest) | **PASS** (local) | 190 passed, 80.34% coverage |
| Frontend production build | **PASS** (local) | `apps/web/dist/` |
| UI screenshots for human review | **PASS** (captured) | `reports/V1_UI_VISUAL_QA.md` |
| Security scans (tracked files) | **PASS** (local) | `reports/V1_SECURITY_AND_PRIVACY_REPORT.md` |
| Labs SQL/API | **PASS** (local) | `reports/V1_LAB_SANDBOX_REPORT.md` |
| Labs Java/Selenium Docker | **NOT VERIFIED** | Optional; flag + Docker required |
| Windows release zip | **PASS** (local) | `releases/Zume-v1.0.0-Windows.zip` (1,444,090 bytes) |
| Zip checksum recorded | **PASS** | `07b8f7eaae762771e6be8b851bbdd5e996a5378cddc34c275ea84bd2d73b789e` |
| Live OpenAI | **NOT REQUIRED** | Doctor: not configured; offline/mocks |
| Clean-room validation | **NOT RUN** | `reports/V1_CLEAN_ROOM_VALIDATION.md` |
| Central GitHub Actions green | **PENDING** | Branch push + workflow run pending |
| Draft PR to `main` | **PENDING** | Builder will open after push |
| Human UI screen review | **BLOCKED** | Until clean-room `READY FOR HUMAN UI REVIEW` |
| Merge to `main` | **NOT DONE** | Per runbook |
| Tag `v1.0.0` | **NOT DONE** | Per runbook |

## What is ready now

- Builder reports under `reports/V1_*.md`
- Local validation evidence (Python 190/190, coverage 80.34%)
- Release artifact staged locally with checksum
- Screenshot set for eventual human review

## What is explicitly not ready

1. **Clean-room independent validation** — mandatory before human UI review.
2. **Central CI visibility** — push and green matrix runs are **PENDING**.
3. **Draft PR** — **PENDING** (builder will push afterward).
4. **Production release** — do not merge, tag, or announce v1.0.0 yet.

## Human UI review (after clean-room only)

When the validator verdict is `READY FOR HUMAN UI REVIEW`, human reviewers should
inspect per `docs/release/v1.0/06_RELEASE_RUNBOOK.md`:

- Home, Library, Practice, Interview Builder
- Candidate Intake / Finalize
- Exercise Lab, Ask Zume, Settings/Doctor
- Audio controls
- Desktop + tablet screenshots in `reports/screenshots/`
- Representative candidate DOCX (fictional only)

Record defects only; do not treat builder screenshots as substitute for live review.

## Known limitations to carry into release notes

| Limitation | Impact |
|------------|--------|
| Templated library breadth vs hand-authored depth | Editorial quality needs ongoing curation |
| Optional live OpenAI | Offline-first; live search/TTS/realtime optional |
| Docker labs optional | Java/Selenium need `ZUME_ENABLE_DOCKER_LABS` + Docker |
| Selenium compose optional | `docker/labs/selenium-compose.yml` not bundled in zip |
| SQL lab uses SQLite | Oracle dialect exercises labeled accordingly |
| Playwright e2e | Not verified in builder pass |
| Public repo methodology exposure | See `reports/PUBLIC_REPOSITORY_RISK_ASSESSMENT.md` |

## Next actions (builder / owner)

1. Commit phase work on `release/zume-1.0` (if not already).
2. Push branch and open/update **draft PR** to `main`.
3. Watch central CI until green (or fix failures without weakening gates).
4. Start **new Cursor chat** with `05_CLEAN_ROOM_VALIDATOR_PROMPT.md` only.
5. After clean-room `READY FOR HUMAN UI REVIEW` → human screen review.
6. After human acceptance + CI green → merge and tag `v1.0.0`.

## Report index

| Report | Path |
|--------|------|
| Implementation | `reports/V1_IMPLEMENTATION_REPORT.md` |
| Library coverage | `reports/V1_LIBRARY_COVERAGE_REPORT.md` |
| UI visual QA | `reports/V1_UI_VISUAL_QA.md` |
| Security & privacy | `reports/V1_SECURITY_AND_PRIVACY_REPORT.md` |
| Lab sandbox | `reports/V1_LAB_SANDBOX_REPORT.md` |
| Clean-room (NOT RUN) | `reports/V1_CLEAN_ROOM_VALIDATION.md` |
| Baseline audit | `reports/V1_BASELINE_AUDIT.md` |
| CI visibility | `reports/CI_VISIBILITY_AND_LOCKDOWN.md` |

## Acceptance contract

`docs/release/v1.0/02_ACCEPTANCE_MATRIX.md` — full PASS required from independent
validator, not from builder reports.
