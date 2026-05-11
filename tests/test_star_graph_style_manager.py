import pytest
from unittest.mock import MagicMock
from novel_app.qt.star_graph_style import StyleManager


def test_style_manager_initialization():
    mock_db = MagicMock()
    mock_db.get_node_styles.return_value = []
    mock_db.get_relationship_types.return_value = []

    manager = StyleManager(mock_db, book_id=1)
    assert manager.book_id == 1
    assert len(manager._node_styles) == 0
    assert len(manager._relationship_types) == 0


def test_style_manager_loads_styles():
    mock_db = MagicMock()
    mock_db.get_node_styles.return_value = [
        {
            "id": 1,
            "book_id": 1,
            "name": "neutral",
            "display_name": "中立",
            "background": "#FFFFFF",
            "border_color": "#D6DFEA",
            "border_width": 1.5,
            "text_color": "#1F2A36",
            "icon_type": "default",
            "is_preset": 1,
        },
        {
            "id": 2,
            "book_id": 1,
            "name": "protagonist",
            "display_name": "主角",
            "background": "#DCE8FB",
            "border_color": "#2E6FD8",
            "border_width": 1.5,
            "text_color": "#1F2A36",
            "icon_type": "hero",
            "is_preset": 1,
        },
    ]
    mock_db.get_relationship_types.return_value = [
        {
            "id": 1,
            "book_id": 1,
            "name": "unknown",
            "display_name": "未知",
            "color": "#5F7088",
            "line_style": "dotted",
            "arrow_type": "bi-directional",
            "is_directed": 0,
            "is_preset": 1,
        },
    ]

    manager = StyleManager(mock_db, book_id=1)
    assert len(manager._node_styles) == 2
    assert len(manager._relationship_types) == 1


def test_get_node_style():
    mock_db = MagicMock()
    mock_db.get_node_styles.return_value = [
        {
            "id": 1,
            "book_id": 1,
            "name": "neutral",
            "display_name": "中立",
            "background": "#FFFFFF",
            "border_color": "#D6DFEA",
            "border_width": 1.5,
            "text_color": "#1F2A36",
            "icon_type": "default",
            "is_preset": 1,
        },
    ]
    mock_db.get_relationship_types.return_value = []

    manager = StyleManager(mock_db, book_id=1)
    style = manager.get_node_style(1)
    assert style is not None
    assert style.name == "neutral"
    assert style.display_name == "中立"


def test_get_node_style_not_found():
    mock_db = MagicMock()
    mock_db.get_node_styles.return_value = []
    mock_db.get_relationship_types.return_value = []

    manager = StyleManager(mock_db, book_id=1)
    style = manager.get_node_style(999)
    assert style is None


def test_get_default_node_style():
    mock_db = MagicMock()
    mock_db.get_node_styles.return_value = [
        {
            "id": 1,
            "book_id": 1,
            "name": "neutral",
            "display_name": "中立",
            "background": "#FFFFFF",
            "border_color": "#D6DFEA",
            "border_width": 1.5,
            "text_color": "#1F2A36",
            "icon_type": "default",
            "is_preset": 1,
        },
    ]
    mock_db.get_relationship_types.return_value = []

    manager = StyleManager(mock_db, book_id=1)
    default_style = manager.get_default_node_style()
    assert default_style.name == "neutral"


def test_get_default_relationship_type():
    mock_db = MagicMock()
    mock_db.get_node_styles.return_value = []
    mock_db.get_relationship_types.return_value = [
        {
            "id": 1,
            "book_id": 1,
            "name": "unknown",
            "display_name": "未知",
            "color": "#5F7088",
            "line_style": "dotted",
            "arrow_type": "bi-directional",
            "is_directed": 0,
            "is_preset": 1,
        },
    ]

    manager = StyleManager(mock_db, book_id=1)
    default_type = manager.get_default_relationship_type()
    assert default_type.name == "unknown"


def test_get_all_node_styles():
    mock_db = MagicMock()
    mock_db.get_node_styles.return_value = [
        {
            "id": 1,
            "book_id": 1,
            "name": "neutral",
            "display_name": "中立",
            "background": "#FFFFFF",
            "border_color": "#D6DFEA",
            "border_width": 1.5,
            "text_color": "#1F2A36",
            "icon_type": "default",
            "is_preset": 1,
        },
        {
            "id": 2,
            "book_id": 1,
            "name": "protagonist",
            "display_name": "主角",
            "background": "#DCE8FB",
            "border_color": "#2E6FD8",
            "border_width": 1.5,
            "text_color": "#1F2A36",
            "icon_type": "hero",
            "is_preset": 1,
        },
    ]
    mock_db.get_relationship_types.return_value = []

    manager = StyleManager(mock_db, book_id=1)
    all_styles = manager.get_all_node_styles()
    assert len(all_styles) == 2


def test_get_all_relationship_types():
    mock_db = MagicMock()
    mock_db.get_node_styles.return_value = []
    mock_db.get_relationship_types.return_value = [
        {
            "id": 1,
            "book_id": 1,
            "name": "unknown",
            "display_name": "未知",
            "color": "#5F7088",
            "line_style": "dotted",
            "arrow_type": "bi-directional",
            "is_directed": 0,
            "is_preset": 1,
        },
        {
            "id": 2,
            "book_id": 1,
            "name": "hostile",
            "display_name": "敌对",
            "color": "#D83A34",
            "line_style": "dashed",
            "arrow_type": "unidirectional",
            "is_directed": 1,
            "is_preset": 1,
        },
    ]

    manager = StyleManager(mock_db, book_id=1)
    all_types = manager.get_all_relationship_types()
    assert len(all_types) == 2


def test_get_node_style_by_name():
    mock_db = MagicMock()
    mock_db.get_node_styles.return_value = [
        {
            "id": 1,
            "book_id": 1,
            "name": "neutral",
            "display_name": "中立",
            "background": "#FFFFFF",
            "border_color": "#D6DFEA",
            "border_width": 1.5,
            "text_color": "#1F2A36",
            "icon_type": "default",
            "is_preset": 1,
        },
    ]
    mock_db.get_relationship_types.return_value = []

    manager = StyleManager(mock_db, book_id=1)
    style = manager.get_node_style_by_name("neutral")
    assert style is not None
    assert style.display_name == "中立"


def test_get_relationship_type_by_name():
    mock_db = MagicMock()
    mock_db.get_node_styles.return_value = []
    mock_db.get_relationship_types.return_value = [
        {
            "id": 1,
            "book_id": 1,
            "name": "hostile",
            "display_name": "敌对",
            "color": "#D83A34",
            "line_style": "dashed",
            "arrow_type": "unidirectional",
            "is_directed": 1,
            "is_preset": 1,
        },
    ]

    manager = StyleManager(mock_db, book_id=1)
    rtype = manager.get_relationship_type_by_name("hostile")
    assert rtype is not None
    assert rtype.display_name == "敌对"


def test_refresh():
    mock_db = MagicMock()
    mock_db.get_node_styles.return_value = []
    mock_db.get_relationship_types.return_value = []

    manager = StyleManager(mock_db, book_id=1)
    manager._node_styles[1] = MagicMock()
    manager._relationship_types[1] = MagicMock()

    manager.refresh()
    assert len(manager._node_styles) == 0
    assert len(manager._relationship_types) == 0
