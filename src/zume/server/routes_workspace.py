"""Typed local API routes for the web workspace. No non-local secret exposure."""

from __future__ import annotations

import json
import re
import shutil
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from zume import candidate as cand
from zume import pipeline
from zume.ai import get_ai_provider
from zume.audio import get_realtime_provider, get_speech_provider
from zume.knowledge.enrich import freshness_state as compute_freshness_state
from zume.knowledge.enrich import question_payload
from zume.knowledge.facets import collect_facets
from zume.knowledge.gaps import collect_gaps
from zume.knowledge.loader import load_all_exercises, load_all_questions, load_sources
from zume.knowledge.search import search as knowledge_search
from zume.knowledge.selection import select_interview_plan
from zume.knowledge.stats import collect_stats
from zume.labs import get_lab_provider

router = APIRouter()


class IntakeRequest(BaseModel):
    resume_text: str = ""
    name: str | None = None
    schedule_details: str | None = None


class FinalizeRequest(BaseModel):
    candidate: str
    notes: str


class AskRequest(BaseModel):
    question: str
    enable_web_search: bool = False


class InterviewPreviewRequest(BaseModel):
    role_track: str = "Senior SDET"
    resume_text: str = ""


class LabRunRequest(BaseModel):
    code: str
    exercise_id: str = "ad-hoc"


class SpeakRequest(BaseModel):
    text: str
    mode: str = "question"


def _root() -> Path:
    from zume.server.runtime import current_root

    return current_root()


def _safe_candidate_root(root: Path, folder_name: str) -> Path:
    base = cand.candidates_root(root).resolve()
    target = (base / folder_name).resolve()
    if base not in target.parents and target != base:
        raise HTTPException(status_code=400, detail="Path traversal rejected.")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", folder_name):
        raise HTTPException(status_code=400, detail="Invalid candidate folder name.")
    return target


def _clean(value: str | None) -> str | None:
    """Treat empty query parameters as absent; the UI omits them anyway."""
    if value is None:
        return None
    value = value.strip()
    return value or None


@router.get("/knowledge/facets")
def api_knowledge_facets(mode: str | None = "reviewed") -> dict[str, Any]:
    return collect_facets(_root(), _clean(mode) or "reviewed")


@router.get("/knowledge/gaps")
def api_knowledge_gaps() -> dict[str, Any]:
    return collect_gaps(_root())


@router.get("/knowledge/search")
def api_knowledge_search(
    q: str = "",
    domain: str | None = None,
    subdomain: str | None = None,
    level: str | None = None,
    priority: str | None = None,
    frequency: str | None = None,
    role: str | None = None,
    tags: str | None = None,
    freshness: str | None = None,
    question_type: str | None = None,
    status: str | None = "published",
    limit: int = 20,
) -> dict[str, Any]:
    root = _root()
    results = knowledge_search(root, q, limit=max(1, min(limit, 100)), domain=_clean(domain))
    sources = load_sources(root / "knowledge")
    questions = {
        question.id: question_payload(question, sources)
        for question in load_all_questions(root / "knowledge")
    }
    enriched = [{**questions.get(item["id"], {}), **item, "references": questions.get(item["id"], {}).get("references", [])} for item in results]
    level, priority, subdomain = _clean(level), _clean(priority), _clean(subdomain)
    frequency, role, tags = _clean(frequency), _clean(role), _clean(tags)
    question_type, status = _clean(question_type), _clean(status)
    freshness_raw = _clean(freshness)
    freshness_days = int(freshness_raw) if freshness_raw else None
    results = [
        item for item in enriched
        if (not level or item.get("level") == level)
        and (not priority or item.get("priority") == priority)
        and (not subdomain or item.get("subdomain") == subdomain)
        and (not frequency or item.get("frequency") == frequency)
        and (not role or role in item.get("role_tracks", []))
        and (not tags or tags in item.get("tags", []))
        and (not freshness_days or int(item.get("freshness_days", 0)) <= freshness_days)
        and (not question_type or item.get("question_type") == question_type)
        and (not status or item.get("status") == status)
    ]
    return {"results": results, "items": results, "request_id": uuid.uuid4().hex[:12]}


