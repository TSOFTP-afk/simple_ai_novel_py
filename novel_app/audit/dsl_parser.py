from __future__ import annotations

import re
from typing import Any


class DSLParser:
    _REF_PATTERN = re.compile(r"@([\u4e00-\u9fff\w]+)(?:\.([\u4e00-\u9fff\w]+))?(?:\.([\u4e00-\u9fff\w]+))?")

    def __init__(self, db: Any) -> None:
        self._db = db

    def resolve(self, book_id: int, text: str) -> str:
        if "@" not in text:
            return text

        def _replace(match: re.Match[str]) -> str:
            entity = match.group(1)
            field = match.group(2)
            subfield = match.group(3)
            return self._lookup(book_id, entity, field, subfield) or match.group(0)

        return self._REF_PATTERN.sub(_replace, text)

    def extract_references(self, text: str) -> list[str]:
        refs: set[str] = set()
        for m in self._REF_PATTERN.finditer(text):
            refs.add(m.group(0))
        return list(refs)

    def _lookup(self, book_id: int, entity: str, field: str | None, subfield: str | None) -> str:
        entity_lower = (entity or "").strip().lower()

        if entity_lower in {"角色", "人物", "character", "char"}:
            return self._lookup_character(book_id, field or "")
        if entity_lower in {"世界", "世界观", "world", "setting"}:
            return self._lookup_world_entry(book_id, field or "", subfield or "")
        if entity_lower in {"章节", "chapter"}:
            return self._lookup_chapter(book_id, field or "")
        if entity_lower in {"关系", "relation", "relationship"}:
            return self._lookup_relationship(book_id, field or "")
        if entity_lower in {"伏笔", "hook"}:
            return self._lookup_hooks(book_id)

        char_result = self._lookup_character(book_id, entity)
        if char_result:
            return char_result
        return self._lookup_world_entry(book_id, entity, field or "")

    def _lookup_character(self, book_id: int, name_or_id: str) -> str:
        try:
            characters = self._db.list_characters(book_id)
        except Exception:
            return ""
        target_name = name_or_id.strip()
        for row in characters:
            ch = dict(row) if not isinstance(row, dict) else row
            ch_name = str(ch.get("name", "")).strip()
            if ch_name == target_name or str(ch.get("id", "")) == target_name:
                parts = [f"角色：{ch_name}"]
                role = str(ch.get("role", "") or "").strip()
                if role:
                    parts.append(f"定位：{role}")
                profile = str(ch.get("profile_text", "") or "").strip()
                if profile:
                    parts.append(f"设定：{profile[:300]}")
                return "\n".join(parts)
        for row in characters:
            ch = dict(row) if not isinstance(row, dict) else row
            ch_name = str(ch.get("name", "")).strip()
            if target_name in ch_name:
                parts = [f"角色：{ch_name}"]
                profile = str(ch.get("profile_text", "") or "").strip()
                if profile:
                    parts.append(f"设定：{profile[:200]}")
                return "\n".join(parts)
        return ""

    def _lookup_world_entry(self, book_id: int, name_or_id: str, subfield: str) -> str:
        try:
            entries = self._db.list_world_entries(book_id)
        except Exception:
            return ""
        target = name_or_id.strip()
        for row in entries:
            we = dict(row) if not isinstance(row, dict) else row
            we_name = str(we.get("name", "")).strip()
            if we_name == target or str(we.get("id", "")) == target:
                content = str(we.get("content_text", "") or "").strip()
                category = str(we.get("category", "") or "").strip()
                parts = [f"世界观：{we_name}"]
                if category:
                    parts.append(f"分类：{category}")
                if content:
                    parts.append(f"内容：{content[:500]}")
                return "\n".join(parts)
        return ""

    def _lookup_chapter(self, book_id: int, title_or_id: str) -> str:
        try:
            chapters = self._db.list_chapters(book_id)
        except Exception:
            return ""
        target = title_or_id.strip()
        for row in chapters:
            ch = dict(row) if not isinstance(row, dict) else row
            ch_title = str(ch.get("title", "")).strip()
            if ch_title == target or str(ch.get("id", "")) == target:
                parts = [f"章节：{ch_title}"]
                summary = str(ch.get("summary_text", "") or "").strip()
                if summary:
                    parts.append(f"摘要：{summary[:300]}")
                return "\n".join(parts)
        return ""

    def _lookup_relationship(self, book_id: int, name_or_id: str) -> str:
        try:
            relationships = self._db.list_relationships(book_id)
        except Exception:
            return ""
        target = name_or_id.strip()
        results: list[str] = []
        for row in relationships:
            rel = dict(row) if not isinstance(row, dict) else row
            source = str(rel.get("source_name", "") or "").strip()
            target_name = str(rel.get("target_name", "") or "").strip()
            if target in (source, target_name):
                results.append(f"{source} ←→ {target_name}: {rel.get('relationship_type', '')}")
        if results:
            return "关系：\n" + "\n".join(results[:10])
        return ""

    def _lookup_hooks(self, book_id: int) -> str:
        try:
            from novel_app.truth import TruthManager
            from pathlib import Path
            tm = TruthManager(Path(""), self._db)
            pending = tm.list_pending_hooks(book_id)
            if not pending:
                return "（暂无未回收伏笔）"
            lines = ["待回收伏笔："]
            for h in pending[:10]:
                lines.append(f"- [{h.get('index', '?')}] {h.get('description', '')}")
            return "\n".join(lines)
        except Exception:
            return ""