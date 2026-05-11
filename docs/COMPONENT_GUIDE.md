# 组件使用手册

## 1. 组件概述

Simple AI Novel App的UI框架提供了丰富的可复用组件，用于构建用户界面。本手册详细介绍如何使用这些组件，包括基础组件、复杂组件和布局组件。

## 2. 基础组件

### 2.1 StyledFrame

**功能**：统一风格的框架容器，自动跟随主题配色

**使用示例**：

```python
from novel_app.components import StyledFrame
from novel_app.theme.theme_manager import ThemeManager

# 创建主题管理器
theme = ThemeManager(config_path)

# 创建StyledFrame
frame = StyledFrame(parent, theme=theme)
frame.pack(fill=tk.BOTH, expand=True)
```

### 2.2 StyledLabel

**功能**：统一风格的标签，自动跟随主题配色和字体层级

**使用示例**：

```python
from novel_app.components import StyledLabel

# 创建StyledLabel
label = StyledLabel(
    parent,
    theme=theme,
    level="heading1",  # 字体层级：display, heading1, heading2, body, body_small, caption, code
    bold=True,        # 是否粗体
    muted=False,      # 是否使用次要文本颜色
    text="Hello World"
)
label.pack()
```

### 2.3 StyledButton

**功能**：统一风格的按钮，支持多种样式变体

**使用示例**：

```python
from novel_app.components import StyledButton

# 创建StyledButton
button = StyledButton(
    parent,
    theme=theme,
    variant="primary",  # 样式变体：primary, secondary, ghost, danger
    text="Click Me",
    command=lambda: print("Button clicked")
)
button.pack()
```

### 2.4 StyledEntry

**功能**：统一风格的输入框

**使用示例**：

```python
from novel_app.components import StyledEntry

# 创建StyledEntry
entry = StyledEntry(parent, theme=theme)
entry.pack(fill=tk.X)
```

## 3. 复杂组件

### 3.1 TextEditor

**功能**：文本编辑器组件，支持主题跟随、脏标记、字数统计等功能

**使用示例**：

```python
from novel_app.components import TextEditor

# 创建TextEditor
editor = TextEditor(
    parent,
    theme=theme,
    height=10,           # 高度
    min_height=60,       # 最小高度
    readonly=False,       # 是否只读
    monospace=False,      # 是否使用等宽字体
    show_line_numbers=False,  # 是否显示行号
    on_change=lambda value: print(f"Content changed: {value}")
)
editor.pack(fill=tk.BOTH, expand=True)

# 设置内容
editor.set_value("Hello World")

# 获取内容
content = editor.get_value()

# 获取字数
word_count = editor.word_count()
```

### 3.2 TreeNav

**功能**：树导航组件，支持拖拽排序、右键菜单等功能

**使用示例**：

```python
from novel_app.components import TreeNav, make_iid, TREE_KIND_BOOK

# 创建TreeNav
tree = TreeNav(
    parent,
    theme=theme,
    on_select=lambda kind, node_id, group_book_id: print(f"Selected: {kind}, {node_id}"),
    on_context_menu=lambda kind, node_id, group_book_id, x, y: print(f"Context menu: {kind}, {node_id}"),
    on_empty_context_menu=lambda x, y: print(f"Empty context menu at: {x}, {y}"),
    searchable=True  # 是否支持搜索
)
tree.pack(fill=tk.BOTH, expand=True)

# 填充数据
tree.populate(books, volumes_by_book, chapters_by_book)

# 选择节点
tree.select_iid(make_iid(TREE_KIND_BOOK, book_id))
```

### 3.3 ListPanel

**功能**：列表面板组件，包含标题栏和操作按钮

**使用示例**：

```python
from novel_app.components import ListPanel

# 创建ListPanel
list_panel = ListPanel(
    parent,
    theme=theme,
    display_field="name",  # 显示字段
    badge_field="role"     # 徽章字段
)
list_panel.pack(fill=tk.BOTH, expand=True)

# 设置数据
items = [
    {"id": 1, "name": "Item 1", "role": "Role 1"},
    {"id": 2, "name": "Item 2", "role": "Role 2"}
]
list_panel.set_items(items)

# 获取选中项
selected = list_panel.get_selected()
```