@router.get("/knowledge/practice")
def api_knowledge_practice(
    limit: int = 20,
    domain: str | None = None,
    level: str | None = None,
) -> dict[str, Any]:
    """Return reviewed published questions with answers for local practice."""
    root = _root()
    questions = [
        q for q in load_all_questions(root / "knowledge")
        if q.status == "published" and q.review_status == "reviewed"
    ]
    if _clean(domain):
        questions = [q for q in questions if q.domain == domain]
    if _clean(level):
        questions = [q for q in questions if q.level == level]
    sources = load_sources(root / "knowledge")
    items = [
        question_payload(q, sources)
        for q in sorted(questions, key=lambda q: q.id)[: max(1, min(limit, 100))]
    ]
    return {"items": items, "results": items}


_PRIORITY_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
_FREQUENCY_RANK = {"very_common": 0, "common": 1, "occasional": 2, "emerging": 3}
_LEVEL_RANK = {"basic": 0, "intermediate": 1, "advanced": 2}


def _sort_questions(questions: list[Any], sort: str) -> list[Any]:
    def by_priority(q: Any) -> tuple[int, str]:
        return (_PRIORITY_RANK.get(q.priority, 4), q.id)

    def by_frequency(q: Any) -> tuple[int, str]:
        return (_FREQUENCY_RANK.get(q.frequency, 4), q.id)

    def by_level_asc(q: Any) -> tuple[int, str]:
        return (_LEVEL_RANK.get(q.level, 3), q.id)

    def by_level_desc(q: Any) -> tuple[int, str]:
        return (-_LEVEL_RANK.get(q.level, 3), q.id)

    def by_domain(q: Any) -> tuple[str, str, str]:
        return (q.domain, q.subdomain, q.id)

    def by_recommended(q: Any) -> tuple[int, int, int, str]:
        return (
            _PRIORITY_RANK.get(q.priority, 4),
            _FREQUENCY_RANK.get(q.frequency, 4),
            _LEVEL_RANK.get(q.level, 3),
            q.id,
        )

    if sort == "recently_verified":
        return sorted(questions, key=lambda q: (q.last_verified, q.id), reverse=True)
    key_fn: Any = {
        "priority": by_priority,
        "frequency": by_frequency,
        "basic_to_advanced": by_level_asc,
        "advanced_to_basic": by_level_desc,
        "domain_az": by_domain,
    }.get(sort, by_recommended)
    return sorted(questions, key=key_fn)


