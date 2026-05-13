from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeTokens:
    mode: str
    bg: str
    surface: str
    surface_alt: str
    text: str
    muted: str
    primary: str
    primary_soft: str
    success: str
    warning: str
    danger: str
    border: str
    focus: str
    editor_bg: str


LIGHT_THEME = ThemeTokens(
    mode="light",
    bg="#EEF3F8",
    surface="#FFFFFF",
    surface_alt="#F6F9FC",
    text="#1F2A36",
    muted="#6A7788",
    primary="#2E6FD8",
    primary_soft="#DCE8FB",
    success="#29B67A",
    warning="#E7B547",
    danger="#E7726A",
    border="#D6DFEA",
    focus="#7BA9F5",
    editor_bg="#FBFDFF",
)

DARK_THEME = ThemeTokens(
    mode="dark",
    bg="#141A21",
    surface="#1B2430",
    surface_alt="#243041",
    text="#EAF1F8",
    muted="#91A0B5",
    primary="#5DA4F5",
    primary_soft="#20314A",
    success="#29B67A",
    warning="#E7B547",
    danger="#E7726A",
    border="#2F3E53",
    focus="#8EC1FF",
    editor_bg="#11171E",
)

WHITE_THEME = ThemeTokens(
    mode="light",
    bg="#F7F9FC",
    surface="#FFFFFF",
    surface_alt="#F1F5FA",
    text="#182232",
    muted="#66758A",
    primary="#2868D8",
    primary_soft="#E5EEFF",
    success="#26A86F",
    warning="#D9A62E",
    danger="#D9635C",
    border="#D8E1EC",
    focus="#6FA3F7",
    editor_bg="#FFFFFF",
)

SEPIA_THEME = ThemeTokens(
    mode="light",
    bg="#F3EBD8",
    surface="#FFF8E8",
    surface_alt="#F6EBCF",
    text="#34291C",
    muted="#7B6A53",
    primary="#9A6A2F",
    primary_soft="#EBD8B6",
    success="#4E9B62",
    warning="#B9852B",
    danger="#C4614E",
    border="#DECBA8",
    focus="#C99B56",
    editor_bg="#FFFDF4",
)

PRESET_THEMES = {
    "white": WHITE_THEME,
    "light_blue": LIGHT_THEME,
    "night": DARK_THEME,
    "sepia": SEPIA_THEME,
    "light": LIGHT_THEME,
    "dark": DARK_THEME,
}


def get_theme(mode: str) -> ThemeTokens:
    return PRESET_THEMES.get(mode, DARK_THEME if mode == "dark" else LIGHT_THEME)


def _rgba(hex_color: str, alpha: int) -> str:
    value = hex_color.strip().lstrip("#")
    if len(value) != 6:
        return hex_color
    try:
        red = int(value[0:2], 16)
        green = int(value[2:4], 16)
        blue = int(value[4:6], 16)
    except ValueError:
        return hex_color
    return f"rgba({red}, {green}, {blue}, {max(0, min(255, alpha))})"


