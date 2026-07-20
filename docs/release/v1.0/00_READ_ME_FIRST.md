# Zume 1.0 Cursor Release Package

This package is the implementation contract for expanding Zume from a validated
local-first hiring CLI into a local interview-preparation and hiring workspace.

It deliberately preserves the existing Zume v2 hiring engine. The new web,
knowledge, AI, audio, and exercise-lab capabilities are adapters around that
engine, not a rewrite of its business rules.

## Baseline

- Repository: `C:\Development\Workspace\Zume`
- GitHub: `swap2you/Zume`
- Required baseline commit: `bdbfbc71b2a129e53fec2dd9ba741e759028d875`
- Product name: **Zume**
- Standard interview: 180 minutes
- Knockout: first 20 minutes
- Existing candidate contract: `source/`, `_internal/`, `deliverables/`
- Existing deliverables: maximum seven
- Existing canonical commands: `zume intake`, `zume finalize`

## Files

1. `01_ZUME_1_0_MASTER_CURSOR_PROMPT.md`
   - Give this to Cursor Agent from the repository root.
   - It contains the full phased build and release program.

2. `02_ACCEPTANCE_MATRIX.md`
   - The objective release contract.
   - Cursor must keep it checked and link evidence for every item.

3. `03_KNOWLEDGE_TAXONOMY.md`
   - Required question-library domains, role tracks, priorities, and coverage.

4. `04_SOURCE_AND_RESEARCH_POLICY.md`
   - How questions and answers are researched, paraphrased, cited, refreshed,
     and protected from low-quality or copied content.

5. `05_CLEAN_ROOM_VALIDATOR_PROMPT.md`
   - Run in a new Cursor chat or independent agent after the builder finishes.
   - The validator must not receive the builder conversation or self-authored
     completion report.

6. `06_RELEASE_RUNBOOK.md`
   - Branch, CI, packaging, review, and release sequence.

## How to use

From Cursor, open this package and send:

> Execute `01_ZUME_1_0_MASTER_CURSOR_PROMPT.md` against the Zume repository.
> Work phase by phase without asking me routine implementation questions.
> Stop only for a real safety blocker, missing operating-system prerequisite, or
> an action requiring account authorization. Keep existing Zume v2 behavior
> locked. Do not merge to main or create the final tag.

The builder may create and push a release branch and a draft pull request so
central CI can run. It must not merge the pull request or tag the release.

When the builder reports completion, open a new Cursor chat with no builder
history and run `05_CLEAN_ROOM_VALIDATOR_PROMPT.md`.

## Secret handling

The user identified `C:\AarohanSecrets` as an approved local secret location.
This is not permission to copy, print, index, summarize, or commit the directory.

Cursor may use a clearly named OpenAI credential from that directory only at
runtime and only under the exact restrictions in the master prompt:

- never print or log the value;
- never copy it into the repository;
- never expose it to the browser;
- never include it in reports, screenshots, commands, or test fixtures;
- tests must use mocks;
- the application must work without the key;
- live AI smoke tests record only pass/fail metadata.
