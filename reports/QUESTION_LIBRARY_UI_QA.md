# Question Library UI QA (CI / review revalidation)

Date: 2026-07-19

## Failure fixed from run `29539705600`

- Test: `reviewed library loads records from facets-driven dropdowns`
- Symptom: Domain `<select>` option count was `1` (only "All")
- Cause: assertion raced ahead of `/api/knowledge/facets` population
- Fix: `data-facets-ready` + `expect.poll` for option count > 1

## Additional defects corrected in this pass

| Defect | Fix |
|--------|-----|
| Browser CI used ordinary `zume serve` | `zume review serve --port 8787 --no-open --reset` + preconditions |
| Review API listed real candidates | Bind routes to `app.state.root` via request ContextVar |
| Sticky review banner intercepted clicks | `pointer-events: none` on `.review-banner` |
| No corpus/source identity endpoint | `GET /api/build-info` + Settings card |

## Local proof

- Preconditions: review_mode, empty candidates, 66/4, gaps 200, Selenium search
- Playwright workflows: 12 passed against clean review server
