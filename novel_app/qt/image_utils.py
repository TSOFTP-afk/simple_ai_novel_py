from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPixmap
from PyQt6.QtWidgets import QLabel


def set_adaptive_image(
    label: QLabel,
    image_path: str | Path,
    *,
    placeholder: str,
    max_width: int,
    max_height: int,
    crop: bool = False,
) -> None:
    path = Path(image_path) if str(image_path).strip() else Path()
    label.setMinimumSize(min(96, max_width), min(120, max_height))
    label.setMaximumSize(max_width, max_height)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    if not path.exists():
        label.setPixmap(QPixmap())
        label.setText(placeholder)
        return

    pixmap = QPixmap(str(path))
    if pixmap.isNull():
        label.setPixmap(QPixmap())
        label.setText(placeholder)
        return

    mode = Qt.AspectRatioMode.KeepAspectRatioByExpanding if crop else Qt.AspectRatioMode.KeepAspectRatio
    fitted = pixmap.scaled(max_width, max_height, mode, Qt.TransformationMode.SmoothTransformation)
    if crop and (fitted.width() > max_width or fitted.height() > max_height):
        left = max(0, int((fitted.width() - max_width) / 2))
        top = max(0, int((fitted.height() - max_height) / 2))
        fitted = fitted.copy(left, top, max_width, max_height)

    canvas = QPixmap(max_width, max_height)
    canvas.fill(QColor(0, 0, 0, 0))
    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    x = int((max_width - fitted.width()) / 2)
    y = int((max_height - fitted.height()) / 2)
    painter.drawPixmap(x, y, fitted)
    painter.end()
    label.setText("")
    label.setPixmap(canvas)
