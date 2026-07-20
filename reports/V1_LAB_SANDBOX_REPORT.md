# V1 Lab Sandbox Report (Post-Correction)

Date: 2026-07-16  
Branch: `release/zume-1.0`  
SHA: `15e248abddabb7b3eb9cebc6088cfe5ea70f199e`

## Runners

| Runner | Isolation model | Correction highlights |
|--------|-----------------|----------------------|
| `sql` | In-process SQLite | Write denial; progress timeout |
| `api` | Localhost HTTP only | Exact origin `http://127.0.0.1:8765`; redirects denied |
| `java` | Optional Docker | Named container; forced `docker rm -f` on timeout/exit |
| `selenium` | Optional Docker compose | No fake success path when runner unavailable |

## Security tests

`tests/test_labs_security.py` and correction regressions cover:

- SQL write statements rejected
- SQL long-running query timeout
- API wrong port rejected
- API redirect rejected
- Java cleanup on timeout (mocked Docker client)

CI job: `lab-security`.

## Docker optional path

Java/Selenium require Docker + `ZUME_ENABLE_DOCKER_LABS`. Without Docker, runners
must fail closed (not invent green results). Live Docker matrix is **NOT VERIFIED**
on every builder machine; central CI exercises unit/security tests; optional Docker
integration remains environment-dependent.

## UI contract

Lab page only offers backend runner names: `sql`, `api`, `java`, `selenium`.
