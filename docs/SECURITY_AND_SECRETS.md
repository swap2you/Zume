# Security and Secrets

Zume is local-first. Real candidate data, generated packages, local indexes,
chat history, audio caches, and release staging are git-ignored.

## External secret sources

`C:\AarohanSecrets` may be used as an external local credential source. Zume
only checks approved filenames at that directory's top level. Never copy,
print, log, paste, package, or commit values from it. `ZUME_SECRETS_DIR` can
point to another approved local directory. Environment variables may also be
used for a session.

Run `zume doctor` to inspect configuration state; it deliberately omits key
material and even key prefixes.

## Release and repository checks

```powershell
zume scan-secrets
git status --short
git diff --cached --name-only
```

Never commit `candidates/`, `input/`, `output/`, `data/`, `.venv`, `.env`,
SQLite indexes, release artifacts, or Docker credentials. The repository should
remain private when it contains hiring methodology or interviewer material.
See `PRIVACY.md` for candidate retention and lifecycle operations.
