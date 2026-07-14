# Start here — using Zume in Cursor

Zume runs from Cursor. You do not need to remember commands. In almost every
case you attach a file and send one short instruction.

## Before an interview (create the pre-interview package)

1. Open this repository folder in Cursor.
2. Attach the candidate's resume (PDF, DOCX, or TXT). Optionally attach or paste
   the interview schedule (a screenshot or a few lines of text).
3. Send exactly:

   > Process this candidate in Zume. Generate the pre-interview package and stop before feedback.

Cursor will screen the resume, build the interviewer guide, scorecard, and the
candidate-shareable exercise sheet, validate the documents, and then **stop and
wait**. No interview feedback is generated yet.

## After the interview (finalize)

1. Paste or attach your interview notes.
2. Send exactly:

   > The interview is complete. Use these notes to finalize the candidate.

Cursor will produce the final evaluation and the recruiter/leadership
communications.

## What you get (at most seven documents, interviewer-only unless noted)

| File | Audience |
|------|----------|
| `01_Screening_Summary.docx` | Interviewer |
| `02_Three_Hour_Interview_Guide.docx` | Interviewer (answers + solutions) |
| `03_Interview_Scorecard.docx` | Interviewer |
| `04_Candidate_Exercise_Sheet.docx` | **Shareable with the candidate** |
| `05_Schedule_and_Communications.docx` | Interviewer (only if a schedule was given) |
| `06_Final_Interview_Evaluation.docx` | Interviewer (after notes) |
| `07_Post_Interview_Communications.docx` | Interviewer (after notes) |

## Rules Zume always follows

- The standard technical interview is **180 minutes**. A different duration is
  flagged and must be confirmed.
- Candidate data is never committed to Git.
- Only `04_Candidate_Exercise_Sheet.docx` is safe to share with a candidate.

See `docs/ZUME_DAILY_USE_GUIDE.md` for a fuller walkthrough and
`docs/ZUME_TROUBLESHOOTING_GUIDE.md` if something looks wrong.
