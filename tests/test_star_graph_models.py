import pytest
from novel_app.qt.star_graph_models import (
    NodeStyle,
    RelationshipType,
    PRESET_NODE_STYLES,
    PRESET_RELATIONSHIP_TYPES,
)


def test_node_style_defaults():
    style = NodeStyle()
    assert style.name == "neutral"
    assert style.background == "#FFFFFF"
    assert style.border_color == "#D6DFEA"
    assert style.border_width == 1.5
    assert style.icon_type == "default"
    assert style.is_preset is True


def test_node_style_custom_values():
    style = NodeStyle(
        name="custom",
        display_name="自定义",
        background="#FF0000",
        border_color="#00FF00",
        border_width=2.0,
        text_color="#0000FF",
        icon_type="hero",
    )
    assert style.name == "custom"
    assert style.background == "#FF0000"
    assert style.border_width == 2.0


def test_relationship_type_defaults():
    rtype = RelationshipType()
    assert rtype.name == "unknown"
    assert rtype.display_name == "未知"
    assert rtype.arrow_type == "bi-directional"
    assert rtype.is_directed is False
    assert rtype.is_preset is True


def test_relationship_type_directed():
    rtype = RelationshipType(
        name="hostile",
        display_name="敌对",
        arrow_type="unidirectional",
        is_directed=True,
    )
    assert rtype.is_directed is True
    assert rtype.arrow_type == "unidirectional"


def test_preset_styles_count():
    assert len(PRESET_NODE_STYLES) == 5


def test_preset_relationship_types_count():
    assert len(PRESET_RELATIONSHIP_TYPES) == 7


def test_preset_styles_have_required_fields():
    for style in PRESET_NODE_STYLES:
        assert style.name
        assert style.display_name
        assert style.background.startswith("#")
        assert style.border_color.startswith("#")
        assert style.icon_type


def test_preset_relationship_types_have_required_fields():
    for rtype in PRESET_RELATIONSHIP_TYPES:
        assert rtype.name
        assert rtype.display_name
        assert rtype.color.startswith("#")
        assert rtype.line_style in ("solid", "dashed", "dotted")
        assert rtype.arrow_type in ("unidirectional", "bi-directional", "none")


def test_preset_style_names():
    expected_names = {"protagonist", "antagonist", "supporting", "minor", "neutral"}
    actual_names = {style.name for style in PRESET_NODE_STYLES}
    assert actual_names == expected_names


def test_preset_relationship_type_names():
    expected_names = {
        "master_apprentice", "blood", "hostile", "friendly",
        "romantic", "subordinate", "unknown"
    }
    actual_names = {rtype.name for rtype in PRESET_RELATIONSHIP_TYPES}
    assert actual_names == expected_names
