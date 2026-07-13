"""Deterministic template provider (manual fallback, no model API required)."""

from __future__ import annotations

import re


class TemplateProvider:
    name = "template"

    def summarize_resume(self, resume_text: str) -> str:
        lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
        head = lines[:4]
        summary = " ".join(head)
        summary = re.sub(r"\s+", " ", summary)
        if len(summary) > 400:
            summary = summary[:397] + "..."
        return summary

    def draft_communication(self, template_body: str, replacements: dict[str, str]) -> str:
        body = template_body
        for key, value in replacements.items():
            body = body.replace(f"[{key}]", value)
        return body
