# Zume knowledge library

`taxonomy.yaml` and `sources.yaml` are the editorial source of truth for the
library's domain map and provenance registry. The question and exercise YAML
files under `questions/` and `exercises/` are generated, reproducible seed
content. Do not hand-edit generated records: update
`scripts/seed_knowledge_library.py` (or the source taxonomy), then re-run it.

Every published record is original Zume wording and references a registered
primary source by ID. References identify the concept to verify; they do not
copy or claim endorsement by the linked source. AI, LLM, agent, and other
fast-moving records are marked with a 90-day freshness window.

The YAML corpus is the human-reviewable source material. Any SQLite/search
index built from it is derived data and can be discarded and rebuilt. A record
may be published only after schema, source, duplicate, and freshness checks
pass.

Generate the seed corpus from the repository root:

```powershell
.\.venv-rel\Scripts\python scripts/seed_knowledge_library.py
```

The generator overwrites only its per-domain, per-level files, so rerunning it
is idempotent. It preserves no candidate data and never creates candidate-facing
answer material; candidate projection is enforced by `ExerciseRecord`.
