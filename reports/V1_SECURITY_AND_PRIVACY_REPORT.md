# V1 Security and Privacy Report (Post-Correction)

Date: 2026-07-16  
Branch: `release/zume-1.0`  
SHA: `f3fd1be90863d513d37ab8eb31612f797a9e00d0`

## Threat model (unchanged)

Local-first hiring toolkit. Candidate PII must never enter git. Secrets stay
outside the repo. Labs run against localhost isolation, not production systems.

## Controls verified in correction pass

| Control | Status | Notes |
|---------|--------|-------|
| Gitignore for candidates/input/output/private/releases | PASS | Local policy |
| `zume scan-secrets` on tracked text/DOCX | PASS (local) | Run before push |
| No live secrets in CI for primary validation | PASS | Mocks/offline |
| Knowledge drafts not selected as interview content | PASS | Publication gates |
| Candidate sheet excludes reference answers | PASS | Deliverable split |
| API lab origin allowlist | PASS | Exact `http://127.0.0.1:8765` |
| SQL lab write denial + timeout | PASS | Authorizer + progress handler |
| Java lab named container cleanup | PASS | `finally` removes container |
| Selenium lab no fake success | PASS | Failure surfaces honestly |
| Frontend no Google Fonts CDN | PASS | Local fonts/CSS only |

## Lab security CI

Workflow job `lab-security` runs `tests/test_labs_security.py` on every PR/push
to the release branch.

## Residual risks / limitations

| Risk | Mitigation / note |
|------|-------------------|
| Optional Docker labs | Disabled unless `ZUME_ENABLE_DOCKER_LABS` |
| Optional live OpenAI | Offline/mocks default; citations required when live |
| Public methodology exposure | See `PUBLIC_REPOSITORY_RISK_ASSESSMENT.md` |
| Localhost lab still code execution | Intended for interviewer machine only |

## Explicit non-actions

- Did not commit `C:\AarohanSecrets` or any credential files
- Did not commit real candidate data
- Did not weaken secret scanning to pass CI