### 3.4 Dialog

**功能**：对话框组件，支持多种类型的对话框

**使用示例**：

```python
from novel_app.components import Dialog

# 信息对话框
Dialog.info(parent, theme, "Information", "This is an information message")

# 警告对话框
Dialog.warning(parent, theme, "Warning", "This is a warning message")

# 错误对话框
Dialog.error(parent, theme, "Error", "This is an error message")

# 确认对话框
if Dialog.confirm(parent, theme, "Confirm", "Are you sure?"):
    print("User confirmed")

# 输入对话框
text = Dialog.input_text(parent, theme, "Input", "Please enter some text:")
if text:
    print(f"User entered: {text}")
```

## 4. 视图组件

### 4.1 SidebarView

**功能**：侧边栏视图，展示作品树

**使用示例**：

```python
from novel_app.views import SidebarView

# 创建SidebarView
sidebar = SidebarView(
    parent,
    theme=theme,
    state=state,
    on_tree_select=lambda kind, node_id, group_book_id: print(f"Tree selected: {kind}, {node_id}"),
    on_tree_context_menu=lambda kind, node_id, group_book_id, x, y: print(f"Tree context menu: {kind}, {node_id}"),
    on_empty_context_menu=lambda x, y: print(f"Empty context menu at: {x}, {y}"),
    on_new_book=lambda: print("New book clicked"),
    on_toggle_collapse=lambda: print("Toggle collapse clicked")
)
sidebar.pack(fill=tk.BOTH, expand=True)

# 填充数据
sidebar.populate(books, volumes_by_book, chapters_by_book)
```

### 4.2 WorkspaceView

**功能**：工作区视图，包含编辑区域

**使用示例**：

```python
from novel_app.views import WorkspaceView

# 创建WorkspaceView
workspace = WorkspaceView(
    parent,
    theme=theme,
    state=state,
    on_save=lambda: print("Save clicked"),
    on_undo=lambda: print("Undo clicked"),
    on_refresh_summary=lambda: print("Refresh summary clicked"),
    on_change=lambda field, value: print(f"Field changed: {field}, {value}"),
    on_toggle_sidebar=lambda: print("Toggle sidebar clicked"),
    on_toggle_focus=lambda: print("Toggle focus clicked"),
    on_toggle_context_panel=lambda: print("Toggle context panel clicked"),
    on_toggle_task_panel=lambda: print("Toggle task panel clicked")
)
workspace.pack(fill=tk.BOTH, expand=True)

# 设置标题
workspace.set_title("Chapter Title", "Book / Volume / Chapter")

# 设置内容
workspace.set_content("Chapter content", "Chapter outline", "Chapter summary")

# 设置呈现模式
workspace.set_presentation_mode("chapter")  # chapter, outline
```

### 4.3 ContextPanel

**功能**：上下文面板视图，展示详细信息

**使用示例**：

```python
from novel_app.views import ContextPanel

# 创建ContextPanel
context = ContextPanel(
    parent,
    theme=theme,
    state=state,
    on_save_book_settings=lambda title: print(f"Save book settings: {title}"),
    on_open_book_settings=lambda: print("Open book settings clicked"),
    on_create_character=lambda: print("Create character clicked"),
    on_save_character=lambda name, role, profile: print(f"Save character: {name}, {role}"),
    on_delete_character=lambda char_id: print(f"Delete character: {char_id}"),
    on_select_character=lambda index: print(f"Select character: {index}"),
    on_create_world_entry=lambda: print("Create world entry clicked"),
    on_save_world_entry=lambda name, category, content: print(f"Save world entry: {name}, {category}"),
    on_delete_world_entry=lambda entry_id: print(f"Delete world entry: {entry_id}"),
    on_select_world_entry=lambda index: print(f"Select world entry: {index}"),
    on_cancel_task=lambda: print("Cancel task clicked"),
    on_close=lambda: print("Close clicked")
)
context.pack(fill=tk.BOTH, expand=True)

# 同步标签页
context.sync_tabs(["overview", "characters", "world", "skills", "task"])

# 显示/隐藏
context.show()
context.hide()
```

