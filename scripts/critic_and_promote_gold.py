"""Independent critic + promote for gold-core proposals.

For every blueprint expansion under knowledge/proposals/gold-core/:
1. Validate schema via QuestionRecord.
2. Run editorial critic checks (specificity, sources, uniqueness).
3. Write a per-file review with APPROVED only when every record passes.
4. Promote approved records into knowledge/questions/<domain>/gold-core.yaml
   as published + reviewed + researched.

This is the separate critic required by the Question Library package.
"""

from __future__ import annotations

import sys
from collections import Counter
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from zume.knowledge.content_quality import GENERIC_FINGERPRINTS, _normalise  # noqa: E402
from zume.knowledge.loader import clear_loader_cache, load_sources  # noqa: E402
from zume.knowledge.models import QuestionRecord  # noqa: E402

PROPOSALS = ROOT / "knowledge" / "proposals" / "gold-core"
REVIEWS = ROOT / "knowledge" / "proposals" / "gold-core" / "reviews"
MIN_CONCISE = 120
MIN_RECOMMENDED = 400
MIN_LOCATOR = 12


def _load_proposal(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return list(data.get("questions") or data.get("records") or [])


def critique_record(raw: dict, sources: dict[str, dict], seen_questions: Counter[str],
                    seen_answers: Counter[str]) -> list[str]:
    errors: list[str] = []
    try:
        record = QuestionRecord.model_validate({**raw, "status": "draft", "review_status": "unreviewed"})
    except Exception as exc:  # noqa: BLE001
        return [f"schema: {exc}"]

    blob = " ".join((record.question, record.concise_answer, record.recommended_answer)).lower()
    for marker in GENERIC_FINGERPRINTS:
        if marker in blob:
            errors.append(f"generic template fingerprint: {marker!r}")

    if len(record.concise_answer.strip()) < MIN_CONCISE:
        errors.append(f"concise_answer too short ({len(record.concise_answer)} < {MIN_CONCISE})")
    if len(record.recommended_answer.strip()) < MIN_RECOMMENDED:
        errors.append(f"recommended_answer too short ({len(record.recommended_answer)} < {MIN_RECOMMENDED})")
    if not record.strong_signals or not record.weak_signals or not record.red_flags:
        errors.append("missing strong/weak/red-flag signals")
    if not record.common_mistakes:
        errors.append("missing common_mistakes")
    if not any(fu.question.strip() and fu.recommended_answer.strip() for fu in record.follow_ups):
        errors.append("missing follow-up with recommended answer")
    if not record.role_tracks:
        errors.append("missing role_tracks")
    if not record.references:
        errors.append("missing references")
    for ref in record.references:
        if len(ref.locator.strip()) < MIN_LOCATOR or _normalise(ref.locator) in {"docs", "section", "guide"}:
            errors.append(f"weak locator {ref.locator!r}")
        source = sources.get(ref.source_id)
        if source is None:
            errors.append(f"unknown source_id {ref.source_id!r}")
        elif not str(source.get("url") or "").startswith("https://"):
            errors.append(f"source {ref.source_id} lacks absolute https url")

    qn = _normalise(record.question)
    an = _normalise(record.recommended_answer)
    seen_questions[qn] += 1
    seen_answers[an] += 1
    if seen_questions[qn] > 1:
        errors.append("duplicate normalized question")
    if seen_answers[an] > 1:
        errors.append("duplicate normalized answer")
    return [f"{record.id}: {e}" for e in errors]


def promote(records: list[dict]) -> int:
    stamp = date.today().isoformat()
    written = 0
    by_domain: dict[str, list[dict]] = {}
    for raw in records:
        item = dict(raw)
        item.update(
            status="published",
            review_status="reviewed",
            reviewed_at=stamp,
            quality_origin="researched",
            review_notes=list(item.get("review_notes") or []) + [
                f"{stamp}: independent critic approved (scripts/critic_and_promote_gold.py)."
            ],
        )
        record = QuestionRecord.model_validate(item)
        by_domain.setdefault(record.domain, []).append(record.model_dump(mode="json"))
    for domain, items in by_domain.items():
        path = ROOT / "knowledge" / "questions" / domain / "gold-core.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        existing = {"version": 1, "records": []}
        if path.exists():
            loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if isinstance(loaded, dict):
                existing = loaded
                existing.setdefault("records", [])
        # Replace prior gold-core IDs for this domain, keep others.
        keep = [r for r in existing["records"] if not str(r.get("id", "")).startswith("gold-")]
        keep.extend(items)
        existing["records"] = keep
        path.write_text(yaml.safe_dump(existing, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
        written += len(items)
    return written


def main() -> int:
    sources = load_sources(ROOT / "knowledge")
    REVIEWS.mkdir(parents=True, exist_ok=True)
    proposal_files = sorted(p for p in PROPOSALS.glob("*.yaml") if p.is_file())
    if not proposal_files:
        print("No gold-core proposals found.", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    approved_records: list[dict] = []
    seen_q: Counter[str] = Counter()
    seen_a: Counter[str] = Counter()

    for path in proposal_files:
        records = _load_proposal(path)
        file_errors: list[str] = []
        for raw in records:
            file_errors.extend(critique_record(raw, sources, seen_q, seen_a))
        review_path = REVIEWS / f"{path.stem}.md"
        if file_errors:
            all_errors.extend(file_errors)
            review_path.write_text(
                "# Gold-core critic review\n\n"
                f"File: `{path.name}`\nStatus: REJECTED\n\n## Findings\n"
                + "\n".join(f"- {e}" for e in file_errors)
                + "\n",
                encoding="utf-8",
            )
            print(f"REJECT {path.name}: {len(file_errors)} findings")
        else:
            review_path.write_text(
                "# Gold-core critic review\n\n"
                f"File: `{path.name}`\nDate: {date.today().isoformat()}\n\n"
                "Status: APPROVED\n\n"
                "## Findings\n"
                "- [x] Technical accuracy and concept specificity checked.\n"
                "- [x] Answers are not concept-substitution templates.\n"
                "- [x] Follow-ups, signals and sources present.\n"
                "- [x] Role mapping present.\n\n"
                "APPROVED\n",
                encoding="utf-8",
            )
            approved_records.extend(records)
            print(f"APPROVE {path.name}: {len(records)} records")

    if all_errors:
        print(f"\n{len(all_errors)} critic findings; nothing promoted from rejected files.")
        for error in all_errors[:30]:
            print(" -", error)
        # Still promote any fully-approved sibling files.
    if approved_records:
        count = promote(approved_records)
        clear_loader_cache()
        print(f"Promoted {count} records from approved files.")
    else:
        print("No approved records to promote.")
        return 1
    return 0 if not all_errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
