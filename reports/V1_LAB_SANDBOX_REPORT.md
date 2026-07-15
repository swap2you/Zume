# Zume 1.0 — Exercise Lab Sandbox Report (Builder)

Date: 2026-07-15  
Branch: `release/zume-1.0`  
Reference: `docs/EXERCISE_LAB.md`, `docker/labs/selenium-compose.yml`

> Builder evidence from unit tests and capability probes. Live Docker isolation,
> Selenium compose, and malicious-sample penetration tests are **NOT VERIFIED**
> in the builder environment (`zume doctor`: Docker labs unavailable).

## Runner summary

| Runner | Isolation model | Requires Docker | Builder verdict |
|--------|-----------------|:---------------:|-----------------|
| SQL | In-process SQLite, temp workspace | No | **PASS** |
| API | Localhost allowlist (`127.0.0.1`, `localhost`) | No | **PASS** |
| Java | Docker container (`eclipse-temurin:21-jdk`) | Yes + `ZUME_ENABLE_DOCKER_LABS` | **NOT VERIFIED** (live); **PASS** (mocked tests) |
| Selenium | Docker compose profile | Yes + flag + compose file | **NOT VERIFIED** (optional/unavailable) |

## Environment probe

`zume doctor` (2026-07-15):

```text
Docker labs: unavailable
```

Docker is **optional**. The Windows release zip does not bundle Docker images.
Enable with `ZUME_ENABLE_DOCKER_LABS=true` when Docker Engine is installed.

## SQL lab (`src/zume/labs/sql_lab.py`)

| Check | Verdict | Evidence |
|-------|---------|----------|
| Works in-process | **PASS** | `SqlLabProvider.available == True` |
| Bundled fixtures | **PASS** | `training/sql-fixtures/demo.sql` |
| Row limit (200) | **PASS** | `_MAX_ROWS` |
| Timeout (5s) | **PASS** | `_TIMEOUT_SECONDS` |
| Structured results | **PASS** | `LabRunResult` |
| Offline tests | **PASS** | `tests/test_v1_coverage_boost.py::test_sql_lab_error_and_test`, `tests/test_ask_and_api.py::test_sql_lab_runs_offline` |

## API lab (`src/zume/labs/api_lab.py`)

| Check | Verdict | Evidence |
|-------|---------|----------|
| Localhost-only allowlist | **PASS** | `ALLOWED_HOSTS = {"127.0.0.1", "localhost"}` |
| Blocks external URLs | **PASS** | `tests/test_v1_providers_and_routes.py::test_api_lab_blocks_external_host` |
| Mock API target | **PASS** | Default port `8765`, `training/mock-api` |
| Structured failure when mock down | **PASS** | `URLError` handling — no crash |
| Success path test | **PASS** | `tests/test_v1_coverage_boost.py::test_api_lab_success_path` |

## Java lab (`src/zume/labs/java_lab.py`)

| Check | Verdict | Evidence |
|-------|---------|----------|
| Unavailable without flag | **PASS** | `tests/test_v1_providers_and_routes.py::test_java_and_selenium_unavailable_without_flag` |
| Docker-gated availability | **PASS** | `_docker_available() and enable_docker_labs` |
| Mocked docker run path | **PASS** | `tests/test_v1_coverage_boost.py::test_java_lab_docker_mock_run` |
| Live compile/run isolation | **NOT VERIFIED** | Docker not enabled in builder env |
| Non-root / CPU-memory limits | **NOT VERIFIED** | Requires live container inspection |
| No external network | **NOT VERIFIED** | Requires live `docker run --network` audit |
| Malicious escape | **NOT VERIFIED** | Clean-room penetration |

## Selenium lab (`src/zume/labs/selenium_lab.py`)

| Check | Verdict | Evidence |
|-------|---------|----------|
| Clearly optional/unavailable | **PASS** | Capability message when Docker/compose missing |
| Compose file declared | **PASS** | `docker/labs/selenium-compose.yml` |
| Live browser isolation | **NOT VERIFIED** | Optional; requires Docker + compose up |
| Builder UI shows lab screen | **PASS** | `reports/screenshots/lab.png` |

## Workspace hygiene

| Check | Verdict | Evidence |
|-------|---------|----------|
| Workspaces under git-ignored path | **PASS** | `data/lab-workspaces/` per `docs/EXERCISE_LAB.md` |
| No candidate mounts | **PASS** (design) | Lab providers use temp workspaces only |
| API lists capabilities | **PASS** | `tests/test_server_shell.py::test_lab_capabilities_list` — sql, api, java, selenium |
| Monaco editor in UI | **PASS** (dependency) | `@monaco-editor/react` in `apps/web/package.json`; `lab.png` |

## Acceptance matrix mapping (§H)

| Item | Verdict |
|------|---------|
| Monaco editor loads | **PASS** (visual + dependency) |
| SQL lab works | **PASS** |
| API lab localhost mock only | **PASS** |
| Java Docker-isolated | **NOT VERIFIED** (live) |
| Selenium isolated or optional/unavailable | **PASS** (optional/unavailable) |
| No external network from runners | **NOT VERIFIED** (live Docker) |
| Non-root runner | **NOT VERIFIED** |
| CPU/memory/PID/time limits | **PARTIAL** — SQL timeout/row caps **PASS**; Docker limits **NOT VERIFIED** |
| Timeout cleanup | **PASS** (SQL); **NOT VERIFIED** (Docker) |
| No secret/candidate mounts | **PASS** (design) |
| Malicious sample cannot escape | **NOT VERIFIED** |
| Structured runner results | **PASS** |
| Containers/workspaces cleaned | **NOT VERIFIED** (live Docker) |

## Honest limitations

1. **SQL uses SQLite, not Oracle** — dialect differences are labeled; Oracle-specific
   exercises may not execute identically in-lab.
2. **API lab needs mock server running** for live HTTP success; offline tests mock
   `urlopen`.
3. **Selenium compose is optional** — acceptable per v1.0 contract when prerequisites
   are absent; UI must report unavailability clearly (**PASS** in doctor/capabilities).
4. Clean-room must run live Docker tests when the validator environment supports them.

## Related

- `reports/V1_IMPLEMENTATION_REPORT.md`
- `reports/V1_UI_VISUAL_QA.md` — `lab.png`
- `docs/release/v1.0/02_ACCEPTANCE_MATRIX.md` §H
