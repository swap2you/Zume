# Process Candidate End to End

## Objective
Screen a resume, then (if the decision allows) generate the interview kit and,
when a confirmed schedule is provided, the schedule record.

## Inputs
A resume file or pasted text, an optional schedule screenshot, and optional
confirmed schedule details.

## Privacy boundary
Candidate files live only in the git-ignored `candidates/` tree. Never commit
them. Do not infer or invent experience, evidence, or schedule facts.

## Files allowed to change
Only candidate-scoped output under `candidates/` and the SQLite index. No source
changes.

## Validation commands
```
zume filter-resume --input <resume>
zume interview-prep --candidate "<ref>"   # gated by screening decision
zume schedule-interview --candidate "<ref>" --details "<confirmed text>"
zume validate --candidate "<ref>"
```

## Stop conditions
Interview prep stops for a Do-Not-Proceed decision unless `--override` and
`--override-reason` are supplied. Schedule stays unconfirmed if timezone/date/
time checks fail.

## Required final report
Decision, resume evidence coverage (not a competency score), generated paths,
and any unverified mandatory skills.

## Git restrictions
Never commit candidate data. Do not push.
