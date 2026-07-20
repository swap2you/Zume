"""Move generated or seed knowledge out of the published interview pool."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
FINGERPRINTS = (
    "should be applied to a stated outcome, observable evidence",
    "start by naming the decision that",
    "what evidence would make you revise your",
    "distinguishes symptom from root cause",
    "recites a tool feature without a decision context",
)


def _records(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ("records", "questions", "exercises", "items"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def _is_generated(record: dict[str, Any]) -> bool:
    blob = " ".join(str(value) for value in record.values()).lower()
    return (
        record.get("quality_origin") == "generated_proposal"
        or record.get("status") == "published"
        or any(fingerprint in blob for fingerprint in FINGERPRINTS)
    )


def main() -> None:
    changed = 0
    files = 0
    for base in (ROOT / "knowledge" / "questions", ROOT / "knowledge" / "exercises"):
        for path in sorted(base.rglob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            records = _records(data)
            file_changed = False
            for record in records:
                if _is_generated(record):
                    record.update(
                        status="draft",
                        review_status="unreviewed",
                        quality_origin="generated_proposal",
                        reviewed_at=None,
                    )
                    changed += 1
                    file_changed = True
            if file_changed:
                path.write_text(
                    yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100),
                    encoding="utf-8",
                )
                files += 1
    print(f"Quarantined {changed} records in {files} files.")


if __name__ == "__main__":
    main()
