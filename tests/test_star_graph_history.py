import pytest
from novel_app.qt.star_graph_history import HistoryManager, HistoryAction


def test_history_manager_initialization():
    manager = HistoryManager()
    assert manager.can_undo() is False
    assert manager.can_redo() is False
    assert manager.get_history_count() == 0
    assert manager.get_current_position() == -1


def test_push_and_undo():
    manager = HistoryManager()
    undo_called = False
    redo_called = False

    def undo_fn(data):
        nonlocal undo_called
        undo_called = True

    def redo_fn(data):
        nonlocal redo_called
        redo_called = True

    action = HistoryAction("test", {"value": 1}, undo_fn, redo_fn)
    manager.push(action)

    assert manager.can_undo() is True
    assert manager.get_current_position() == 0

    manager.undo()
    assert undo_called is True
    assert manager.can_undo() is False


def test_redo():
    manager = HistoryManager()
    redo_called = False

    def undo_fn(data):
        pass

    def redo_fn(data):
        nonlocal redo_called
        redo_called = True

    action = HistoryAction("test", {"value": 1}, undo_fn, redo_fn)
    manager.push(action)
    manager.undo()

    assert manager.can_redo() is True
    assert manager.get_current_position() == -1

    manager.redo()
    assert redo_called is True
    assert manager.get_current_position() == 0


def test_max_history_limit():
    manager = HistoryManager(max_history=3)

    for i in range(5):

        def make_undo(i):
            def undo_fn(data):
                pass

            return undo_fn

        action = HistoryAction("test", {"value": i}, make_undo(i), lambda d: None)
        manager.push(action)

    assert len(manager._history) == 3
    assert manager.get_current_position() == 2


def test_redo_after_new_action_clears_forward_history():
    manager = HistoryManager()

    for i in range(3):

        def make_undo(i):
            def undo_fn(data):
                pass

            return undo_fn

        action = HistoryAction("test", {"value": i}, make_undo(i), lambda d: None)
        manager.push(action)

    manager.undo()
    manager.undo()

    manager.push(HistoryAction("new", {"value": 99}, lambda d: None, lambda d: None))

    assert manager.get_history_count() == 2
    assert manager.can_redo() is False


def test_clear():
    manager = HistoryManager()

    def dummy_undo(data):
        pass

    def dummy_redo(data):
        pass

    for i in range(5):
        action = HistoryAction("test", {"value": i}, dummy_undo, dummy_redo)
        manager.push(action)

    assert manager.get_history_count() == 5

    manager.clear()
    assert manager.get_history_count() == 0
    assert manager.can_undo() is False
    assert manager.can_redo() is False


def test_multiple_undo_redo():
    manager = HistoryManager()
    call_order = []

    def make_undo(i):
        def undo_fn(data):
            call_order.append(f"undo-{i}")

        return undo_fn

    def make_redo(i):
        def redo_fn(data):
            call_order.append(f"redo-{i}")

        return redo_fn

    for i in range(5):
        action = HistoryAction("test", {"value": i}, make_undo(i), make_redo(i))
        manager.push(action)

    manager.undo()
    manager.undo()
    manager.redo()
    manager.undo()

    assert call_order == ["undo-4", "undo-3", "redo-3", "undo-3"]
    assert manager.get_current_position() == 2
