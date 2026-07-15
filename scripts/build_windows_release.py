"""Build the clean, local-only Zume 1.0 Windows release archive."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


VERSION = "1.0.0"
ROOT = Path(__file__).resolve().parents[1]
STAGING_ROOT = ROOT / "release-staging"
PACKAGE_NAME = f"Zume-v{VERSION}-Windows"
STAGE = STAGING_ROOT / PACKAGE_NAME
RELEASES = ROOT / "releases"
ARCHIVE = RELEASES / f"{PACKAGE_NAME}.zip"
CHECKSUM = ARCHIVE.with_suffix(".zip.sha256")


def run(command: list[str], *, cwd: Path) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def copy_path(relative: str, *, required: bool = True) -> None:
    source = ROOT / relative
    destination = STAGE / relative
    if not source.exists():
        if required:
            raise FileNotFoundError(f"Required release path is missing: {source}")
        return
    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def build_frontend() -> None:
    web = ROOT / "apps" / "web"
    if not web.exists():
        return
    npm = shutil.which("npm.cmd") or shutil.which("npm")
    if npm is None:
        raise RuntimeError("npm is required to build apps/web but was not found on PATH.")
    run([npm, "ci"], cwd=web)
    run([npm, "run", "build"], cwd=web)
    if not (web / "dist" / "index.html").is_file():
        raise RuntimeError("Frontend build completed without apps/web/dist/index.html")


def assert_clean_stage() -> None:
    forbidden = (
        "candidates",
        "input",
        "output",
        "data",
        ".venv",
        "node_modules",
        ".env",
        "release-staging",
        "releases",
    )
    present = [name for name in forbidden if (STAGE / name).exists()]
    if present:
        raise RuntimeError(f"Release staging contains forbidden paths: {', '.join(present)}")
    if list(STAGE.rglob("*.db")) or list(STAGE.rglob("*.sqlite*")):
        raise RuntimeError("Release staging contains a database cache.")


def write_archive() -> None:
    RELEASES.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(STAGE.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(STAGING_ROOT))
    digest = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    CHECKSUM.write_text(f"{digest}  {ARCHIVE.name}\n", encoding="ascii")


def main() -> int:
    build_frontend()
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)

    for relative in (
        "src",
        "config",
        "knowledge",
        "examples/fictional-candidate",
        "docs",
        "training",
        "scripts",
        "apps/web/dist",
        "README.md",
        "CURSOR_START_HERE.md",
        "pyproject.toml",
        "constraints.txt",
        ".gitignore",
    ):
        copy_path(relative)
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "NOTICE", "NOTICE.md", "NOTICE.txt"):
        copy_path(name, required=False)

    assert_clean_stage()
    write_archive()
    print(f"Created {ARCHIVE.relative_to(ROOT)}")
    print(f"Created {CHECKSUM.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"Release build failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
