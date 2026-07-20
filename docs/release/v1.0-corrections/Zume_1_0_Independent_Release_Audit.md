# Zume 1.0 Independent Release Audit

## Reviewed target

- Repository: `swap2you/Zume`
- Branch: `release/zume-1.0`
- SHA: `2dcde4bd189d8c11cfbd560193383a1a17012166`
- Draft PR: `#1`
- Baseline: `bdbfbc71b2a129e53fec2dd9ba741e759028d875`

## Independent verdict

**NOT READY — CORRECTIONS REQUIRED**

The release branch is structurally sound and central Python CI is green. The
existing Zume v2 hiring workflow remains broadly protected. The release is not
ready to merge because the expanded library and several web-workspace screens
do not satisfy their stated functional and quality contracts.

This is not a request to redesign the product. Keep the current Python core,
FastAPI shell, React shell, SQLite FTS approach, three-folder candidate contract,
and seven deliverables. Correct the implementation gaps below.

## What is independently verified

- Draft PR is open, mergeable, and not merged.
- Release SHA matches the builder output.
- Central PR CI completed successfully.
- Ubuntu and Windows, Python 3.11 and 3.13 validation jobs passed.
- Pinned reproducible-install job passed.
- Existing Python compile, lint, typing, tests, fictional demo, candidate
  invariants, privacy checks, and package build ran centrally.
- The committed UI screenshot files exist.
- The frontend has a coherent visual system in source: restrained palette,
  keyboard focus outline, skip link, responsive breakpoint, and consistent
  navigation.
- FastAPI binds through the local server helper.
- Candidate workflows still call the existing Zume pipeline.

## Release blockers

### 1. Published knowledge corpus is mainly count-driven template output

The corpus reports 1,899 published questions and 285 published exercises, but
most records are mechanically produced by `scripts/seed_knowledge_library.py`.

The generator applies the same generic answer template, signal lists, mistakes,
follow-up answer, and exercise structure across unrelated concepts and domains.
Representative examples are visible in:

- `knowledge/questions/java/basic.yaml`
- `knowledge/questions/agentic-ai/advanced.yaml`
- `scripts/seed_knowledge_library.py`

Concrete metadata defects already exist:

- `java-b2` asks about exceptions but its follow-up and tags refer to OOP.
- `java-b3` asks about collections but its follow-up and tags refer to String
  immutability.

The present validator proves that fields are populated. It does not prove that
an answer is domain-specific, correct, relevant to the question, source-located,
or editorially reviewed.

**Required correction**

- Automatically generated records must default to `draft`, not `published`.
- Only domain-specific reviewed records may be selected for real interviews.
- Replace generic templates with researched, original, concept-specific content.
- Add content-quality gates for repeated answers, question-answer relevance,
  metadata consistency, source locator specificity, and review status.
- Preserve honest gap reporting. Do not count draft filler as completed coverage.

### 2. Generated filler now enters real candidate interviewer guides

`src/zume/pipeline.py` overlays the expanded knowledge selection into real
candidate interview kits. Therefore library quality is a hiring-workflow issue,
not merely a future preparation-screen issue.

**Required correction**

- Candidate selection may use only reviewed/published records.
- Add a safe fallback to the previously validated curated library when a domain
  lacks enough reviewed records.
- Expanded exercises must be integrated deliberately or excluded; do not claim
  that all 285 exercises drive candidate packages when they do not.

### 3. Candidate-specific selection contains domain and explanation defects

`src/zume/knowledge/selection.py` uses taxonomy names inconsistently:

- `appium` instead of `mobile-appium`
- `performance` instead of `performance-observability`
- `llm-generative` instead of `llm-engineering`

It also labels mandatory domains as “resume-aligned” even when the resume did
not contain them.

**Required correction**

- Use one canonical alias registry.
- Separate `mandatory`, `resume-aligned`, `role-aligned`, and `risk-validation`
  reasons.
- Prove selection for mobile, performance, AI, architecture, leadership,
  strong, conditional, and weak synthetic profiles.
- Preserve selected IDs on rerun and require reasons for rotation.

### 4. Question Library UI is functionally broken

In `apps/web/src/pages/WorkspacePages.tsx`:

- Search expects `items` or `questions`, while `/api/knowledge/search` returns
  `results`; typed search displays no records.
- Priority options are `high/medium/low`, while the data uses `P0/P1/P2/P3`;
  the filter returns no records.
- Required filters are absent.
- Cards show only the question; answers, deep dives, citations, follow-ups,
  bookmarks, and detail expansion are absent.

**Required correction**

Build the Library as a real knowledge browser with typed API contracts and
working filters for domain, subdomain, level, P0-P3, frequency, role, tags,
freshness, question type, and status. Show concise answer, recommended answer,
deep dive, follow-ups, and clickable source citations.

### 5. Practice Session is a hardcoded demo

The screen contains one hardcoded flaky-test question and one hardcoded answer.
It does not draw from the knowledge library.

**Required correction**

Create filter-based study sets, next/previous/random controls, reveal answer,
self-rating, bookmarks, progress, and browser read-aloud.

### 6. Exercise Lab UI cannot call any implemented backend runner

The UI offers `python` and `javascript`. The backend implements only:

- `sql`
- `api`
- `java`
- `selenium`

Every current UI Run action therefore targets an unknown provider and returns
404.

**Required correction**

