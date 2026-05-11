from __future__ import annotations

from typing import Any, Callable

from novel_app.agents.prompts import WRITER_SYSTEM, WRITER_TEMPLATE


class WriterAgent:
    def __init__(self, post_chat: Callable[..., dict[str, Any]]) -> None:
        self._post_chat = post_chat

    def write(self, state: Any) -> None:
        skills = state.selected_skills or []
        skill_text = "\n".join(
            f"- {s.get('name', '')}：{s.get('instruction_text', s.get('instruction', ''))}"
            for s in skills[:8]
        ) if skills else "无"

        prompt = WRITER_TEMPLATE.format(
            book_title=state.book_title,
            chapter_title=state.chapter_title,
            outline=state.outline,
            plan=state.plan,
            current_content=state.current_content[:5000] or "（全新章节）",
            skills=skill_text,
            truth_file=state.truth_file[:6000],
            sourcebook_context=state.sourcebook_context[:3000],
            template_content=state.template_content[:2000],
            style_voices_block=state.style_voices_block[:2000],
        )
        result = self._post_chat(
            messages=[
                {"role": "system", "content": WRITER_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        raw = result["choices"][0]["message"]["content"].strip()
        state.draft = raw
        state.log(f"Writer 生成正文 {len(raw)} 字")