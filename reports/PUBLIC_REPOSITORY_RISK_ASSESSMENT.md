# Public Repository Risk Assessment

Date: 2026-07-13
Repository: `https://github.com/swap2you/Zume`
Assessed commit: `53bfc291c9134890b9751f7ac7a155df1a9f177d`
Assessed visibility: **Public** (confirmed via the repository page)

## Summary

The repository is currently **public**. While no real candidate PII is tracked
in Git (verified — see below), the repository still exposes the complete hiring
methodology. For a hiring process this is a meaningful integrity and fairness
risk: candidates who find the repository gain an unfair advantage, and the
evaluation approach can be gamed. **Recommendation: make the repository private.**

This assessment does not change GitHub visibility automatically. The owner must
do that manually in GitHub → Settings → General → Danger Zone → Change
visibility.

## What is exposed by the current public repository

| Exposed content | Location | Why it matters |
|-----------------|----------|----------------|
| Senior SDET hiring standard, gate and weights | `config/hiring-standard.yaml`, `docs/04_Hiring_Standard_and_Scoring.docx` | Reveals exactly what is scored and the pass thresholds. |
| Decision rules (Proceed / Conditional / Do Not Proceed) | `src/zume/screening.py`, docs | Candidates can reverse-engineer how to be marked "Proceed". |
| Interview exercises **with expected answers and reference solutions** | `config/exercise-library.yaml`, `docs/05_Core_Interview_Exercise_Library.docx` | Full answer key to the live coding assessment is public. |
| Red flags and independence-verification methods | `config/exercise-library.yaml`, `src/zume/feedback.py` | Candidates learn what interviewers watch for. |
| Communication templates and scoring bands | `docs/06_*.docx`, `src/zume/*` | Reveals internal wording and decision bands. |
| Automatic-reject signals | `config/hiring-standard.yaml` | Candidates learn which phrases trigger rejection. |

## What is NOT exposed (verified)

Git tracks no real candidate data. `git check-ignore` confirms the following are
ignored and therefore never committed:

- `candidates/**` (all candidate folders and `candidate.json` audit records)
- `input/**`, `output/**`
- `data/*.db` (the SQLite index)
- `General Docs/` (the owner's real candidate material on disk)
- `*.pdf`, `*.png`, `*.jpg`, `*.jpeg`
- `.env`

Only the fictional sample candidate (`examples/fictional-candidate/`, "Aarav
Mehta") is tracked. It contains no real PII.

> Note: this repository being public does not currently leak candidate PII. The
> risk is methodology exposure plus the standing danger that a future
> contributor could accidentally commit real data into a public repository.

## Concrete risks

1. **Assessment integrity** — the exercise answer key and scoring rules are
   public, so the live coding assessment can be rehearsed or gamed.
2. **Fairness** — candidates who find the repository are advantaged over those
   who do not.
3. **Future PII leakage** — a public repository raises the blast radius if
   anyone ever mis-commits a real resume, screenshot or database.
4. **Reputation** — public internal hiring rubrics can be quoted out of context.

## Recommendations (in priority order)

1. **Make the repository private now.** This is the single most important
   action and must be done manually by the owner.
2. Keep the answer keys (`config/exercise-library.yaml`) even more tightly held;
   consider a separate private submodule if the main repo ever needs to be
   shared more widely.
3. Rotate interview exercises regularly (see `07_ROTATE_EXERCISES.md`) so that
   any prior exposure decays in value.
4. Keep enforcing the privacy ignore rules and the automated privacy/secret
   tests added in this hardening pass (Phase 11) on every change.
5. Before inviting collaborators, confirm branch protection and that CI never
   uploads candidate folders as artifacts (enforced in Phase 10).

## Residual risk after making the repository private

Even when private, anyone with read access sees the full methodology. Limit
collaborator access to those who must have it, and continue rotating exercises.
