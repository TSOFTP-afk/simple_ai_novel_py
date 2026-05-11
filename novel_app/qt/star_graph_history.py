from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class HistoryAction:
    action_type: str
    data: dict[str, Any]
    undo: Callable[[dict[str, Any]], None]
    redo: Callable[[dict[str, Any]], None]


class HistoryManager:
    def __init__(self, max_history: int = 50):
        self._history: list[HistoryAction] = []
        self._position: int = -1
        self._max_history: int = max_history

    def push(self, action: HistoryAction) -> None:
        self._history = self._history[: self._position + 1]
        self._history.append(action)

        if len(self._history) > self._max_history:
            self._history.pop(0)
        else:
            self._position += 1

    def undo(self) -> bool:
        if self._position < 0:
            return False
        action = self._history[self._position]
        action.undo(action.data)
        self._position -= 1
        return True

    def redo(self) -> bool:
        if self._position >= len(self._history) - 1:
            return False
        self._position += 1
        action = self._history[self._position]
        action.redo(action.data)
        return True

    def can_undo(self) -> bool:
        return self._position >= 0

    def can_redo(self) -> bool:
        return self._position < len(self._history) - 1

    def clear(self) -> None:
        self._history.clear()
        self._position = -1

    def get_history_count(self) -> int:
        return len(self._history)

    def get_current_position(self) -> int:
        return self._position
