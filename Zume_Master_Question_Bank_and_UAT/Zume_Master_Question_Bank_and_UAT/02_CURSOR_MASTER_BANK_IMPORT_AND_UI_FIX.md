# Zume Master Question Bank — One-Pass Import, Enrichment, UI and Validation Prompt

## Fixed repository state

- Repository: `C:\Development\Workspace\Zume`
- Branch: `release/zume-1.0`
- Start from the latest pushed tip after `a3fc503`.
- PR #1 stays draft.
- Do not merge or tag.

## Inputs

Use one of these equivalent import files:

- `Zume_Master_Question_Bank_1546.xlsx`
- `Zume_Master_Question_Bank_1546.csv`
- `Zume_Master_Question_Bank_1546.json`

The files contain 1,546 stable, unique draft blueprints across 36 domains:

- Java: 68
- Selenium: 60
- API/OpenAPI: 68
- SQL/Oracle: 72
- LLM engineering: 64
- Agentic AI: 68
- plus the remaining technical, architecture, management and behavioral domains.

## Objective

Make Zume a broad interview preparation library without weakening the hiring
workflow or pretending unreviewed material is production-ready.

The final system must contain:

1. a complete searchable Master Inventory;
2. an independently reviewed Published Library;
3. clear Draft/Reviewed/Rejected states;
4. high-quality answers and sources;
5. role-specific interview selection;
6. a polished, non-overlapping Library UI;
7. import/export administration;
8. deterministic validation and Cowork UAT.

## Non-negotiable behavior

Preserve:

- `zume intake`;
- `zume finalize`;
- three candidate folders;
- seven canonical deliverables;
- 180-minute interview;
- 20-minute knockout where role policy requires it;
- sparse-notes protection;
- finalized-candidate rerun protection;
- local-first privacy.

Unreviewed imports must never enter real candidate packages.

## Phase 1 — Import staging

Implement:

```text
zume knowledge import <xlsx|csv|json> --mode draft --source master-inventory
zume knowledge import-report
zume knowledge export --format xlsx|csv|json
```

Requirements:

- read all 1,546 records;
- stable ID upsert;
- no duplicate creation;
- validate domains/subdomains/levels/priorities/roles;
- reject malformed rows with line/sheet evidence;
- preserve the original import file checksum;
- import as `draft`, `unreviewed`, `master_inventory`;
- do not publish automatically;
- do not overwrite reviewed records without an explicit reviewed merge process.

Create a staging manifest with:

- file SHA-256;
- imported count;
- inserted count;
- updated count;
- duplicate count;
- rejected count;
- counts by domain/level/priority;
- exact error rows.

## Phase 2 — Reconcile existing content

There are three current content sets:

- 66 reviewed gold-core questions;
- 1,899 older draft/generated questions;
- 1,546 new master-inventory blueprints.

Do not display or count these as an undifferentiated total.

Deduplicate semantically:

- exact ID;
- normalized question;
- concept/subdomain;
- semantic similarity;
- same answer intent.

Rules:

- preserve the 66 reviewed records when genuinely stronger;
- merge useful details from the master inventory;
- archive weak old generated drafts;
- retain provenance;
- never create two visible copies of the same interview question.

Produce:
`reports/MASTER_BANK_RECONCILIATION.md`

## Phase 3 — Full enrichment

Process by domain in controlled batches.

For every master-inventory blueprint, generate the full Zume record:

- title;
- precise question;
- concise answer;
- complete recommended answer;
- deep dive;
- key points;
- strong signals;
- weak signals;
- red flags;
- common mistakes;
- concrete examples;
- code/query/config examples where appropriate;
- follow-up question;
- complete follow-up answer;
- what the follow-up tests;
- difficulty increase;
- scoring anchors;
- role tracks;
- estimated minutes;
- source references;
- verified date;
- freshness period.

Do not use one answer template with substituted concept names.

## Phase 4 — Research rules

Use official or primary sources.

Current content must be checked against current documentation, especially:

- Java language/platform behavior;
- Selenium WebDriver/BiDi;
- TestNG;
- Cucumber;
- Maven/GitHub Actions;
- Appium;
- OpenAPI/HTTP;
- Oracle;
- Postman;
- Docker/Kubernetes;
- OpenTelemetry;
- OWASP;
- OpenAI Responses/tools/evals;
- MCP;
- agent security and governance.

For technical records, every factual answer needs:

- source ID;
- source name;
- absolute HTTPS source URL;
- specific locator;
- verification date.

Behavioral and internal leadership questions may cite an internal Zume standard,
but must remain original and scenario-specific.

## Phase 5 — Independent critic

The writing agent may not approve its own records.

For each batch, run a separate clean critic context that receives:

- the record;
- source references;
- schema;
- content-quality rubric;
- no writer completion claim.

The critic checks:

- technical correctness;
- answer/question alignment;
- specificity;
- originality;
- level;
- priority;
- role mapping;
- source support;
- current versus legacy behavior;
- follow-up depth;
- scoring fairness;
- unsafe guidance;
- duplicate/template similarity.

Outcomes:

- APPROVED;
- REVISE;
- REJECTED.

A record becomes reviewed/published only after APPROVED.

