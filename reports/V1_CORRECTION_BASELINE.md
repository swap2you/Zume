# V1 Correction Baseline

Date: 2026-07-16
Starting SHA: `2dcde4bd189d8c11cfbd560193383a1a17012166`
Branch: `release/zume-1.0`
Source: Independent Release Audit (NOT READY — CORRECTIONS REQUIRED)

## Phase 0 reproduction

Command:

```text
pytest -q tests/test_correction_regressions.py
```

Result before corrections: **12 failed, 4 passed**

| Test | Initial |
|------|---------|
| `test_knowledge_search_returns_results_key` | FAIL (no `items` alias) |
| `test_knowledge_questions_accept_p0_priority` | PASS |
| `test_practice_endpoint_returns_library_records` | FAIL (404) |
| `test_lab_runners_are_sql_api_java_selenium_only` | PASS |
| `test_ask_response_includes_citations_and_source_mode` | PASS |
| `test_unconfirmed_join_subject_is_proposed_not_confirmation` | PASS |
| `test_resume_aliases_map_to_canonical_domains` | FAIL |
| `test_selection_reasons_are_truthful` | FAIL |
| `test_published_questions_reject_generic_template_fingerprints` | FAIL |
| `test_java_b2_b3_metadata_matches_question_topic` | FAIL |
| `test_sql_lab_denies_writes_and_times_out` | FAIL |
| `test_api_lab_rejects_wrong_localhost_port_and_redirects` | FAIL |
| `test_java_lab_uses_named_container_and_cleanup_on_timeout` | FAIL |
| `test_playwright_spec_does_not_skip_when_server_down` | FAIL |
| `test_frontend_implements_speech_synthesis_controls` | FAIL |
| `test_knowledge_stats_distinguish_published_and_draft` | FAIL |

Audit defects reproduced. Corrections proceed on this branch without redesign.
