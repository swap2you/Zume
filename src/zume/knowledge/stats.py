"""Knowledge library statistics."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any


def collect_stats(root: Path) -> dict[str, Any]:
    knowledge_root = root / "knowledge"
    questions_dir = knowledge_root / "questions"
    exercises_dir = knowledge_root / "exercises"
    if not questions_dir.exists() and not exercises_dir.exists():
        return {
            "available": False,
            "questions": 0,
            "exercises": 0,
            "by_domain": {},
            "by_level": {},
            "by_priority": {},
            "published_questions": 0,
            "draft_questions": 0,
            "reviewed_published_questions": 0,
            "published_exercises": 0,
        }
    from zume.knowledge.loader import load_all_exercises, load_all_questions

    questions = load_all_questions(knowledge_root)
    exercises = load_all_exercises(knowledge_root)
    published_q = [q for q in questions if q.status == "published"]
    draft_q = [q for q in questions if q.status == "draft"]
    reviewed_published_q = [q for q in published_q if q.review_status == "reviewed"]
    published_e = [e for e in exercises if e.status == "published"]
    return {
        "available": True,
        "questions": len(questions),
        "exercises": len(exercises),
        "published_questions": len(published_q),
        "draft_questions": len(draft_q),
        "reviewed_published_questions": len(reviewed_published_q),
        "published_exercises": len(published_e),
        "by_domain": dict(Counter(q.domain for q in published_q)),
        "by_level": dict(Counter(q.level for q in published_q)),
        "by_priority": dict(Counter(q.priority for q in published_q)),
    }
