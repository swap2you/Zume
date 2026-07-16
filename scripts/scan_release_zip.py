"""Scan the Windows release ZIP for forbidden paths and secret-like content."""

from __future__ import annotations

import hashlib
import re
import sys
import zipfile
from pathlib import Path

# Require a plausible key body so detector source code is not flagged.
_AWS_ACCESS_KEY = re.compile(r"AK" + r"IA[0-9A-Z]{16}")
_PRIVATE_KEY_BLOCK = re.compile(r"BEGIN " + r"PRIVATE KEY")


def main() -> int:
    zip_path = Path("releases/Zume-v1.0.0-Windows.zip")
    if not zip_path.exists():
        print("release zip missing", file=sys.stderr)
        return 1
    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    Path("releases/Zume-v1.0.0-Windows.zip.sha256").write_text(
        f"{digest}  {zip_path.name}\n", encoding="utf-8"
    )
    forbidden = (
        "candidates/",
        ".venv",
        "node_modules/",
        "OPENAI_API_KEY",
        "AarohanSecrets",
        "data/chat/",
        "data/audio-cache/",
    )
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        bad = [n for n in names if any(f in n.replace("\\", "/") for f in forbidden)]
        if bad:
            print("forbidden paths in zip:", bad, file=sys.stderr)
            return 1
        for name in names:
            if name.endswith((".py", ".md", ".txt", ".json", ".yml", ".yaml", ".ps1")):
                text = zf.read(name).decode("utf-8", errors="ignore")
                if _PRIVATE_KEY_BLOCK.search(text) or _AWS_ACCESS_KEY.search(text):
                    print(f"secret-like content in {name}", file=sys.stderr)
                    return 1
    print("release scan OK", digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