@router.get("/knowledge/questions")
def api_list_questions(  # noqa: PLR0913 — mirrors the documented query contract
    mode: str | None = None,
    q: str | None = None,
    domain: str | None = None,
    subdomain: str | None = None,
    level: str | None = None,
    priority: str | None = None,
    frequency: str | None = None,
    role: str | None = None,
    tag: str | None = None,
    tags: str | None = None,
    freshness: str | None = None,
    freshness_state: str | None = None,
    source_family: str | None = None,
    question_type: str | None = None,
    has_exercise: str | None = None,
    has_followups: str | None = None,
    has_code_example: str | None = None,
    sort: str | None = None,
    status: str | None = "published",
    offset: int = 0,
    limit: int = 50,
) -> dict[str, Any]:
    root = _root()
    all_questions = load_all_questions(root / "knowledge")
    mode = _clean(mode)
    status = _clean(status)
    if mode == "draft":
        questions = [item for item in all_questions if item.status == "draft"]
    elif mode in {"reviewed", "gaps"}:
        questions = [
            item for item in all_questions
            if item.status == "published" and item.review_status == "reviewed"
        ]
    else:
        questions = [item for item in all_questions if (not status or item.status == status)]

    sources = load_sources(root / "knowledge")
    exercise_domains = {
        e.domain for e in load_all_exercises(root / "knowledge")
        if e.status == "published" and e.review_status == "reviewed"
    }

    search_ids: list[str] | None = None
    query = _clean(q)
    if query:
        search_ids = [item["id"] for item in knowledge_search(root, query, limit=200)]
        rank = {qid: pos for pos, qid in enumerate(search_ids)}
        questions = sorted(
            (item for item in questions if item.id in rank), key=lambda item: rank[item.id],
        )

    domain, subdomain, level = _clean(domain), _clean(subdomain), _clean(level)
    priority, frequency, role = _clean(priority), _clean(frequency), _clean(role)
    tag = _clean(tag) or _clean(tags)
    question_type, source_family = _clean(question_type), _clean(source_family)
    freshness_state_filter = _clean(freshness_state)
    freshness_raw = _clean(freshness)
    freshness_days = int(freshness_raw) if freshness_raw else None

    def _matches(item: Any) -> bool:
        if domain and item.domain != domain:
            return False
        if subdomain and item.subdomain != subdomain:
            return False
        if level and item.level != level:
            return False
        if priority and item.priority != priority:
            return False
        if frequency and item.frequency != frequency:
            return False
        if role and role not in item.role_tracks:
            return False
        if tag and tag not in item.tags:
            return False
        if freshness_days and item.freshness_days > freshness_days:
            return False
        if question_type and item.question_type != question_type:
            return False
        if freshness_state_filter and compute_freshness_state(item) != freshness_state_filter:
            return False
        if source_family and not any(
            str(sources.get(ref.source_id, {}).get("family") or "") == source_family
            for ref in item.references
        ):
            return False
        if _clean(has_exercise) == "true" and item.domain not in exercise_domains:
            return False
        if _clean(has_followups) == "true" and not item.follow_ups:
            return False
        if _clean(has_code_example) == "true" and not item.code_examples:
            return False
        return True

    questions = [item for item in questions if _matches(item)]
    if not query:
        questions = _sort_questions(questions, _clean(sort) or "recommended")
    limit = max(1, min(limit, 100))
    page = questions[offset : offset + limit]
    facets_applied = {
        key: value
        for key, value in {
            "mode": mode, "q": query, "domain": domain, "subdomain": subdomain,
            "level": level, "priority": priority, "frequency": frequency, "role": role,
            "tag": tag, "question_type": question_type, "source_family": source_family,
            "freshness_state": freshness_state_filter, "sort": _clean(sort),
        }.items()
        if value
    }
    return {
        "total": len(questions),
        "offset": offset,
        "limit": limit,
        "request_id": uuid.uuid4().hex[:12],
        "facets_applied": facets_applied,
        "items": [
            question_payload(item, sources, exercise_domains=exercise_domains)
            for item in page
        ],
    }


@router.get("/knowledge/questions/{question_id}")
def api_get_question(question_id: str) -> dict[str, Any]:
    root = _root()
    sources = load_sources(root / "knowledge")
    for item in load_all_questions(root / "knowledge"):
        if item.id == question_id:
            return question_payload(item, sources)
    raise HTTPException(status_code=404, detail="Question not found")


@router.get("/candidates")
def api_list_candidates() -> dict[str, Any]:
    root = _root()
    items = []
    base = cand.candidates_root(root)
    if base.exists():
        for folder in sorted(base.iterdir()):
            meta = folder / "_internal" / "candidate.json"
            if meta.exists():
                data = json.loads(meta.read_text(encoding="utf-8"))
                items.append(
                    {
                        "folder": folder.name,
                        "status": data.get("status"),
                        "display_name": data.get("display_name") or data.get("name") or folder.name,
                    }
                )
    return {"items": items}


