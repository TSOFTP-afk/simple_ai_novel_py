from __future__ import annotations

import json
from typing import Any, Callable

from novel_app.agents.prompts import (
    AUDITOR_SYSTEM,
    AUDITOR_GENERATION_TEMPLATE,
    AUDITOR_REVIEW_TEMPLATE,
)


class AuditorAgent:
    def __init__(self, post_chat: Callable[..., dict[str, Any]]) -> None:
        self._post_chat = post_chat

    def audit(self, state: Any) -> None:
        content = state.draft or state.current_content
        template = AUDITOR_GENERATION_TEMPLATE if state.draft else AUDITOR_REVIEW_TEMPLATE
        prompt = template.format(
            book_title=state.book_title,
            chapter_title=state.chapter_title,
            outline=state.outline,
            draft=state.draft,
            content=content[:12000],
            truth_file=state.truth_file[:6000],
            sourcebook_context=state.sourcebook_context[:2000],
            template_content=state.template_content[:2000],
        )
        result = self._post_chat(
            messages=[
                {"role": "system", "content": AUDITOR_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.25,
        )
        raw = result["choices"][0]["message"]["content"].strip()
        payload = self._extract_json(raw)
        findings_raw = payload.get("findings", [])
        if not isinstance(findings_raw, list):
            findings_raw = []
        findings: list[dict[str, Any]] = []
        for f in findings_raw[:30]:
            if not isinstance(f, dict):
                continue
            severity = str(f.get("severity", "low")).strip().lower()
            if severity not in {"high", "medium", "low"}:
                severity = "low"
            issue = str(f.get("issue", "")).strip()
            suggestion = str(f.get("suggestion", "")).strip()
            if not issue and not suggestion:
                continue
            findings.append({
                "agent": str(f.get("agent", "auditor")).strip(),
                "severity": severity,
                "category": str(f.get("category", "")).strip(),
                "location_hint": str(f.get("location_hint", "")).strip(),
                "quote": str(f.get("quote", "")).strip(),
                "issue": issue,
                "suggestion": suggestion,
            })
        state.audit_findings = findings
        state.summary = str(payload.get("summary", "")).strip()
        high = sum(1 for f in findings if f["severity"] == "high")
        medium = sum(1 for f in findings if f["severity"] == "medium")
        state.log(f"Auditor 发现 {len(findings)} 个问题 (high={high}, medium={medium})")

    @staticmethod
    def _extract_json(text: str) -> dict[str, Any]:
        import re
        stripped = text.strip()
        if stripped.startswith("```"):
            stripped = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", stripped)
            stripped = re.sub(r"\s*```$", "", stripped)
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start != -1 and end != -1 and end > start:
            stripped = stripped[start:end + 1]
        return json.loads(stripped)