# V1 Release Readiness (Post CI / Cowork Revalidation)

Date: 2026-07-19  
Branch: `release/zume-1.0`  
Baseline tip that failed Playwright: `411a3b3dd86006993249b15c53c15d7fa5c76831`  
Draft PR: `#1`

## Builder release verdict

**QUESTION LIBRARY + REVIEW ISOLATION FIXED LOCALLY — AWAITING TIP CI GREEN**

Production release still requires:

1. Green expanded central CI against the tip SHA after this push
2. Human UI review after independent verdict `READY FOR HUMAN UI REVIEW`
3. Explicit human approval before merge / tag

## Readiness checklist

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Reviewed gold-core inventory | PASS | 66 Q / 4 E |
| Draft filler quarantined | PASS | 1,899 draft Q |
| Review workspace isolation | PASS | API binds `app.state.root`; candidates empty after `--reset` |
| `/api/build-info` | PASS | SHA + corpus/frontend digests |
| Browser CI uses review serve | PASS | `.github/workflows/ci.yml` |
| Playwright facets race fixed | PASS | wait for `data-facets-ready` |
| Review banner click-through | PASS | `pointer-events: none` |
| Local Playwright workflows | PASS | 12/12 on clean review server |
| Clean revalidation report | PASS | `reports/COWORK_FULL_VALIDATION.md` |
| Stale Cowork evidence preserved | PASS | `reports/COWORK_FULL_VALIDATION_STALE_ENV.md` |
| Central CI green on tip SHA | PENDING | Fill after push |
| PR `#1` draft / unmerged | REQUIRED | Keep draft |
| Merge / tag | NOT DONE | Forbidden here |

## Next actions

1. Push tip; confirm CI green; record run ID
2. Keep PR `#1` draft
3. Human UI review only
4. Do **not** merge or tag without explicit approval
