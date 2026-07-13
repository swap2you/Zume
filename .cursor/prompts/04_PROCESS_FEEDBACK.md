# Process Interview Feedback

## Objective
Turn interviewer notes into grounded feedback, scores, and communication drafts.

## Inputs
The interviewer narrative and the existing candidate record.

## Privacy boundary
Use only the provided notes. Do not label suspected external assistance as
cheating; record neutral observations and a confidence level.

## Files allowed to change
Only candidate-scoped output under `candidates/` and the SQLite index.

## Validation commands
```
zume interview-feedback --candidate "<ref>" --notes <notes> --leadership
zume validate --candidate "<ref>"
```

## Stop conditions
Stop if the candidate record does not exist. Preserve uncertainty; never invent
scores unsupported by the notes.

## Required final report
Decision, interview performance score (separate from resume evidence coverage),
independence confidence, and generated paths.

## Git restrictions
Never commit candidate data. Do not push.
