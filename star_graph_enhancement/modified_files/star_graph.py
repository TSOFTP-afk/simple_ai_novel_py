from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Callable

from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen, QPixmap, QPolygonF
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsItem,
    QGraphicsPathItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMenu,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


def _elide_text(painter: QPainter, text: str, width: int) -> str:
    return painter.fontMetrics().elidedText(text, Qt.TextElideMode.ElideRight, width)


class CharacterNodeItem(QGraphicsItem):
    WIDTH = 168
    HEIGHT = 72
    AVATAR = 48

    def __init__(
        self,
        character: dict[str, Any],
        pixmap: QPixmap | None,
        owner: "StarGraphView",
    ) -> None:
        super().__init__()
        self.character = character
        self.character_id = int(character["id"])
        self.owner = owner
        self.pixmap = pixmap
        self.hovered = False
        self._style_id: int | None = None
        self._current_style_colors: dict[str, str] = {}
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)
        self.setZValue(2)
        self.setToolTip(self._build_tooltip())

    def _lighten_color(self, hex_color: str, percent: int) -> str:
        color = QColor(hex_color)
        h, s, l, a = color.hslHue(), color.hslSaturation(), color.lightness(), color.alpha()
        color.setHsl(h, s, min(100, l + percent), a)
        return color.name()

    def apply_style(
        self,
        style_id: int,
        background: str,
        border_color: str,
        text_color: str,
        border_width: float = 1.5,
    ) -> None:
        self._style_id = style_id
        self._current_style_colors = {
            "background": background,
            "border_color": border_color,
            "text_color": text_color,
            "border_width": str(border_width),
        }
        self.update()

    def get_style_id(self) -> int | None:
        return self._style_id

    def _build_tooltip(self) -> str:
        name = str(self.character.get("name", "") or "未命名")
        role = str(self.character.get("role", "") or "").strip()
        profile = str(self.character.get("profile_text", "") or "").strip()
        lines = [name]
        if role:
            lines.append(role)
        if profile:
            lines.append(profile[:180])
        return "\n".join(lines)

    def boundingRect(self) -> QRectF:  # noqa: N802
        return QRectF(-self.WIDTH / 2, -self.HEIGHT / 2, self.WIDTH, self.HEIGHT)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addRoundedRect(self.boundingRect(), 18, 18)
        return path

    def edge_point_towards(self, other: QPointF) -> QPointF:
        center = self.pos()
        dx = other.x() - center.x()
        dy = other.y() - center.y()
        if dx == 0 and dy == 0:
            return center
        half_w = self.WIDTH / 2
        half_h = self.HEIGHT / 2
        scale = min(half_w / abs(dx) if dx else float("inf"), half_h / abs(dy) if dy else float("inf"))
        return QPointF(center.x() + dx * scale * 0.92, center.y() + dy * scale * 0.92)

    def paint(self, painter: QPainter, option, widget=None) -> None:  # noqa: ANN001
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = self.boundingRect().adjusted(1.0, 1.0, -1.0, -1.0)
        pending = self.owner.pending_relationship_source == self.character_id

        default_bg = self._current_style_colors.get("background", "#FFFFFF")
        default_border = self._current_style_colors.get("border_color", "#D6DFEA")
        default_border_width = float(self._current_style_colors.get("border_width", "1.5"))

        if self._current_style_colors:
            fill = QColor(default_bg)
            border = QColor(default_border)
            border_width = default_border_width
        else:
            fill = QColor(255, 255, 255, 232)
            border = QColor("#D6DFEA")
            border_width = 1.4

        if self.hovered:
            fill = QColor(255, 255, 255, 246) if not self._current_style_colors else QColor(self._lighten_color(default_bg, 5))
            border = QColor("#7BA9F5") if not self._current_style_colors else QColor(self._lighten_color(default_border, 20))
        if self.isSelected():
            fill = QColor("#FFF6D9") if not self._current_style_colors else QColor(self._lighten_color(default_bg, 10))
            border = QColor("#E7B547") if not self._current_style_colors else QColor(self._lighten_color(default_border, 30))
            border_width *= 1.5
        if pending:
            fill = QColor("#E5EEFF") if not self._current_style_colors else QColor(self._lighten_color(default_bg, 15))
            border = QColor("#2E6FD8") if not self._current_style_colors else QColor(self._lighten_color(default_border, 40))
            border_width *= 1.5

        painter.setBrush(QBrush(fill))
        painter.setPen(QPen(border, border_width))
        painter.drawRoundedRect(rect, 18, 18)

        avatar_rect = QRectF(rect.left() + 12, rect.top() + 12, self.AVATAR, self.AVATAR)
        painter.setPen(QPen(border, 1.4))
        painter.setBrush(QBrush(QColor(255, 255, 255, 235)))
        painter.drawEllipse(avatar_rect)
        if self.pixmap and not self.pixmap.isNull():
            clipped = QPainterPath()
            clipped.addEllipse(avatar_rect.adjusted(3, 3, -3, -3))
            painter.save()
            painter.setClipPath(clipped)
            scaled = self.pixmap.scaled(
                int(avatar_rect.width()),
                int(avatar_rect.height()),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = int(avatar_rect.left() - max(0, (scaled.width() - avatar_rect.width()) / 2))
            y = int(avatar_rect.top() - max(0, (scaled.height() - avatar_rect.height()) / 2))
            painter.drawPixmap(x, y, scaled)
            painter.restore()
        else:
            painter.setPen(QColor("#6A7788"))
            painter.drawText(avatar_rect, Qt.AlignmentFlag.AlignCenter, "人")

        text_x = int(rect.left() + 72)
        text_width = int(rect.width() - 84)
        name = str(self.character.get("name", "") or "未命名")
        role = str(self.character.get("role", "") or "未设定").strip()
        profile = str(self.character.get("profile_text", "") or "").strip()

        font = QFont(painter.font())
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor("#1F2A36"))
        painter.drawText(text_x, int(rect.top() + 26), _elide_text(painter, name, text_width))

        font.setBold(False)
        font.setPointSize(8)
        painter.setFont(font)
        painter.setPen(QColor("#6A7788"))
        painter.drawText(text_x, int(rect.top() + 45), _elide_text(painter, role or "未设定", text_width))
        if profile:
            painter.setPen(QColor("#91A0B5"))
            painter.drawText(text_x, int(rect.top() + 61), _elide_text(painter, profile, text_width))

    def hoverEnterEvent(self, event) -> None:  # noqa: ANN001, N802
        self.hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event) -> None:  # noqa: ANN001, N802
        self.hovered = False
        self.update()
        super().hoverLeaveEvent(event)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.owner.update_edges()
        return super().itemChange(change, value)

    def mousePressEvent(self, event) -> None:  # noqa: ANN001, N802
        if event.button() == Qt.MouseButton.LeftButton and self.owner.connect_mode:
            self.owner.pick_relationship_node(self.character_id)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: ANN001, N802
        super().mouseReleaseEvent(event)
        if not self.owner.connect_mode:
            pos = self.pos()
            self.owner.characterMoved.emit(self.character_id, float(pos.x()), float(pos.y()))

    def contextMenuEvent(self, event) -> None:  # noqa: ANN001, N802
        menu = QMenu()
        edit_action = menu.addAction("编辑人物")
        connect_action = menu.addAction("从此建立关系")
        style_action = menu.addAction("更改样式")
        delete_action = menu.addAction("删除人物")
        chosen = menu.exec(event.screenPos())
        if chosen == edit_action:
            self.owner.editCharacterRequested.emit(self.character_id)
        elif chosen == connect_action:
            self.owner.begin_relationship_from(self.character_id)
        elif chosen == style_action:
            self.owner.changeStyleRequested.emit(self.character_id)
        elif chosen == delete_action:
            self.owner.deleteCharacterRequested.emit(self.character_id)


