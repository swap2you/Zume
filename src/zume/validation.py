"""Structural validation for candidate folders and generated DOCX files."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from docx import Document

from zume.candidate import SUBFOLDERS

EXPECTED_SECTIONS = {
    "ATS Screening Report": ["Decision", "Resume evidence coverage — mandatory skills",
                             "Risks and inconsistencies"],
    "Full Interview Guide (3 Hours)": ["Session plan", "Exercises with expected reasoning",
                                       "Scoring per exercise"],
    "Interview Scorecard": ["Skill scores", "Recommendation bands",
                            "Independence observations"],
    "Final Interview Evaluation": ["Decision", "Skill assessment",
                                   "Independence observations (neutral record)"],
    "Interview Schedule": ["Details", "Interviewer preparation checklist"],
}

_PLACEHOLDER = re.compile(r"\[(?:[A-Za-z][A-Za-z ]{2,})\]")


@dataclass
class ValidationReport:
    passed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def merge(self, other: "ValidationReport") -> None:
        self.passed.extend(other.passed)
        self.warnings.extend(other.warnings)
        self.errors.extend(other.errors)


def validate_docx(path: Path) -> ValidationReport:
    report = ValidationReport()
    name = path.name
    try:
        doc = Document(str(path))
    except Exception as exc:  # noqa: BLE001 - report any unreadable document
        report.errors.append(f"{name}: cannot be opened by python-docx ({exc})")
        return report

    paragraphs = [p for p in doc.paragraphs if p.text.strip()]
    if not paragraphs:
        report.errors.append(f"{name}: document body is empty")
        return report

    headings = [p for p in paragraphs
                if p.style is not None and str(p.style.name).startswith(("Heading", "Title"))]
    if not headings:
        report.errors.append(f"{name}: no headings found")
    else:
        report.passed.append(f"{name}: heading hierarchy present ({len(headings)} headings)")

    section = doc.sections[0]
    header_text = " ".join(p.text for p in section.header.paragraphs)
    if "ZUME" not in header_text.upper():
        report.errors.append(f"{name}: Zume header missing")
    else:
        report.passed.append(f"{name}: Zume header present")

    footer_text = " ".join(p.text for p in section.footer.paragraphs)
    footer_xml = section.footer.paragraphs[0]._p.xml if section.footer.paragraphs else ""
    if "Private" not in footer_text:
        report.errors.append(f"{name}: confidentiality footer missing")
    else:
        report.passed.append(f"{name}: confidentiality footer present")
    if "PAGE" not in footer_xml:
        report.errors.append(f"{name}: page-number field missing")
    else:
        report.passed.append(f"{name}: page numbers present")

    title = paragraphs[0].text.strip()
    expected = EXPECTED_SECTIONS.get(title, [])
    if expected:
        heading_texts = {h.text.strip() for h in headings}
        missing = [s for s in expected if s not in heading_texts]
        if missing:
            report.errors.append(f"{name}: missing expected sections: {', '.join(missing)}")
        else:
            report.passed.append(f"{name}: all expected sections present")

    body_text = "\n".join(p.text for p in paragraphs)
    leftovers = sorted(set(_PLACEHOLDER.findall(body_text)))
    if leftovers:
        report.warnings.append(f"{name}: possible unfilled placeholders: {', '.join(leftovers)}")
    else:
        report.passed.append(f"{name}: no unfilled placeholders")
    return report


def find_soffice() -> str | None:
    for name in ("soffice", "soffice.exe"):
        found = shutil.which(name)
        if found:
            return found
    for candidate in (
        Path("C:/Program Files/LibreOffice/program/soffice.exe"),
        Path("C:/Program Files (x86)/LibreOffice/program/soffice.exe"),
    ):
        if candidate.exists():
            return str(candidate)
    return None


def _expected_headings_for(path: Path) -> list[str]:
    try:
        doc = Document(str(path))
    except Exception:  # noqa: BLE001
        return []
    paragraphs = [p for p in doc.paragraphs if p.text.strip()]
    title = paragraphs[0].text.strip() if paragraphs else ""
    return EXPECTED_SECTIONS.get(title, [])


def render_docx(path: Path, soffice: str) -> ValidationReport:
    """Render a DOCX to PDF and verify the rendered content, not just XML.

    Checks: conversion succeeds, page count is nonzero, the document is not empty,
    expected headings appear in the extracted PDF text, header and footer text are
    present, and a page-number value is rendered.
    """
    report = ValidationReport()
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", tmp, str(path)],
            capture_output=True, text=True, timeout=180, check=False,
        )
        rendered = Path(tmp) / (path.stem + ".pdf")
        if result.returncode != 0 or not rendered.exists() or rendered.stat().st_size == 0:
            report.errors.append(
                f"{path.name}: LibreOffice render failed ({result.stderr.strip()[:200]})")
            return report
        report.passed.append(f"{path.name}: rendered to PDF via LibreOffice")
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(rendered))
            page_count = len(reader.pages)
            if page_count == 0:
                report.errors.append(f"{path.name}: rendered PDF has zero pages")
                return report
            report.passed.append(f"{path.name}: rendered PDF has {page_count} page(s)")
            text = "\n".join((p.extract_text() or "") for p in reader.pages)
            if not text.strip():
                report.errors.append(f"{path.name}: rendered PDF has no extractable text")
                return report
            # last page should not be blank (trailing empty page check)
            last = (reader.pages[-1].extract_text() or "").strip()
            if page_count > 1 and not last:
                report.warnings.append(f"{path.name}: last rendered page appears blank")
            if "ZUME" not in text.upper():
                report.warnings.append(f"{path.name}: header text not found in rendered PDF")
            else:
                report.passed.append(f"{path.name}: header text present in rendered PDF")
            if "Private" not in text:
                report.warnings.append(f"{path.name}: footer text not found in rendered PDF")
            else:
                report.passed.append(f"{path.name}: footer text present in rendered PDF")
            missing = [h for h in _expected_headings_for(path) if h not in text]
            if missing:
                report.warnings.append(
                    f"{path.name}: headings not found in rendered PDF: {', '.join(missing)}")
            elif _expected_headings_for(path):
                report.passed.append(f"{path.name}: expected headings present in rendered PDF")
        except Exception as exc:  # noqa: BLE001
            report.warnings.append(f"{path.name}: rendered but PDF inspection failed ({exc})")
    return report


def validate_candidate_folder(folder: Path, render: bool = True) -> ValidationReport:
    report = ValidationReport()
    for sub in SUBFOLDERS:
        if (folder / sub).is_dir():
            report.passed.append(f"folder: {sub} present")
        else:
            report.errors.append(f"folder: {sub} missing")
    audit = folder / "candidate.json"
    if not audit.exists():
        report.errors.append("candidate.json missing")
    else:
        try:
            json.loads(audit.read_text(encoding="utf-8"))
            report.passed.append("candidate.json parses as JSON")
        except json.JSONDecodeError as exc:
            report.errors.append(f"candidate.json is invalid JSON: {exc}")

    docx_files = sorted(p for p in folder.rglob("*.docx") if not p.name.startswith("~$"))
    if not docx_files:
        report.warnings.append("no DOCX artifacts found to validate")
    for doc_path in docx_files:
        report.merge(validate_docx(doc_path))

    soffice = find_soffice()
    if soffice is None:
        report.warnings.append(
            "LibreOffice is not installed; DOCX render verification was skipped. "
            "Install LibreOffice to enable PDF render checks."
        )
    elif render:
        final_docs = sorted((folder / "99-final").glob("*.docx")) or docx_files[:2]
        for doc_path in final_docs:
            report.merge(render_docx(doc_path, soffice))
    return report


def check_privacy(root: Path) -> ValidationReport:
    """Verify that real candidate paths are ignored by Git."""
    report = ValidationReport()
    probes = [
        "candidates/Probe_Test_2026-01-01/candidate.json",
        "input/probe-resume.pdf",
        "output/probe.docx",
        "data/zume.db",
        "General Docs/probe.docx",
    ]
    for probe in probes:
        result = subprocess.run(
            ["git", "check-ignore", "-q", probe],
            cwd=root, capture_output=True, check=False,
        )
        if result.returncode == 0:
            report.passed.append(f"git ignores {probe}")
        elif result.returncode == 1:
            report.errors.append(f"git does NOT ignore {probe}")
        else:
            report.warnings.append(f"git check-ignore unavailable for {probe}")
    return report
