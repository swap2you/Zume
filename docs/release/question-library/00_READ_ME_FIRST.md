# Zume Question Library Final Package

This package replaces the current count-driven Question Library screen with a
database-driven preparation and interviewer workspace.

It does not replace the Zume hiring engine. It corrects the Library experience,
content publication standard, role-specific filtering, and full-screen
validation.

## Files

1. `01_QUESTION_LIBRARY_UI_SPEC.md`
   - Exact desktop/tablet behavior.
   - Dropdowns, facets, cards, answer presentation, empty/error states.

2. `02_QUESTION_LIBRARY_TAXONOMY.yaml`
   - Canonical dropdown values and dependent domain/subdomain options.

3. `03_GOLD_CORE_QUESTION_CATALOG.yaml`
   - A specific high-signal starter catalog modeled on the detailed interview
     guides used elsewhere in this project.
   - It is a content blueprint. Cursor must turn each blueprint record into a
     complete sourced Zume question record and run the publication gates.

4. `04_CURSOR_STARTUP_PROMPT.md`
   - Main implementation and correction prompt.

5. `05_COWORK_VALIDATION_PROMPT.md`
   - Independent browser validation for every route, element, API response,
     content record, and package.

6. `06_SECURE_REMOTE_REVIEW_RUNBOOK.md`
   - Local Cowork review first.
   - Authenticated tunnel instructions only when remote access is necessary.

## Required outcome

The default Question Library must show reviewed-published questions immediately.
A user should never have to type internal taxonomy identifiers into blank text
fields.

The screen must make these distinctions explicit:

- reviewed and available for interviews;
- draft research proposals;
- retired records;
- current gaps.

No generic generated proposal may be labeled reviewed or enter a real candidate
interview package.
