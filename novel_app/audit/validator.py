from __future__ import annotations

import json
import re
from typing import Any


class OutputValidator:
    _FIELD_SCHEMA: dict[str, dict[str, Any]] = {
        "summary": {"type": str, "required": False, "label": "审计摘要"},
        "overall_score": {"type": int, "required": False, "label": "综合评分"},
        "final_verdict": {"type": str, "required": False, "label": "最终结论", "enum": ["approve", "revise", "reject"]},
        "findings": {"type": list, "required": False, "label": "审计发现"},
        "revised_content": {"type": str, "required": False, "label": "修订正文"},
        "revised_outline": {"type": str, "required": False, "label": "修订大纲"},
        "risk_notes": {"type": str, "required": False, "label": "风险提示"},
        "template_comparison": {"type": str, "required": False, "label": "模板对比"},
    }

    _FINDING_FIELDS: list[tuple[str, type, bool]] = [
        ("agent", str, True),
        ("severity", str, True),
        ("category", str, False),
        ("location_hint", str, False),
        ("quote", str, False),
        ("issue", str, True),
        ("suggestion", str, False),
    ]

    @classmethod
    def validate_review_payload(cls, payload: dict[str, Any]) -> dict[str, Any]:
        cleaned: dict[str, Any] = {}
        for key, schema in cls._FIELD_SCHEMA.items():
            value = payload.get(key)
            if value is None:
                cleaned[key] = cls._default_for_type(schema["type"])
                continue
            if schema["type"] is int:
                try:
                    cleaned[key] = int(value)
                except (ValueError, TypeError):
                    cleaned[key] = cls._str_parse_score(value)
            elif schema["type"] is str:
                cleaned[key] = str(value)
            elif schema["type"] is list:
                if not isinstance(value, list):
                    cleaned[key] = []
                else:
                    cleaned[key] = value
            else:
                cleaned[key] = value

        if cleaned.get("final_verdict"):
            verdict = str(cleaned["final_verdict"]).strip().lower()
            if verdict not in {"approve", "revise", "reject"}:
                cleaned["final_verdict"] = "revise"

        findings = cleaned.get("findings", [])
        if isinstance(findings, list):
            cleaned["findings"] = [cls._validate_finding(f) for f in findings[:35] if isinstance(f, dict)]

        if not cleaned.get("revised_content"):
            cleaned["final_verdict"] = "reject"
            if not cleaned.get("summary"):
                cleaned["summary"] = "AI 未返回有效修订内容"

        return cleaned

    @classmethod
    def _validate_finding(cls, finding: dict[str, Any]) -> dict[str, Any]:
        cleaned: dict[str, Any] = {}
        for field_name, field_type, required in cls._FINDING_FIELDS:
            value = finding.get(field_name, "")
            if field_type is str:
                cleaned[field_name] = str(value) if value else ""
            elif required and not value:
                cleaned[field_name] = ""
        severity = str(cleaned.get("severity", "")).strip().lower()
        cleaned["severity"] = severity
        if severity not in {"high", "medium", "low"}:
            cleaned["severity"] = "low"
        issue = str(cleaned.get("issue", "")).strip()
        suggestion = str(cleaned.get("suggestion", "")).strip()
        if not issue and not suggestion:
            cleaned["severity"] = "low"
            cleaned["issue"] = "(空问题)"
        return cleaned

    @staticmethod
    def _default_for_type(t: type) -> Any:
        if t is str:
            return ""
        if t is int:
            return 0
        if t is list:
            return []
        return None

    @staticmethod
    def _str_parse_score(value: Any) -> int:
        if isinstance(value, (int, float)):
            return int(value)
        try:
            s = str(value)
            nums = re.findall(r"\d+", s)
            if nums:
                return int(nums[0])
        except Exception:
            pass
        return 50

    @staticmethod
    def try_parse_json(text: str) -> dict[str, Any]:
        stripped = text.strip()
        if stripped.startswith("```"):
            stripped = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", stripped)
            stripped = re.sub(r"\s*```$", "", stripped)
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start != -1 and end != -1 and end > start:
            stripped = stripped[start:end + 1]
        return json.loads(stripped)