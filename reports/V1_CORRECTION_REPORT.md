# V1 Correction Report

Date: 2026-07-16  
Branch: `release/zume-1.0`  
Starting SHA (audit tip): `2dcde4bd189d8c11cfbd560193383a1a17012166`  
Corrected SHA: `CORRECTION_TIP`  
Draft PR: `#1` (remains draft; not merged; no `v1.0.0` tag)

## Verdict

**CORRECTIONS APPLIED — AWAITING CLEAN-ROOM VALIDATION**

Independent audit defects from `docs/release/v1.0-corrections/Zume_1_0_Independent_Release_Audit.md`
were reproduced with failing tests, then corrected without redesigning Zume architecture,
hiring workflow, three-folder contract, or seven deliverables.

## Correction commits (after starting SHA)

| SHA | Summary |
|-----|---------|
| `42395fd` | Phase 0: failing correction regression tests + audit baseline |
| `4b1ebbd` | Phase 1–2: quarantine generated filler; reviewed knowledge gates |
| `1151916` | Phase 3–7: selection aliases, lab hardening, Ask citations |
| `8548017` | Phase 4–5–9: web workspace, browser speech, Playwright gates |
| `f9388c6` | Phase 8: expand central CI (frontend, knowledge, labs, release) |
| `a2e326e` | Align API lab unit test with redirect-disabled opener |
| `CORRECTION_TIP` | Phase 10: regenerate correction release evidence |

## Audit defect disposition

| # | Defect | Resolution |
|---|--------|------------|
| 1 | Library search contract | API returns both `results` and `items` |
| 2 | P0–P3 priority filter | Covered by regression + API filter |
| 3 | Practice from library | `/api/knowledge/practice` returns published library records |
| 4 | Lab runner names | UI limited to `sql` / `api` / `java` / `selenium` |
| 5 | Ask citations / source mode | Structured citations + source mode in Ask UI |
| 6 | Unconfirmed schedule subject | Proposed (not confirmed) join subject |
| 7 | Domain aliases | Canonical aliases for mobile/performance/AI/etc. |
| 8 | Templated published answers | Generated filler quarantined to `draft` / `unreviewed` |
| 9 | Java metadata mismatches | Hand-authored reviewed records; quality gates |
| 10 | SQL timeout / write denial | Authorizer + progress timeout |
| 11 | API lab port / redirects | Exact origin `http://127.0.0.1:8765`; no redirects |
| 12 | Java container cleanup | Named container + `docker rm -f` in `finally` |
| 13 | Playwright skip | Suite fails when server unavailable (no skip) |
| 14 | Browser read-aloud | `speechSynthesis` controls in web audio module |

## Library honesty after correction

| Metric | Count |
|--------|------:|
| Published reviewed questions | 89 |
| Draft / unreviewed questions | 1,899 |
| Published reviewed exercises | 4 |
| Draft / unreviewed exercises | 285 |
| Taxonomy gaps (reviewed published vs targets) | 148 (honest; drafts not counted as coverage) |

Generated proposals remain `status: draft`, `review_status: unreviewed`,
`quality_origin: generated_proposal` until concept-specific research and independent
review promote them.

## What was not done

- No merge of PR `#1`
- No `v1.0.0` tag
- No redesign of hiring engine or deliverable contract
- Clean-room validation not run in this chat (see Phase 11 inputs)

## Next required action

Run a new clean-room validator chat with
`docs/release/v1.0-corrections/Zume_1_0_Clean_Room_Validation_Prompt_v2.md`
against SHA `CORRECTION_TIP` after central CI is green.
