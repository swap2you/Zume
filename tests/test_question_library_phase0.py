"""Phase 0 — Question Library correction regressions.

Each test encodes a binding requirement from the Question Library final
package. They are expected to FAIL against the uncorrected baseline
(fa44f8f) and must pass after the correction phases.
"""

from __future__ import annotations

import hashlib
import os
import time
from pathlib import Path

from fastapi.testclient import TestClient

from zume.knowledge.content_quality import scan_content_quality
from zume.knowledge.loader import load_all_exercises, load_all_questions
from zume.knowledge.search import search as knowledge_search
from zume.knowledge.selection import select_interview_plan
from zume.server.app import create_app

TEMPLATE_FINGERPRINT = "explain the purpose and failure boundary of"


# ---------------------------------------------------------------------------
# 1. Facets endpoint must exist and be generated from actual records
# ---------------------------------------------------------------------------

def test_facets_endpoint_reviewed_mode(repo_root: Path):
    client = TestClient(create_app(repo_root))
    resp = client.get("/api/knowledge/facets", params={"mode": "reviewed"})
    assert resp.status_code == 200, "facets endpoint must exist"
    body = resp.json()
    assert body["mode"] == "reviewed"
    for key in ("questions", "exercises", "domains", "gaps"):
        assert key in body["counts"]
    assert body["domains"], "facets must list reviewed domains"
    first = body["domains"][0]
    assert {"value", "label", "count", "subdomains"} <= set(first)
    assert first["count"] > 0
    for group in ("levels", "priorities", "frequencies", "roles",
                  "question_types", "source_families", "freshness_states", "tags"):
        assert group in body


def test_facets_counts_match_question_list(repo_root: Path):
    client = TestClient(create_app(repo_root))
    facets = client.get("/api/knowledge/facets", params={"mode": "reviewed"}).json()
    domain = facets["domains"][0]
    listed = client.get(
        "/api/knowledge/questions",
        params={"mode": "reviewed", "domain": domain["value"], "limit": 100},
    ).json()
    assert listed["total"] == domain["count"]


# ---------------------------------------------------------------------------
# 2. Question list contract: mode, request_id, tolerated empty parameters
# ---------------------------------------------------------------------------

def test_questions_list_contract_fields(repo_root: Path):
    client = TestClient(create_app(repo_root))
    resp = client.get("/api/knowledge/questions", params={"mode": "reviewed", "limit": 5})
    assert resp.status_code == 200
    body = resp.json()
    for key in ("items", "total", "offset", "limit", "request_id", "facets_applied"):
        assert key in body, f"question list response must include {key}"


def test_empty_query_parameters_are_tolerated(repo_root: Path):
    """The UI omits empty params, but the API must not 422 on them either."""
    client = TestClient(create_app(repo_root))
    resp = client.get(
        "/api/knowledge/questions",
        params={"freshness": "", "level": "", "priority": "", "limit": 5},
    )
    assert resp.status_code == 200, f"empty params must be tolerated, got {resp.status_code}"


# ---------------------------------------------------------------------------
# 3. Reviewed library must contain meaningful, non-template content
# ---------------------------------------------------------------------------

def test_default_reviewed_library_is_meaningful(repo_root: Path):
    client = TestClient(create_app(repo_root))
    resp = client.get("/api/knowledge/questions", params={"mode": "reviewed", "limit": 100})
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert items, "reviewed mode must return records"
    templated = [i["id"] for i in items if TEMPLATE_FINGERPRINT in i["question"].lower()]
    assert not templated, f"reviewed library still contains semantic templates: {templated[:5]}"


def test_content_quality_detects_concept_substitution_templates(repo_root: Path):
    """The gate must flag repeated concept-substitution wording in published content."""
    questions = [
        q for q in load_all_questions(repo_root / "knowledge")
        if q.status == "published" and q.review_status == "reviewed"
    ]
    has_templates = any(TEMPLATE_FINGERPRINT in q.question.lower() for q in questions)
    errors = scan_content_quality(repo_root)
    if has_templates:
        assert any("template" in e.lower() for e in errors), (
            "content-quality gate must detect concept-substitution templates"
        )
    else:
        assert not any("template" in e.lower() for e in errors)


# ---------------------------------------------------------------------------
# 4. Citations must resolve to absolute source URLs
# ---------------------------------------------------------------------------

