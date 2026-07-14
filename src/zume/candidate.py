"""Candidate folder contract, atomic writes and audit records."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
from datetime import date
from pathlib import Path

from zume.models import Candidate, SourceFile, StatusEvent, utc_now_iso

SUBFOLDERS = [
    "00-source",
    "01-screening",
    "02-schedule",
    "03-interview-prep",
    "04-interview",
    "05-feedback",
    "06-communications",
    "99-final",
]

# Phase 2 — simplified three-folder candidate contract (v2).
SOURCE_DIR = "source"
INTERNAL_DIR = "_internal"
DELIVERABLES_DIR = "deliverables"
HISTORY_DIR = "history"  # nested under _internal, git-ignored, opt-in only
CONTRACT_SUBFOLDERS = [SOURCE_DIR, INTERNAL_DIR, DELIVERABLES_DIR]

CANDIDATES_DIR = "candidates"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """Stage to a temp file in the same directory, then atomically replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=".zume-tmp-")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(tmp_name, path)
    except BaseException:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
        raise


def atomic_write_text(path: Path, text: str) -> None:
    atomic_write_bytes(path, text.encode("utf-8"))


def versioned_write_bytes(path: Path, data: bytes) -> bool:
    """Write with versioning.

    If the target exists with identical content, skip. If content differs,
    archive the previous file as <stem>__vN<suffix> before replacing.
    Returns True when the file was (re)written.
    """
    if path.exists():
        if sha256_file(path) == sha256_bytes(data):
            return False
        version = 1
        while True:
            archive = path.with_name(f"{path.stem}__v{version}{path.suffix}")
            if not archive.exists():
                break
            version += 1
        shutil.copy2(path, archive)
    atomic_write_bytes(path, data)
    return True


def normalize_name(raw: str) -> tuple[str, str]:
    """Split a raw display name into (first, last)."""
    cleaned = re.sub(r"[^A-Za-z\s'-]", " ", raw).strip()
    parts = [p for p in cleaned.split() if p]
    if not parts:
        raise ValueError(f"Cannot derive a candidate name from: {raw!r}")
    if len(parts) == 1:
        return parts[0].title(), "Unknown"
    return " ".join(parts[:-1]).title(), parts[-1].title()


def folder_name_for(first: str, last: str, on_date: date | None = None) -> str:
    stamp = (on_date or date.today()).isoformat()
    safe_first = first.replace(" ", "")
    safe_last = last.replace(" ", "")
    return f"{safe_last}_{safe_first}_{stamp}"


def candidates_root(root: Path) -> Path:
    return root / CANDIDATES_DIR


def create_candidate_folder(root: Path, folder_name: str) -> Path:
    folder = candidates_root(root) / folder_name
    for sub in SUBFOLDERS:
        (folder / sub).mkdir(parents=True, exist_ok=True)
    return folder


def create_package_folder(root: Path, folder_name: str) -> Path:
    """Create the v2 three-folder contract: source/_internal/deliverables."""
    folder = candidates_root(root) / folder_name
    for sub in CONTRACT_SUBFOLDERS:
        (folder / sub).mkdir(parents=True, exist_ok=True)
    return folder


def candidate_json_path(folder: Path) -> Path:
    """Return the candidate.json location, preferring the v2 _internal location
    but staying readable for legacy folders that store it at the root."""
    internal = folder / INTERNAL_DIR / "candidate.json"
    if internal.exists():
        return internal
    root_level = folder / "candidate.json"
    if root_level.exists():
        return root_level
    return internal


def save_candidate(folder: Path, candidate: Candidate) -> None:
    candidate.updated_at = utc_now_iso()
    payload = json.dumps(candidate.model_dump(), indent=2, ensure_ascii=False)
    if candidate.contract_version >= 2 or (folder / INTERNAL_DIR).is_dir():
        atomic_write_text(folder / INTERNAL_DIR / "candidate.json", payload)
    else:
        atomic_write_text(folder / "candidate.json", payload)


def load_candidate(folder: Path) -> Candidate:
    payload = json.loads(candidate_json_path(folder).read_text(encoding="utf-8"))
    return Candidate.model_validate(payload)


def has_candidate(folder: Path) -> bool:
    return (folder / INTERNAL_DIR / "candidate.json").exists() or \
        (folder / "candidate.json").exists()


