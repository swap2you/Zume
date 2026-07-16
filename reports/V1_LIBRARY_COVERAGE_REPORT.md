# V1 Library Coverage Report (Post-Correction)

Date: 2026-07-16  
Branch: `release/zume-1.0`  
SHA: `f3fd1be90863d513d37ab8eb31612f797a9e00d0`

## Publication policy

| State | Meaning | Selected for real interviews? |
|-------|---------|-------------------------------|
| `published` + `reviewed` | Editorial pass complete | Yes |
| `draft` / `unreviewed` / `generated_proposal` | Proposal only | No |
| `retired` / `rejected` | Not active | No |

Draft proposals must not be counted as completed Tier coverage.

## Inventory (computed)

| Metric | Count |
|--------|------:|
| Total questions on disk | 1,988 |
| Published questions | 89 |
| Reviewed published questions | 89 |
| Draft questions | 1,899 |
| Total exercises on disk | 289 |
| Published exercises | 4 |
| Draft exercises | 285 |

### Published questions by domain

| Domain | Count |
|--------|------:|
| agentic-ai | 4 |
| ai-for-qa | 3 |
| ai-governance | 3 |
| api-openapi | 6 |
| cicd | 4 |
| cucumber | 4 |
| debugging-reliability | 4 |
| framework-architecture | 4 |
| git-maven | 4 |
| java | 8 |
| llm-engineering | 4 |
| mobile-appium | 4 |
| performance-observability | 4 |
| postman-newman | 3 |
| rest-assured | 6 |
| selenium | 8 |
| solution-architecture | 3 |
| sql-oracle | 6 |
| technical-leadership | 3 |
| testng | 4 |

### Published questions by level / priority

| Level | Count | Priority | Count |
|-------|------:|----------|------:|
| basic | 37 | P0 | 1 |
| intermediate | 27 | P1 | 88 |
| advanced | 25 | | |

### Origin / review

| Field | Value | Count |
|-------|-------|------:|
| quality_origin | hand_authored | 89 Q / 4 E |
| quality_origin | generated_proposal | 1,899 Q / 285 E |
| review_status | reviewed | 89 Q / 4 E |
| review_status | unreviewed | 1,899 Q / 285 E |

## Gaps

`zume knowledge gaps` reports **148** gaps against Tier targets using
**reviewed published** inventory only. Drafts do not close gaps.

This is intentional honesty after quarantining count-driven filler. Expanding
published coverage requires concept-specific research + independent review +
`knowledge promote`, not seed volume.

## Selection behavior

1. Prefer published + reviewed knowledge records.
2. Canonical domain aliases (e.g. mobile → `mobile-appium`).
3. Curated YAML fallback (`config/interview-question-library.yaml`,
   `config/exercise-library.yaml`) when reviewed depth is insufficient.
4. Never fill packages with draft generated proposals to meet a count.
5. Selection reasons are truthful (`mandatory-core`, `resume-claimed`, …).

## Content-quality gates

- CLI: `zume knowledge content-quality` / `critique` / `promote`
- Published records reject generic repeated answer fingerprints
- Metadata topic consistency enforced for reviewed set
- Stats/search defaults distinguish published vs draft
