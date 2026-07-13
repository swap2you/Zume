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


def save_candidate(folder: Path, candidate: Candidate) -> None:
    candidate.updated_at = utc_now_iso()
    payload = json.dumps(candidate.model_dump(), indent=2, ensure_ascii=False)
    atomic_write_text(folder / "candidate.json", payload)


def load_candidate(folder: Path) -> Candidate:
    payload = json.loads((folder / "candidate.json").read_text(encoding="utf-8"))
    return Candidate.model_validate(payload)


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
    if direct.is_dir() and (direct / "candidate.json").exists():
        return direct
    base = candidates_root(root)
    exact = base / name_or_folder
    if exact.is_dir() and (exact / "candidate.json").exists():
        return exact
    needle = re.sub(r"[^a-z]", "", name_or_folder.lower())
    matches = []
    if base.is_dir():
        for folder in sorted(base.iterdir(), reverse=True):
            if not (folder / "candidate.json").exists():
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


def copy_source_file(folder: Path, source: Path, kind: str) -> SourceFile:
    """Copy a source file into 00-source without ever overwriting an existing file."""
    target = folder / "00-source" / source.name
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


def record_status(candidate: Candidate, status: str, note: str = "") -> None:
    candidate.status = status
    candidate.status_history.append(StatusEvent(status=status, note=note))


def record_artifact(candidate: Candidate, folder: Path, artifact: Path) -> None:
    rel = str(artifact.relative_to(folder))
    if rel not in candidate.artifacts:
        candidate.artifacts.append(rel)