- Populate runners dynamically from `/api/labs`.
- Load an actual exercise and starter content.
- Use language modes appropriate to SQL, HTTP/JSON, and Java.
- Show capability/unavailable state.
- Do not expose a runner that is not implemented.

### 7. Selenium lab is a declaration, not an executable lab

The Selenium provider returns success with a message telling the user to run
Docker Compose. It never executes submitted code. The compose file lacks an
actual mounted training application and test-run command.

**Required correction**

Implement a minimal real Selenium exercise path or mark Selenium as explicitly
not implemented and remove success claims. For release 1.0, the intended result
is a working Docker smoke against a bundled local page.

### 8. SQL/API/Java lab security controls are incomplete

SQL:

- SQLite connection timeout is not query-execution timeout.
- Modifying SQL is allowed.
- No authorizer or progress-handler cancellation exists.

API:

- Any localhost port is allowed, not only the bundled mock server.
- Redirect handling can escape the original host check.
- This can become local SSRF against other local services.

Java:

- Image is tag-pinned, not digest-pinned.
- No `no-new-privileges` or capability drop.
- On subprocess timeout, the Docker client can die while the container continues.
- No named-container force cleanup.

**Required correction**

- SQL: deny writes and unsafe operations with an authorizer; enforce a deadline
  with `set_progress_handler`; cap output.
- API: allow only the exact configured mock scheme/host/port; disable redirects
  or revalidate every redirect; block loopback alternatives and unexpected ports.
- Java: unique container name, digest/configurable image, capability drop,
  no-new-privileges, forced removal on timeout, cleanup assertion.
- Add malicious/timeout/network/filesystem tests.

### 9. Ask Zume UI drops citations and source metadata

The API returns citations, confidence, source mode, and model. The UI displays
only answer text.

**Required correction**

Render local-record citations and web citations, confidence/source mode, and
offline/web state. Add history clear control and error states.

### 10. OpenAI web-grounding path is not release-grade

The provider asks the model to return JSON but does not enforce a structured
schema. It does not reliably extract native web-search source annotations, and
there are no retry/rate-limit/cancellation tests.

**Required correction**

Recheck the current official OpenAI Responses API documentation during
implementation. Use supported structured output, parse actual source
annotations/citations, and test timeout, retryable status, rate limit,
cancellation, malformed output, and no-citation behavior. Live access remains
optional; mocks are mandatory.

### 11. Browser read-aloud is not implemented in the browser

The backend returns a descriptor saying playback should happen in the browser,
but the React application contains no speech-synthesis implementation or audio
controls.

**Required correction**

Implement `speechSynthesis` controls for question, answer, and queued study set:
play, pause, resume, stop, rate, and voice. Keep OpenAI TTS optional.

### 12. Candidate UI is less capable than the CLI

- Intake accepts text and `.txt/.md`, not PDF/DOCX/TXT.
- Finalize requires manually typing a candidate identifier.
- It does not list ready candidates or preflight missing evidence.

**Required correction**

Use safe multipart upload and the existing ingestion service for PDF/DOCX/TXT.
Populate finalize from ready/scheduled candidates and surface completeness
before confirming finalization.

### 13. Frontend and end-to-end validation is insufficient

- Only two frontend unit tests exist.
- One Playwright test exists.
- The Playwright test skips when the server is absent, allowing a false green.
- Central CI does not install/build/test the frontend.
- Central CI does not run Playwright, knowledge validation, content-quality
  gates, lab isolation tests, or release-ZIP inspection.

**Required correction**

Add central jobs for:

- `npm ci`
- lint
- typecheck
- Vitest
- production build
- start Zume server
- non-skipping Playwright workflows
- accessibility smoke
- knowledge schema/content validation
- lab security tests
- Windows release package scan
- UI screenshot artifact upload
- release-candidate artifact upload without candidate data or secrets

### 14. Screenshot set is not independent visual proof

The screenshots exist, but the builder report itself says keyboard,
accessibility, loading/error states, Monaco resize, most tablet screens, and
Playwright are not verified.

**Required correction**

Generate screenshots through Playwright in clean CI or clean-room validation at
desktop and tablet widths. Upload them as a workflow artifact. The validator
must inspect actual pixels for clipping, overlap, overflow, empty states,
loading/error states, and long content.

### 15. Reports are stale at the final SHA

Some reports retain earlier builder SHAs and pending states, then append later
CI evidence.

**Required correction**

Regenerate all V1 reports from the final corrected SHA. Do not append a second
truth block to stale status tables.

## Additional quality findings

- Remove the external Google Fonts import or bundle fonts locally; the local
  workspace should not make an unnecessary third-party request.
- Replace broad `"latest"` frontend dependency declarations with explicit
  compatible versions and retain `package-lock.json`.
- Update the draft PR checklist with independently verified states.
- The release ZIP is local and Git-ignored, so its contents and checksum still
  need independent validation.

## Required release sequence

1. Keep PR #1 in draft.
2. Apply the correction prompt on `release/zume-1.0`.
3. Run expanded local validation.
4. Push correction commits.
5. Run expanded central CI.
6. Upload UI screenshots and release candidate as safe workflow artifacts.
7. Start a separate clean-room validator in a fresh worktree.
8. Require `READY FOR HUMAN UI REVIEW`.
9. Perform live human/Cowork UI review.
10. Merge and tag only after all gates pass.