def new_candidate(root: Path, display_name: str, on_date: date | None = None) -> tuple[Candidate, Path]:
    first, last = normalize_name(display_name)
    folder_name = folder_name_for(first, last, on_date)
    folder = create_candidate_folder(root, folder_name)
    if (folder / "candidate.json").exists():
        return load_candidate(folder), folder
    candidate = Candidate(
        first_name=first,
        last_name=last,
        display_name=f"{first} {last}",
        folder_name=folder_name,
        created_date=(on_date or date.today()).isoformat(),
        status_history=[StatusEvent(status="RECEIVED", note="Candidate record created")],
    )
    save_candidate(folder, candidate)
    return candidate, folder


def resolve_candidate(root: Path, name_or_folder: str) -> Path:
    """Resolve a candidate reference to an existing folder path."""
    direct = Path(name_or_folder)
    if direct.is_dir() and has_candidate(direct):
        return direct
    base = candidates_root(root)
    exact = base / name_or_folder
    if exact.is_dir() and has_candidate(exact):
        return exact
    needle = re.sub(r"[^a-z]", "", name_or_folder.lower())
    matches = []
    if base.is_dir():
        for folder in sorted(base.iterdir(), reverse=True):
            if not has_candidate(folder):
                continue
            haystack = re.sub(r"[^a-z]", "", folder.name.lower())
            if needle and needle in haystack:
                matches.append(folder)
                continue
            candidate = load_candidate(folder)
            display = re.sub(r"[^a-z]", "", candidate.display_name.lower())
            if needle and (needle in display or display in needle):
                matches.append(folder)
    if not matches:
        raise FileNotFoundError(f"No candidate folder found for {name_or_folder!r}")
    return matches[0]


def new_package_candidate(root: Path, display_name: str,
                          on_date: date | None = None) -> tuple[Candidate, Path]:
    """Create (or load) a candidate using the v2 three-folder contract."""
    first, last = normalize_name(display_name)
    folder_name = folder_name_for(first, last, on_date)
    folder = create_package_folder(root, folder_name)
    if has_candidate(folder):
        return load_candidate(folder), folder
    candidate = Candidate(
        first_name=first,
        last_name=last,
        display_name=f"{first} {last}",
        folder_name=folder_name,
        created_date=(on_date or date.today()).isoformat(),
        contract_version=2,
        status_history=[StatusEvent(status="RECEIVED", note="Candidate record created")],
    )
    save_candidate(folder, candidate)
    return candidate, folder


def copy_source_file(folder: Path, source: Path, kind: str,
                     subdir: str = "00-source") -> SourceFile:
    """Copy a source file into the source folder without ever overwriting."""
    target = folder / subdir / source.name
    if target.exists() and sha256_file(target) != sha256_file(source):
        version = 1
        while True:
            alt = target.with_name(f"{target.stem}__v{version}{target.suffix}")
            if not alt.exists():
                target = alt
                break
            version += 1
    if not target.exists():
        atomic_write_bytes(target, source.read_bytes())
    return SourceFile(
        original_name=source.name,
        stored_path=str(target.relative_to(folder)),
        sha256=sha256_file(target),
        kind=kind,
    )


def export_candidate(root: Path, folder: Path, export_dir_name: str = "output") -> Path:
    """Zip a candidate folder into the git-ignored export directory."""
    export_dir = root / export_dir_name
    export_dir.mkdir(parents=True, exist_ok=True)
    base = export_dir / f"{folder.name}_package"
    archive_str = shutil.make_archive(str(base), "zip", root_dir=folder)
    return Path(archive_str)


def archive_candidate(root: Path, folder: Path, archive_subdir: str = "_archive") -> Path:
    """Move a candidate folder under candidates/<archive_subdir> (stays git-ignored)."""
    archive_root = candidates_root(root) / archive_subdir
    archive_root.mkdir(parents=True, exist_ok=True)
    target = archive_root / folder.name
    if target.exists():
        stamp = utc_now_iso().replace(":", "").replace("-", "")
        target = archive_root / f"{folder.name}__{stamp}"
    shutil.move(str(folder), str(target))
    return target


LEGACY_SUBFOLDERS = ["00-source", "01-screening", "02-schedule", "03-interview-prep",
                     "04-interview", "05-feedback", "06-communications", "99-final"]

