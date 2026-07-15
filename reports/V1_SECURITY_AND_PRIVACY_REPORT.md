# Zume 1.0 — Security and Privacy Report (Builder)

Date: 2026-07-15  
Branch: `release/zume-1.0`  
Environment: Windows 11, `.venv-rel`

> Builder-local scans and tests. Release zip content audit and clean-room
> reproduction are **NOT RUN** / **PENDING**. No secret values are printed below.

## Executive summary

| Area | Verdict |
|------|---------|
| Tracked text/DOCX secret scan | **PASS** |
| Git ignore for candidate/private/runtime | **PASS** (verified patterns) |
| Server binds localhost | **PASS** |
| Doctor reports state, not values | **PASS** |
| OpenAI / live keys | **NOT CONFIGURED** (offline mode) |
| Frontend production bundle pattern scan | **PASS** |
| AI excluded from candidate workflow by default | **PASS** (architecture) |
| `C:\AarohanSecrets` never copied/indexed/logged | **PASS** (policy + builder conduct) |
| Release zip secret/PII scan | **NOT VERIFIED** | Independent validator |
| Central CI security job | **PENDING** |

## Scans and commands

| Check | Command / path | Result |
|-------|----------------|--------|
| Tracked secret/PII scan | `zume scan-secrets` | **PASS** — no secrets or PII in tracked files |
| Doctor (configuration state) | `zume doctor` | OpenAI not configured; bind `127.0.0.1`; Docker labs unavailable; external secret source configured (name only) |
| Frontend bundle scan | Pattern grep on `apps/web/dist/assets/*.js` | **PASS** — no high-signal secret patterns |
| Path traversal | `tests/test_ask_and_api.py` | **PASS** |
| Security module tests | `tests/test_security.py` | **PASS** |
| Local bind enforcement | `tests/test_v1_providers_and_routes.py` | **PASS** |

### `zume doctor` output (state only, 2026-07-15)

```text
OpenAI provider: not configured
Web search: disabled
TTS: browser available
Realtime voice: disabled
Docker labs: unavailable
Secrets: external secret source configured
Bind host: 127.0.0.1
```

No API keys, tokens, or paths under `C:\AarohanSecrets` were printed.

## Acceptance matrix mapping (§I)

| Item | Verdict | Evidence |
|------|---------|----------|
| Candidate/private paths ignored | **PASS** | `.gitignore` — `candidates/`, `input/`, `output/`, `private/` |
| Runtime data ignored | **PASS** | `.gitignore` — `data/*.db`, `data/lab-workspaces/`, caches |
| Tracked text/DOCX secret scan | **PASS** | `zume scan-secrets`, `src/zume/security.py` |
| Frontend secret scan | **PASS** (pattern) | `apps/web/dist/` |
| `C:\AarohanSecrets` never copied/indexed/logged | **PASS** | Builder reports contain no secret values; `runtime_settings.py` loads at runtime only |
| Live key server-side only | **PASS** (design) | `src/zume/ai/openai_provider.py` — not bundled in UI |
| Tests use mocks | **PASS** | `tests/test_ask_and_api.py`, provider tests |
| Doctor reports state, not values | **PASS** | `src/zume/doctor.py` |
| AI calls excluded from candidate workflow | **PASS** | Hiring pipeline uses template/deterministic paths; AI is preparation-only |
| Web server binds localhost | **PASS** | `runtime_settings.py`, doctor output |
| No unexpected telemetry | **PASS** (code review) | No outbound analytics modules in `src/zume/` |
| Release zip no secret/PII | **NOT VERIFIED** | Validator must scan `releases/Zume-v1.0.0-Windows.zip` |

## Privacy boundaries

| Data class | Location | Git tracked | Indexed by FTS |
|------------|----------|:-----------:|:--------------:|
| Real candidates | `candidates/`, `input/` | No | No |
| Fictional demo | `examples/fictional-candidate/` | Yes | No |
| Knowledge library | `knowledge/` | Yes | Yes (questions/exercises only) |
| Local DB | `data/zume.db` | No | — |
| Chat / audio cache | `data/` (ignored) | No | — |

## OpenAI / live provider posture

Live OpenAI is **optional** and **not required** for v1.0. Builder environment:

- Provider: **not configured**
- Web search: **disabled**
- Tests and default UX: **offline / mocks**
- Live smoke (if ever run): record pass/fail metadata only — no key values in reports

## Release artifact

| Artifact | Path | Checksum (SHA-256) |
|----------|------|-------------------|
| Windows zip | `releases/Zume-v1.0.0-Windows.zip` | `07b8f7eaae762771e6be8b851bbdd5e996a5378cddc34c275ea84bd2d73b789e` |
| Checksum file | `releases/Zume-v1.0.0-Windows.zip.sha256` | Matches above |

Zip size: 1,444,090 bytes. Contents were built from `release-staging/`; independent
secret/PII scan of the zip is **NOT VERIFIED** by this report.

## Known risks (documented, not blocking builder)

1. **Public repository methodology exposure** — see
   `reports/PUBLIC_REPOSITORY_RISK_ASSESSMENT.md` (pre-v1.0 assessment; hiring
   rubrics in tracked config/docs).
2. **Near-duplicate / low-quality library content** — security-adjacent integrity
   risk for interview fairness; editorial audit is **NOT VERIFIED**.

## Related

- `docs/SECURITY_AND_SECRETS.md`
- `docs/release/v1.0/04_SOURCE_AND_RESEARCH_POLICY.md`
- `reports/V1_CLEAN_ROOM_VALIDATION.md` (pending)