class RelationshipEdgeItem(QGraphicsPathItem):
    def __init__(
        self,
        relationship: dict[str, Any],
        source: CharacterNodeItem,
        target: CharacterNodeItem,
        owner: "StarGraphView",
    ) -> None:
        super().__init__()
        self.relationship = relationship
        self.relationship_id = int(relationship["id"])
        self.source = source
        self.target = target
        self.owner = owner
        self._type_id: int | None = None
        self._line_color = "#5F7088"
        self._line_style: str = "solid"
        self._arrow_type: str = "unidirectional"
        self._description: str = str(relationship.get("description", "") or "")
        self.setZValue(0)
        self._apply_style_from_relationship()
        self.label = QGraphicsSimpleTextItem("", self)
        self.label.setBrush(QBrush(QColor("#1F2A36")))
        self._update_label()
        self.update_path()

    def _apply_style_from_relationship(self) -> None:
        rtype_id = self.relationship.get("relationship_type_id")
        if rtype_id:
            self._type_id = int(rtype_id) if rtype_id else None
            relationship_type = self.relationship.get("relationship_type_data", {})
            if relationship_type:
                self._line_color = relationship_type.get("color", "#5F7088")
                self._line_style = relationship_type.get("line_style", "solid")
                self._arrow_type = relationship_type.get("arrow_type", "bi-directional")

        line_styles = {
            "solid": Qt.PenStyle.SolidLine,
            "dashed": Qt.PenStyle.DashLine,
            "dotted": Qt.PenStyle.DotLine,
        }
        pen = QPen(QColor(self._line_color), 1.8)
        pen.setStyle(line_styles.get(self._line_style, Qt.PenStyle.SolidLine))
        self.setPen(pen)

    def _update_label(self) -> None:
        rtype_name = str(self.relationship.get("relationship_type", "") or "")
        display_text = self._description if self._description else rtype_name
        if not display_text or display_text == "关系":
            display_text = ""
        if len(display_text) > 10:
            display_text = f"{display_text[:9]}…"
        self.label.setPlainText(display_text)

    def apply_relationship_type(
        self,
        type_id: int,
        color: str,
        line_style: str,
        arrow_type: str,
        description: str = "",
    ) -> None:
        self._type_id = type_id
        self._line_color = color
        self._line_style = line_style
        self._arrow_type = arrow_type
        self._description = description

        line_styles = {
            "solid": Qt.PenStyle.SolidLine,
            "dashed": Qt.PenStyle.DashLine,
            "dotted": Qt.PenStyle.DotLine,
        }
        pen = QPen(QColor(color), 1.8)
        pen.setStyle(line_styles.get(line_style, Qt.PenStyle.SolidLine))
        self.setPen(pen)
        self._update_label()
        self.update()

    def get_type_id(self) -> int | None:
        return self._type_id

    def get_description(self) -> str:
        return self._description

    def update_path(self) -> None:
        start = self.source.edge_point_towards(self.target.pos())
        end = self.target.edge_point_towards(self.source.pos())
        path = QPainterPath(start)
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        distance = max(1.0, math.hypot(dx, dy))
        normal = QPointF(-dy / distance, dx / distance)
        bend = min(56.0, max(18.0, distance * 0.12))
        mid = QPointF((start.x() + end.x()) / 2 + normal.x() * bend, (start.y() + end.y()) / 2 + normal.y() * bend)
        path.quadTo(mid, end)
        self.setPath(path)
        self.label.setPos(mid.x() - self.label.boundingRect().width() / 2, mid.y() - 18)

    def paint(self, painter: QPainter, option, widget=None) -> None:  # noqa: ANN001
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        super().paint(painter, option, widget)
        start = self.source.edge_point_towards(self.target.pos())
        end = self.target.edge_point_towards(self.source.pos())

        if self._arrow_type in ("unidirectional", "bi-directional"):
            angle = math.atan2(end.y() - start.y(), end.x() - start.x())
            arrow_tip = end
            size = 9
            left = QPointF(
                arrow_tip.x() - math.cos(angle - math.pi / 6) * size,
                arrow_tip.y() - math.sin(angle - math.pi / 6) * size,
            )
            right = QPointF(
                arrow_tip.x() - math.cos(angle + math.pi / 6) * size,
                arrow_tip.y() - math.sin(angle + math.pi / 6) * size,
            )
            painter.setBrush(QBrush(QColor(self._line_color)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPolygon(QPolygonF([arrow_tip, left, right]))

        if self._arrow_type == "bi-directional":
            start_for_arrow = self.target.edge_point_towards(self.source.pos())
            end_for_arrow = self.source.edge_point_towards(self.target.pos())
            angle = math.atan2(end_for_arrow.y() - start_for_arrow.y(), end_for_arrow.x() - start_for_arrow.x())
            arrow_tip = end_for_arrow
            size = 9
            left = QPointF(
                arrow_tip.x() - math.cos(angle - math.pi / 6) * size,
                arrow_tip.y() - math.sin(angle - math.pi / 6) * size,
            )
            right = QPointF(
                arrow_tip.x() - math.cos(angle + math.pi / 6) * size,
                arrow_tip.y() - math.sin(angle + math.pi / 6) * size,
            )
            painter.setBrush(QBrush(QColor(self._line_color)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPolygon(QPolygonF([arrow_tip, left, right]))

    def contextMenuEvent(self, event) -> None:  # noqa: ANN001, N802
        menu = QMenu()
        edit_action = menu.addAction("编辑关系")
        change_type_action = menu.addAction("更改关系类型")
        delete_action = menu.addAction("删除关系")
        chosen = menu.exec(event.screenPos())
        if chosen == edit_action:
            self.owner.editRelationshipRequested.emit(self.relationship_id)
        elif chosen == change_type_action:
            self.owner.changeRelationshipTypeRequested.emit(self.relationship_id)
        elif chosen == delete_action:
            self.owner.deleteRelationshipRequested.emit(self.relationship_id)


class StarGraphView(QGraphicsView):
    createCharacterRequested = pyqtSignal(float, float)
    characterMoved = pyqtSignal(int, float, float)
    relationshipRequested = pyqtSignal(int, int)
    editCharacterRequested = pyqtSignal(int)
    deleteCharacterRequested = pyqtSignal(int)
    editRelationshipRequested = pyqtSignal(int)
    deleteRelationshipRequested = pyqtSignal(int)
    changeStyleRequested = pyqtSignal(int)
    changeRelationshipTypeRequested = pyqtSignal(int)
    connectModeChanged = pyqtSignal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("StarGraphView")
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setScene(QGraphicsScene(self))
        self.setBackgroundBrush(QBrush(Qt.BrushStyle.NoBrush))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.nodes: dict[int, CharacterNodeItem] = {}
        self.edges: list[RelationshipEdgeItem] = []
        self.relationships: list[dict[str, Any]] = []
        self.connect_mode = False
        self.pending_relationship_source: int | None = None
        self.style_manager: "StyleManager | None" = None

    def set_connect_mode(self, enabled: bool) -> None:
        if self.connect_mode == enabled and (enabled or self.pending_relationship_source is None):
            return
        self.connect_mode = enabled
        if not enabled:
            self.pending_relationship_source = None
        self.setDragMode(QGraphicsView.DragMode.NoDrag if enabled else QGraphicsView.DragMode.ScrollHandDrag)
        for node in self.nodes.values():
            node.update()
        self.connectModeChanged.emit(enabled)

    def begin_relationship_from(self, character_id: int) -> None:
        self.set_connect_mode(True)
        self.pending_relationship_source = character_id
        for node in self.nodes.values():
            node.update()

    def pick_relationship_node(self, character_id: int) -> None:
        if not self.connect_mode:
            return
        if self.pending_relationship_source is None:
            self.pending_relationship_source = character_id
            for node in self.nodes.values():
                node.update()
            return
        source_id = self.pending_relationship_source
        self.pending_relationship_source = None
        for node in self.nodes.values():
            node.update()
        if source_id != character_id:
            self.relationshipRequested.emit(source_id, character_id)

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: ANN001, N802
        if self.connect_mode:
            return
        scene_pos = self.mapToScene(event.position().toPoint())
        if not self.itemAt(event.position().toPoint()):
            self.createCharacterRequested.emit(float(scene_pos.x()), float(scene_pos.y()))
            return
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event) -> None:  # noqa: ANN001, N802
        if self.itemAt(event.pos()):
            super().contextMenuEvent(event)
            return
        scene_pos = self.mapToScene(event.pos())
        menu = QMenu(self)
        create_action = menu.addAction("新建人物")
        layout_action = menu.addAction("自动布局")
        fit_action = menu.addAction("适配视图")
        connect_action = menu.addAction("退出关系模式" if self.connect_mode else "关系模式")
        chosen = menu.exec(event.globalPos())
        if chosen == create_action:
            self.createCharacterRequested.emit(float(scene_pos.x()), float(scene_pos.y()))
        elif chosen == layout_action:
            self.auto_layout()
        elif chosen == fit_action:
            self.fit_to_content()
        elif chosen == connect_action:
            self.set_connect_mode(not self.connect_mode)

    def keyPressEvent(self, event) -> None:  # noqa: ANN001, N802
        if event.key() == Qt.Key.Key_Escape and self.connect_mode:
            self.set_connect_mode(False)
            event.accept()
            return
        super().keyPressEvent(event)

    def wheelEvent(self, event) -> None:  # noqa: ANN001, N802
        factor = 1.12 if event.angleDelta().y() > 0 else 0.88
        self.scale(factor, factor)

    def load_graph(
        self,
        characters: list[dict[str, Any]],
        relationships: list[dict[str, Any]],
        image_resolver: Callable[[str], Path],
    ) -> None:
        scene = self.scene()
        scene.clear()
        self.nodes.clear()
        self.edges.clear()
        self.relationships = relationships
        self.pending_relationship_source = None

        missing_positions = 0
        count = max(1, len(characters))
        for index, character in enumerate(characters):
            x = float(character.get("graph_x") or 0)
            y = float(character.get("graph_y") or 0)
            if x == 0 and y == 0:
                missing_positions += 1
                x, y = self._default_position(index, count)
            path = image_resolver(str(character.get("image_path", "") or ""))
            pixmap = QPixmap(str(path)) if path and path.exists() else QPixmap()
            node = CharacterNodeItem(character, pixmap, self)
            node.setPos(x, y)
            scene.addItem(node)
            self.nodes[int(character["id"])] = node

        for relationship in relationships:
            source = self.nodes.get(int(relationship["source_character_id"]))
            target = self.nodes.get(int(relationship["target_character_id"]))
            if not source or not target:
                continue
            edge = RelationshipEdgeItem(relationship, source, target, self)
            scene.addItem(edge)
            self.edges.append(edge)

        if characters and missing_positions == len(characters):
            self._apply_degree_layout()
        self._reset_scene_rect()
        if characters:
            self.fit_to_content()

    def _default_position(self, index: int, count: int) -> tuple[float, float]:
        columns = max(1, math.ceil(math.sqrt(count * 1.35)))
        col = index % columns
        row = index // columns
        spacing_x = 210
        spacing_y = 108
        x = (col - (columns - 1) / 2) * spacing_x
        y = row * spacing_y
        return float(x), float(y)

    def _relationship_degrees(self) -> dict[int, int]:
        degrees = {node_id: 0 for node_id in self.nodes}
        for relationship in self.relationships:
            source_id = int(relationship.get("source_character_id", 0) or 0)
            target_id = int(relationship.get("target_character_id", 0) or 0)
            if source_id in degrees:
                degrees[source_id] += 1
            if target_id in degrees:
                degrees[target_id] += 1
        return degrees

    def _apply_degree_layout(self) -> None:
        if not self.nodes:
            return
        degrees = self._relationship_degrees()
        ordered = sorted(
            self.nodes,
            key=lambda node_id: (
                -degrees.get(node_id, 0),
                str(self.nodes[node_id].character.get("name", "")),
            ),
        )
        if not any(degrees.values()):
            self._apply_grid_layout(ordered)
            return

        focus_id = ordered[0]
        self.nodes[focus_id].setPos(0, 0)
        related: set[int] = set()
        for relationship in self.relationships:
            source_id = int(relationship.get("source_character_id", 0) or 0)
            target_id = int(relationship.get("target_character_id", 0) or 0)
            if source_id == focus_id and target_id in self.nodes:
                related.add(target_id)
            elif target_id == focus_id and source_id in self.nodes:
                related.add(source_id)

        primary = [node_id for node_id in ordered if node_id in related]
        secondary = [node_id for node_id in ordered if node_id not in related and node_id != focus_id]
        self._place_ring(primary, 265)
        if secondary:
            if len(primary) <= 10:
                self._place_grid(secondary, y_start=270, columns=4)
            else:
                self._place_ring(secondary, 505, angle_offset=math.pi / max(1, len(secondary)))
        self.update_edges()

    def _apply_grid_layout(self, ordered: list[int]) -> None:
        self._place_grid(ordered, y_start=0, columns=max(1, math.ceil(math.sqrt(len(ordered)))))
        self.update_edges()

    def _place_ring(self, node_ids: list[int], radius: float, angle_offset: float = -math.pi / 2) -> None:
        if not node_ids:
            return
        node_count = len(node_ids)
        min_radius = node_count * 94 / math.pi
        radius = max(radius, min_radius)
        for index, node_id in enumerate(node_ids):
            angle = angle_offset + 2 * math.pi * index / node_count
            self.nodes[node_id].setPos(math.cos(angle) * radius, math.sin(angle) * radius)

    def _place_grid(self, node_ids: list[int], y_start: float, columns: int) -> None:
        if not node_ids:
            return
        columns = max(1, columns)
        spacing_x = 225
        spacing_y = 108
        rows = math.ceil(len(node_ids) / columns)
        for index, node_id in enumerate(node_ids):
            col = index % columns
            row = index // columns
            x = (col - (columns - 1) / 2) * spacing_x
            y = y_start + (row - (rows - 1) / 2) * spacing_y
            self.nodes[node_id].setPos(x, y)

    def auto_layout(self) -> None:
        self._apply_degree_layout()
        self._reset_scene_rect()
        self.fit_to_content()

    def node_positions(self) -> dict[int, tuple[float, float]]:
        return {node_id: (float(node.pos().x()), float(node.pos().y())) for node_id, node in self.nodes.items()}

    def fit_to_content(self) -> None:
        scene_rect = self.scene().itemsBoundingRect().adjusted(-90, -80, 90, 80)
        if scene_rect.isValid() and not scene_rect.isEmpty():
            self.scene().setSceneRect(scene_rect)
            self.resetTransform()
            self.fitInView(scene_rect, Qt.AspectRatioMode.KeepAspectRatio)

    def _reset_scene_rect(self) -> None:
        rect = self.scene().itemsBoundingRect().adjusted(-160, -120, 160, 120)
        if rect.isValid() and not rect.isEmpty():
            self.scene().setSceneRect(rect)

    def update_edges(self) -> None:
        for edge in self.edges:
            edge.update_path()


class StarGraphWidget(QWidget):
    createCharacterRequested = pyqtSignal(float, float)
    characterMoved = pyqtSignal(int, float, float)
    relationshipRequested = pyqtSignal(int, int)
    editCharacterRequested = pyqtSignal(int)
    deleteCharacterRequested = pyqtSignal(int)
    editRelationshipRequested = pyqtSignal(int)
    deleteRelationshipRequested = pyqtSignal(int)
    changeCharacterStyleRequested = pyqtSignal(int)
    changeRelationshipTypeRequested = pyqtSignal(int)
    chapterSelected = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        toolbar = QFrame()
        toolbar.setObjectName("GraphToolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(6)
        self.layout_button = QPushButton("自动布局")
        self.layout_button.setObjectName("TinyButton")
        self.fit_button = QPushButton("适配")
        self.fit_button.setObjectName("TinyButton")
        self.relationship_mode_button = QPushButton("关系模式")
        self.relationship_mode_button.setObjectName("TinyButton")
        self.relationship_mode_button.setCheckable(True)
        toolbar_layout.addWidget(self.layout_button)
        toolbar_layout.addWidget(self.fit_button)
        toolbar_layout.addWidget(self.relationship_mode_button)
        toolbar_layout.addStretch(1)

        self.view = StarGraphView(self)
        self.timeline = QFrame()
        self.timeline.setObjectName("Card")
        self.timeline_layout = QHBoxLayout(self.timeline)
        self.timeline_layout.setContentsMargins(8, 6, 8, 6)
        self.timeline_layout.setSpacing(6)
        self.timeline_scroll = QScrollArea()
        self.timeline_scroll.setObjectName("TimelineScroll")
        self.timeline_scroll.setWidget(self.timeline)
        self.timeline_scroll.setWidgetResizable(True)
        self.timeline_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.timeline_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.timeline_scroll.setFixedHeight(58)
        self.timeline_scroll.setFrameShape(QFrame.Shape.NoFrame)
        layout.addWidget(toolbar)
        layout.addWidget(self.view, 1)
        layout.addWidget(self.timeline_scroll)

        self.layout_button.clicked.connect(self._auto_layout_and_persist)
        self.fit_button.clicked.connect(self.view.fit_to_content)
        self.relationship_mode_button.toggled.connect(self.view.set_connect_mode)
        self.view.connectModeChanged.connect(self._sync_connect_button)
        self.view.createCharacterRequested.connect(self.createCharacterRequested)
        self.view.characterMoved.connect(self.characterMoved)
        self.view.relationshipRequested.connect(self.relationshipRequested)
        self.view.editCharacterRequested.connect(self.editCharacterRequested)
        self.view.deleteCharacterRequested.connect(self.deleteCharacterRequested)
        self.view.editRelationshipRequested.connect(self.editRelationshipRequested)
        self.view.deleteRelationshipRequested.connect(self.deleteRelationshipRequested)
        self.view.changeStyleRequested.connect(self.changeCharacterStyleRequested)
        self.view.changeRelationshipTypeRequested.connect(self.changeRelationshipTypeRequested)

    def _sync_connect_button(self, enabled: bool) -> None:
        self.relationship_mode_button.blockSignals(True)
        self.relationship_mode_button.setChecked(enabled)
        self.relationship_mode_button.setText("退出关系" if enabled else "关系模式")
        self.relationship_mode_button.blockSignals(False)

    def _auto_layout_and_persist(self) -> None:
        self.view.auto_layout()
        for character_id, (x, y) in self.view.node_positions().items():
            self.characterMoved.emit(character_id, x, y)

    def set_style_manager(self, style_manager: "StyleManager") -> None:
        self.view.style_manager = style_manager

    def load_book(
        self,
        characters: list[dict[str, Any]],
        relationships: list[dict[str, Any]],
        chapters: list[dict[str, Any]],
        events: list[dict[str, Any]],
        image_resolver: Callable[[str], Path],
    ) -> None:
        self.view.load_graph(characters, relationships, image_resolver)
        self._load_timeline(chapters, events)

    def _load_timeline(self, chapters: list[dict[str, Any]], events: list[dict[str, Any]]) -> None:
        while self.timeline_layout.count():
            item = self.timeline_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        if not chapters:
            return
        event_map: dict[int, list[str]] = {}
        for event in events:
            event_map.setdefault(int(event["chapter_id"]), []).append(str(event.get("label", "")))
        for chapter in chapters:
            chapter_id = int(chapter["id"])
            label = str(chapter.get("title", "") or f"章节 {chapter_id}")
            button = QPushButton(label[:8])
            button.setObjectName("TinyButton")
            button.setToolTip("\n".join(event_map.get(chapter_id, [])) or label)
            button.clicked.connect(lambda _checked=False, cid=chapter_id: self.chapterSelected.emit(cid))
            self.timeline_layout.addWidget(button)
        self.timeline_layout.addStretch(1)


def ask_relationship_type(parent: QWidget, default: str = "") -> str | None:
    value, accepted = QInputDialog.getText(parent, "人物关系", "关系类型：", text=default)
    if not accepted:
        return None
    return value.strip() or "关系"
