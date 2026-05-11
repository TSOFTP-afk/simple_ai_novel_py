from __future__ import annotations

from dataclasses import dataclass


@dataclass
class QtAppState:
    selected_book_id: int | None = None
    selected_book_title: str = ""
    selected_volume_id: int | None = None
    selected_chapter_id: int | None = None
    current_node_kind: str = ""
    editor_scope_kind: str | None = None
    editor_scope_id: int | None = None
    editor_dirty: bool = False
    task_running: bool = False
    drawer_kind: str = "details"
    theme_mode: str = "light"

    def clear_selection(self) -> None:
        self.selected_book_id = None
        self.selected_book_title = ""
        self.selected_volume_id = None
        self.selected_chapter_id = None
        self.current_node_kind = ""
        self.editor_scope_kind = None
        self.editor_scope_id = None
        self.editor_dirty = False