Completion means every imported ID is resolved to:

- published/reviewed; or
- rejected with a specific reason and a replacement when the rejection creates
  a required coverage gap.

No imported ID may remain silently unprocessed.

## Phase 6 — Quality gates

Extend deterministic quality checks:

- normalized duplicate questions;
- normalized duplicate answers;
- semantic template clusters;
- repeated signal/mistake/follow-up clusters;
- answer/question vocabulary mismatch;
- incorrect subdomain;
- role mismatch;
- empty or relative source URL;
- weak source locator;
- stale P0/P1;
- missing follow-up answer;
- missing code/query example when required;
- generic exercise;
- candidate answer leakage;
- unresolved import row.

Add domain coverage floors and report them separately from total inventory.

Do not claim “all questions on the internet.” Report:

- total inventory;
- reviewed published;
- rejected;
- remaining gaps.

## Phase 7 — Library UI correction

The current screen must be redesigned for density and responsive layout, not
just patched.

### Layout

Desktop:

- page header and metrics;
- one full-width search row;
- compact filter toolbar;
- results list on the left;
- sticky detail panel on the right;
- optional full-card mobile/tablet mode.

Tablet:

- filters in a drawer or accordion;
- one-column results;
- no overlap;
- no horizontal scrolling.

### Primary dropdowns

API-driven only:

- Domain;
- Subdomain;
- Level;
- Priority;
- Role;
- Status.

### Secondary filters

- Frequency;
- Question type;
- Source;
- Freshness;
- Tags;
- Has exercise;
- Has code;
- Has follow-ups.

### Required modes

- Published & reviewed;
- Master inventory;
- Draft research;
- Rejected/retired;
- Coverage gaps.

### Metrics

Show separately:

- total master inventory;
- reviewed published;
- draft/unreviewed;
- rejected;
- reviewed exercises;
- domains with reviewed coverage;
- open gaps.

### Results

Question cards/detail must show:

- question;
- answer;
- examples;
- interviewer guidance;
- follow-ups;
- scoring;
- sources;
- review state;
- source/import provenance.

### Admin import page

Add a local-only Knowledge Administration section:

- upload XLSX/CSV/JSON;
- dry-run preview;
- validation errors;
- domain counts;
- duplicate preview;
- import;
- export;
- rebuild index;
- run validation;
- view critic status.

Do not expose this remotely or to candidate-shareable views.

## Phase 8 — Search/index

Index:

- question;
- answer;
- key points;
- examples;
- tags;
- source;
- role;
- subdomain.

Support:

- natural-language stop-word removal;
- strict and ranked fallback;
- phrase matching;
- filters;
- pagination;
- typo-tolerant domain/tag matching;
- no stale index after import.

Add relevance tests across all major domains.

## Phase 9 — Candidate selection

Candidate packages may use only reviewed-published records.

Selection should choose a small subset from the large library using:

- resume evidence;
- role policy;
- mandatory core;
- priority;
- progression;
- interview time;
- risk;
- rotation;
- previous assignment.

Do not increase the interview document size merely because the library is large.

Test role families:

- Senior SDET;
- Lead SDET;
- Mobile;
- Performance;
- AI QA;
- Architect;
- QA Manager.

## Phase 10 — Validation

### Automated

Run:

- Python compile/lint/type/tests/coverage/build;
- frontend lint/type/test/build;
- import dry run;
- import;
- schema validation;
- content quality;
- critic resolution;
- source URL check;
- FTS rebuild;
- relevance tests;
- role selection tests;
- Playwright desktop/tablet;
- deterministic package build twice;
- secret/PII/package scan.

### Data acceptance

Require:

- input records = 1,546;
- unique stable IDs = 1,546;
- unresolved IDs = 0;
- no duplicate visible questions;
- Java inventory ≥68;
- Selenium inventory ≥60;
- every domain represented;
- published count reported honestly;
- rejected records include reasons;
- all published citations resolve;
- all P0/P1 published records reviewed.

### UI acceptance

Require:

- no filter overlap at 1440, 1280, 1024, 900, 768 widths;
- dropdowns populated;
- status modes distinct;
- large dataset paginates/virtualizes;
- details readable;
- no console/network failures;
- keyboard and accessibility pass.

## Phase 11 — Cowork

After CI is green, run the separate post-import Cowork prompt:

`03_COWORK_UAT_AFTER_MASTER_BANK.md`

Cowork must verify frontend, backend, data, content, import/export and package.

## Git rules

- focused commits;
- branch remains `release/zume-1.0`;
- PR #1 remains draft;
- no merge;
- no tag;
- no secrets or candidate data;
- import files may live under a release/input documentation directory;
- generated runtime indexes remain ignored.

## Final response

Return:

1. final SHA;
2. commits;
3. import checksum;
4. 1,546-row reconciliation;
5. reviewed/draft/rejected counts;
6. counts by domain;
7. Java/Selenium counts;
8. content-quality and critic results;
9. UI screenshots at four widths;
10. Playwright results;
11. CI run;
12. deterministic ZIP checksum;
13. Cowork inputs;
14. known gaps;
15. confirmation PR is draft and no merge/tag occurred.