@router.post("/candidates/intake")
def api_intake(body: IntakeRequest) -> dict[str, Any]:
    if not body.resume_text.strip():
        raise HTTPException(status_code=400, detail="resume_text is required")
    try:
        result = pipeline.run_intake(
            _root(),
            resume_text=body.resume_text,
            name=body.name,
            schedule_details=body.schedule_details,
        )
    except pipeline.WorkflowError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "folder": result.folder.name,
        "status": result.status,
        "decision": result.screening.decision.value,
        "score_percent": result.screening.score_percent,
        "deliverables": result.deliverables,
        "export_zip": str(result.export_zip) if result.export_zip else None,
        "wait_message": pipeline.WAIT_MESSAGE if result.status != pipeline.DO_NOT_PROCEED else None,
        "validation_errors": result.validation_errors,
    }


@router.post("/candidates/intake-upload")
async def api_intake_upload(
    resume: UploadFile = File(...),
    schedule_details: str | None = Form(default=None),
    name: str | None = Form(default=None),
) -> dict[str, Any]:
    """Persist a supported resume temporarily then use the canonical intake pipeline."""
    suffix = Path(resume.filename or "").suffix.lower()
    if suffix not in {".pdf", ".docx", ".txt"}:
        raise HTTPException(status_code=400, detail="Resume must be a PDF, DOCX, or TXT file.")
    payload = await resume.read()
    if not payload:
        raise HTTPException(status_code=400, detail="Uploaded resume is empty.")
    if len(payload) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Uploaded resume exceeds the 20 MB limit.")
    temporary = _root() / "input" / f"upload-{uuid.uuid4().hex}{suffix}"
    temporary.parent.mkdir(parents=True, exist_ok=True)
    temporary.write_bytes(payload)
    try:
        result = pipeline.run_intake(
            _root(), resume_path=temporary, name=name, schedule_details=schedule_details,
        )
    except pipeline.WorkflowError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        temporary.unlink(missing_ok=True)
    return {
        "folder": result.folder.name,
        "status": result.status,
        "decision": result.screening.decision.value,
        "score_percent": result.screening.score_percent,
        "deliverables": result.deliverables,
        "wait_message": pipeline.WAIT_MESSAGE if result.status != pipeline.DO_NOT_PROCEED else None,
        "validation_errors": result.validation_errors,
    }


@router.post("/candidates/finalize")
def api_finalize(body: FinalizeRequest) -> dict[str, Any]:
    try:
        result = pipeline.run_finalize(_root(), body.candidate, body.notes)
    except pipeline.WorkflowError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    # Surface completeness from internal feedback if present.
    feedback_path = result.folder / "_internal" / "feedback.json"
    missing: list[str] = []
    decision_permitted = True
    if feedback_path.exists():
        fb = json.loads(feedback_path.read_text(encoding="utf-8"))
        missing = fb.get("missing_areas") or []
        decision_permitted = bool(fb.get("decision_permitted", True))
    return {
        "folder": result.folder.name,
        "status": result.status,
        "deliverables": result.deliverables,
        "missing_areas": missing,
        "decision_permitted": decision_permitted,
        "export_zip": str(result.export_zip) if result.export_zip else None,
    }


@router.post("/interview/preview")
def api_interview_preview(body: InterviewPreviewRequest) -> dict[str, Any]:
    root = _root()
    plan = select_interview_plan(
        load_all_questions(root / "knowledge"),
        load_all_exercises(root / "knowledge"),
        resume_text=body.resume_text,
        role_track=body.role_track,
        config_root=root,
    )
    # Preview only — never bypasses intake/finalize candidate workflow.
    return {"preview": True, "plan": plan}


