from typing import Optional

from novel_app.qt.star_graph_models import (
    NodeStyle,
    RelationshipType,
    PRESET_NODE_STYLES,
    PRESET_RELATIONSHIP_TYPES,
)


class StyleManager:
    def __init__(self, database, book_id: int):
        self.db = database
        self.book_id = book_id
        self._node_styles: dict[int, NodeStyle] = {}
        self._relationship_types: dict[int, RelationshipType] = {}
        self._load_styles()

    def _load_styles(self) -> None:
        rows = self.db.get_node_styles(self.book_id)
        for row in rows:
            style = NodeStyle(
                id=row["id"],
                book_id=row["book_id"],
                name=row["name"],
                display_name=row["display_name"],
                background=row["background"],
                border_color=row["border_color"],
                border_width=row["border_width"],
                text_color=row["text_color"],
                icon_type=row["icon_type"],
                is_preset=bool(row["is_preset"]),
            )
            self._node_styles[style.id] = style

        rows = self.db.get_relationship_types(self.book_id)
        for row in rows:
            rtype = RelationshipType(
                id=row["id"],
                book_id=row["book_id"],
                name=row["name"],
                display_name=row["display_name"],
                color=row["color"],
                line_style=row["line_style"],
                arrow_type=row["arrow_type"],
                is_directed=bool(row["is_directed"]),
                is_preset=bool(row["is_preset"]),
            )
            self._relationship_types[rtype.id] = rtype

    def get_node_style(self, style_id: int) -> Optional[NodeStyle]:
        return self._node_styles.get(style_id)

    def get_default_node_style(self) -> NodeStyle:
        for style in self._node_styles.values():
            if style.name == "neutral":
                return style
        return PRESET_NODE_STYLES[-1]

    def get_relationship_type(self, type_id: int) -> Optional[RelationshipType]:
        return self._relationship_types.get(type_id)

    def get_default_relationship_type(self) -> RelationshipType:
        for rtype in self._relationship_types.values():
            if rtype.name == "unknown":
                return rtype
        return PRESET_RELATIONSHIP_TYPES[-1]

    def get_all_node_styles(self) -> list[NodeStyle]:
        return list(self._node_styles.values())

    def get_all_relationship_types(self) -> list[RelationshipType]:
        return list(self._relationship_types.values())

    def get_node_style_by_name(self, name: str) -> Optional[NodeStyle]:
        for style in self._node_styles.values():
            if style.name == name:
                return style
        return None

    def get_relationship_type_by_name(self, name: str) -> Optional[RelationshipType]:
        for rtype in self._relationship_types.values():
            if rtype.name == name:
                return rtype
        return None

    def initialize_defaults(self) -> None:
        if not self._node_styles:
            self.db.initialize_book_star_graph_defaults(self.book_id)
            self._load_styles()

    def refresh(self) -> None:
        self._node_styles.clear()
        self._relationship_types.clear()
        self._load_styles()
