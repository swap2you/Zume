# Question Library UI QA

## Library screen

- Modes: Reviewed (default) / Draft Research / Coverage & Gaps
- Search: prominent, 300 ms debounce, `/` shortcut, local history, clear
- Filters: Domain, Subdomain (disabled until domain), Level, Priority, Role —
  all from `/api/knowledge/facets`, counts in labels (`Java (6)`)
- More filters: Frequency, Question type, Source family, Freshness, Tags,
  Has exercise / follow-ups / code example
- Active chips + Clear all
- Result header shows reviewed/draft count; API errors show Retry (never “0 results”)
- Cards: priority/level/domain/frequency/roles, expand tabs for answer,
  interviewer guidance (incl. 0–4 scoring anchors), follow-ups, absolute HTTPS
  sources, practice controls

## Home

- Headline metrics: Reviewed questions / Draft research proposals / Reviewed exercises
- No combined “library questions” figure as the primary metric

## Builder

- Role track dropdown (7 policies)
- Shows role policy label, knockout minutes, coverage warning, candidate-safe exercises

## Review mode

- Banner: `Review mode — fictional data`
- `X-Robots-Tag: noindex, nofollow`

## Routes validated in unit/E2E contracts

Overview, Intake, Finalize, Library, Practice, Builder, Lab, Ask, Settings

## Known gaps

- Split-view sticky detail panel is deferred; cards expand in place.
- Screenshot capture for desktop/tablet is in Playwright (`every route loads at desktop and tablet`).