@router.post("/ask")
def api_ask(body: AskRequest) -> dict[str, Any]:
    root = _root()
    # Guard: refuse obvious candidate PII payloads to provider context.
    if _looks_like_candidate_pii(body.question):
        raise HTTPException(
            status_code=400,
            detail="Refusing to send candidate PII to Ask Zume. Use the candidate workflow instead.",
        )
    context = knowledge_search(root, body.question, limit=6)
    provider = get_ai_provider()
    from zume.runtime_settings import load_runtime_settings

    settings = load_runtime_settings()
    enable_web = bool(body.enable_web_search and settings.enable_web_search and settings.openai_api_key_configured)
    answer = provider.answer(body.question, context=context, enable_web_search=enable_web)
    payload = answer.model_dump()
    payload["model"] = settings.openai_model if settings.openai_api_key_configured else "offline"
    _append_chat(root, {"question": body.question, "answer": payload})
    return payload


@router.delete("/ask/history")
def api_clear_ask_history() -> dict[str, str]:
    path = _root() / "data" / "chat" / "history.jsonl"
    if path.exists():
        path.unlink()
    return {"status": "cleared"}


@router.post("/labs/{runner}/run")
def api_lab_run(runner: str, body: LabRunRequest) -> dict[str, Any]:
    try:
        provider = get_lab_provider(runner)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    workspace = _root() / "data" / "lab-workspaces" / f"{runner}-{body.exercise_id}"
    if workspace.exists():
        shutil.rmtree(workspace, ignore_errors=True)
    provider.prepare(body.exercise_id, str(workspace))
    result = provider.run(body.exercise_id, str(workspace), body.code)
    provider.cleanup(str(workspace))
    return result.model_dump()


@router.get("/labs")
def api_labs() -> dict[str, Any]:
    from zume.labs import list_lab_capabilities

    return {"labs": [c.model_dump() for c in list_lab_capabilities()]}


@router.get("/labs/exercises")
def api_lab_exercises(runner: str) -> dict[str, Any]:
    """Return safe exercise metadata and starter files for the selected runner."""
    supported = {"sql", "api", "java", "selenium"}
    if runner not in supported:
        raise HTTPException(status_code=400, detail="Unsupported lab runner.")
    items = [
        {
            "id": exercise.id,
            "title": exercise.title,
            "starter_files": exercise.starter_files,
            "runner_type": exercise.runner_type,
        }
        for exercise in load_all_exercises(_root() / "knowledge")
        if exercise.status == "published" and exercise.runner_type == runner
    ]
    return {"items": items}


@router.post("/audio/speak")
def api_speak(body: SpeakRequest) -> dict[str, Any]:
    if _looks_like_candidate_pii(body.text):
        raise HTTPException(status_code=400, detail="Refusing to narrate candidate PII by default.")
    result = get_speech_provider().synthesize(body.text)
    # Do not return raw audio bytes in JSON for large payloads; include disclosure always.
    return {
        "provider": result.provider,
        "ai_generated": result.ai_generated,
        "disclosure": result.disclosure,
        "mime_type": result.mime_type,
        "has_audio": bool(result.audio_bytes),
        "mode": body.mode,
        "browser_playback": result.provider == "browser",
    }


@router.post("/audio/cache/clear")
def api_clear_audio_cache() -> dict[str, str]:
    """The browser speech implementation has no server cache; retain a stable UI endpoint."""
    return {"status": "cleared"}


@router.get("/audio/realtime/session")
def api_realtime_session() -> dict[str, Any]:
    session = get_realtime_provider().create_ephemeral_session()
    # Never include a long-lived API key.
    payload = session.model_dump()
    payload.pop("api_key", None)
    return payload


@router.get("/knowledge/stats")
def api_stats_alias() -> dict[str, Any]:
    return collect_stats(_root())


def _append_chat(root: Path, item: dict[str, Any]) -> None:
    path = root / "data" / "chat" / "history.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(item, ensure_ascii=True) + "\n")


def _looks_like_candidate_pii(text: str) -> bool:
    lowered = text.lower()
    if "resume:" in lowered or "interview notes:" in lowered:
        return True
    if re.search(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", text):
        return True
    if re.search(r"\b\d{3}[-. ]?\d{3}[-. ]?\d{4}\b", text):
        return True
    return False
