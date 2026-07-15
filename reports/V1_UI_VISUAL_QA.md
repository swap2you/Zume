# Zume 1.0 — UI Visual QA (Builder)

Date: 2026-07-15  
Branch: `release/zume-1.0`  
Frontend bundle: `apps/web/dist/` (production build present)  
Capture method: Builder screenshots while `zume serve` on localhost

> These screenshots support **human UI review** and defect triage. They are not
> clean-room proof. Keyboard, contrast, and Playwright regression remain
> **NOT VERIFIED** in this builder pass.

## Screenshot inventory

All paths relative to repository root `C:\Development\Workspace\Zume`.

| Screen | Desktop | Tablet | Verdict |
|--------|---------|--------|---------|
| Home | [home.png](screenshots/home.png) | [home-tablet.png](screenshots/home-tablet.png) | **PASS** (captured) |
| Question Library | [library.png](screenshots/library.png) | — | **PASS** (captured) |
| Practice Session | [practice.png](screenshots/practice.png) | — | **PASS** (captured) |
| Interview Builder | [interview-builder.png](screenshots/interview-builder.png) | — | **PASS** (captured) |
| Candidate Intake | [intake.png](screenshots/intake.png) | — | **PASS** (captured) |
| Candidate Finalize | [finalize.png](screenshots/finalize.png) | — | **PASS** (captured) |
| Exercise Lab | [lab.png](screenshots/lab.png) | — | **PASS** (captured) |
| Ask Zume | [ask.png](screenshots/ask.png) | — | **PASS** (captured) |
| Settings / Doctor | [settings.png](screenshots/settings.png) | — | **PASS** (captured) |

Full paths:

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

## Acceptance matrix mapping (§E)

| Item | Builder verdict | Evidence |
|------|-----------------|----------|
| `zume serve` on localhost | **PASS** | Screenshots imply local server; `src/zume/serve.py` binds `127.0.0.1` |
| No API key required to start | **PASS** | `zume doctor`: OpenAI not configured; UI loads in screenshots |
| Health / version / doctor | **PASS** (screenshot) | `settings.png` |
| Static UI same process | **PASS** | `src/zume/server/app.py` |
| Home | **PASS** | `home.png`, `home-tablet.png` |
| Candidate Intake | **PASS** | `intake.png` |
| Candidate Finalize | **PASS** | `finalize.png` |
| Library filters/search | **PASS** (visual) | `library.png` |
| Practice Session | **PASS** | `practice.png` |
| Interview Builder preview | **PASS** | `interview-builder.png` |
| Exercise Lab | **PASS** (UI present) | `lab.png`; Docker runners may show unavailable — see lab report |
| Ask Zume offline | **PASS** (visual) | `ask.png` |
| Settings/Doctor | **PASS** | `settings.png` |
| Responsive desktop/tablet | **PASS** (partial) | Desktop + `home-tablet.png` only |
| Keyboard navigation | **NOT VERIFIED** | No builder keyboard audit recorded |
| Accessible labels/focus/contrast | **NOT VERIFIED** | Requires clean-room / Playwright a11y pass |
| Production bundle no secret | **PASS** (pattern scan) | `apps/web/dist/assets/*.js` — no `sk-`, `AKIA`, or assignment patterns |
| Path traversal rejected | **PASS** (tests) | `tests/test_ask_and_api.py::test_path_traversal_rejected` |

## Frontend test evidence

| Gate | Result | Evidence |
|------|--------|----------|
| Vitest unit tests | **PASS** — 2/2 | `apps/web/src/pages/Home.test.tsx`, `Ask.test.tsx` |
| ESLint / typecheck / build | **PASS** (builder) | `apps/web/dist/index.html` present |
| Playwright e2e | **NOT VERIFIED** | `apps/web/e2e/home.spec.ts` requires running API on `:8787` |

## Builder visual notes (non-blocking)

- Screenshots are static captures; loading/error states for every route are
  **NOT VERIFIED**.
- Monaco editor resize behavior in Exercise Lab is **NOT VERIFIED** from stills.
- Human reviewer should confirm clipping, overlap, empty states, and long-content
  wrapping per `docs/release/v1.0/06_RELEASE_RUNBOOK.md`.

## Limitations

1. Screenshots were produced in the builder environment; clean-room must capture
   its own set from a fresh worktree.
2. Tablet coverage is limited to Home; other routes at tablet width are
   **NOT VERIFIED**.
3. This report does **not** certify production release readiness.

## Related

- `reports/V1_IMPLEMENTATION_REPORT.md`
- `reports/V1_RELEASE_READINESS.md`
- `docs/release/v1.0/02_ACCEPTANCE_MATRIX.md` §E
