"""Deterministic release packaging.

Building the same staged tree twice must produce byte-identical ZIP archives:
- entries sorted by normalized arcname;
- fixed timestamp for every entry;
- forward-slash path separators;
- fixed external attributes (0644 files, 0755 dirs);
- fixed compression method and level.
"""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

# Fixed, documented timestamp (release epoch), independent of build machine.
FIXED_DATE_TIME = (2026, 1, 1, 0, 0, 0)
FILE_ATTR = 0o644 << 16
DIR_ATTR = (0o755 << 16) | 0x10


def zip_directory_deterministic(stage: Path, archive_path: Path) -> str:
    """Write a deterministic ZIP of `stage` (rooted at stage.name); return SHA-256."""
    stage = stage.resolve()
    entries = sorted(
        stage.rglob("*"),
        key=lambda p: p.relative_to(stage.parent).as_posix(),
    )
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path, "w") as archive:
        for path in entries:
            arcname = path.relative_to(stage.parent).as_posix()
            if path.is_dir():
                info = zipfile.ZipInfo(arcname + "/", date_time=FIXED_DATE_TIME)
                info.external_attr = DIR_ATTR
                info.compress_type = zipfile.ZIP_STORED
                archive.writestr(info, b"")
            elif path.is_file():
                info = zipfile.ZipInfo(arcname, date_time=FIXED_DATE_TIME)
                info.external_attr = FILE_ATTR
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, path.read_bytes(), compresslevel=9)
    return hashlib.sha256(archive_path.read_bytes()).hexdigest()
