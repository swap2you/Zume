# CI Visibility and Lockdown

## Investigation

Why lockdown commit `bdbfbc7` looked “pushed but not green”:

1. Actions are enabled; workflow name `CI` is active.
2. `.github/workflows/ci.yml` is recognized and ran on push to `main`.
3. The run failed (not missing): https://github.com/swap2you/Zume/actions/runs/29300715399
4. Failure mode was Linux-only: pathlib `exists()` on over-long note text raised
   `OSError` (ENAMETOOLONG). Windows local validation did not surface it.
5. Job names remain stable: `validate (${{ matrix.os }}, py${{ matrix.python-version }})`
   and `reproducible install (pinned constraints)` — suitable for branch protection.

## Fixes in Phase 0

1. `pipeline._read_arg` treats multi-line / long values as literal text and catches
   `OSError` when probing paths.
2. Schedule join subject contradiction fixed (unconfirmed ≠ “Confirmation”).
3. CI also runs on `release/zume-1.0` so the release branch has central visibility.
4. `workflow_dispatch` gains an optional `reason` input for diagnostics only
   (does not weaken gates).

## Policies preserved

- No candidate artifacts uploaded by Actions.
- No weakening of coverage or test gates to obtain green CI.
- Fictional demo data only in CI.

## V1.0 release branch CI status (2026-07-15)

| Item | Status | Notes |
|------|--------|-------|
| `release/zume-1.0` workflow trigger | **CONFIGURED** | Phase 0 adds branch to `.github/workflows/ci.yml` |
| Green run on release branch | **PENDING** | Branch push + draft PR not completed at builder report time |
| Draft PR to `main` | **PENDING** | Builder will push afterward |
| Inferring green from local tests | **NOT ALLOWED** | 190 passed locally, 80.34% coverage — see `reports/V1_IMPLEMENTATION_REPORT.md` |

Central CI evidence must come from GitHub Actions after push. Clean-room validator
must inspect workflow runs independently (`reports/V1_CLEAN_ROOM_VALIDATION.md`).
