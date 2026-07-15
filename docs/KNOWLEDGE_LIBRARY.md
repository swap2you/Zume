# Knowledge Library

`knowledge/` is Zume's human-reviewable source of truth. Published questions
and exercises are YAML under `questions/` and `exercises/`; taxonomy and source
provenance live in `taxonomy.yaml` and `sources.yaml`.

## Use it

```powershell
zume knowledge validate
zume knowledge stats
zume knowledge build-index
zume knowledge search "test isolation"
zume knowledge gaps
```

`build-index` creates a local SQLite FTS5 index at `data/knowledge-fts.sqlite`.
It is derived, git-ignored data: delete and rebuild it rather than editing or
committing it.

## Editorial rules

- Validate before relying on changed content.
- Generated seed records are reproducible; update the generator or source
  taxonomy rather than hand-editing generated content.
- References identify concepts and provenance; they do not copy source text.
- Candidate-facing material excludes recommended answers and reference
  solutions. The candidate exercise sheet is the only shareable hiring artifact.

The workspace UI exposes library browsing and search locally at
`http://127.0.0.1:8787` after `zume serve`.
