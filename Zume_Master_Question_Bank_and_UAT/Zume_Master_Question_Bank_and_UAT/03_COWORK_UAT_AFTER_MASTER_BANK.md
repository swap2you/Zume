# Zume Master Question Bank — Post-Import Cowork UAT Prompt

Validate the completed Master Question Bank implementation independently.

## Environment proof

- URL: `http://127.0.0.1:8787/`
- review mode must be true;
- candidate list initially empty;
- build SHA must equal the supplied final SHA;
- build-info corpus digest must equal the packaged corpus digest.

Stop with `NOT VERIFIED — ENVIRONMENT MISMATCH` when these checks fail.

## Import proof

Inspect the import manifest and APIs.

Require:

- input inventory: 1,546;
- unique input IDs: 1,546;
- every input ID resolved;
- no silent unprocessed rows;
- Java inventory: at least 68;
- Selenium inventory: at least 60;
- all 36 domains represented;
- reviewed/draft/rejected counts shown separately;
- import SHA-256 recorded;
- old 1,899 generated drafts reconciled and not duplicated visibly.

## Content audit

Sample:

- every reviewed P0;
- at least 15 reviewed questions per Tier A domain;
- at least 10 per Tier B domain;
- at least 5 per Tier C domain;
- all reviewed exercises;
- all AI/agentic records marked current/emerging.

For each sampled item verify:

- specific question;
- technically correct answer;
- answer directly addresses the question;
- meaningful example;
- non-generic signals/mistakes;
- deeper follow-up and answer;
- correct level/priority/role;
- official source URL;
- locator supports the answer;
- no semantic template repetition.

Fail when bulk-generated substitution text is labeled reviewed.

## UI

Validate at widths 1440, 1280, 1024, 900 and 768.

Question Library:

- no overlap;
- no horizontal overflow;
- search full width;
- compact filters;
- filter drawer/accordion at smaller widths;
- all dropdowns API-driven;
- Subdomain depends on Domain;
- Status modes distinct;
- counts correct;
- pagination/virtualization works with 1,500+ rows;
- detail panel readable;
- citations absolute;
- import provenance visible;
- errors are not shown as zero results.

Knowledge Administration:

- XLSX dry run;
- CSV dry run;
- JSON dry run;
- invalid row report;
- duplicate preview;
- import idempotency;
- export XLSX/CSV/JSON;
- validation and index rebuild;
- admin is local-only.

## Search relevance

Test natural-language queries for:

- Java HashMap mutable keys;
- Java virtual threads;
- Selenium explicit waits;
- Selenium BiDi;
- TestNG parallel data providers;
- Cucumber scenario state;
- REST idempotency;
- OpenAPI contract compatibility;
- Oracle latest row;
- Appium contexts;
- p95 latency;
- GitHub Actions matrix;
- prompt injection;
- agent tool permissions;
- MCP tools versus resources;
- QA roadmap;
- stakeholder conflict.

The top results must be relevant and filters must narrow them correctly.

## Candidate packages

Use fictional profiles for all role families.

Verify:

- only reviewed records selected;
- no draft/rejected record selected;
- role-specific knockout and depth;
- 180-minute total;
- question progression;
- exercises;
- rerun preservation;
- candidate sheet has no answers.

## Full application

Repeat intake, finalize, Practice, Builder, Lab, Ask Zume, Settings and package
tests. Fail on console errors, request failures and unexpected API 4xx/5xx.

## Package

Build twice and require identical checksum.
Extract and verify the same corpus digest and inventory counts.
Scan for secrets, PII, candidate data, runtime data, venv and node_modules.

## Report

Create:

`reports/COWORK_MASTER_BANK_UAT.md`

Record PASS / FAIL / NOT VERIFIED with evidence for every requirement.

End with exactly one:

- `READY FOR HUMAN UI REVIEW`
- `NOT READY — CORRECTIONS REQUIRED`
- `NOT VERIFIED — ENVIRONMENT MISMATCH`
- `NOT VERIFIED — ENVIRONMENT CAPABILITY BLOCKER`

Do not merge or tag.
