# Release and Recovery

## Build the Windows package

```powershell
python scripts/build_windows_release.py
```

The builder runs `npm ci` and `npm run build` when `apps/web` exists, stages a
clean package under git-ignored `release-staging/`, and writes
`releases/Zume-v1.0.0-Windows.zip` plus a `.sha256` file. It includes no Docker
images, candidate data, secrets, virtual environments, or generated data caches.

Verify the checksum before distribution:

```powershell
Get-FileHash releases\Zume-v1.0.0-Windows.zip -Algorithm SHA256
Get-Content releases\Zume-v1.0.0-Windows.zip.sha256
```

## Recover safely

1. Keep the ZIP intact and verify its checksum.
2. Extract to a new local folder.
3. Run `.\scripts\install-zume.ps1`, then `.\scripts\start-zume.ps1`.
4. Run `zume doctor`, `zume knowledge validate`, and `zume knowledge build-index`.
5. Restore candidate data only from a validated local backup and never from a
   release package.

For a working installation, run `zume db backup` before `zume db check`; never
overwrite a database before confirming the backup.
