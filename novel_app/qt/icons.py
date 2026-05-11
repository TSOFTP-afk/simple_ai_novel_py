from __future__ import annotations

from typing import Any

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap, QPolygonF


def make_tree_icon(kind: str, tokens: Any, accent: str = "", size: int = 22) -> QIcon:
    """Build small, theme-aware icons for the library tree."""
    primary = _color(accent or getattr(tokens, "primary", ""), "#2F80ED")
    border = _color(getattr(tokens, "border", ""), "#C8D2E0")
    surface = _color(getattr(tokens, "surface", ""), "#FFFFFF")
    muted = _color(getattr(tokens, "muted", ""), "#6D7C90")
    is_dark = str(getattr(tokens, "mode", "light")) == "dark"

    bg_alpha = 56 if is_dark else 28
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(_alpha(primary, bg_alpha))
    painter.drawRoundedRect(QRectF(1.0, 1.0, size - 2.0, size - 2.0), 6.0, 6.0)

    if kind == "book":
        _draw_book(painter, primary, surface, size)
    elif kind == "volume":
        _draw_volume(painter, primary, border, surface, size)
    elif kind == "group":
        _draw_folder(painter, primary, surface, size)
    elif kind == "template":
        _draw_chapter(painter, primary, border, surface, size)
        _draw_star(painter, _color(getattr(tokens, "warning", ""), "#F2C94C"), size)
    else:
        _draw_chapter(painter, primary, muted, surface, size)

    painter.end()
    return QIcon(pixmap)


def _color(value: str, fallback: str) -> QColor:
    color = QColor(str(value or "").strip())
    if not color.isValid():
        color = QColor(fallback)
    return color


def _alpha(color: QColor, alpha: int) -> QColor:
    copy = QColor(color)
    copy.setAlpha(max(0, min(255, alpha)))
    return copy


def _draw_book(painter: QPainter, primary: QColor, surface: QColor, size: int) -> None:
    cover = QRectF(size * 0.28, size * 0.20, size * 0.44, size * 0.60)
    painter.setBrush(primary)
    painter.setPen(QPen(_alpha(primary.darker(125), 190), 1.1))
    painter.drawRoundedRect(cover, 2.6, 2.6)

    painter.setPen(QPen(_alpha(surface, 210), 1.0))
    x = cover.left() + cover.width() * 0.22
    painter.drawLine(QPointF(x, cover.top() + 2.0), QPointF(x, cover.bottom() - 2.0))
    painter.drawLine(
        QPointF(cover.left() + cover.width() * 0.38, cover.top() + 5.0),
        QPointF(cover.right() - 3.0, cover.top() + 5.0),
    )
    painter.drawLine(
        QPointF(cover.left() + cover.width() * 0.38, cover.top() + 8.5),
        QPointF(cover.right() - 4.0, cover.top() + 8.5),
    )


def _draw_volume(painter: QPainter, primary: QColor, border: QColor, surface: QColor, size: int) -> None:
    rows = [
        QRectF(size * 0.26, size * 0.24, size * 0.50, size * 0.13),
        QRectF(size * 0.22, size * 0.42, size * 0.56, size * 0.13),
        QRectF(size * 0.26, size * 0.60, size * 0.50, size * 0.13),
    ]
    colors = [_alpha(primary, 225), _alpha(primary.lighter(118), 235), _alpha(surface, 245)]
    for index, rect in enumerate(rows):
        painter.setBrush(colors[index])
        painter.setPen(QPen(_alpha(border if index == 2 else primary.darker(125), 210), 1.0))
        painter.drawRoundedRect(rect, 2.0, 2.0)
        painter.setPen(QPen(_alpha(surface if index != 2 else primary, 190), 1.0))
        painter.drawLine(QPointF(rect.left() + 4.0, rect.center().y()), QPointF(rect.right() - 4.0, rect.center().y()))


def _draw_folder(painter: QPainter, primary: QColor, surface: QColor, size: int) -> None:
    tab = QRectF(size * 0.18, size * 0.30, size * 0.28, size * 0.12)
    body = QRectF(size * 0.16, size * 0.38, size * 0.68, size * 0.36)
    painter.setBrush(_alpha(primary, 210))
    painter.setPen(QPen(_alpha(primary.darker(125), 200), 1.0))
    painter.drawRoundedRect(tab, 2.0, 2.0)
    painter.setBrush(primary)
    painter.drawRoundedRect(body, 2.8, 2.8)
    painter.setPen(QPen(_alpha(surface, 165), 1.0))
    painter.drawLine(QPointF(body.left() + 4.0, body.center().y()), QPointF(body.right() - 4.0, body.center().y()))


def _draw_chapter(painter: QPainter, primary: QColor, muted: QColor, surface: QColor, size: int) -> None:
    page = QRectF(size * 0.28, size * 0.18, size * 0.46, size * 0.64)
    painter.setBrush(_alpha(surface, 245))
    painter.setPen(QPen(_alpha(primary, 230), 1.2))
    painter.drawRoundedRect(page, 2.4, 2.4)

    fold = QPolygonF(
        [
            QPointF(page.right() - 5.0, page.top()),
            QPointF(page.right(), page.top() + 5.0),
            QPointF(page.right() - 5.0, page.top() + 5.0),
        ]
    )
    painter.setBrush(_alpha(primary, 70))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawPolygon(fold)

    painter.setPen(QPen(_alpha(muted, 185), 1.0))
    for offset, width_scale in ((8.0, 0.56), (12.0, 0.44), (16.0, 0.50)):
        painter.drawLine(
            QPointF(page.left() + 4.0, page.top() + offset),
            QPointF(page.left() + 4.0 + page.width() * width_scale, page.top() + offset),
        )


def _draw_star(painter: QPainter, warning: QColor, size: int) -> None:
    center = QPointF(size * 0.72, size * 0.28)
    points = QPolygonF(
        [
            QPointF(center.x(), center.y() - 4.2),
            QPointF(center.x() + 1.3, center.y() - 1.2),
            QPointF(center.x() + 4.5, center.y() - 1.0),
            QPointF(center.x() + 2.0, center.y() + 0.9),
            QPointF(center.x() + 2.7, center.y() + 4.0),
            QPointF(center.x(), center.y() + 2.2),
            QPointF(center.x() - 2.7, center.y() + 4.0),
            QPointF(center.x() - 2.0, center.y() + 0.9),
            QPointF(center.x() - 4.5, center.y() - 1.0),
            QPointF(center.x() - 1.3, center.y() - 1.2),
        ]
    )
    painter.setBrush(warning)
    painter.setPen(QPen(_alpha(warning.darker(130), 220), 0.8))
    painter.drawPolygon(points)
