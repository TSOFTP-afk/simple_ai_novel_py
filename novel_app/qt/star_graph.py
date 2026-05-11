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
    QVBoxLayout,
    QWidget,
)


def _elide_text(painter: QPainter, text: str, width: int) -> str:
    return painter.fontMetrics().elidedText(text, Qt.TextElideMode.ElideRight, width)


class CharacterNodeItem(QGraphicsItem):
    DIAMETER = 96
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
        color.setHsl(h, s, min(255, l + percent), a)
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
        return QRectF(-self.DIAMETER / 2, -self.DIAMETER / 2, self.DIAMETER, self.DIAMETER)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def edge_point_towards(self, other: QPointF) -> QPointF:
        center = self.pos()
        dx = other.x() - center.x()
        dy = other.y() - center.y()
        if dx == 0 and dy == 0:
            return center
        distance = max(1.0, math.hypot(dx, dy))
        radius = self.DIAMETER / 2 - 2
        return QPointF(center.x() + dx / distance * radius, center.y() + dy / distance * radius)

    def paint(self, painter: QPainter, option, widget=None) -> None:  # noqa: ANN001
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = self.boundingRect().adjusted(1.0, 1.0, -1.0, -1.0)

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

        painter.setBrush(QBrush(fill))
        painter.setPen(QPen(border, border_width))
        painter.drawEllipse(rect)

        avatar_rect = QRectF(-self.AVATAR / 2, rect.top() + 10, self.AVATAR, self.AVATAR)
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
            name = str(self.character.get("name", "") or "人").strip()
            initial = name[:1] if name else "人"
            font = QFont(painter.font())
            font.setPointSize(18)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QColor("#4C5E73"))
            painter.drawText(avatar_rect, Qt.AlignmentFlag.AlignCenter, initial)

        text_width = int(rect.width() - 16)
        name = str(self.character.get("name", "") or "未命名")

        font = QFont(painter.font())
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(self._current_style_colors.get("text_color", "#1F2A36")))
        text_rect = QRectF(rect.left() + 8, rect.bottom() - 28, rect.width() - 16, 20)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, _elide_text(painter, name, text_width))

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
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: ANN001, N802
        super().mouseReleaseEvent(event)
        if not self.owner.connect_mode:
            pos = self.pos()
            self.owner.characterMoved.emit(self.character_id, float(pos.x()), float(pos.y()))

    def contextMenuEvent(self, event) -> None:  # noqa: ANN001, N802
        menu = QMenu()
        edit_action = menu.addAction("编辑人物")
        style_action = menu.addAction("更改样式")
        chosen = menu.exec(event.screenPos())
        if chosen == edit_action:
            self.owner.editCharacterRequested.emit(self.character_id)
        elif chosen == style_action:
            self.owner.changeStyleRequested.emit(self.character_id)


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
        tooltip_parts = [
            str(relationship.get("source_name", "") or ""),
            str(relationship.get("relationship_type", "") or "关联"),
            str(relationship.get("target_name", "") or ""),
        ]
        description = str(relationship.get("description", "") or "").strip()
        tooltip = " - ".join(part for part in tooltip_parts if part)
        if description:
            tooltip = f"{tooltip}\n{description}" if tooltip else description
        self.setToolTip(tooltip)

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
        self.label.setText(display_text)

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
        event.ignore()


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
        self._background_color = "#F5F8FC"
        self._dot_color = QColor(132, 154, 178, 36)
        self.setBackgroundBrush(QBrush(QColor(self._background_color)))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.nodes: dict[int, CharacterNodeItem] = {}
        self.edges: list[RelationshipEdgeItem] = []
        self.relationships: list[dict[str, Any]] = []
        self.connect_mode = False
        self.pending_relationship_source: int | None = None
        self.style_manager: "StyleManager | None" = None

    def apply_theme(self, background: str, border: str) -> None:
        bg = QColor(background)
        bd = QColor(border)
        if not bg.isValid():
            bg = QColor("#F5F8FC")
        if not bd.isValid():
            bd = QColor(132, 154, 178)
        bd.setAlpha(42)
        self._background_color = bg.name()
        self._dot_color = bd
        self.setBackgroundBrush(QBrush(bg))
        self.viewport().update()

    def set_connect_mode(self, enabled: bool) -> None:
        enabled = False
        if self.connect_mode == enabled and self.pending_relationship_source is None:
            return
        self.connect_mode = enabled
        self.pending_relationship_source = None
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        for node in self.nodes.values():
            node.update()
        self.connectModeChanged.emit(enabled)

    def begin_relationship_from(self, character_id: int) -> None:
        self.set_connect_mode(False)

    def pick_relationship_node(self, character_id: int) -> None:
        self.set_connect_mode(False)

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: ANN001, N802
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event) -> None:  # noqa: ANN001, N802
        if self.itemAt(event.pos()):
            super().contextMenuEvent(event)
            return
        menu = QMenu(self)
        layout_action = menu.addAction("自动布局")
        fit_action = menu.addAction("适配视图")
        chosen = menu.exec(event.globalPos())
        if chosen == layout_action:
            self.auto_layout()
        elif chosen == fit_action:
            self.fit_to_content()

    def keyPressEvent(self, event) -> None:  # noqa: ANN001, N802
        if event.key() == Qt.Key.Key_Escape and self.connect_mode:
            self.set_connect_mode(False)
            event.accept()
            return
        super().keyPressEvent(event)

    def wheelEvent(self, event) -> None:  # noqa: ANN001, N802
        factor = 1.12 if event.angleDelta().y() > 0 else 0.88
        self.scale(factor, factor)

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:  # noqa: N802
        painter.fillRect(rect, QColor(self._background_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self._dot_color))
        step = 44
        left = int(math.floor(rect.left() / step) * step)
        top = int(math.floor(rect.top() / step) * step)
        x = left
        while x < rect.right():
            y = top
            while y < rect.bottom():
                painter.drawEllipse(QPointF(x, y), 1.2, 1.2)
                y += step
            x += step

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
            self._place_ring(ordered, max(160.0, len(ordered) * 76 / math.pi))
            self.update_edges()
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
        self._place_ring(primary, 255)
        if secondary:
            self._place_ring(secondary, 470, angle_offset=math.pi / max(1, len(secondary)))
        self.update_edges()

    def _apply_grid_layout(self, ordered: list[int]) -> None:
        if len(ordered) == 1:
            self.nodes[ordered[0]].setPos(0, 0)
        else:
            self._place_ring(ordered, max(160.0, len(ordered) * 76 / math.pi))
        self.update_edges()

    def _place_ring(self, node_ids: list[int], radius: float, angle_offset: float = -math.pi / 2) -> None:
        if not node_ids:
            return
        node_count = len(node_ids)
        if node_count == 1:
            self.nodes[node_ids[0]].setPos(0, 0)
            return
        min_radius = node_count * 76 / math.pi
        radius = max(radius, min_radius)
        for index, node_id in enumerate(node_ids):
            angle = angle_offset + 2 * math.pi * index / node_count
            self.nodes[node_id].setPos(math.cos(angle) * radius, math.sin(angle) * radius)

    def _place_grid(self, node_ids: list[int], y_start: float, columns: int) -> None:
        if not node_ids:
            return
        columns = max(1, columns)
        spacing_x = 155
        spacing_y = 135
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
        self.scope_label = QLabel("书籍级最终关系")
        self.scope_label.setObjectName("MutedLabel")
        toolbar_layout.addWidget(self.layout_button)
        toolbar_layout.addWidget(self.fit_button)
        toolbar_layout.addStretch(1)
        toolbar_layout.addWidget(self.scope_label)

        graph_panel = QFrame()
        graph_panel.setObjectName("StarGraphPanel")
        graph_panel_layout = QVBoxLayout(graph_panel)
        graph_panel_layout.setContentsMargins(8, 8, 8, 8)
        graph_panel_layout.setSpacing(0)
        self.view = StarGraphView(self)
        graph_panel_layout.addWidget(self.view, 1)
        layout.addWidget(toolbar)
        layout.addWidget(graph_panel, 1)

        self.layout_button.clicked.connect(self._auto_layout_and_persist)
        self.fit_button.clicked.connect(self.view.fit_to_content)
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
        self.view.set_connect_mode(False)

    def _auto_layout_and_persist(self) -> None:
        self.view.auto_layout()
        for character_id, (x, y) in self.view.node_positions().items():
            self.characterMoved.emit(character_id, x, y)

    def set_style_manager(self, style_manager: "StyleManager") -> None:
        self.view.style_manager = style_manager

    def apply_theme(self, background: str, border: str) -> None:
        self.view.apply_theme(background, border)

    def load_book(
        self,
        characters: list[dict[str, Any]],
        relationships: list[dict[str, Any]],
        image_resolver: Callable[[str], Path],
    ) -> None:
        self.view.load_graph(characters, relationships, image_resolver)


def ask_relationship_type(parent: QWidget, default: str = "") -> str | None:
    value, accepted = QInputDialog.getText(parent, "人物关系", "关系类型：", text=default)
    if not accepted:
        return None
    return value.strip() or "关系"
