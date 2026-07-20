# Question Library Implementation Report

Branch: `release/zume-1.0`
PR: #1 (draft — not merged, not tagged)

## What changed

1. **Taxonomy** — Binding `02_QUESTION_LIBRARY_TAXONOMY.yaml` imported into
   `knowledge/taxonomy.yaml` (36 domains, facet vocabularies, modes).
2. **Facets API** — `GET /api/knowledge/facets?mode=reviewed|draft|gaps` returns
   real option counts from stored records.
3. **Question list contract** — `mode`, `request_id`, `facets_applied`, `limit`,
   empty-parameter tolerance, sort, boolean filters, resolved citations.
4. **Library UI** — Rebuilt per `01_QUESTION_LIBRARY_UI_SPEC.md`: modes, search,
   facet dropdowns, dependent subdomain, chips, expandable answer/guidance/
   follow-up/source/practice tabs, error≠empty.
5. **Gold core** — 66 blueprint records expanded, independently criticized, and
   published as reviewed `researched` content. Previous 89 concept-substitution
   templates retired.
6. **Content quality** — Gate detects templates, duplicates, weak locators,
   role mapping, stale P0/P1, executable exercise completeness.
7. **Role policies** — Seven role families in `config/role-policies.yaml` with
   distinct knockouts and honest coverage warnings.
8. **Search** — Stop-word removal, AND → reduced → OR → prefix fallback.
9. **Review mode** — `zume review serve --port 8787` (fictional data, noindex,
   OpenAI/Docker off by default) + `zume review reset`.
10. **Deterministic packaging** — `scripts/package_release.py` fixed timestamps,
    ordering, permissions, compression.

## Counts (this SHA)

| Metric | Value |
|---|---|
| Reviewed published questions | 66 |
| Draft research proposals | 1899 |
| Retired templates | 89 |
| Reviewed published exercises | 4 |
| Domains with reviewed questions | 23 |
| Open gaps (taxonomy targets) | many — library is not claimed complete |

## Commands

```text
zume knowledge facets   # via API
zume knowledge content-quality
zume knowledge review-report
zume review serve --port 8787
zume review reset
```

## Explicit non-claims

- The library is **not** complete against the internet or the full taxonomy.
- Draft proposals remain draft; they are never selected into candidate packages.
- PR #1 stays draft. No `v1.0.0` tag.
