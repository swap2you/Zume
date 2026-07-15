"""Typed local API routes for the web workspace. No non-local secret exposure."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from zume import candidate as cand
from zume import pipeline
from zume.ai import get_ai_provider
from zume.audio import get_realtime_provider, get_speech_provider
from zume.knowledge.loader import load_all_exercises, load_all_questions
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
    from zume import config as cfg

    return cfg.find_root()


def _safe_candidate_root(root: Path, folder_name: str) -> Path:
    base = cand.candidates_root(root).resolve()
    target = (base / folder_name).resolve()
    if base not in target.parents and target != base:
        raise HTTPException(status_code=400, detail="Path traversal rejected.")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", folder_name):
        raise HTTPException(status_code=400, detail="Invalid candidate folder name.")
    return target


@router.get("/knowledge/search")
def api_knowledge_search(
    q: str = "",
    domain: str | None = None,
    level: str | None = None,
    priority: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    results = knowledge_search(_root(), q, limit=max(1, min(limit, 100)), domain=domain)
    if level:
        results = [r for r in results if r.get("level") == level]
    if priority:
        results = [r for r in results if r.get("priority") == priority]
    return {"results": results}


@router.get("/knowledge/questions")
def api_list_questions(
    domain: str | None = None,
    level: str | None = None,
    priority: str | None = None,
    offset: int = 0,
    limit: int = 50,
) -> dict[str, Any]:
    questions = [q for q in load_all_questions(_root() / "knowledge") if q.status == "published"]
    if domain:
        questions = [q for q in questions if q.domain == domain]
    if level:
        questions = [q for q in questions if q.level == level]
    if priority:
        questions = [q for q in questions if q.priority == priority]
    questions = sorted(questions, key=lambda q: q.id)
    page = questions[offset : offset + max(1, min(limit, 100))]
    return {
        "total": len(questions),
        "offset": offset,
        "items": [
            {
                "id": q.id,
                "title": q.title,
                "domain": q.domain,
                "level": q.level,
                "priority": q.priority,
                "frequency": q.frequency,
                "question": q.question,
                "tags": q.tags,
            }
            for q in page
        ],
    }


@router.get("/knowledge/questions/{question_id}")
def api_get_question(question_id: str) -> dict[str, Any]:
    for q in load_all_questions(_root() / "knowledge"):
        if q.id == question_id:
            return q.model_dump()
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


@router.post("/candidates/finalize")
def api_finalize(body: FinalizeRequest) -> dict[str, Any]:
    try:
        result = pipeline.run_finalize(_root(), body.candidate, body.notes)
    except pipeline.WorkflowError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
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
    _append_chat(root, {"question": body.question, "answer": answer.model_dump()})
    return answer.model_dump()


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
