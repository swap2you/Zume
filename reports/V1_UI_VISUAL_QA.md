# V1 UI Visual QA (Post-Correction)

Date: 2026-07-16  
Branch: `release/zume-1.0`  
SHA: `f3fd1be90863d513d37ab8eb31612f797a9e00d0`

## Scope

Builder evidence for workspace pages after audit corrections. Screenshots are
fictional / privacy-scanned and live under `reports/screenshots/`. They are
**claims for the clean-room validator to challenge**, not a substitute for human
UI review.

## Pages corrected

| Page | Contract fixes |
|------|----------------|
| Library | Search uses `results`/`items`; P0–P3 filters; published defaults |
| Practice | Backed by `/api/knowledge/practice` library records |
| Lab | Runners: `sql`, `api`, `java`, `selenium` only |
| Ask Zume | Citations + source mode rendered |
| Intake | Upload + unconfirmed schedule subject wording |
| Finalize | Missing candidate → clear 404 path |
| Interview Builder | Alias-aware selection; truthful reasons |
| Settings / Doctor | Local provider status; no Google Fonts CDN |

## Browser read-aloud

- Module: `apps/web/src/audio/speech.ts`
- Uses browser `speechSynthesis` (offline-capable)
- Operable controls: speak / pause / resume / stop (covered by regression test)

## Screenshot artifacts

Tracked PNGs (also expected as CI `ui-screenshots` artifact after green run):

- `home.png`, `home-tablet.png`
- `library.png`, `practice.png`, `lab.png`
- `ask.png`, `intake.png`, `finalize.png`
- `interview-builder.png`, `settings.png`

## Playwright

- Specs under `apps/web` must **fail** when the app server is unavailable
- No suite-wide `test.skip` for missing server
- CI job `browser-e2e` uploads screenshots

## Human UI review gate

Blocked until clean-room verdict:

`READY FOR HUMAN UI REVIEW`
