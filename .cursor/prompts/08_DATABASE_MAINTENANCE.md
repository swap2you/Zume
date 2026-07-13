# Database Maintenance

## Objective
Verify and maintain the SQLite index: integrity, foreign keys, backups,
duplicate detection, and schema version.

## Inputs
`data/zume.db` (git-ignored).

## Privacy boundary
The database and its backups are git-ignored and must never be committed. Do not
print candidate rows into reports.

## Files allowed to change
None in source by default. Backups are written to git-ignored `data/`.

## Validation commands
```
zume db check
zume db backup --output data\zume-backup.db
```

## Stop conditions
Stop and report if `integrity_check` or `foreign_key_check` fails, or if the
backup does not validate.

## Required final report
Schema version, integrity result, duplicate candidates found, and validated
backup path.

## Git restrictions
Never commit `data/*.db` or any backup. Do not push.