# Legacy internal files mapped to their v2 _internal names.
_LEGACY_INTERNAL_MAP = {
    "01-screening/screening.json": "screening.json",
    "02-schedule/schedule.json": "schedule.json",
    "03-interview-prep/interview-kit.json": "interview-plan.json",
    "04-interview/interviewer-notes.txt": "interviewer-notes.txt",
    "05-feedback/feedback.json": "feedback.json",
}


def is_legacy_folder(folder: Path) -> bool:
    if (folder / INTERNAL_DIR / "candidate.json").exists():
        return False
    return (folder / "candidate.json").exists() and any(
        (folder / sub).is_dir() for sub in LEGACY_SUBFOLDERS)


def plan_migration(folder: Path) -> dict[str, list[str]]:
    """Preview a legacy -> v2 migration. Never plans deletion of source files."""
    plan: dict[str, list[str]] = {"move": [], "merge": [], "retain": [], "remove": []}
    if not is_legacy_folder(folder):
        plan["retain"].append("Folder already uses the v2 contract; nothing to migrate.")
        return plan
    src = folder / "00-source"
    if src.is_dir():
        for item in sorted(src.iterdir()):
            plan["move"].append(f"00-source/{item.name} -> source/{item.name}")
    plan["merge"].append("candidate.json -> _internal/candidate.json (contract_version=2)")
    for legacy, target in _LEGACY_INTERNAL_MAP.items():
        if (folder / legacy).exists():
            plan["move"].append(f"{legacy} -> _internal/{target}")
    final = folder / "99-final"
    if final.is_dir():
        for item in sorted(final.glob("*")):
            plan["remove"].append(f"99-final/{item.name} (redundant final copy)")
    for legacy_file in sorted(folder.rglob("*__v[0-9]*")):
        plan["remove"].append(f"{legacy_file.relative_to(folder)} (versioned copy)")
    return plan


def apply_migration(folder: Path) -> dict[str, list[str]]:
    """Apply the migration. Source files are moved (never deleted)."""
    done: dict[str, list[str]] = {"moved": [], "removed": []}
    if not is_legacy_folder(folder):
        return done
    for sub in CONTRACT_SUBFOLDERS:
        (folder / sub).mkdir(parents=True, exist_ok=True)
    src = folder / "00-source"
    if src.is_dir():
        for item in sorted(src.iterdir()):
            if item.is_file():
                shutil.move(str(item), str(folder / SOURCE_DIR / item.name))
                done["moved"].append(item.name)
    candidate = load_candidate(folder)
    candidate.contract_version = 2
    for legacy, target in _LEGACY_INTERNAL_MAP.items():
        source_file = folder / legacy
        if source_file.exists():
            (folder / INTERNAL_DIR).mkdir(parents=True, exist_ok=True)
            shutil.move(str(source_file), str(folder / INTERNAL_DIR / target))
            done["moved"].append(legacy)
    save_candidate(folder, candidate)
    old_root_json = folder / "candidate.json"
    if old_root_json.exists() and (folder / INTERNAL_DIR / "candidate.json").exists():
        old_root_json.unlink()
        done["removed"].append("candidate.json (moved to _internal)")
    final = folder / "99-final"
    if final.is_dir():
        for item in sorted(final.glob("*")):
            if item.is_file():
                item.unlink()
                done["removed"].append(f"99-final/{item.name}")
        final.rmdir()
    for legacy_file in sorted(folder.rglob("*__v[0-9]*")):
        if legacy_file.is_file():
            legacy_file.unlink()
            done["removed"].append(str(legacy_file.relative_to(folder)))
    return done


def plan_cleanup(folder: Path) -> list[str]:
    """List redundant __vN and 99-final artifacts a cleanup would remove."""
    targets: list[str] = []
    final = folder / "99-final"
    if final.is_dir():
        targets.extend(f"99-final/{p.name}" for p in sorted(final.glob("*")) if p.is_file())
    targets.extend(str(p.relative_to(folder)) for p in sorted(folder.rglob("*__v[0-9]*"))
                   if p.is_file())
    return targets