def build_stylesheet(tokens: ThemeTokens, background_image: str = "") -> str:
    has_background = bool(background_image)
    window_background = "transparent" if has_background else tokens.bg
    chrome_background = tokens.bg
    panel_background = _rgba(tokens.surface, 172) if has_background else tokens.surface
    card_background = _rgba(tokens.surface, 188) if has_background else tokens.surface
    graph_panel_background = _rgba(tokens.editor_bg, 238) if has_background else tokens.editor_bg
    ghost_background = _rgba(tokens.surface, 72) if has_background else tokens.surface
    drawer_background = _rgba(tokens.surface, 142) if has_background else tokens.surface
    drawer_pane_background = _rgba(tokens.surface, 124) if has_background else tokens.surface
    drawer_title_background = _rgba(tokens.surface, 128) if has_background else tokens.surface
    surface_alt_background = _rgba(tokens.surface_alt, 212) if has_background else tokens.surface_alt
    tab_background = _rgba(tokens.surface_alt, 168) if has_background else tokens.surface_alt
    tab_selected_background = _rgba(tokens.surface, 212) if has_background else tokens.surface
    editor_background = _rgba(tokens.editor_bg, 232) if has_background else tokens.editor_bg
    stat_background = _rgba(tokens.editor_bg, 226) if has_background else tokens.editor_bg
    splitter_handle = _rgba(tokens.border, 82) if has_background else tokens.border
    scrollbar_handle = _rgba(tokens.muted, 148) if has_background else tokens.muted
    scrollbar_handle_hover = _rgba(tokens.muted, 220) if has_background else tokens.primary
    root_background = ""
    if background_image:
        safe_path = background_image.replace("\\", "/").replace('"', '\\"')
        root_background = f"""
    QMainWindow#MainWindow {{
        border-image: url("{safe_path}") 0 0 0 0 stretch stretch;
        background: transparent;
    }}
    QWidget#AppRoot {{
        background: transparent;
    }}
    QSplitter, QStackedWidget {{
        background: transparent;
    }}
    QWidget#SideDrawer {{
        background: transparent;
    }}
    QWidget#DrawerPage {{
        background: transparent;
    }}
    """
    return f"""
    QWidget {{
        background: {window_background};
        color: {tokens.text};
        font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
        font-size: 10.5pt;
    }}
    {root_background}
    QDialog, QDialog#ViewSettingsDialog {{
        background: {tokens.surface};
        color: {tokens.text};
    }}
    QDialog QLabel {{
        background: transparent;
    }}
    QMainWindow::separator {{
        background: transparent;
        width: 2px;
        height: 2px;
    }}
    QDockWidget {{
        background: {chrome_background};
        border: none;
    }}
    QDockWidget::title {{
        background: transparent;
        padding: 4px;
    }}
    QFrame#SideDrawer {{
        background: transparent;
        border: none;
    }}
    QFrame#DrawerTitleBar {{
        background: {drawer_title_background};
        border: 1px solid {tokens.border};
        border-radius: 16px;
    }}
    QLabel#DrawerTitleLabel {{
        background: transparent;
        font-size: 10pt;
        font-weight: 700;
    }}
    QWidget#DrawerPage {{
        background: transparent;
        border: none;
    }}
    QTabWidget#DrawerTabs {{
        background: {drawer_background};
        border: 1px solid {tokens.border};
        border-radius: 22px;
        padding: 10px;
    }}
    QTabWidget#DrawerTabs::pane {{
        background: {drawer_pane_background};
        border: 1px solid {tokens.border};
        border-radius: 18px;
        top: -1px;
    }}
    QTabWidget#DrawerTabs QTabBar::tab {{
        background: {tab_background};
        color: {tokens.muted};
        padding: 8px 12px;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        margin-right: 3px;
    }}
    QTabWidget#DrawerTabs QTabBar::tab:selected {{
        background: {tab_selected_background};
        color: {tokens.text};
        font-weight: 600;
    }}
    QTabWidget#DrawerTabs QTabBar QToolButton {{
        background: {tab_background};
        border: 1px solid {tokens.border};
        border-radius: 8px;
        margin: 2px;
    }}
    QTabWidget#DrawerTabs QTabBar QToolButton:hover {{
        background: {tokens.primary_soft};
        border-color: {tokens.focus};
    }}
    QFrame#HeaderBar, QFrame#StatusBar {{
        background: {chrome_background};
        border: none;
        border-radius: 16px;
    }}
    QFrame#HeaderBar {{
        min-height: 50px;
    }}
    QFrame#StatusBar {{
        min-height: 30px;
    }}
    QFrame#Panel {{
        background: {panel_background};
        border: 1px solid {tokens.border};
        border-radius: 20px;
    }}
    QFrame#Card {{
        background: {card_background};
        border: 1px solid {tokens.border};
        border-radius: 18px;
    }}
    QFrame#GhostCard {{
        background: {ghost_background};
        border: 1px solid {tokens.border};
        border-radius: 20px;
    }}
    QFrame#GraphToolbar {{
        background: transparent;
        border: none;
    }}
    QFrame#StarGraphPanel {{
        background: {graph_panel_background};
        border: 1px solid {tokens.border};
        border-radius: 14px;
    }}
    QFrame#StatCell {{
        background: {stat_background};
        border: 1px solid {tokens.border};
        border-radius: 14px;
    }}
    QLabel#TitleLabel {{
        font-size: 22pt;
        font-weight: 700;
        background: transparent;
    }}
    QLabel#SectionTitle {{
        font-size: 11pt;
        font-weight: 700;
        background: transparent;
    }}
    QLabel#MetaLabel, QLabel#StatusText {{
        color: {tokens.muted};
        background: transparent;
    }}
    QLabel#StatusMetric {{
        color: {tokens.muted};
        background: {surface_alt_background};
        border: 1px solid {tokens.border};
        border-radius: 10px;
        padding: 2px 10px;
    }}
    QLabel#ImagePreview {{
        background: {surface_alt_background};
        color: {tokens.muted};
        border: 1px dashed {tokens.border};
        border-radius: 16px;
        padding: 6px;
    }}
    QPushButton {{
        background: {surface_alt_background};
        border: 1px solid {tokens.border};
        border-radius: 12px;
        min-height: 30px;
        padding: 5px 12px;
    }}
    QPushButton:hover {{
        border-color: {tokens.focus};
        background: {tokens.primary_soft};
    }}
    QPushButton:pressed {{
        background: {tokens.primary};
        color: white;
    }}
    QPushButton#PrimaryButton {{
        background: {tokens.primary};
        color: white;
        border-color: {tokens.primary};
        font-weight: 600;
    }}
    QPushButton#DangerButton {{
        color: {tokens.danger};
    }}
    QPushButton#DrawerToggle {{
        text-align: left;
        font-weight: 600;
    }}
    QPushButton#ToolbarButton {{
        min-height: 32px;
        padding: 5px 14px;
        border-radius: 12px;
    }}
    QPushButton#TinyButton {{
        min-height: 30px;
        padding: 4px 10px;
        border-radius: 10px;
        font-size: 9.5pt;
    }}
    QLineEdit, QPlainTextEdit, QTextEdit, QListWidget, QTreeView, QComboBox {{
        background: {editor_background};
        color: {tokens.text};
        border: 1px solid {tokens.border};
        border-radius: 14px;
        selection-background-color: {tokens.primary};
        selection-color: white;
    }}
    QHeaderView::section {{
        background: {surface_alt_background};
        color: {tokens.text};
        border: 1px solid {tokens.border};
        padding: 4px;
    }}
    QPlainTextEdit, QTextEdit {{
        padding: 10px;
        line-height: 1.45em;
    }}
    QTreeView::item, QListWidget::item {{
        min-height: 24px;
        border-radius: 6px;
        padding: 1px 3px;
    }}
    QTreeView::item:hover, QListWidget::item:hover {{
        background: {tokens.primary_soft};
    }}
    QTreeView::item:selected, QListWidget::item:selected {{
        background: {tokens.primary};
        color: white;
    }}
    QListWidget#DrawerList {{
        background: transparent;
        border: none;
        padding: 4px;
    }}
    QListWidget#DrawerList::item {{
        background: {card_background};
        border: 1px solid {tokens.border};
        border-radius: 12px;
        margin: 4px 2px;
        padding: 8px;
        min-height: 42px;
    }}
    QListWidget#DrawerList::item:hover {{
        background: {tokens.primary_soft};
        border-color: {tokens.focus};
    }}
    QListWidget#DrawerList::item:selected {{
        background: {tokens.primary_soft};
        color: {tokens.text};
        border-color: {tokens.primary};
    }}
    QListWidget#LibraryCompactList, QListWidget#LibraryHistoryList {{
        background: transparent;
        border: none;
        padding: 4px 2px;
    }}
    QListWidget#LibraryCompactList::item, QListWidget#LibraryHistoryList::item {{
        background: {card_background};
        border: 1px solid {tokens.border};
        border-radius: 12px;
        margin: 4px 0px;
        padding: 7px 4px;
        min-height: 42px;
    }}
    QListWidget#LibraryCompactList::item:selected, QListWidget#LibraryHistoryList::item:selected {{
        background: {tokens.primary};
        color: white;
        border-color: {tokens.primary};
    }}
    QListWidget#LibraryCompactList {{
        padding: 2px 0px;
    }}
    QListWidget#LibraryCompactList::item {{
        text-align: center;
        margin: 3px 0px;
        padding: 7px 0px;
        min-height: 40px;
    }}
    QLabel#ChatUserBubble {{
        background: {tokens.primary};
        color: white;
        border: 1px solid {tokens.primary};
        border-radius: 16px;
        padding: 10px 12px;
    }}
    QLabel#ChatAssistantBubble {{
        background: {card_background};
        color: {tokens.text};
        border: 1px solid {tokens.border};
        border-radius: 16px;
        padding: 10px 12px;
    }}
    QSplitter#MainSplitter::handle {{
        background: transparent;
    }}
    QSplitter#MainSplitter::handle:hover {{
        background: {splitter_handle};
        border-radius: 5px;
    }}
    QSplitter#MainSplitter::handle:horizontal {{
        width: 10px;
    }}
    QSplitter::handle {{
        background: transparent;
    }}
    QSplitter::handle:hover {{
        background: {splitter_handle};
    }}
    QSplitter::handle:horizontal {{
        width: 6px;
    }}
    QTabWidget::pane {{
        border: 1px solid {tokens.border};
        border-radius: 16px;
        background: {card_background};
    }}
    QTabBar::tab {{
        background: {surface_alt_background};
        color: {tokens.muted};
        padding: 8px 12px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        margin-right: 3px;
    }}
    QTabBar::tab:selected {{
        background: {card_background};
        color: {tokens.text};
        font-weight: 600;
    }}
    QMenu {{
        background: {tokens.surface};
        color: {tokens.text};
        border: 1px solid {tokens.border};
        border-radius: 8px;
        padding: 6px;
    }}
    QMenu::item {{
        padding: 7px 28px 7px 14px;
        border-radius: 6px;
    }}
    QMenu::item:selected {{
        background: {tokens.primary_soft};
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {scrollbar_handle};
        border-radius: 4px;
        min-height: 22px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {scrollbar_handle_hover};
    }}
    QScrollBar:horizontal {{
        background: transparent;
        height: 6px;
        margin: 0px;
    }}
    QScrollBar::handle:horizontal {{
        background: {scrollbar_handle};
        border-radius: 4px;
        min-width: 22px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {scrollbar_handle_hover};
    }}
    QScrollBar::add-line, QScrollBar::sub-line {{
        width: 0px;
        height: 0px;
        border: none;
        background: transparent;
    }}
    QGraphicsView#StarGraphView {{
        background: transparent;
        border: none;
    }}
    QProgressBar {{
        border: 1px solid {tokens.border};
        border-radius: 8px;
        text-align: center;
        background: {tokens.surface_alt};
    }}
    QProgressBar::chunk {{
        background: {tokens.primary};
        border-radius: 8px;
    }}
    """
