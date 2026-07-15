# Zume 1.0 Acceptance Matrix

The clean-room validator must mark every row PASS, FAIL, or NOT VERIFIED and
attach concrete evidence.

## A. Existing hiring product remains locked

- [ ] Baseline is descended from `bdbfbc71...`.
- [ ] `zume intake` behavior remains compatible.
- [ ] `zume finalize` behavior remains compatible.
- [ ] Three candidate subfolders only.
- [ ] Maximum seven user-facing DOCX deliverables.
- [ ] No `99-final`.
- [ ] No user-visible `__vN`.
- [ ] Candidate sheet contains no recommended answers, solutions, rubrics, or interviewer guidance.
- [ ] Incomplete notes cannot select.
- [ ] Finalized candidate rerun guard remains.
- [ ] Export does not change hiring status.
- [ ] Unconfirmed schedule subject/body are both unconfirmed.
- [ ] 180-minute agenda and 20-minute knockout remain.

## B. Knowledge model and library

- [ ] Canonical taxonomy exists.
- [ ] Question schema validated.
- [ ] Exercise schema validated.
- [ ] All published questions have concise and recommended answers.
- [ ] All follow-ups have answers.
- [ ] All active exercises have full answer sets and tests/rubrics.
- [ ] Stable unique IDs.
- [ ] No unresolved placeholders.
- [ ] No exact duplicates.
- [ ] Near-duplicate rate is documented and acceptable.
- [ ] Priority distribution is reasonable.
- [ ] Frequency labels are calibrated.
- [ ] Technical answers carry source provenance.
- [ ] Current AI/tool facts meet freshness requirements.
- [ ] Source registry resolves.
- [ ] Published content is original paraphrase, not copied question-bank text.
- [ ] FTS index rebuild is deterministic.
- [ ] Search returns relevant results.
- [ ] Gap report exists and does not pretend total completeness.

## C. Domain coverage

For every required domain:

- [ ] basic coverage;
- [ ] intermediate coverage;
- [ ] advanced coverage;
- [ ] P0/P1 coverage;
- [ ] appropriate exercises;
- [ ] role mappings;
- [ ] sources;
- [ ] freshness.

## D. Candidate-specific selection

- [ ] Resume evidence affects selected questions.
- [ ] Knockout uses P0/must-verify questions.
- [ ] Basic/intermediate/advanced progression exists.
- [ ] Selection fits the agenda.
- [ ] Same candidate rerun preserves IDs.
- [ ] Rotation requires a reason.
- [ ] Interview guide contains all selected answers.
- [ ] Candidate sheet remains task-only.
- [ ] Strong, conditional, weak, mobile, performance, AI, architecture, and leadership synthetic profiles produce sensible packages.

## E. Local server and UI

- [ ] `zume serve` starts on localhost.
- [ ] No API key required to start.
- [ ] Health/version/doctor work.
- [ ] Static UI served by same process.
- [ ] Home works.
- [ ] Candidate Intake works.
- [ ] Candidate Finalize works.
- [ ] Question Library filters/search work.
- [ ] Practice Session works.
- [ ] Interview Builder preview works.
- [ ] Exercise Lab works or clearly reports unavailable provider.
- [ ] Ask Zume offline works.
- [ ] Settings/Doctor works.
- [ ] Responsive desktop/tablet.
- [ ] Keyboard navigation.
- [ ] Accessible labels/focus/contrast smoke.
- [ ] Production frontend bundle contains no secret.
- [ ] Path traversal attempts rejected.

## F. Ask Zume

- [ ] Retrieval-first.
- [ ] Local-only answer works without internet.
- [ ] Citations link to library/source records.
- [ ] Optional live search clearly labeled.
- [ ] Web citations visible.
- [ ] Web-source prompt injection ignored.
- [ ] No candidate PII sent in provider payload tests.
- [ ] Timeouts/retries/cancellation.
- [ ] Chat history local and deletable.
- [ ] Provider unavailable state is usable.

## G. Audio and voice

- [ ] Browser read-aloud works without key.
- [ ] Play/pause/resume/stop.
- [ ] Speed/voice selection.
- [ ] Study-set queue.
- [ ] AI-generated voice disclosure for OpenAI speech.
- [ ] Audio cache ignored and deletable.
- [ ] No candidate PII by default.
- [ ] Realtime adapter disabled safely when unavailable.
- [ ] Long-lived key never appears in browser.

## H. Exercise labs

- [ ] Monaco editor loads.
- [ ] SQL lab works.
- [ ] API lab works only against allowed local mock host.
- [ ] Java runner is Docker-isolated.
- [ ] Selenium runner is isolated or clearly optional/unavailable.
- [ ] No external network from runners.
- [ ] Non-root runner.
- [ ] CPU/memory/PID/time limits.
- [ ] Timeout cleanup.
- [ ] No secret/candidate mounts.
- [ ] Malicious sample cannot escape.
- [ ] Runner results are structured.
- [ ] Containers/workspaces cleaned.

## I. Security, privacy, and secrets

- [ ] Candidate/private paths ignored.
- [ ] Runtime data ignored.
- [ ] Tracked text/DOCX secret scan passes.
- [ ] Frontend secret scan passes.
- [ ] `C:\AarohanSecrets` never copied/indexed/logged.
- [ ] Live key is server-side only.
- [ ] Tests use mocks.
- [ ] `zume doctor` reports state, not values.
- [ ] AI calls excluded from candidate workflow by default.
- [ ] Web server binds localhost.
- [ ] No unexpected telemetry.

## J. Testing and release

- [ ] Python compile/lint/type/tests/build pass.
- [ ] Python coverage gate passes.
- [ ] Frontend lint/type/tests/build pass.
- [ ] Playwright passes.
- [ ] Knowledge validation passes.
- [ ] Existing demo passes.
- [ ] DB check passes.
- [ ] DOCX structural validation passes.
- [ ] DOCX rendered validation passes where renderer exists.
- [ ] Central GitHub Actions has visible green runs.
- [ ] Clean-room worktree/clone used.
- [ ] Clean-room validator did not use builder claims as evidence.
- [ ] Windows release zip exists.
- [ ] Zip contains no secret/PII/runtime data.
- [ ] Zip checksum recorded.
- [ ] Draft PR exists.
- [ ] Main not merged and final tag not created before human screen review.