def apply_cleanup(folder: Path) -> list[str]:
    removed: list[str] = []
    for rel in plan_cleanup(folder):
        path = folder / rel
        if path.exists():
            path.unlink()
            removed.append(rel)
    final = folder / "99-final"
    if final.is_dir() and not any(final.iterdir()):
        final.rmdir()
    return removed


def record_status(candidate: Candidate, status: str, note: str = "") -> None:
    candidate.status = status
    candidate.status_history.append(StatusEvent(status=status, note=note))


def record_status_once(candidate: Candidate, status: str, note: str = "") -> bool:
    """Idempotent status update (Phase 15): set current status, but only append
    a history event when the most recent event differs in status or note."""
    candidate.status = status
    history = candidate.status_history
    if history and history[-1].status == status and history[-1].note == note:
        return False
    history.append(StatusEvent(status=status, note=note))
    return True


def deliverables_dir(folder: Path) -> Path:
    path = folder / DELIVERABLES_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_deliverable(folder: Path, name: str, data: bytes,
                      keep_history: bool = False) -> Path:
    """Write a deliverable, replacing the current file atomically.

    No user-visible ``__vN`` copies are ever produced. When ``keep_history`` is
    explicitly enabled, the previous bytes are snapshotted into the git-ignored
    ``_internal/history/`` folder (disabled by default)."""
    target = deliverables_dir(folder) / name
    if keep_history and target.exists() and sha256_file(target) != sha256_bytes(data):
        stamp = utc_now_iso().replace(":", "").replace("-", "")
        snapshot = folder / INTERNAL_DIR / HISTORY_DIR / f"{target.stem}__{stamp}{target.suffix}"
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_bytes(snapshot, target.read_bytes())
    atomic_write_bytes(target, data)
    return target


def clean_deliverables(folder: Path, keep: set[str]) -> list[str]:
    """Remove deliverables no longer applicable (e.g. schedule doc when there is
    no schedule). Returns the names removed."""
    removed: list[str] = []
    target = folder / DELIVERABLES_DIR
    if not target.is_dir():
        return removed
    for item in target.iterdir():
        if item.is_file() and item.name not in keep:
            item.unlink()
            removed.append(item.name)
    return removed


def export_deliverables(root: Path, folder: Path, export_dir_name: str = "output",
                        include_source: bool = False,
                        include_internal: bool = False) -> Path:
    """Phase 14 — export a clean, deliverables-only ZIP by default."""
    export_dir = root / export_dir_name
    export_dir.mkdir(parents=True, exist_ok=True)
    staging = tempfile.mkdtemp(prefix=".zume-export-")
    try:
        staging_path = Path(staging)
        deliverables = folder / DELIVERABLES_DIR
        if deliverables.is_dir():
            shutil.copytree(deliverables, staging_path / DELIVERABLES_DIR)
        if include_source and (folder / SOURCE_DIR).is_dir():
            shutil.copytree(folder / SOURCE_DIR, staging_path / SOURCE_DIR)
        if include_internal and (folder / INTERNAL_DIR).is_dir():
            shutil.copytree(folder / INTERNAL_DIR, staging_path / INTERNAL_DIR,
                            ignore=shutil.ignore_patterns(HISTORY_DIR))
        _write_package_readme(staging_path / "PACKAGE_README.txt")
        base = export_dir / f"{folder.name}_package"
        archive_str = shutil.make_archive(str(base), "zip", root_dir=staging_path)
        return Path(archive_str)
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def _write_package_readme(path: Path) -> None:
    text = (
        "Zume candidate package\n"
        "======================\n\n"
        "INTERVIEWER-ONLY (never share with the candidate):\n"
        "  01_Screening_Summary.docx\n"
        "  02_Three_Hour_Interview_Guide.docx  (contains recommended answers + solutions)\n"
        "  03_Interview_Scorecard.docx\n"
        "  05_Schedule_and_Communications.docx\n"
        "  06_Final_Interview_Evaluation.docx\n"
        "  07_Post_Interview_Communications.docx\n\n"
        "CANDIDATE-SHAREABLE:\n"
        "  04_Candidate_Exercise_Sheet.docx  (tasks only, no answers)\n"
    )
    atomic_write_text(path, text)


def record_artifact(candidate: Candidate, folder: Path, artifact: Path) -> None:
    rel = str(artifact.relative_to(folder))
    if rel not in candidate.artifacts:
        candidate.artifacts.append(rel)