def test_question_references_resolve_to_absolute_urls(repo_root: Path):
    client = TestClient(create_app(repo_root))
    listed = client.get("/api/knowledge/questions", params={"mode": "reviewed", "limit": 20}).json()
    assert listed["items"]
    checked = 0
    for item in listed["items"]:
        for ref in item.get("references", []):
            assert str(ref.get("source_url", "")).startswith("https://"), (
                f"{item['id']}: reference must carry an absolute https source_url, got {ref}"
            )
            assert ref.get("source_name"), f"{item['id']}: reference must carry source_name"
            checked += 1
    assert checked, "reviewed questions must carry citations"


# ---------------------------------------------------------------------------
# 5. Home counts must distinguish reviewed and draft (backend contract)
# ---------------------------------------------------------------------------

def test_stats_expose_reviewed_and_draft_separately(repo_root: Path):
    client = TestClient(create_app(repo_root))
    stats = client.get("/api/knowledge/stats").json()
    assert "reviewed_published_questions" in stats
    assert "draft_questions" in stats
    assert stats["reviewed_published_questions"] <= stats["questions"]


def test_gaps_endpoint_exists(repo_root: Path):
    client = TestClient(create_app(repo_root))
    resp = client.get("/api/knowledge/gaps")
    assert resp.status_code == 200
    body = resp.json()
    assert "gaps" in body
    assert body.get("complete_claim") is False


# ---------------------------------------------------------------------------
# 6. Role-specific plans must not all be identical
# ---------------------------------------------------------------------------

def test_role_specific_plans_differ(repo_root: Path):
    questions = load_all_questions(repo_root / "knowledge")
    exercises = load_all_exercises(repo_root / "knowledge")
    plans = {
        role: select_interview_plan(
            questions, exercises, role_track=role, config_root=repo_root,
        )
        for role in ("Senior SDET", "QA Manager", "Performance Engineer")
    }
    knockouts = {role: tuple(plan["knockout_question_ids"]) for role, plan in plans.items()}
    assert len(set(knockouts.values())) > 1, (
        f"role tracks must not share one identical knockout: {knockouts}"
    )
    question_sets = {role: tuple(plan["question_ids"]) for role, plan in plans.items()}
    assert len(set(question_sets.values())) > 1, "role tracks must produce distinct plans"


def test_plan_flags_insufficient_reviewed_role_coverage(repo_root: Path):
    questions = load_all_questions(repo_root / "knowledge")
    exercises = load_all_exercises(repo_root / "knowledge")
    plan = select_interview_plan(
        questions, exercises, role_track="Mobile Automation Engineer", config_root=repo_root,
    )
    assert "role_coverage" in plan, "plan must report reviewed role coverage honestly"


# ---------------------------------------------------------------------------
# 7. Natural-language search must have a fallback
# ---------------------------------------------------------------------------

def test_natural_language_search_has_fallback(repo_root: Path):
    results = knowledge_search(repo_root, "What is an explicit wait in Selenium?", limit=10)
    assert results, "natural-language query must fall back instead of returning nothing"
    blob = " ".join(
        f"{r.get('title', '')} {r.get('domain', '')} {r.get('snippet', '')}".lower()
        for r in results
    )
    assert "selenium" in blob or "wait" in blob


# ---------------------------------------------------------------------------
# 8. Release ZIP bytes must be deterministic
# ---------------------------------------------------------------------------

def test_release_zip_bytes_are_deterministic(tmp_path: Path, repo_root: Path):
    import importlib.util

    module_path = repo_root / "scripts" / "package_release.py"
    spec = importlib.util.spec_from_file_location("package_release", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    zip_directory_deterministic = module.zip_directory_deterministic

    stage_a = tmp_path / "a" / "Zume-pkg"
    stage_b = tmp_path / "b" / "Zume-pkg"
    for stage in (stage_a, stage_b):
        (stage / "sub").mkdir(parents=True)
        (stage / "readme.txt").write_text("zume", encoding="utf-8")
        (stage / "sub" / "data.txt").write_text("payload", encoding="utf-8")
    # Different mtimes must not change archive bytes.
    old = time.time() - 86400 * 30
    for file in stage_a.rglob("*"):
        os.utime(file, (old, old))
    zip_a = tmp_path / "a.zip"
    zip_b = tmp_path / "b.zip"
    zip_directory_deterministic(stage_a, zip_a)
    zip_directory_deterministic(stage_b, zip_b)
    assert hashlib.sha256(zip_a.read_bytes()).hexdigest() == \
        hashlib.sha256(zip_b.read_bytes()).hexdigest()