### 4.4 FocusModeView

**功能**：专注模式视图，提供沉浸式写作体验

**使用示例**：

```python
from novel_app.views import FocusModeView

# 创建FocusModeView
focus_view = FocusModeView(
    parent,
    theme=theme,
    state=state,
    on_exit=lambda: print("Exit focus mode clicked"),
    on_save=lambda: print("Save clicked"),
    on_change=lambda field, value: print(f"Field changed: {field}, {value}")
)

# 设置内容
focus_view.set_up("Chapter Title", "Chapter content", "Chapter outline", "Chapter summary")

# 获取内容
content = focus_view.get_content()

# 更新字数
focus_view.update_word_count()
```

## 5. 布局组件

### 5.1 ThreeColumnLayout

**功能**：三栏布局策略，管理PanedWindow的分割比例

**使用示例**：

```python
from novel_app.layouts import ThreeColumnLayout

# 创建ThreeColumnLayout
layout = ThreeColumnLayout(
    paned_window,
    sidebar_container,
    workspace_container,
    context_container,
    theme=theme,
    state=state
)
```

### 5.2 TwoColumnLayout

**功能**：两栏布局策略，实现侧边栏和工作区的布局

**使用示例**：

```python
from novel_app.layouts import TwoColumnLayout

# 创建TwoColumnLayout
layout = TwoColumnLayout(
    paned_window,
    sidebar_container,
    workspace_container,
    theme=theme,
    state=state
)
```

## 6. 组件工厂

**功能**：组件工厂用于创建组件实例

**使用示例**：

```python
from novel_app.components import register_component, create_component

# 注册组件
register_component("my_component", MyComponent)

# 创建组件
component = create_component("my_component", parent, theme, **kwargs)
```

## 7. 主题定制

**功能**：主题定制器用于定制和扩展主题

**使用示例**：

```python
from novel_app.theme import ThemeCustomizer

# 创建自定义主题
custom_theme = ThemeCustomizer.create_custom_theme(
    "custom_theme",
    base_tokens,
    color_overrides={
        "primary": "#ff0000",
        "primary_hover": "#cc0000"
    },
    font_overrides={
        "family_ui": "Arial"
    }
)

# 创建高对比度主题
high_contrast_theme = ThemeCustomizer.create_high_contrast_theme()
```

## 8. 最佳实践

### 8.1 组件使用

- **组件复用**：尽量复用现有组件，避免重复开发
- **组件配置**：通过参数配置组件，而不是硬编码
- **组件通信**：使用事件总线进行组件通信，避免直接依赖
- **组件测试**：为组件编写测试，确保组件的稳定性

### 8.2 性能优化

- **懒加载**：对于大型组件，使用懒加载减少初始加载时间
- **虚拟滚动**：对于长列表，使用虚拟滚动减少DOM元素
- **事件防抖**：对于频繁触发的事件，使用防抖减少处理次数
- **资源释放**：组件销毁时释放资源，避免内存泄漏

### 8.3 代码风格

- **命名规范**：使用清晰、一致的命名规范
- **代码组织**：组织代码结构，提高可读性
- **注释**：添加必要的注释，提高代码可维护性
- **文档**：为组件添加文档，说明使用方法和参数

## 9. 总结

Simple AI Novel App的UI框架提供了丰富的可复用组件，用于构建用户界面。这些组件不仅功能丰富，而且易于使用和扩展。通过遵循本手册的使用示例和最佳实践，您可以快速构建出美观、高效的用户界面。

组件库的设计理念是模块化、可复用、可扩展，通过事件总线、状态管理器等核心模块，实现了组件之间的解耦和高效通信。设计令牌系统确保了界面视觉样式的一致性和可维护性。

希望本手册能够帮助您更好地理解和使用UI框架的组件，为您的应用开发提供便利。