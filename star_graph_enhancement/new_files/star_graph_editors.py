from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QLabel,
    QLineEdit,
    QColorDialog,
    QMessageBox,
)


class NodeStyleSelectorDialog(QDialog):
    def __init__(self, parent, style_manager):
        super().__init__(parent)
        self.style_manager = style_manager
        self.selected_style_id: int | None = None
        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowTitle("选择节点样式")
        self.setMinimumWidth(300)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("选择节点样式："))

        self.list_widget = QListWidget()
        for style in self.style_manager.get_all_node_styles():
            preset_marker = "⭐ " if style.is_preset else ""
            item_text = f"{preset_marker}{style.display_name}"
            self.list_widget.addItem(item_text)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")
        self.ok_btn.clicked.connect(self._on_ok)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def _on_ok(self) -> None:
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            styles = self.style_manager.get_all_node_styles()
            if current_row < len(styles):
                self.selected_style_id = styles[current_row].id
                self.accept()


class RelationshipTypeSelectorDialog(QDialog):
    def __init__(self, parent, style_manager, current_type_id: int | None = None):
        super().__init__(parent)
        self.style_manager = style_manager
        self.selected_type_id: int | None = None
        self.description: str = ""
        self._current_type_id = current_type_id
        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowTitle("选择关系类型")
        self.setMinimumWidth(350)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("关系类型："))

        self.list_widget = QListWidget()
        types = self.style_manager.get_all_relationship_types()
        for rtype in types:
            arrow_symbol = "→" if rtype.arrow_type == "unidirectional" else "↔"
            preset_marker = "⭐ " if rtype.is_preset else ""
            item_text = f"{preset_marker}{rtype.display_name} ({arrow_symbol})"
            self.list_widget.addItem(item_text)

        for i, rtype in enumerate(types):
            if rtype.id == self._current_type_id:
                self.list_widget.setCurrentRow(i)
                break

        layout.addWidget(self.list_widget)

        desc_label = QLabel("关系描述（可选）：")
        layout.addWidget(desc_label)

        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("例如：师徒情深、同门师兄妹...")
        layout.addWidget(self.desc_edit)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")
        self.ok_btn.clicked.connect(self._on_ok)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def _on_ok(self) -> None:
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            types = self.style_manager.get_all_relationship_types()
            if current_row < len(types):
                self.selected_type_id = types[current_row].id
                self.description = self.desc_edit.text()
                self.accept()


class CreateCustomStyleDialog(QDialog):
    def __init__(self, parent, default_values: dict | None = None):
        super().__init__(parent)
        self.default_values = default_values or {}
        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowTitle("创建自定义样式")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("样式名称："))
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.default_values.get("name", ""))
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        display_name_layout = QHBoxLayout()
        display_name_layout.addWidget(QLabel("显示名称："))
        self.display_name_edit = QLineEdit()
        self.display_name_edit.setText(self.default_values.get("display_name", ""))
        display_name_layout.addWidget(self.display_name_edit)
        layout.addLayout(display_name_layout)

        bg_layout = QHBoxLayout()
        bg_layout.addWidget(QLabel("背景颜色："))
        self.bg_color_btn = QPushButton("选择颜色")
        self.bg_color = self.default_values.get("background", "#FFFFFF")
        bg_layout.addWidget(self.bg_color_btn)
        layout.addLayout(bg_layout)
        self.bg_color_btn.clicked.connect(self._select_bg_color)

        border_layout = QHBoxLayout()
        border_layout.addWidget(QLabel("边框颜色："))
        self.border_color_btn = QPushButton("选择颜色")
        self.border_color = self.default_values.get("border_color", "#2E6FD8")
        border_layout.addWidget(self.border_color_btn)
        layout.addLayout(border_layout)
        self.border_color_btn.clicked.connect(self._select_border_color)

        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("文字颜色："))
        self.text_color_btn = QPushButton("选择颜色")
        self.text_color = self.default_values.get("text_color", "#1F2A36")
        text_layout.addWidget(self.text_color_btn)
        layout.addLayout(text_layout)
        self.text_color_btn.clicked.connect(self._select_text_color)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")
        self.ok_btn.clicked.connect(self._on_ok)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def _select_bg_color(self) -> None:
        color = QColorDialog.getColor()
        if color.isValid():
            self.bg_color = color.name()
            self.bg_color_btn.setText(color.name())

    def _select_border_color(self) -> None:
        color = QColorDialog.getColor()
        if color.isValid():
            self.border_color = color.name()
            self.border_color_btn.setText(color.name())

    def _select_text_color(self) -> None:
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_color = color.name()
            self.text_color_btn.setText(color.name())

    def _on_ok(self) -> None:
        name = self.name_edit.text().strip()
        display_name = self.display_name_edit.text().strip()

        if not name:
            QMessageBox.warning(self, "警告", "请输入样式名称")
            return
        if not display_name:
            QMessageBox.warning(self, "警告", "请输入显示名称")
            return

        self.accept()

    def get_values(self) -> dict:
        return {
            "name": self.name_edit.text().strip(),
            "display_name": self.display_name_edit.text().strip(),
            "background": self.bg_color,
            "border_color": self.border_color,
            "text_color": self.text_color,
        }


class CreateCustomRelationshipTypeDialog(QDialog):
    def __init__(self, parent, default_values: dict | None = None):
        super().__init__(parent)
        self.default_values = default_values or {}
        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowTitle("创建自定义关系类型")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("类型名称："))
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.default_values.get("name", ""))
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        display_layout = QHBoxLayout()
        display_layout.addWidget(QLabel("显示名称："))
        self.display_name_edit = QLineEdit()
        self.display_name_edit.setText(self.default_values.get("display_name", ""))
        display_layout.addWidget(self.display_name_edit)
        layout.addLayout(display_layout)

        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("线条颜色："))
        self.color_btn = QPushButton("选择颜色")
        self.color = self.default_values.get("color", "#5F7088")
        color_layout.addWidget(self.color_btn)
        layout.addLayout(color_layout)
        self.color_btn.clicked.connect(self._select_color)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")
        self.ok_btn.clicked.connect(self._on_ok)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def _select_color(self) -> None:
        color = QColorDialog.getColor()
        if color.isValid():
            self.color = color.name()
            self.color_btn.setText(color.name())

    def _on_ok(self) -> None:
        name = self.name_edit.text().strip()
        display_name = self.display_name_edit.text().strip()

        if not name:
            QMessageBox.warning(self, "警告", "请输入类型名称")
            return
        if not display_name:
            QMessageBox.warning(self, "警告", "请输入显示名称")
            return

        self.accept()

    def get_values(self) -> dict:
        return {
            "name": self.name_edit.text().strip(),
            "display_name": self.display_name_edit.text().strip(),
            "color": self.color,
        }
