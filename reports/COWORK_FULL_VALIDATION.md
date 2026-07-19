# Zume Full Browser Validation — Clean Review Revalidation

- Validator: Cursor revalidation against clean `zume review serve --reset`
- Date: 2026-07-19
- Target: `http://127.0.0.1:8787/`
- Startup: `zume review serve --port 8787 --no-open --reset`
- Prior stale-environment report preserved as: `reports/COWORK_FULL_VALIDATION_STALE_ENV.md`

## Environment gate

| Check | Result | Evidence |
|-------|--------|----------|
| `GET /api/health` → `review_mode=true` | PASS | `{"status":"ok","review_mode":true}` |
| Header `X-Zume-Review-Mode: 1` | PASS | Present on review responses |
| `GET /api/candidates` empty | PASS | `items: []` after `--reset` |
| `GET /api/knowledge/facets?mode=reviewed` | PASS | 66 questions, 4 exercises, 23 domains |
| `GET /api/knowledge/gaps` | PASS | 200; open gaps remain honest |
| Selenium natural-language search | PASS | ≥1 Selenium hit |
| `GET /api/build-info` | PASS | SHA + digests + 66Q/4E |

**No ENVIRONMENT MISMATCH.**

## Root-cause note (why the prior Cowork report was wrong)

Review API routes previously called `find_root()` (real repository) instead of the
bound review workspace. That leaked real `candidates/` into `/api/candidates`
even when `review_mode=true`. Fixed by request-scoped `app.state.root` binding
(`src/zume/server/runtime.py`).

## Automated browser proof

Playwright `apps/web/e2e/workflows.spec.ts` against the clean review server:

- 12/12 workflow tests passed after warm + `--workers=1`
- Facet-driven Domain dropdown waits for `data-facets-ready`
- Distinct role policies asserted via `/api/interview/preview` (policy IDs + domains)
- Review banner visible and no longer intercepts clicks (`pointer-events: none`)
- Settings shows compact build identity (`66Q/4E`)

## CI changes validating this environment

Browser job now starts:

```text
zume review serve --port 8787 --no-open --reset
```

and fails immediately unless review preconditions (empty candidates, 66/4, facets,
gaps, Selenium search, build-info) pass.

## Verdict

```text
READY FOR HUMAN UI REVIEW
```

Caveats (honest, non-blocking for human UI review):

- Reviewed corpus is gold-core depth (66 Q), not taxonomy-complete.
- Central CI green status must be confirmed on the tip SHA after push.
- Do not merge PR `#1` or tag `v1.0.0` without explicit human approval.
