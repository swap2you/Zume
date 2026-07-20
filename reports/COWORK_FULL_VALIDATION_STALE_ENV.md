# Zume Full Browser Validation — Independent Report

- Validator: Cowork (independent product / UI / API / data validation)
- Date: 2026-07-16
- Target: `http://127.0.0.1:8787/` (`zume review serve --port 8787`)
- Browser: Chrome, desktop viewport (effective 2400×1111 CSS px at 0.8 zoom on 1920×1080)
- Note on screenshots: screenshots were captured live during the session (IDs referenced below, e.g. `ss_8919r5e5b`) but the Cowork session cannot persist screenshot files to disk. Every claim below is backed by a live browser action, an API call, or a filesystem inspection performed during the run.

## Verdict summary

11 FAIL, 4 WARN, 41 PASS, 6 NOT VERIFIED across 62 checks. The core hiring flows
(intake → builder preview → finalize) and the exercise/practice surfaces work.
The Question Library backend contract is broken (facets 404, search inert, modes
identical), role policies are not applied to interview plans, and review mode is
serving real-looking candidate data. Full detail follows.

---

## 1. Overview route (`/`)

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1.1 | Health is online | PASS | `GET /api/health` → 200 `{"status":"ok"}`; "API online" badge rendered (ss_8919r5e5b) |
| 1.2 | Reviewed count labeled correctly | PASS | UI "89 Reviewed questions" = API `published_questions: 89` |
| 1.3 | Draft count labeled correctly | WARN | UI label is "Draft research proposals" (1899). Number matches `draft_questions: 1899`, but the label conflates draft *questions* with "research proposals". Severity: low. Correction: rename metric to "Draft questions" or bind to a proposals metric if one exists. |
| 1.4 | Exercise count | PASS | UI "4 Reviewed exercises" = API `published_exercises: 4` |
| 1.5 | Domain and gap counts present | FAIL | Overview shows only 3 metrics. No covered-domain count (API has 20 domains) and no gap count anywhere. Severity: medium. Correction: add the two metrics to the Overview strip, backed by `/api/knowledge/stats` and a working gaps endpoint. |
| 1.6 | No blank metric | PASS (Overview only) | All three rendered metrics have values. (Library metric strip is blank — see 4.2.) |
| 1.7 | Quick links work | PASS | "Bring in a candidate" navigates to `/intake` (verified click); links target `/intake`, `/builder`, `/library` |
| 1.8 | Review-mode banner appears | FAIL | Only badge shown is "Local workspace — interviewer tools stay on this device". No banner states the app is in review mode with fictional data, although `/api/health` of the packaged build exposes `review_mode: true`. Severity: medium. Correction: render an explicit review-mode banner when `review_mode` is true. |
| 1.9 | Review mode uses fictional data only | FAIL | `GET /api/candidates` and `candidates/` on disk contain `Patil_Swapnil_2026-07-15` (the machine owner's name) and `Unknown_Reshma_2026-07-15` alongside fictional candidates. `private/legacy-candidate-material/` holds real-looking resumes (Rohan N., Rajeev). Severity: **high** (privacy / review-data hygiene). Correction: point review mode at a fictional-only candidates directory or exclude non-fictional folders from the review data root. |

## 2. Candidate intake (`/intake`)

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 2.1 | Paste fictional resume | PASS | "Avery Testperson" pasted resume → `POST /api/candidates/intake` 200; Decision "Proceed", coverage 92% (ss_7405kjlee) |
| 2.2 | Upload fictional TXT | PASS | `fictional_resume.txt` → `POST /api/candidates/intake-upload` 200; "Do Not Proceed", 27% (ss_9474dwmgm) |
| 2.3 | Upload fictional DOCX | PASS | `fictional_resume.docx` → 200; folder `Fictionaldocx_Jordan_2026-07-16` created (ss_018628u7j) |
| 2.4 | Upload fictional PDF | PASS (with defect) | Well-formed PDF → 200, processed (ss_1176erdlv). **Defect:** a structurally malformed PDF returned HTTP **500** surfaced as raw "Request failed (500)" (ss_6989fyo2x). Severity: medium. Correction: catch parser errors and return 400 with a "file could not be read" message. |
| 2.5 | Unsupported file rejection | PASS | `unsupported_file.xyz` → HTTP 400, UI message "Resume must be a PDF, DOCX, or TXT file." (ss_2331xa5s5) |
| 2.6 | Generate package | PASS | Deliverables listed after intake |
| 2.7 | Decision, evidence coverage, deliverables | PASS | Screening decision card, "Resume evidence coverage: NN%", deliverables card all rendered |
| 2.8 | Generated folder & DOCX names | PASS | `candidates/Testperson_Avery_2026-07-16/deliverables/` contains `01_Screening_Summary.docx`, `02_Three_Hour_Interview_Guide.docx`, `03_Interview_Scorecard.docx`, `04_Candidate_Exercise_Sheet.docx` (filesystem-verified) |
| 2.9 | No feedback generated | PASS | "No feedback has been generated." shown; no feedback files in folder |
| 2.10 | UX note | WARN | Deliverable names are clipped in the card ("02_Three_Hour_Interview_G…"), and a stale previous result stays visible under a new error banner. Severity: low. Correction: wrap/expand names; clear result cards when a new submission errors. |

## 3. Finalize interview (`/finalize`)

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 3.1 | Ready candidates in dropdown | PASS | READY_FOR_INTERVIEW candidates listed with status suffix. Note: non-ready (DO_NOT_PROCEED / SECOND_ROUND) candidates are also listed; selecting them is blocked server-side with an explicit message. |
| 3.2 | Sparse notes → missing areas, no final selection | PASS | "Candidate seemed fine. Knows some Java." → "Manual review required", Missing areas: Selenium, REST Assured/API, SQL/Oracle, independent explanation evidence (ss_3623fv79j) |
| 3.3 | Complete notes → permitted decision | PASS | Full multi-domain notes for "Morgan Fictionalfull" → "Decision permitted: Yes", "Missing areas: None reported" (ss_4437be96q) |
| 3.4 | Deliverables appear | PASS | `06_Final_Interview_Evaluation…`, `07_Post_Interview_Commun…` listed (names clipped — same UX note as 2.10) |
| 3.5 | Finalized candidate cannot be silently reset | PASS | Re-finalizing Avery (now SECOND_ROUND) blocked with explicit error: "Candidate status is 'SECOND_ROUND'; finalize requires one of ['INTERVIEW_SCHEDULED','READY_FOR_INTERVIEW']. Run intake first." (ss_0272so957) |

## 4. Question Library (`/library`)

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 4.1 | Reviewed mode loads nonzero records | PASS | "89 reviewed questions · page 1 of 9"; API total 89 |
| 4.2 | Metric strip populated | FAIL | REVIEWED QUESTIONS / REVIEWED EXERCISES / COVERED DOMAINS / OPEN GAPS all render "—" (ss_326983vld). Root cause: page calls `GET /api/knowledge/facets?mode=reviewed` → **404** (endpoint does not exist; confirmed absent from `/openapi.json`). Severity: **high**. Correction: implement `/api/knowledge/facets` (or bind the strip to `/api/knowledge/stats`, which works). |
| 4.3 | Draft mode visibly different | PARTIAL FAIL | Visually distinct (orange border, DRAFT RESEARCH chip, exclusion banner) but data identical to reviewed: `?mode=draft` returns the same 89 items, same first record, while stats report 1899 drafts. Severity: **high**. Correction: honor `mode=draft` in the questions query. |
| 4.4 | Gap mode works | FAIL | "Coverage & Gaps" tab renders the same 89 reviewed questions with no gap analysis; `/api/knowledge/gaps` → 404. Severity: **high**. Correction: implement gaps endpoint + dedicated gap view; show an error state instead of silently reusing reviewed data. |
| 4.5 | Categorical filters populated by API | FAIL | Domain / Subdomain / Level / Priority / Role-track dropdowns contain only "All" — they depend on the 404 facets call. Severity: **high**. Correction: as 4.2. |
| 4.6 | Domain changes subdomain options | FAIL | Impossible — both dropdowns are empty (blocked by 4.5). |
| 4.7 | Counts match results | PASS (list) / FAIL (strip) | List count 89 matches API; strip is blank (4.2). |
| 4.8 | Natural-language search works | FAIL | Query "how do I handle flaky waits in selenium" → chip applied, but result set unchanged (89/89, first result agentic-ai). API confirms: `questions?q=…` ignores `q` (returns 89); `GET /api/knowledge/search?q=selenium+flaky+waits` returns `{"results":[],"items":[]}`. Severity: **high**. Correction: implement `q` filtering / fix search index. |
| 4.9 | P0/P1 filters correct | FAIL | Priority dropdown empty (4.5); cannot filter. Data note: reviewed set has 1×P0, 88×P1. |
| 4.10 | Role filter correct | FAIL | Role-track dropdown empty (4.5). |
| 4.11 | Active chips & Clear All | PASS | Search chip with "×" and "Clear all" both work (verified click) |
| 4.12 | Expand a question | PASS | "Open details" reveals tabs: Interview answer / Interviewer guidance / Follow-ups / Sources / Practice (ss_9834eqn86) |
| 4.13 | Concise + complete answer, scoring guidance, follow-ups, signals | PASS | Concise answer, complete recommended answer, key points, examples, common mistakes, strong/weak signals, red flags, scoring anchors 0–4, knockout relevance, follow-ups all present (ss_1217nvrs5, ss_16621q8gk) |
| 4.14 | Source links absolute + official, open in new tab | FAIL | Sources render as plain text ("mcp-spec — MCP: architecture · verified ·"). Where anchors exist (Ask Zume), href is the page itself. API check across all 89 reviewed questions: `references` = `{source_id, locator}` with **zero** URLs. Severity: **high** (traceability requirement). Correction: add absolute official URLs to reference records and render them as `target="_blank"` links. |
| 4.15 | Bookmark works | PASS | Toggles to highlighted "Remove bookmark" |
| 4.16 | Error and empty states distinguishable | FAIL | The facets 404 renders as dashes (ambiguous), and the gaps tab silently shows reviewed data — a failed/absent API presented as normal results. Severity: medium. Correction: explicit error banners on failed fetches. |
| 4.17 | No failed API call presented as zero results | PASS (narrow) | No case found where a failure rendered as "0 results"; failures render as dashes or fall back to reviewed data (still wrong — see 4.16). |
| 4.18 | Content quality (observation) | WARN | All 89 reviewed questions are one template: "In {domain}, explain the purpose and failure boundary of {topic}…", with near-identical answer text referencing "MCP: {topic}" even for Java/SQL/Selenium topics. The packaged release contains a different, better curated gold library (see §9.6). Severity: high for library credibility, though outside strict UI scope. |

## 5. Practice (`/practice`)

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 5.1 | Records come from reviewed Library | PASS | Questions match reviewed records. Note: session pool is 20 of 89 ("1 OF 20"). |
| 5.2 | Next / previous / random | PASS | Next → 2 OF 20; Previous → 1 OF 20; Random repositions |
| 5.3 | Reveal/hide | PASS | "Reveal answer" ↔ "Hide answer" with suggested approach panel (ss_0564f6ncx) |
| 5.4 | Self-rating persists | PASS | "Getting there" selected on Q1 → Next → Previous → still selected (localStorage-backed, page states rating "stays in this browser") |
| 5.5 | Bookmark | FAIL | No bookmark control exists on the Practice route. Severity: low-medium. Correction: add the bookmark toggle to the practice card. |
| 5.6 | Read aloud play/pause/resume/stop | PASS | Programmatically verified: Play → `speechSynthesis.speaking: true`; Pause → `paused: true`; Resume → `paused: false`; Stop → `speaking: false` |
| 5.7 | Voice / rate / mode controls | PASS | Read-mode select (question/answer/both), 20+ voices, rate slider |
| 5.8 | Empty/unavailable speech state | NOT VERIFIED | Browser voices were available; unavailable state could not be simulated in this session. |
| 5.9 | A11y note | WARN | Confidence radio buttons expose accessible name "on" only. Severity: low. Correction: label radios with their visible text. |

## 6. Interview builder (`/builder`)

Tested via UI (Senior SDET) and `POST /api/interview/preview` for all six required role tracks (plus Lead SDET present in UI).

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 6.1 | 180-minute total | PASS | `agenda_fit_minutes: 180` for all 6 roles; UI "180 minute interview" |
| 6.2 | 20-minute knockout | PASS (count label wrong) | `knockout_minutes: 20`, 6 knockout questions for every role. **Defect:** UI labels the knockout "6 P0 questions" but the library contains exactly 1 P0 question — 5 of 6 are P1. Untruthful label. Severity: medium. Correction: label as "knockout questions" or fix P0 tagging. |
| 6.3 | Role-relevant domain mix | FAIL | All six roles return **byte-identical** domain mixes: java 4, selenium 3, rest-assured 3, sql-oracle 3, api-openapi 3, debugging-reliability 3, agentic-ai 3, ai-for-qa 3, ai-governance 3. Mobile Automation Engineer gets 0 mobile-appium; Performance Engineer 0 performance-observability; QA Manager 0 technical-leadership; AI QA Engineer 0 ai-quality/llm-engineering as mandated. `config/role-policies.yaml` defines correct per-role mandatory cores and knockout domains, but the selector ignores them (appears to always use the default senior-sdet policy). Severity: **critical** for the builder's purpose. Correction: fix role_track → policy resolution in the plan selector and honor `mandatory_core` / `knockout.domains` per policy. |
| 6.4 | Truthful selection reasons | PARTIAL FAIL | Per-question reasons exist ("mandatory-core: required java validation") and match the chosen question's domain, but since the same reasons/mix are emitted for every role they are not truthful role-fit rationales (e.g. "mandatory-core: required java validation" on a Performance Engineer plan contradicts the policy file). |
| 6.5 | Warning when reviewed role coverage insufficient | PASS | "Role coverage: Limited — 0 reviewed role questions" card shown (ss_9954m90fy) |
| 6.6 | Candidate-safe exercises | FAIL (UI) | API returns 4 `candidate_exercises` (titles/tasks only, no answers — content is candidate-safe), but the "CANDIDATE-SAFE EXERCISES" card renders empty (ss_2987ns3u1). Severity: medium. Correction: bind the card to `plan.candidate_exercises`. |
| 6.7 | No raw JSON as primary UI | PASS | Cards and lists throughout; no raw JSON rendered |

## 7. Exercise lab (`/lab`)

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 7.1 | SQL SELECT | PASS | Starter query → exit 0, tabular stdout with fictional rows (Ada Lovelace / Alan Turing, QA) (ss_6027yxyr8) |
| 7.2 | SQL write denial | PASS | `INSERT …` → exit 1, stderr "not authorized" |
| 7.3 | SQL timeout | PASS | Unbounded recursive CTE → exit 1, "Query timeout after 2.5 seconds." |
| 7.4 | API mock success | NOT VERIFIED | Mock API server not running in this environment: `/health` → "Mock API unavailable (URLError). Start training/mock-api or use fixtures." Graceful message confirmed; success path untestable here. |
| 7.5 | API external / alternate-port rejection | PASS | `http://example.com/...` and `127.0.0.1:9999` both rejected: "Only the exact origin http://127.0.0.1:8765 is allowed…" exit 3 |
| 7.6 | Java unavailable/available | PASS / NOT VERIFIED | Unavailable state clear ("enable ZUME_ENABLE_DOCKER_LABS and install Docker", exit 4; dropdown shows "java — unavailable"). Available state untestable (no Docker). |
| 7.7 | Selenium unavailable/available | PASS / NOT VERIFIED | Same pattern, including compose-file hint. |
| 7.8 | Monaco resizing | NOT VERIFIED | Window resize is blocked in this environment (managed window); editor rendered correctly at desktop size with no overflow. |
| 7.9 | Starter exercise selection | WARN | Exercise selectable and runs, but `starter_files: {}` for every exercise — selecting an exercise changes nothing in the editor. Severity: medium. Correction: populate starter files per exercise. |
| 7.10 | Structured output and tests | PARTIAL | Output structured (exit code / stdout / stderr / tests cards). **Tests never populate** — `test_results: []` even when running the chosen exercise (exercise records ship no tests). Severity: medium. Correction: add test specs to reviewed exercises. |
| 7.11 | Exercise/runner data consistency | WARN | Stats report 4 published exercises; lab exposes sql/api/java = 3, selenium runner lists none, yet `selenium-reviewed-exercise-01` exists (cited by Ask Zume). Correction: expose the selenium exercise under its runner. |

## 8. Ask Zume (`/ask`)

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 8.1 | Natural-language Selenium question | PARTIAL FAIL | "How should I handle flaky element waits in Selenium WebDriver?" → "No matching local library records were found…" despite the library containing selenium waiting-strategy content. Retrieval only matches near-literal phrasing ("selenium waiting strategies" works). Same root cause as 4.8 (search). Severity: high. |
| 8.2 | Local answer | PARTIAL | Grounded response returned for literal query, but body contains no substantive answer text — only the grounding preamble and record links (ss_1508jnd1p). Correction: include the matched records' concise answers in the reply. |
| 8.3 | Absolute citations | FAIL | Citation anchors point to `http://127.0.0.1:8787/ask` (self) with `target="_blank"`; no absolute official sources (upstream: reference records have no URLs). Severity: high. |
| 8.4 | Confidence / source mode | PASS | "OFFLINE SOURCES" badge + "Confidence: low · Model: offline" on every reply |
| 8.5 | Web-disabled state | PASS | With "Allow web search" checked, reply still explains web research requires a configured provider; doctor reports `web_search: disabled` |
| 8.6 | Clear history | PASS | Conversation cleared (ss_3644kny2r) |
| 8.7 | Provider error state | PASS (by design) | Provider "not configured" degrades to offline mode with explicit messaging rather than an error. True provider-failure (configured but erroring) NOT VERIFIED — no provider available. |

## 9. Settings & doctor (`/settings`)

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 9.1 | Cards, not raw JSON | PASS | Five cards (OpenAI provider / Web search / TTS / Docker labs / Secrets source) (ss_5255qo6cb) |
| 9.2 | No secret value/prefix/suffix | PASS | Only "external secret source configured"; page states secrets are never displayed; `/api/doctor` exposes no values |
| 9.3 | Cache/history clearing | PASS | "Clear audio cache" → `POST /api/audio/cache/clear` 200; "Clear Ask history" → "Local data cleared." |
| 9.4 | Provider and Docker states accurate | PASS | Cards match `/api/doctor`: provider not configured, web search disabled, TTS browser available, docker labs unavailable |

## 10. Browser engineering validation

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 10.1 | Desktop 1440×900 | PASS (at effective 2400×1111) | All routes rendered without layout breakage; exact 1440×900 could not be forced (see 10.2) |
| 10.2 | Tablet 900×1200 | NOT VERIFIED | `resize_window` accepted but the OS-managed/maximized window did not change (`window.innerWidth` stayed 2400). Environment blocker. |
| 10.3 | Keyboard-only pass | PASS (sampled) | Tab order reaches nav links and controls on `/` and `/library` |
| 10.4 | Focus visibility | PASS | Focused elements show 2.5px solid orange outline (computed style verified) |
| 10.5 | No horizontal overflow | PASS | `scrollWidth <= clientWidth` verified on `/`, `/library`, `/lab`, `/practice` |
| 10.6 | No overlap/clipping | WARN | Deliverable filenames clipped in intake/finalize cards; builder "Selected questions" column extremely long with an empty exercises column beside it (layout imbalance). |
| 10.7 | No console error | PASS | Zero console errors/exceptions across the whole session |
| 10.8 | No failed request / no 4xx/5xx | FAIL | Every `/library` load fires `GET /api/knowledge/facets` → 404 (three modes). One 500 on malformed PDF upload. Severity: high (repeats on a primary route). |
| 10.9 | Loading/error/empty/success states | PARTIAL | Success and some error states good (intake 400, finalize status guard); Library error states poor (4.16) |
| 10.10 | Long content wrapping | PASS | Long questions/answers wrap; no overflow detected |
| 10.11 | Valid accessible names | WARN | 1 unnamed visible control on `/lab`; practice radios named "on"; all other sampled controls named |

## 11. Backend/data validation

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 11.1 | `/api/knowledge/facets` | FAIL | 404 — not implemented (absent from `/openapi.json`), yet called by the UI |
| 11.2 | `/api/knowledge/questions` | PASS (with defects) | 200; `mode=draft` and `q=` parameters ignored (4.3, 4.8) |
| 11.3 | `/api/knowledge/stats` | PASS | 200; internally consistent |
| 11.4 | `/api/knowledge/gaps` | FAIL | 404 — not implemented |
| 11.5 | `/api/interview/preview` | PASS (transport) / FAIL (logic) | POST 200; role policy not applied (6.3) |
| 11.6 | `/api/labs` | PASS | 200; availability flags match doctor |
| 11.7 | `/api/doctor` | PASS | 200; no secret material |
| 11.8 | Displayed counts = API counts | PASS where rendered | Overview 89/1899/4 all match; Library strip renders none (4.2) |
| 11.9 | Every P0 reviewed question inspected | PASS | Exactly 1 P0 (`java-reviewed-01`, java/basic); fields complete |
| 11.10 | 10 questions per reviewed domain | PASS (all 89 inspected) | All 89 records across 20 domains: required fields (question, concise/recommended answer, key points, signals, red flags, follow-ups, references) 100% populated; 89 unique titles; all `published/reviewed`. Domain histogram exactly matches `stats.by_domain`. |
| 11.11 | All reviewed exercises | PASS (with 7.9–7.11 defects) | 4 published; 3 exposed via lab API; all lack starter files and tests |
| 11.12 | All role-policy configurations | FAIL | `config/role-policies.yaml` (7 policies, correct invariants documented) is not honored by the preview API — all roles resolve to one mix (6.3) |

## 12. Package validation

Executed in an isolated Linux sandbox on a copy of the source (user's tree untouched; `main` not modified; nothing merged or tagged).

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 12.1 | Release build runs twice | PASS | `scripts/build_windows_release.py` (frontend `npm ci && npm run build` + deterministic zip) completed twice |
| 12.2 | SHA-256 comparison | PASS | Both builds: `12d1582abbd023b4b724b67bdef008942afd2f84eac168ae6ee561a2f130a3e0` — byte-identical |
| 12.3 | Extract and compare file lists/content | PASS | `diff -rq` of both extractions: zero differences |
| 12.4 | Checked-in release freshness | WARN | `releases/Zume-v1.0.0-Windows.zip.sha256` in the repo is `07b8f7ea…` ≠ current-source build `12d1582a…`. The committed artifact is stale relative to the working tree. Correction: rebuild/republish before release. |
| 12.5 | Secret scan | PASS | No API-key patterns (sk-, AKIA, private keys), no `.env`, no personal emails. "rohan" hits are the documented `C:\AarohanSecrets` path string, not PII. |
| 12.6 | PII / candidate data scan | PASS | No real candidate names or candidate folders in the archive; only the fictional sample package docx. |
| 12.7 | Runtime data scan | FAIL (minor) | 8 `__pycache__` directories with `.pyc` files are shipped inside `src/` (e.g. `src/zume/__pycache__/candidate.cpython-313.pyc`). Severity: low-medium. Correction: exclude `__pycache__`/`*.pyc` in the staging copy. |
| 12.8 | Start extracted package, health + Library smoke | PASS | Extracted package served: `/api/health` → `{"status":"ok","review_mode":true}`, `/` → 200, `questions?mode=reviewed` → total 66 with a fully-populated first record (`gold-api-001`, P0). |
| 12.9 | Data divergence (observation) | WARN → investigate | The packaged `knowledge/` library (66 reviewed "gold" questions, 23 domains, realistic titles like "Safety and idempotency across HTTP methods") differs materially from the 89 templated questions the dev review server serves. The instance under test is not serving the curated content that ships in the release. Correction: confirm which corpus is canonical and align the review server's data source. |

## 13. Rules compliance

- No real candidate data was used for any test action (all test candidates fictional; real-looking records were observed and reported, not opened).
- No secret values inspected or revealed.
- `main` not modified; nothing merged or tagged; builds ran on an isolated copy.
- Screenshots captured only after content loaded; API/DOM evidence used wherever a heading alone would not prove function.

## 14. Priority corrections (ordered)

1. **Implement `/api/knowledge/facets` and `/api/knowledge/gaps`** (or rebind UI) — unblocks Library metric strip, all five categorical filters, domain→subdomain cascading, P0/P1 and role filters, and the gaps tab (4.2, 4.4–4.6, 4.9, 4.10, 10.8, 11.1, 11.4).
2. **Fix role-policy resolution in `/api/interview/preview`** so each role track applies its `mandatory_core`/`knockout.domains` from `config/role-policies.yaml` (6.3, 6.4, 11.12).
3. **Fix knowledge search**: honor `q=` on `/api/knowledge/questions` and make `/api/knowledge/search` return matches; reuse for Ask Zume retrieval (4.8, 8.1).
4. **Honor `mode=draft`** in the questions endpoint (4.3).
5. **Remove real candidate folders from review-mode data** and add an explicit review-mode banner (1.8, 1.9).
6. **Add absolute official source URLs** to question references and render them as links (4.14, 8.3).
7. Return 400 (not 500) for unparseable resume files (2.4).
8. Render `candidate_exercises` in the builder card (6.6); fix "6 P0 questions" knockout label (6.2).
9. Ship starter files + test specs for exercises; expose the selenium exercise (7.9–7.11).
10. Exclude `__pycache__` from the release; rebuild the stale committed zip; reconcile dev data vs packaged gold library (12.4, 12.7, 12.9).

---

`NOT READY — CORRECTIONS REQUIRED`
