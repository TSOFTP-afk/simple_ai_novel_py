from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from threading import Event
from typing import Any

from PyQt6.QtCore import QObject, QThread, QTimer, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from novel_app.ai_service import SimpleAIService


class ChatStreamWorker(QObject):
    chunk = pyqtSignal(str)
    done = pyqtSignal(str)
    error = pyqtSignal(str)
    cancelled = pyqtSignal()

    def __init__(
        self,
        ai_service: SimpleAIService,
        messages: list[dict[str, str]],
        cancel_event: Event,
    ) -> None:
        super().__init__()
        self.ai_service = ai_service
        self.messages = messages
        self.cancel_event = cancel_event

    def run(self) -> None:
        collected: list[str] = []
        try:
            for chunk in self.ai_service.stream_chat(self.messages, self.cancel_event, require_remote=True):
                if self.cancel_event.is_set():
                    self.cancelled.emit()
                    return
                collected.append(chunk)
                self.chunk.emit(chunk)
            self.done.emit("".join(collected))
        except Exception as exc:  # noqa: BLE001
            if self.cancel_event.is_set():
                self.cancelled.emit()
            else:
                self.error.emit(str(exc))


class ChatDialog(QDialog):
    def __init__(
        self,
        parent: QWidget,
        ai_service: SimpleAIService,
        context_builder: Callable[[dict[str, Any] | None], str],
        character_provider: Callable[[], list[dict[str, Any]]] | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("AI 对话")
        self.setModal(False)
        self.resize(720, 640)
        self.ai_service = ai_service
        self.context_builder = context_builder
        self.character_provider = character_provider
        self.chat_history: list[dict[str, str]] = []
        self.current_thread: QThread | None = None
        self.current_worker: ChatStreamWorker | None = None
        self.cancel_event: Event | None = None
        self.pending_text = ""
        self.current_ai_label: QLabel | None = None
        self.close_after_cancel = False

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        role_row = QHBoxLayout()
        role_row.addWidget(QLabel("对话身份"))
        self.character_combo = QComboBox()
        self.character_combo.setMinimumWidth(220)
        self.character_combo.currentIndexChanged.connect(self._on_character_changed)
        role_row.addWidget(self.character_combo, 1)
        root.addLayout(role_row)
        self.refresh_characters()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.messages_host = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_host)
        self.messages_layout.setContentsMargins(4, 4, 4, 4)
        self.messages_layout.setSpacing(10)
        self.messages_layout.addStretch(1)
        self.scroll_area.setWidget(self.messages_host)
        root.addWidget(self.scroll_area, 1)

        input_box = QFrame()
        input_box.setObjectName("Card")
        input_layout = QVBoxLayout(input_box)
        input_layout.setContentsMargins(10, 10, 10, 10)
        self.input_editor = QPlainTextEdit()
        self.input_editor.setPlaceholderText("输入你想问 AI 或角色的问题... (Enter 发送)")
        self.input_editor.setMaximumHeight(108)
        self.input_editor.installEventFilter(self)
        input_layout.addWidget(self.input_editor)

        buttons = QHBoxLayout()
        clear_btn = QPushButton("清空历史")
        self.cancel_btn = QPushButton("取消回复")
        self.send_btn = QPushButton("发送")
        clear_btn.clicked.connect(self.clear_history)
        self.cancel_btn.clicked.connect(self.cancel_reply)
        self.send_btn.clicked.connect(self.send_message)
        self.cancel_btn.setEnabled(False)
        buttons.addWidget(clear_btn)
        buttons.addStretch(1)
        buttons.addWidget(self.cancel_btn)
        buttons.addWidget(self.send_btn)
        input_layout.addLayout(buttons)
        root.addWidget(input_box)

        self.flush_timer = QTimer(self)
        self.flush_timer.setInterval(50)
        self.flush_timer.timeout.connect(self._flush_pending_text)

    def update_ai_service(self, ai_service: SimpleAIService) -> None:
        self.ai_service = ai_service

    def refresh_characters(self) -> None:
        current_id = None
        current_data = self.character_combo.currentData()
        if isinstance(current_data, dict):
            current_id = int(current_data.get("id", 0) or 0)
        self.character_combo.blockSignals(True)
        self.character_combo.clear()
        self.character_combo.addItem("写作助手", None)
        if self.character_provider:
            for character in self.character_provider():
                name = str(character.get("name", "") or "").strip()
                if not name:
                    continue
                role = str(character.get("role", "") or "").strip()
                label = f"{name} · {role}" if role else name
                self.character_combo.addItem(label, dict(character))
                if current_id and int(character.get("id", 0) or 0) == current_id:
                    self.character_combo.setCurrentIndex(self.character_combo.count() - 1)
        self.character_combo.blockSignals(False)

    def _selected_character(self) -> dict[str, Any] | None:
        data = self.character_combo.currentData()
        return dict(data) if isinstance(data, dict) else None

    def _on_character_changed(self) -> None:
        if self.current_thread is None:
            self.clear_history()

    def eventFilter(self, obj, event) -> bool:
        from PyQt6.QtCore import QEvent
        if obj is self.input_editor and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                self.send_message()
                return True
        return super().eventFilter(obj, event)

    def send_message(self) -> None:
        text = self.input_editor.toPlainText().strip()
        if not text or self.current_thread is not None:
            return
        self.input_editor.clear()
        self._append_bubble("user", text)
        self.chat_history.append({"role": "user", "content": text})
        self.current_ai_label = self._append_bubble("assistant", "")
        self.pending_text = ""

        context = self.context_builder(self._selected_character()).strip()
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.extend(self.chat_history[-12:])

        self.cancel_event = Event()
        thread = QThread(self)
        worker = ChatStreamWorker(self.ai_service, messages, self.cancel_event)
        self.current_thread = thread
        self.current_worker = worker
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.chunk.connect(self._queue_chunk)
        worker.done.connect(self._finish_reply)
        worker.error.connect(self._fail_reply)
        worker.cancelled.connect(self._cancelled_reply)
        worker.done.connect(thread.quit)
        worker.error.connect(thread.quit)
        worker.cancelled.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(self._cleanup_thread)
        self.send_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.flush_timer.start()
        thread.start()

    def cancel_reply(self) -> None:
        if self.cancel_event:
            self.cancel_event.set()
        self.cancel_btn.setEnabled(False)

    def clear_history(self) -> None:
        if self.current_thread is not None:
            return
        self.chat_history.clear()
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _append_bubble(self, role: str, text: str) -> QLabel:
        row_widget = QWidget()
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row_widget.setLayout(row)
        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        bubble.setObjectName("ChatUserBubble" if role == "user" else "ChatAssistantBubble")
        bubble.setMinimumWidth(120)
        bubble.setMaximumWidth(520)
        time_label = QLabel(datetime.now().strftime("%H:%M"))
        time_label.setObjectName("MetaLabel")
        box = QVBoxLayout()
        box.addWidget(bubble)
        box.addWidget(time_label, 0, Qt.AlignmentFlag.AlignRight if role == "user" else Qt.AlignmentFlag.AlignLeft)
        holder = QWidget()
        holder.setLayout(box)
        if role == "user":
            row.addStretch(1)
            row.addWidget(holder)
        else:
            row.addWidget(holder)
            row.addStretch(1)
        self.messages_layout.insertWidget(max(0, self.messages_layout.count() - 1), row_widget)
        QTimer.singleShot(0, self._scroll_to_bottom)
        return bubble

    def _queue_chunk(self, chunk: str) -> None:
        self.pending_text += chunk

    def _flush_pending_text(self) -> None:
        if not self.pending_text or self.current_ai_label is None:
            return
        self.current_ai_label.setText(self.current_ai_label.text() + self.pending_text)
        self.pending_text = ""
        self._scroll_to_bottom()

    def _finish_reply(self, text: str) -> None:
        self._flush_pending_text()
        final_text = text.strip()
        if final_text:
            self.chat_history.append({"role": "assistant", "content": final_text})

    def _fail_reply(self, message: str) -> None:
        self._flush_pending_text()
        if self.current_ai_label is not None:
            self.current_ai_label.setText(f"对话失败：{message}")

    def _cancelled_reply(self) -> None:
        self._flush_pending_text()
        if self.current_ai_label is not None and not self.current_ai_label.text().strip():
            self.current_ai_label.setText("回复已取消。")

    def _cleanup_thread(self) -> None:
        self.flush_timer.stop()
        self.current_thread = None
        self.current_worker = None
        self.cancel_event = None
        self.send_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        if self.close_after_cancel:
            self.close_after_cancel = False
            self.close()

    def _scroll_to_bottom(self) -> None:
        bar = self.scroll_area.verticalScrollBar()
        bar.setValue(bar.maximum())

    def closeEvent(self, event) -> None:  # noqa: N802, ANN001
        if self.current_thread is not None:
            self.close_after_cancel = True
            self.cancel_reply()
            event.ignore()
            return
        super().closeEvent(event)
