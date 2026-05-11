from __future__ import annotations

from collections.abc import Callable
from threading import Event
from typing import Any

from PyQt6.QtCore import QObject, pyqtSignal

from novel_app.ai_service import SimpleAIService


class AiWorker(QObject):
    chunk = pyqtSignal(str)
    log = pyqtSignal(str)
    done = pyqtSignal(str)
    error = pyqtSignal(str)
    cancelled = pyqtSignal(str)

    def __init__(
        self,
        ai_service: SimpleAIService,
        *,
        mode: str,
        book_title: str,
        chapter_title: str,
        outline: str,
        current_content: str,
        summary_text: str,
        selected_skills: list[dict[str, Any]],
        sourcebook_context: str,
        cancel_event: Event,
        require_remote: bool = True,
    ) -> None:
        super().__init__()
        self.ai_service = ai_service
        self.mode = mode
        self.book_title = book_title
        self.chapter_title = chapter_title
        self.outline = outline
        self.current_content = current_content
        self.summary_text = summary_text
        self.selected_skills = selected_skills
        self.sourcebook_context = sourcebook_context
        self.cancel_event = cancel_event
        self.require_remote = require_remote

    def run(self) -> None:
        label = {
            "draft": "草稿生成",
            "continue": "续写",
            "polish": "润色",
            "summary": "大纲同步",
        }.get(self.mode, self.mode)
        try:
            self.ai_service.clear_last_remote_error()
            self.log.emit(f"开始{label}：{self.chapter_title}")
            if self.mode == "summary":
                result = self.ai_service.summarize_chapter(
                    book_title=self.book_title,
                    chapter_title=self.chapter_title,
                    outline=self.outline,
                    content=self.current_content,
                    require_remote=self.require_remote,
                )
                if self.cancel_event.is_set():
                    self.cancelled.emit(f"{label}已取消。")
                    return
                remote_error = self.ai_service.consume_last_remote_error()
                if remote_error:
                    self.log.emit(remote_error)
                self.chunk.emit(result)
                self.done.emit(f"{label}完成。")
                return

            for chunk in self.ai_service.stream_generate(
                mode=self.mode,
                book_title=self.book_title,
                chapter_title=self.chapter_title,
                outline=self.outline,
                current_content=self.current_content,
                summary_text=self.summary_text,
                selected_skills=self.selected_skills,
                sourcebook_context=self.sourcebook_context,
                cancel_event=self.cancel_event,
                require_remote=self.require_remote,
            ):
                if self.cancel_event.is_set():
                    self.cancelled.emit(f"{label}已取消，当前临时内容未自动保存。")
                    return
                self.chunk.emit(chunk)
            remote_error = self.ai_service.consume_last_remote_error()
            if remote_error:
                self.log.emit(remote_error)
            self.done.emit(f"{label}完成。")
        except Exception as exc:  # noqa: BLE001
            if self.cancel_event.is_set():
                self.cancelled.emit(f"{label}已取消，当前临时内容未自动保存。")
            else:
                self.error.emit(f"{label}失败：{exc}")


class FunctionWorker(QObject):
    done = pyqtSignal(object)
    error = pyqtSignal(str)
    log = pyqtSignal(str)
    cancelled = pyqtSignal(str)

    def __init__(
        self,
        callback: Callable[..., Any],
        pass_logger: bool = False,
        pass_cancel: bool = False,
        cancel_event: Event | None = None,
        deliver_result_on_cancel: bool = False,
    ) -> None:
        super().__init__()
        self.callback = callback
        self.pass_logger = pass_logger
        self.pass_cancel = pass_cancel
        self.cancel_event = cancel_event
        self.deliver_result_on_cancel = deliver_result_on_cancel

    def run(self) -> None:
        try:
            if self.cancel_event and self.cancel_event.is_set() and not self.deliver_result_on_cancel:
                self.cancelled.emit("任务已取消。")
                return
            if self.pass_logger and self.pass_cancel:
                result = self.callback(self.log.emit, self.cancel_event)
            elif self.pass_logger:
                result = self.callback(self.log.emit)
            elif self.pass_cancel:
                result = self.callback(self.cancel_event)
            else:
                result = self.callback()
            if self.cancel_event and self.cancel_event.is_set() and not self.deliver_result_on_cancel:
                self.cancelled.emit("任务已取消，已丢弃未写入结果。")
            else:
                self.done.emit(result)
        except Exception as exc:  # noqa: BLE001
            if self.cancel_event and self.cancel_event.is_set():
                self.cancelled.emit("任务已取消，已丢弃未写入结果。")
            else:
                self.error.emit(str(exc))
