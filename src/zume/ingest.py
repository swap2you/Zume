"""Input ingestion: PDF, DOCX, TXT, pasted text and screenshot metadata."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from docx import Document
from PIL import Image
from pypdf import PdfReader


@dataclass
class ResumeProfile:
    name: str
    experience_years: float | None
    text: str
    skills_mentioned: list[str] = field(default_factory=list)


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    if suffix == ".docx":
        doc = Document(str(path))
        parts = [p.text for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                parts.append(" | ".join(cell.text for cell in row.cells))
        return "\n".join(parts)
    if suffix in {".txt", ".md", ""}:
        return path.read_text(encoding="utf-8", errors="replace")
    raise ValueError(f"Unsupported resume format: {suffix}")


_YEARS_PATTERNS = [
    re.compile(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs)", re.IGNORECASE),
    re.compile(r"(?:experience|exp)\D{0,10}(\d+(?:\.\d+)?)", re.IGNORECASE),
]

_NAME_STOPWORDS = {
    "resume", "curriculum", "vitae", "cv", "profile", "senior", "junior",
    "engineer", "developer", "automation", "sdet", "qa", "lead", "analyst",
}


def parse_name(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        words = re.findall(r"[A-Za-z][A-Za-z'.-]*", line)
        if not words:
            continue
        if any(w.lower() in _NAME_STOPWORDS for w in words):
            continue
        if 1 <= len(words) <= 4:
            return " ".join(words)
        break
    raise ValueError("Could not confidently detect the candidate name; provide --name.")


def parse_experience_years(text: str) -> float | None:
    for pattern in _YEARS_PATTERNS:
        match = pattern.search(text)
        if match:
            value = float(match.group(1))
            if 0 < value < 50:
                return value
    return None


def parse_resume(text: str, name_override: str | None = None) -> ResumeProfile:
    name = name_override or parse_name(text)
    return ResumeProfile(
        name=name,
        experience_years=parse_experience_years(text),
        text=text,
    )


def image_metadata(path: Path) -> dict[str, str]:
    """Read reliable, non-OCR metadata from a screenshot."""
    meta: dict[str, str] = {"file": path.name}
    with Image.open(path) as img:
        meta["format"] = img.format or "unknown"
        meta["size"] = f"{img.width}x{img.height}"
        exif = img.getexif()
        if exif:
            # 306 = DateTime, 36867 = DateTimeOriginal
            for tag in (36867, 306):
                if tag in exif:
                    meta["captured_at"] = str(exif[tag])
                    break
    return meta


def parse_schedule_text(text: str) -> dict[str, str]:
    """Parse `Key: Value` schedule lines from pasted/confirmed text."""
    known = {
        "candidate": "candidate",
        "date": "date",
        "time": "time",
        "duration": "duration",
        "interviewers": "interviewers",
        "interviewer": "interviewers",
        "platform": "platform",
        "meeting": "platform",
        "notes": "notes",
    }
    details: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        mapped = known.get(key.strip().lower())
        if mapped and value.strip():
            details[mapped] = value.strip()
    return details
