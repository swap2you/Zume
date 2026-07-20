# Architecture

Zume 1.0 is a local-first Python CLI with an optional localhost preparation UI.

## Components

- `src/zume/cli.py`: Typer commands, including intake, finalize, serve, doctor,
  and knowledge operations.
- `src/zume/pipeline.py`: protected candidate lifecycle and document generation.
- `src/zume/server/`: FastAPI app and workspace API, served only on localhost.
- `apps/web/`: React/Vite single-page UI; its built `dist/` is served by FastAPI.
- `knowledge/`: YAML source of truth for questions, exercises, taxonomy, and
  sources.
- `src/zume/knowledge/`: schema validation, selection, stats, and deterministic
  SQLite FTS5 indexing.
- `src/zume/labs/`: local and optionally Docker-isolated exercise runners.
- `training/`: bundled mock API and SQL fixtures.

## Data flow

Hiring input enters the ignored `input/` area, is processed by `intake`, and
creates exactly `source/`, `_internal/`, and `deliverables/` beneath a candidate
folder. `finalize` consumes real interviewer notes and preserves workflow
guards. The UI calls local `/api` routes; it reads library YAML/derived FTS and
does not bypass the candidate workflow.

YAML is authoritative; `data/knowledge-fts.sqlite` is generated and disposable.
Candidate data and runtime caches are ignored. Offline providers are the
default. Hosted AI, web search, voice, and Docker labs require explicit local
configuration.

Historical material is isolated under `docs/reference/legacy/`; it does not
define the current 1.0 workflow.
