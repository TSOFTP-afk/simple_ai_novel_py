# Simple AI Novel App — Code Wiki

> 面向长篇小说创作的本地桌面工作台，技术栈 `Python 3.13 + PyQt6 + SQLite3`。
> 当前版本：Beta 3.2

---

## 目录

1. [项目概览](#1-项目概览)
2. [项目架构](#2-项目架构)
3. [目录结构](#3-目录结构)
4. [启动流程](#4-启动流程)
5. [核心模块详解](#5-核心模块详解)
   - 5.1 [main.py — 应用入口](#51-mainpy--应用入口)
   - 5.2 [database.py — 数据持久层](#52-databasepy--数据持久层)
   - 5.3 [ai_service.py — AI 服务层](#53-ai_servicepy--ai-服务层)
   - 5.4 [qt_app.py — PyQt6 主窗口](#54-qt_apppy--pyqt6-主窗口)
   - 5.5 [exporter.py — 书籍导出](#55-exporterpy--书籍导出)
   - 5.6 [text_importer.py — 智能导入](#56-text_importerpy--智能导入)
   - 5.7 [research_sources.py — 调研源池](#57-research_sourcespy--调研源池)
   - 5.8 [secure_storage.py — 安全存储](#58-secure_storagepy--安全存储)
6. [Qt 子模块详解](#6-qt-子模块详解)
   - 6.1 [qt/workers.py — 后台线程 Worker](#61-qtworkerspy--后台线程-worker)
   - 6.2 [qt/helpers.py — 工具函数](#62-qthelperspy--工具函数)
   - 6.3 [qt/theme.py — 主题与样式](#63-qtthemepy--主题与样式)
   - 6.4 [qt/star_graph.py — 人物关系星图](#64-qtstar_graphpy--人物关系星图)
   - 6.5 [qt/dialogs.py — 通用对话框](#65-qtdialogspy--通用对话框)
   - 6.6 [qt/chat_dialog.py — AI 对话窗口](#66-qtchat_dialogpy--ai-对话窗口)
   - 6.7 [qt/image_utils.py — 图片适配](#67-qtimage_utilspy--图片适配)
   - 6.8 [qt/state.py — Qt 状态快照](#68-qtstatepy--qt-状态快照)
7. [Core 基础设施模块](#7-core-基础设施模块)
   - 7.1 [core/event_bus.py — 事件总线](#71-coreevent_buspy--事件总线)
   - 7.2 [core/service_locator.py — 服务定位器](#72-coreservice_locatorpy--服务定位器)
   - 7.3 [core/state.py — 状态管理器](#73-corestatepy--状态管理器)
8. [State 模块](#8-state-模块)
9. [Theme 设计系统模块](#9-theme-设计系统模块)
10. [数据库 Schema](#10-数据库-schema)
11. [依赖关系](#11-依赖关系)
12. [AI 用途分离机制](#12-ai-用途分离机制)
13. [多智能体审查/生成流程](#13-多智能体审查生成流程)
14. [安全护栏机制](#14-安全护栏机制)
15. [项目运行与构建](#15-项目运行与构建)

---

## 1. 项目概览

Simple AI Novel App 是一款面向长篇小说创作的本地桌面工作台，核心能力包括：

| 能力域 | 功能 |
|--------|------|
| 作品管理 | 书籍/卷/章节目录管理、大纲编辑、封面设置 |
| 正文编辑 | 章节正文编辑、字数统计、自动保存 |
| AI 辅助写作 | 草稿生成、续写、润色、大纲同步 |
| AI 概率检测 | 章节正文 AI 生成概率评估与分级标识 |
| 多智能体审查 | 章节级/卷级/全书批量审查，含安全护栏 |
| 多智能体生成 | 大纲拆解→场景规划→正文写手→审查→修订→校验 |
| Skills 提炼 | 从参考书/开源项目提炼抽象写作技法 |
| 人物与世界观 | 人物卡、人物关系星图、世界观条目 |
| 章节快照 | 编辑前自动创建快照，支持回滚 |
| 智能导入 | TXT/DOCX 长文本自动分章、分卷、提炼大纲 |
| 书籍导出 | TXT / Markdown / DOCX 三种格式 |
| 主题系统 | 亮色/暗色/护眼/自定义，支持背景图玻璃拟态 |

---

## 2. 项目架构

```
┌─────────────────────────────────────────────────────────┐
│                      main.py (入口)                      │
│  初始化 Database → 初始化 AIService → 启动 Qt 应用       │
└──────────────────────────┬──────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐
   │  database   │  │ ai_service  │  │     qt_app       │
   │  (数据层)   │  │  (AI 层)    │  │   (表现层)       │
   └──────┬──────┘  └──────┬──────┘  └────────┬─────────┘
          │                │                   │
          │         ┌──────┴──────┐     ┌──────┴──────┐
          │         │  OpenAI API │     │  qt 子模块  │
          │         │  (HTTP)     │     │  workers    │
          │         └─────────────┘     │  helpers    │
          │                             │  theme      │
          │                             │  star_graph │
          │                             │  dialogs    │
          │                             │  chat_dialog│
          │                             │  image_utils│
          │                             │  state      │
          │                             └─────────────┘
          │
    ┌─────┴──────────────────────────────┐
    │            SQLite (novels.db)       │
    │  books / volumes / chapters / ...  │
    └────────────────────────────────────┘
```

**分层原则：**

- **数据层** (`database.py`)：纯 SQLite 操作，不依赖 Qt 和 AI
- **AI 层** (`ai_service.py`)：OpenAI 兼容 API 交互，不依赖 Qt
- **表现层** (`qt_app.py` + `qt/`)：PyQt6 GUI，依赖数据层和 AI 层
- **基础设施层** (`core/`)：事件总线、服务定位器、状态管理器（预留扩展）

---

## 3. 目录结构

```
simple_ai_novel_py/
├── main.py                          # 应用入口
├── requirements.txt                 # pip 依赖声明
├── novel_app/                       # 核心应用包
│   ├── __init__.py
│   ├── ai_service.py                # AI 服务（OpenAI 兼容）
│   ├── database.py                  # SQLite 数据持久层
│   ├── exporter.py                  # 书籍导出（TXT/MD/DOCX）
│   ├── qt_app.py                    # PyQt6 主窗口（~5000行）
│   ├── text_importer.py             # 智能文本导入与分章
│   ├── research_sources.py          # 开源项目调研源池
│   ├── secure_storage.py            # Windows DPAPI 密钥保护
│   ├── qt/                          # Qt 子模块
│   │   ├── __init__.py
│   │   ├── chat_dialog.py           # AI 多轮对话窗口
│   │   ├── dialogs.py               # 通用对话框
│   │   ├── helpers.py               # 工具函数
│   │   ├── image_utils.py           # 图片适配显示
│   │   ├── star_graph.py            # 人物关系星图
│   │   ├── state.py                 # Qt 状态快照
│   │   ├── theme.py                 # 主题与样式表
│   │   └── workers.py               # 后台线程 Worker
│   ├── core/                        # 基础设施（预留扩展）
│   │   ├── __init__.py
│   │   ├── event_bus.py             # 事件总线
│   │   ├── service_locator.py       # 服务定位器
│   │   └── state.py                 # 状态管理器
│   ├── state/                       # 应用状态
│   │   ├── __init__.py
│   │   └── app_state.py             # 集中式应用状态
│   └── theme/                       # 设计系统
│       ├── __init__.py
│       ├── colors.py                # 色彩调色板
│       ├── design_tokens.py         # 设计令牌
│       ├── spacing.py               # 间距系统
│       └── typography.py            # 字体系统
├── data/                            # 运行时数据目录
│   ├── novels.db                    # 默认 SQLite 数据库
│   ├── media/                       # 媒体资源
│   ├── exports/                     # 导出文件
│   └── references/                  # 参考资料存储
├── vendor/                          # 内嵌第三方库
│   ├── PyQt6/                       # Qt6 绑定
│   ├── PIL/ (Pillow)               # 图像处理
│   ├── docx/ (python-docx)         # DOCX 读写
│   ├── lxml/                        # XML 解析
│   └── ...
├── packaging/                       # 打包脚本
├── release/                         # 构建产物
├── tools/                           # 运维工具
├── docs/                            # 项目文档
└── test_*.py                        # 单元测试
```

---

## 4. 启动流程

```
main.py
  │
  ├─ 1. 将 vendor/ 加入 sys.path（内嵌依赖优先加载）
  │
  ├─ 2. Database() → SQLite 连接
  │     └─ database.initialize()
  │         ├─ 创建全部表（books, volumes, chapters, ...）
  │         ├─ _migrate_schema() → 增量迁移缺失列
  │         ├─ _normalize_all_volume_orders() → 修整卷排序
  │         └─ _normalize_all_chapter_orders() → 修整章排序
  │
  ├─ 3. SimpleAIService.from_env() → AI 服务
  │     └─ 读取 OPENAI_API_KEY / OPENAI_BASE_URL / OPENAI_MODEL
  │
  ├─ 4. 烟雾测试出口（SIMPLE_AI_NOVEL_SMOKE_EXIT=1）
  │
  └─ 5. run_qt_app(database, ai_service) → PyQt6 主循环
        └─ raise SystemExit(app.exec())
```

---

## 5. 核心模块详解

### 5.1 main.py — 应用入口

**职责**：应用启动编排，初始化核心服务并启动 GUI。

| 函数 | 说明 |
|------|------|
| `main()` | 入口函数：初始化 DB → 初始化 AI → 启动 Qt 应用 |

**关键逻辑**：
- `vendor/` 目录优先加入 `sys.path`，实现内嵌依赖免安装加载
- 支持 `SIMPLE_AI_NOVEL_SMOKE_EXIT=1` 环境变量做冒烟测试
- `finally` 块确保数据库连接关闭

---

### 5.2 database.py — 数据持久层

**职责**：封装全部 SQLite 操作，提供书籍/卷/章节/人物/世界观/审查等实体的 CRUD。

#### 关键类：`Database`

| 方法分组 | 方法 | 说明 |
|----------|------|------|
| **初始化** | `__init__(db_path)` | 确定数据目录、创建子目录、连接 SQLite |
| | `initialize()` | 建表、迁移、排序修整 |
| | `_migrate_schema()` | 增量列迁移（`_ensure_column`） |
| | `close()` | 关闭连接 |
| **书籍** | `list_books()` / `create_book()` / `get_book()` / `rename_book()` / `update_book_outline()` / `update_book_cover()` / `delete_book()` | 书籍 CRUD |
| **卷** | `list_volumes()` / `create_volume()` / `get_volume()` / `rename_volume()` / `update_volume_outline()` / `delete_volume()` / `move_volume()` | 卷 CRUD + 排序交换 |
| **章节** | `list_chapters()` / `create_chapter()` / `get_chapter()` / `rename_chapter()` / `delete_chapter()` / `update_chapter()` / `move_chapter()` / `update_chapter_volume()` / `update_chapter_summary()` / `update_chapter_ai_probability()` | 章节 CRUD + 排序 + AI 概率 |
| **章节标签** | `set_chapter_tag()` / `remove_chapter_tag()` / `has_chapter_tag()` / `list_template_chapters()` | 标签系统（template 等） |
| **AI 区间** | `list_chapter_ai_spans()` / `add_chapter_ai_span()` / `delete_chapter_ai_spans()` / `delete_chapter_ai_spans_in_range()` | AI 生成文本区间追踪 |
| **快照** | `create_snapshot()` / `list_snapshots()` / `get_snapshot()` | 章节快照（审查/生成前自动创建） |
| **审查** | `create_review_run()` / `replace_review_findings()` / `list_review_runs()` / `get_review_run()` / `list_review_findings()` | 审查运行与发现项 |
| **章节事件** | `list_chapter_events()` / `create_chapter_event()` / `update_chapter_event()` / `delete_chapter_event()` | 时间轴事件 |
| **参考源** | `list_reference_sources()` / `create_reference_source()` / `get_reference_source()` / `get_reference_source_by_url()` | 参考资料管理 |
| **Skills** | `replace_skills_for_source()` / `list_skills()` / `bind_skill_to_book()` / `unbind_skill_from_book()` / `list_bound_skills_for_book()` / `bind_skill_to_chapter()` / `unbind_skill_from_chapter()` / `list_bound_skills_for_chapter()` | Skills 提炼与绑定 |
| **人物** | `list_characters()` / `create_character()` / `get_character()` / `update_character()` / `update_character_image()` / `update_character_position()` / `delete_character()` | 人物卡 CRUD |
| **人物关系** | `list_relationships()` / `get_relationship()` / `create_relationship()` / `update_relationship()` / `delete_relationship()` / `list_relationships_by_character()` | 关系 CRUD |
| **世界观** | `list_world_entries()` / `create_world_entry()` / `get_world_entry()` / `update_world_entry()` / `delete_world_entry()` | 世界观条目 CRUD |
| **导出** | `get_book_export_data()` | 聚合导出数据 |
| **路径** | `normalize_media_path()` / `resolve_media_path()` | 媒体路径处理 |

**常量**：
- `ALL_VOLUMES = "__all__"` — 查询所有卷的章节
- `UNASSIGNED_VOLUMES = "__unassigned__"` — 查询未分卷章节

**排序机制**：卷和章节使用 `sort_order` 整数字段排序，删除/移动后自动重整序号（`_normalize_volume_order` / `_normalize_chapter_order`）。

---

### 5.3 ai_service.py — AI 服务层

**职责**：封装 OpenAI 兼容 API 交互，支持远程调用与本地 Mock 双模式。

#### 关键类：`SimpleAIService`

| 方法 | 说明 |
|------|------|
| `from_env()` | 类方法，从环境变量创建实例 |
| `configure(api_key, base_url, model)` | 配置 API 参数 |
| `is_remote_configured()` | 检查远程 API 是否可用 |
| `get_mode_label()` | 返回当前模式标签（远程/Mock） |
| `require_remote(purpose)` | 强制要求远程配置，否则抛异常 |
| `stream_chat(messages, cancel_event, require_remote)` | 流式多轮对话 |
| `clone()` | 克隆服务实例（用途隔离） |
| **写作生成** | | 
| `generate_draft(...)` | 草稿生成（委托多智能体生成） |
| `continue_writing(...)` | 续写 |
| `polish_text(...)` | 润色 |
| `stream_generate(mode, ...)` | 统一流式生成入口（draft/continue/polish） |
| `summarize_chapter(...)` | 章节摘要生成 |
| **Skills 提炼** | |
| `distill_skills(...)` | 从参考文本提炼 Skills |
| `distill_project_skills(...)` | 从开源项目提炼 Skills |
| **分析** | |
| `analyze_document(text, require_remote)` | 文档分类（body/outline/character/world） |
| `detect_ai_probability(text)` | AI 概率检测 |
| `analyze_book(...)` | 全书分析 |
| **多智能体** | |
| `multi_agent_review(...)` | 多智能体审查 |
| `multi_agent_generate_from_outline(...)` | 多智能体生成 |
| **内部方法** | |
| `_post_chat_completion(messages, temperature)` | 同步 Chat Completion 请求 |
| `_stream_chat_completion(messages, temperature, cancel_event)` | 流式 Chat Completion 请求 |
| `_extract_json_payload(text)` | 从模型输出提取 JSON 数组 |
| `_extract_json_object_payload(text)` | 从模型输出提取 JSON 对象 |
| `_normalize_review_payload(payload, ...)` | 标准化审查/生成结果，含安全护栏 |
| `_format_skill_block(selected_skills)` | 格式化 Skills 提示词块 |
| `_build_remote_generation_prompt(mode, ...)` | 构建远程生成提示词 |

#### 辅助类：`SkillCard`

```python
@dataclass
class SkillCard:
    name: str          # 技法名称
    category: str      # 分类
    summary: str       # 摘要
    instruction: str   # 执行指令
    use_cases: str     # 适用场景
    risk_note: str     # 风险提示
```

**Mock 机制**：每个远程方法都有对应的 `_xxx_mock` 实现，在 API 不可用时提供本地兜底。Mock 返回结构化的占位内容，保证应用不会因缺少 API 而崩溃。

**AI 概率分级**：

| 概率范围 | 级别 | 含义 |
|----------|------|------|
| 92-100 | `certain` | 几乎确定 AI 生成 |
| 68-91 | `high` | 高风险 |
| 42-67 | `medium` | 中等风险 |
| 18-41 | `low` | 低风险 |
| 0-17 | `none` | 无明显 AI 痕迹 |

---

### 5.4 qt_app.py — PyQt6 主窗口

**职责**：应用主界面，约 5000 行，包含全部 GUI 交互逻辑。

#### 关键类：`NovelMainWindow(QMainWindow)`

这是整个应用的核心窗口类，整合了以下功能区域：

| 区域 | 说明 |
|------|------|
| 左侧目录树 | 书籍/卷/章节层级导航（QTreeView） |
| 中央编辑区 | 章节大纲 + 正文编辑（QPlainTextEdit） |
| 右侧抽屉 | 概览/大纲/人物/星图/世界观/Skills/审查/任务 8 个 Tab |
| 顶部工具栏 | AI 操作按钮、模式切换 |
| 底部状态栏 | 字数统计、AI 模式、任务进度 |

#### 其他对话框类

| 类 | 说明 |
|----|------|
| `ViewSettingsDialog` | 视图配置（主题预设、自定义颜色、AI 标识颜色、背景图） |
| `AiSettingsDialog`（qt/dialogs.py） | AI 设置（按用途分离的 API 配置） |

#### 关键常量

| 常量 | 说明 |
|------|------|
| `AI_PURPOSES` | AI 用途列表（writing/outline/detector/import/skills/book_analysis/review/chat） |
| `AI_MODE_PURPOSE` | 写作模式到用途的映射 |
| `THEME_PRESET_LABELS` | 主题预设选项 |
| `THEME_COLOR_FIELDS` | 可自定义颜色字段 |
| `DRAWER_TAB_SEQUENCE` | 右侧抽屉 Tab 顺序 |

---

### 5.5 exporter.py — 书籍导出

**职责**：将书籍数据导出为 TXT / Markdown / DOCX 格式。

#### 关键类：`BookExporter`

| 方法 | 说明 |
|------|------|
| `export_txt(book_id, output_path)` | 导出全书为 TXT |
| `export_markdown(book_id, output_path)` | 导出全书为 Markdown |
| `export_docx(book_id, output_path)` | 导出全书为 DOCX |
| `export_chapter_txt(chapter_id, output_path)` | 导出单章为 TXT |
| `export_chapter_markdown(chapter_id, output_path)` | 导出单章为 Markdown |
| `export_chapter_docx(chapter_id, output_path)` | 导出单章为 DOCX |

**导出结构**：书名 → 书籍大纲 → 人物卡 → 世界观 → 正文（按卷分组，按章节排列）

**DOCX 支持**：通过 `vendor/docx`（python-docx）实现，缺失时抛出 `RuntimeError`。

---

### 5.6 text_importer.py — 智能导入

**职责**：将长文本（TXT/DOCX）自动解析为结构化的书籍（卷 + 章节 + 大纲）。

#### 关键数据类

```python
@dataclass(frozen=True)
class ParsedChapter:
    title: str
    content: str
    outline: str
    volume_title: str | None = None

@dataclass(frozen=True)
class ParsedBook:
    title: str
    outline: str
    chapters: list[ParsedChapter]
```

#### 关键函数：`parse_long_text(book_title, raw_text) -> ParsedBook`

**解析策略**：

1. **标题检测**：识别中文/英文章节标题（第X章、Chapter X、序章、番外等）
2. **卷级检测**：识别卷标题（第X卷、Volume X 等）
3. **隐式分章**：无明确标题时按段落长度自动分块（4500字目标，6800字硬上限）
4. **大纲提炼**：从正文首句、中句、末句自动生成章节大纲
5. **总纲生成**：汇总卷结构、章节数、字数

**正则模式**：

| 模式 | 匹配目标 |
|------|----------|
| `_VOLUME_RE` | 卷标题（第X卷、Volume X） |
| `_STRONG_CHAPTER_RE` | 强章节标题（第X章、Chapter X、序章、番外） |
| `_ACT_RE` | 幕标题（第X幕） |
| `_PIPE_SECTION_RE` | 竖线分隔章节（\|X\| 标题） |
| `_NUMBERED_SECTION_RE` | 数字编号章节（1. 标题） |

---

### 5.7 research_sources.py — 调研源池

**职责**：维护开源 AI 写作项目的调研数据，供 Skills 提炼使用。

#### 关键数据：`GITHUB_RESEARCH_POOL`

内置 7 个调研项目（OpenWrite、AugmentedQuill、Writingway2、NovelForge、AI_NovelGenerator、WriteHERE、autonovel），每项包含：

| 字段 | 说明 |
|------|------|
| `title` | 项目名 |
| `url` / `repo_url` | 项目地址 |
| `license` | 许可状态 |
| `reuse_level` | 复用级别（默认 `pattern_only`） |
| `focus` | 关注方向 |
| `patterns` | 可提炼模式列表 |
| `risk_note` | 风险提示 |

#### 关键函数：`render_research_note(project) -> str`

将调研项目渲染为 Markdown 笔记。

---

### 5.8 secure_storage.py — 安全存储

**职责**：使用 Windows DPAPI 保护敏感数据（如 API Key）。

| 函数 | 说明 |
|------|------|
| `protect_secret(secret) -> str` | 加密秘密，返回 `dpapi:` 前缀的 Base64 字符串 |
| `unprotect_secret(value) -> str` | 解密秘密，非 Windows 原样返回 |

**实现**：通过 `ctypes` 调用 Windows `crypt32.dll` 的 `CryptProtectData` / `CryptUnprotectData`。

---

## 6. Qt 子模块详解

### 6.1 qt/workers.py — 后台线程 Worker

**职责**：将耗时 AI 操作移至 QThread，避免阻塞 UI。

#### `AiWorker(QObject)`

| 信号 | 说明 |
|------|------|
| `chunk(str)` | 流式文本片段 |
| `log(str)` | 日志消息 |
| `done(str)` | 完成消息 |
| `error(str)` | 错误消息 |
| `cancelled(str)` | 取消消息 |

**支持模式**：`draft`（草稿）、`continue`（续写）、`polish`（润色）、`summary`（大纲同步）

#### `FunctionWorker(QObject)`

通用后台任务执行器，支持传入回调函数、日志回调和取消事件。

| 信号 | 说明 |
|------|------|
| `done(object)` | 任务完成，携带返回值 |
| `error(str)` | 错误消息 |
| `log(str)` | 日志消息 |
| `cancelled(str)` | 取消消息 |

---

### 6.2 qt/helpers.py — 工具函数

| 函数 | 说明 |
|------|------|
| `row_to_dict(row)` | sqlite3.Row → dict |
| `normalize_ai_color_config(overrides)` | 合并 AI 概率颜色配置 |
| `set_ai_probability_meta(overrides)` | 设置全局 AI 概率颜色 |
| `get_ai_probability_meta(overrides)` | 获取 AI 概率颜色 |
| `normalize_ai_probability_pair(level, probability)` | 标准化 AI 概率级别对 |
| `format_chapter_tree_title(sort_order, title)` | 格式化目录树章节标题 |
| `format_chapter_tree_display_title(...)` | 格式化目录树显示标题（含字数、模板标记） |
| `count_text_characters(text)` | 统计有效字符数（去空白） |
| `compute_template_stats(content)` | 计算模板统计（字数、对话密度、描写比例） |

**AI 概率颜色默认值** (`DEFAULT_AI_PROBABILITY_META`)：

| 级别 | 标签 | 文字色 | 背景色 | 目录色 |
|------|------|--------|--------|--------|
| certain | AI 100% | #FFFFFF | #D83A34 | #C92A2A |
| high | AI 高 | #3A2A00 | #F2C94C | #B7791F |
| medium | AI 中 | #3A2A00 | #F7D774 | #B7791F |
| low | AI 低 | #FFFFFF | #2FA66A | #258A55 |
| none | AI 无 | #FFFFFF | #2F80ED | #2F80ED |

---

### 6.3 qt/theme.py — 主题与样式

**职责**：定义主题令牌并生成全局 QSS 样式表。

#### 关键类：`ThemeTokens`

```python
@dataclass(frozen=True)
class ThemeTokens:
    mode: str           # "light" / "dark"
    bg: str             # 底层背景
    surface: str        # 主面板
    surface_alt: str    # 次级面板
    text: str           # 正文文字
    muted: str          # 弱提示文字
    primary: str        # 强调色
    primary_soft: str   # 强调浅色
    success: str        # 成功
    warning: str        # 警告
    danger: str         # 危险
    border: str         # 边框
    focus: str          # 聚焦光圈
    editor_bg: str      # 正文编辑区
```

#### 预设主题

| 代码 | 名称 | 模式 |
|------|------|------|
| `white` | 白色亮色 | light |
| `light_blue` | 浅蓝亮色（默认） | light |
| `night` | 暗色夜间 | dark |
| `sepia` | 米黄护眼 | light |

#### 关键函数

| 函数 | 说明 |
|------|------|
| `get_theme(mode)` | 获取预设主题令牌 |
| `build_stylesheet(tokens, background_image)` | 生成完整 QSS 样式表 |

**玻璃拟态**：当设置背景图时，面板/卡片/抽屉自动切换为半透明模式（`_rgba` 函数控制透明度）。

**滚动条**：轨道透明，宽度 6px，滑块使用 `muted` 色，悬停高亮。

---

### 6.4 qt/star_graph.py — 人物关系星图

**职责**：可视化展示书籍人物关系网络。

#### 关键类

| 类 | 说明 |
|----|------|
| `CharacterNodeItem(QGraphicsItem)` | 人物节点（可拖拽、可选中、可建立关系） |
| `RelationshipEdgeItem(QGraphicsPathItem)` | 关系连线（贝塞尔曲线 + 箭头 + 标签） |
| `StarGraphView(QGraphicsView)` | 星图画布（缩放、平移、关系模式） |
| `StarGraphWidget(QWidget)` | 星图容器（工具栏 + 画布 + 时间轴） |

#### `StarGraphView` 信号

| 信号 | 说明 |
|------|------|
| `createCharacterRequested(x, y)` | 请求创建人物 |
| `characterMoved(id, x, y)` | 人物位置变更 |
| `relationshipRequested(source_id, target_id)` | 请求建立关系 |
| `editCharacterRequested(id)` | 请求编辑人物 |
| `deleteCharacterRequested(id)` | 请求删除人物 |
| `editRelationshipRequested(id)` | 请求编辑关系 |
| `deleteRelationshipRequested(id)` | 请求删除关系 |
| `connectModeChanged(enabled)` | 关系模式切换 |

#### 布局算法

- **度数布局**（`_apply_degree_layout`）：关系最多的角色居中，关联角色环形排列，其余角色网格排列
- **网格布局**（`_apply_grid_layout`）：无关系时均匀网格排列
- **环形布局**（`_place_ring`）：关联角色围绕焦点角色排列

#### 辅助函数：`ask_relationship_type(parent, default) -> str | None`

弹出对话框输入关系类型。

---

### 6.5 qt/dialogs.py — 通用对话框

| 函数/类 | 说明 |
|---------|------|
| `ask_text(parent, title, prompt, initial)` | 单行文本输入对话框 |
| `ask_multiline(parent, title, prompt, initial)` | 多行文本输入对话框 |
| `confirm(parent, title, message, danger)` | 确认对话框（支持危险模式） |
| `info(parent, title, message)` | 信息提示 |
| `error(parent, title, message)` | 错误提示 |
| `ask_unsaved(parent)` | 未保存修改三选一（保存/不保存/取消） |
| `AiSettingsDialog` | AI 设置对话框（按用途分 Tab 配置 API） |

---

### 6.6 qt/chat_dialog.py — AI 对话窗口

**职责**：提供独立的多轮 AI 对话界面。

#### 关键类

| 类 | 说明 |
|----|------|
| `ChatStreamWorker(QObject)` | 对话流式 Worker（QThread 中运行） |
| `ChatDialog(QDialog)` | 对话窗口（气泡式 UI、流式输出、取消支持） |

**特性**：
- 非模态窗口，可同时编辑和对话
- 自动注入书籍上下文（`context_builder` 回调）
- 保留最近 12 条对话历史
- 50ms 定时刷新待显示文本，避免频繁 UI 更新

---

### 6.7 qt/image_utils.py — 图片适配

| 函数 | 说明 |
|------|------|
| `set_adaptive_image(label, image_path, placeholder, max_width, max_height, crop)` | 自适应图片显示 |

**特性**：支持等比缩放和裁剪模式，居中绘制在透明画布上。

---

### 6.8 qt/state.py — Qt 状态快照

```python
@dataclass
class QtAppState:
    selected_book_id: int | None
    selected_book_title: str
    selected_volume_id: int | None
    selected_chapter_id: int | None
    current_node_kind: str
    editor_scope_kind: str | None
    editor_scope_id: int | None
    editor_dirty: bool
    task_running: bool
    drawer_kind: str
    theme_mode: str
```

用于在 Qt 组件间传递当前 UI 状态的轻量数据类。

---

## 7. Core 基础设施模块

> 预留的扩展基础设施，当前主流程未直接使用，为后续重构解耦准备。

### 7.1 core/event_bus.py — 事件总线

| 类/函数 | 说明 |
|---------|------|
| `EventBus` | 事件总线核心类（subscribe/unsubscribe/publish） |
| `get_event_bus()` | 获取全局实例 |
| `subscribe(event_type, callback)` | 全局订阅快捷方式 |
| `unsubscribe(event_type, callback)` | 全局取消订阅快捷方式 |
| `publish(event_type, *args, **kwargs)` | 全局发布快捷方式 |

### 7.2 core/service_locator.py — 服务定位器

| 类/函数 | 说明 |
|---------|------|
| `ServiceLocator` | 服务定位器核心类（register/register_factory/get/has/remove） |
| `get_service_locator()` | 获取全局实例 |
| `register_service(name, service)` | 全局注册快捷方式 |
| `get_service(name)` | 全局获取快捷方式 |

### 7.3 core/state.py — 状态管理器

| 类/函数 | 说明 |
|---------|------|
| `StateProperty[T]` | 状态属性（值 + 验证器 + 默认值） |
| `StateManager` | 状态管理器（register_property/get/set/reset） |
| `get_state_manager()` | 获取全局实例 |
| `register_state_property(name, initial_value, validator)` | 全局注册快捷方式 |
| `get_state(name)` / `set_state(name, value)` | 全局读写快捷方式 |

状态变更时通过 `EventBus` 发布 `state:{name}` 和 `state:changed` 事件。

---

## 8. State 模块

### app_state.py — 集中式应用状态

#### `AppState`

完整的可变应用状态数据类，包含：

| 分组 | 字段 |
|------|------|
| 选择状态 | `selected_book_id`, `selected_book_title`, `selected_volume_id`, `selected_chapter_id`, `selected_character_id`, `selected_world_entry_id` |
| 导航状态 | `current_tree_iid`, `current_node_kind` |
| 编辑器状态 | `editor_scope_kind`, `editor_scope_id`, `editor_content`, `editor_outline`, `editor_summary`, `editor_dirty`, `editor_save_time`, `editor_word_count` |
| 工作区 | `workspace_mode`, `sidebar_collapsed`, `sidebar_width`, `context_panel_visible`, `context_panel_width`, `context_panel_tab`, `focus_mode` |
| 任务状态 | `task_running`, `task_name`, `task_detail`, `task_generated_chars` |
| AI 状态 | `ai_remote_enabled`, `ai_api_key`, `ai_base_url`, `ai_model`, `ai_mode_label`, `active_skills_label`, `bound_skill_count` |

#### `StateStore`

状态存储器，管理 `AppState` 实例和变更监听器：

| 方法 | 说明 |
|------|------|
| `get(key)` / `set(key, value)` | 读写状态 |
| `update(**kwargs)` | 批量更新 |
| `on_change(key, callback)` / `off_change(key, callback)` | 监听变更 |
| `clear_book_context()` | 清空书籍相关状态 |
| `is_chapter_active()` / `is_book_active()` / `has_management_scope()` | 状态判断 |

---

## 9. Theme 设计系统模块

### colors.py — 色彩调色板

`ColorPalette` 数据类定义 21 个色彩槽位，提供 `LIGHT_PALETTE` 和 `DARK_PALETTE` 两套预设。

### design_tokens.py — 设计令牌

完整的 Design Token 体系：

| 令牌类 | 说明 |
|--------|------|
| `ColorTokens` | 色彩令牌（21 个色值） |
| `FontTokens` | 字体令牌（家族、大小、权重） |
| `SpacingTokens` | 间距令牌（xs~xl3，7 级） |
| `BorderTokens` | 边框令牌（圆角、宽度） |
| `ShadowTokens` | 阴影令牌（sm~xl，4 级） |
| `DesignTokens` | 令牌集合（聚合以上全部） |

### spacing.py — 间距系统

`SpacingScale` + `SpacingSystem`，提供 `xs(4)` ~ `xl3(48)` 的 7 级间距。

### typography.py — 字体系统

`FontScale` + `FontSystem`，提供 `display` ~ `code` 的 8 级字体规格，支持 `scaled(factor)` 缩放。

---

## 10. 数据库 Schema

```
books
├── id (PK)
├── title
├── outline_text
├── cover_image_path
└── created_at

volumes
├── id (PK)
├── book_id (FK → books)
├── title
├── outline_text
├── sort_order
├── created_at
└── updated_at

chapters
├── id (PK)
├── book_id (FK → books)
├── volume_id (FK → volumes, SET NULL)
├── title
├── outline
├── content
├── summary_text
├── ai_probability (0-100)
├── ai_probability_level (certain/high/medium/low/none)
├── sort_order
└── updated_at

characters
├── id (PK)
├── book_id (FK → books)
├── name
├── role
├── profile_text
├── image_path
├── graph_x, graph_y
├── created_at
└── updated_at

character_relationships
├── id (PK)
├── book_id (FK → books)
├── source_character_id (FK → characters)
├── target_character_id (FK → characters)
├── relationship_type
├── description
├── created_at
└── updated_at

world_entries
├── id (PK)
├── book_id (FK → books)
├── name
├── category
├── content_text
├── created_at
└── updated_at

chapter_snapshots
├── id (PK)
├── chapter_id (FK → chapters)
├── label
├── outline
├── content
└── created_at

chapter_tags
├── chapter_id (PK, FK → chapters)
├── tag (PK)
└── created_at

chapter_ai_spans
├── id (PK)
├── chapter_id (FK → chapters)
├── start_offset
├── end_offset
├── source_task_id
└── created_at

chapter_events
├── id (PK)
├── book_id (FK → books)
├── chapter_id (FK → chapters)
├── label
├── description
├── sort_order
├── created_at
└── updated_at

reference_sources
├── id (PK)
├── title
├── author
├── source_path
├── rights_note
├── source_type
├── source_url
├── source_license
├── reusable_level
├── attribution_note
└── created_at

distilled_skills
├── id (PK)
├── source_id (FK → reference_sources)
├── name
├── category
├── summary
├── instruction_text
├── use_cases_text
├── risk_note
└── created_at

skill_bindings
├── id (PK)
├── scope_type (book/chapter)
├── scope_id
├── skill_id (FK → distilled_skills)
├── weight
└── created_at

review_runs
├── id (PK)
├── book_id (FK → books)
├── chapter_id (FK → chapters)
├── scope_type
├── status
├── truth_snapshot
├── summary
├── overall_score (0-100)
├── snapshot_id (FK → chapter_snapshots)
├── revised_content
├── revised_outline
├── final_verdict (approve/reject)
├── template_comparison
├── risk_notes
├── created_at
├── updated_at
└── applied_at

review_findings
├── id (PK)
├── run_id (FK → review_runs)
├── agent
├── severity (high/medium/low)
├── category
├── location_hint
├── quote_text
├── issue_text
├── suggestion_text
└── created_at
```

---

## 11. 依赖关系

### 声明依赖（requirements.txt）

| 包 | 版本 | 用途 |
|----|------|------|
| `PyQt6` | 6.11.0 | GUI 框架 |
| `python-docx` | 1.1.2 | DOCX 导入/导出 |

### 内嵌依赖（vendor/）

| 包 | 用途 |
|----|------|
| `PyQt6` | Qt6 绑定 + Qt6 运行时 DLL |
| `Pillow` (PIL) | 图像处理（封面、人物头像） |
| `python-docx` (docx) | DOCX 读写 |
| `lxml` | XML 解析（python-docx 依赖） |
| `typing_extensions` | 类型扩展 |
| `ttkbootstrap` | 残留（旧 UI，已弃用） |

### 标准库依赖

| 模块 | 用途 |
|------|------|
| `sqlite3` | 数据库 |
| `urllib.request` | HTTP 请求（AI API） |
| `ctypes` (Windows) | DPAPI 密钥保护 |
| `json` / `re` / `pathlib` / `threading` | 基础工具 |

### 模块间依赖图

```
qt_app ──→ database
       ──→ ai_service
       ──→ exporter ──→ database
       ──→ text_importer
       ──→ research_sources
       ──→ secure_storage
       ──→ qt/workers ──→ ai_service
       ──→ qt/helpers
       ──→ qt/theme
       ──→ qt/star_graph
       ──→ qt/dialogs
       ──→ qt/chat_dialog ──→ ai_service
       ──→ qt/image_utils
       ──→ qt/state

ai_service ──→ (urllib, json, re)  # 无内部依赖

database ──→ (sqlite3, os, sys)  # 无内部依赖
```

---

## 12. AI 用途分离机制

AI 设置按用途（purpose）分离，每个用途独立配置 API Key / Base URL / Model：

| 用途代码 | 标签 | 对应功能 |
|----------|------|----------|
| `writing` | 写作生成 | 草稿、续写、润色 |
| `outline` | 同步大纲 | 章节摘要生成 |
| `detector` | AI概率检测 | AI 概率检测 |
| `import` | 智能导入分类 | 文档分类 |
| `skills` | Skills提炼 | 参考书/项目 Skills 提炼 |
| `book_analysis` | 全书分析 | 全书分析 |
| `review` | 多智能体审查 | 审查 + 多智能体生成 |
| `chat` | AI 对话 | 多轮对话 |

**规则**：未配置对应用途时，该功能不可执行（不会回退到本地 Mock）。

---

## 13. 多智能体审查/生成流程

### 审查流程

```
用户触发审查
  │
  ├─ 创建章节快照（chapter_snapshots）
  │
  ├─ 构建 Truth File（书名+章节+大纲+正文+设定+人物+世界观）
  │
  ├─ 调用 AI（review 用途）
  │   └─ 模拟多智能体流水线：
  │       上下文整理器 → 剧情审查员 → 连续性审查员
  │       → 文风审查员 → 修订智能体 → 最终校验员
  │
  ├─ _normalize_review_payload() 安全护栏检查
  │
  ├─ 写入 review_runs + review_findings
  │
  └─ UI 展示审查结果（右侧审查抽屉）
```

### 生成流程

```
用户触发生成
  │
  ├─ 创建章节快照
  │
  ├─ 构建 Truth File + Sourcebook 上下文 + Skills
  │
  ├─ 调用 AI（review 用途）
  │   └─ 模拟多智能体生成流水线：
  │       大纲拆解员 → 场景规划员 → 正文写手
  │       → 剧情审查员 → 连续性审查员 → 文风修订员 → 最终校验员
  │
  ├─ _normalize_review_payload() 安全护栏检查
  │
  └─ 写入 review_runs + review_findings
```

---

## 14. 安全护栏机制

`_normalize_review_payload()` 实现了多层安全护栏，防止 AI 输出意外覆盖作者原文：

| 护栏 | 条件 | 动作 |
|------|------|------|
| 空正文护栏 | `revised_content` 为空 | 强制 `reject`，保留原文，插入 `safety_gate` 发现项 |
| 缩短护栏 | 正文缩短超过 60% | 强制 `reject`，保留原文，插入 `safety_gate` 发现项 |
| Verdict 规范化 | 非 approve 词汇 | 统一为 `reject` |
| Findings 截断 | 超过 40 条 | 截断保留前 40 条 |
| 字段长度限制 | 各文本字段 | 截断到安全长度 |

**应用规则**：只有 `final_verdict == "approve"` 且通过全部护栏时，才允许自动覆盖正文。

---

## 15. 项目运行与构建

### 运行

```powershell
cd F:\项目\simple_ai_novel_py
python main.py
```

### 安装依赖

```powershell
python -m pip install -r requirements.txt
```

### AI 配置（环境变量）

```powershell
$env:OPENAI_API_KEY = "your_api_key"
$env:OPENAI_BASE_URL = "https://api.openai.com/v1"
$env:OPENAI_MODEL = "your_model_name"
python main.py
```

### 编译检查

```powershell
python -m compileall novel_app
```

### 单元测试

```powershell
python -m unittest -v
```

### 健康检查

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\health_check.ps1
```

### 打包发布

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\packaging\build_first_exe.ps1
```

### 数据约定

| 路径 | 说明 |
|------|------|
| `data/novels.db` | 默认 SQLite 数据库 |
| `data/media/` | 图片资源（封面、人物头像） |
| `data/exports/` | 导出文件 |
| `data/references/` | 参考资料存储 |
| `release/` | 构建产物（不应在开发清理中删除） |

### 环境变量

| 变量 | 说明 |
|------|------|
| `OPENAI_API_KEY` | AI API 密钥 |
| `OPENAI_BASE_URL` | AI API 基础 URL（默认 `https://api.openai.com/v1`） |
| `OPENAI_MODEL` | AI 模型名称 |
| `SIMPLE_AI_NOVEL_DATA_DIR` | 自定义数据目录 |
| `SIMPLE_AI_NOVEL_SMOKE_EXIT` | 设为 `1` 时启动后立即退出（冒烟测试） |
