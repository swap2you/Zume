"""Render the user Markdown guides into polished branded DOCX files.

Run from the repo root:  python scripts/generate_user_docs.py

Keeps `docs/*.md` and `docs/*.docx` in sync. Safe to run in CI.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from zume.config import find_root, load_theme  # noqa: E402
from zume.documents import ZumeDocument  # noqa: E402

GUIDES = [
    ("ZUME_DAILY_USE_GUIDE.md", "Zume_Daily_Use_Guide.docx"),
    ("ZUME_TROUBLESHOOTING_GUIDE.md", "Zume_Troubleshooting_Guide.docx"),
]


def _flush_bullets(doc: ZumeDocument, bullets: list[str]) -> None:
    if bullets:
        doc.bullets(bullets)
        bullets.clear()


def markdown_to_docx(theme: dict, md_path: Path, out_path: Path) -> None:
    lines = md_path.read_text(encoding="utf-8").splitlines()
    title = md_path.stem.replace("_", " ").title()
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    doc = ZumeDocument(theme, title)

    bullets: list[str] = []
    code: list[str] | None = None
    for line in lines:
        if line.startswith("```"):
            if code is None:
                _flush_bullets(doc, bullets)
                code = []
            else:
                doc.code_block("\n".join(code))
                code = None
            continue
        if code is not None:
            code.append(line)
            continue
        if line.startswith("# "):
            continue
        if line.startswith("### "):
            _flush_bullets(doc, bullets)
            doc.heading(line[4:].strip(), 2)
        elif line.startswith("## "):
            _flush_bullets(doc, bullets)
            doc.heading(line[3:].strip(), 1)
        elif line.startswith("- "):
            bullets.append(line[2:].strip())
        elif line.startswith("> "):
            _flush_bullets(doc, bullets)
            doc.banner(line[2:].strip(), kind="info", label="INSTRUCTION")
        elif line.strip():
            _flush_bullets(doc, bullets)
            doc.paragraph(line.strip())
    _flush_bullets(doc, bullets)
    doc.save(out_path, versioned=False)
    print(f"wrote {out_path}")


def main() -> None:
    root = find_root(Path(__file__).resolve().parents[1])
    theme = load_theme(root)
    docs_dir = root / "docs"
    for md_name, docx_name in GUIDES:
        markdown_to_docx(theme, docs_dir / md_name, docs_dir / docx_name)


if __name__ == "__main__":
    main()
