# Preparation Workspace

Zume's optional local workspace combines a React UI (`apps/web`) with a FastAPI
server (`src/zume/server`). It is a preparation aid, not a replacement for the
protected hiring workflow.

## Start

```powershell
.\scripts\start-zume.ps1
# or: zume serve
```

The service binds only to localhost and opens `http://127.0.0.1:8787`. Build
the UI manually with `npm ci; npm run build` in `apps/web` if needed. API
documentation is available locally at `/docs`.

## Available areas

- Question library search and browsing.
- Interview-plan preview for the 180-minute standard.
- Ask Zume for knowledge-grounded, non-candidate questions.
- Practice and exercise-lab pages.
- Local health and capability status.

Do not paste resumes, interview notes, email addresses, or phone numbers into
Ask Zume or practice tools. Use `zume intake` before an interview and
`zume finalize` only after real notes exist. Candidate folders remain
`source/`, `_internal/`, and `deliverables/`.
