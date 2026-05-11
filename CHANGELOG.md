# 更新日志

## 打包文件时间线

| 版本 | 构建时间 | 文件名 | SHA256 |
| --- | --- | --- | --- |
| Beta.3.7 | 2026-05-10 | `SimpleAINovelApp-Beta.3.7.exe` | `ADF5AC84492AAA4B89FB7C60AC36738B9C39920A9C888D6B48B76A99D6FBC875` |
| Beta.3.6 | 2026-05-10 | `SimpleAINovelApp-Beta.3.6.exe` | `9B309A3B4880EBE5A11C6A303E868C70C946A4D141F6697ADE5EE1A9A26CFC59` |

## Beta.3.7 — 三级卡片适配版（2026-05-10）

- **概览卡片书籍专属**：概览 tab 仅在书籍级显示，新增「AI 总结全书」按钮
- **卷级大纲卡片**：卷级生成卡片改名为「卷大纲」，显示卷级大纲编辑器 + 保存按钮
- **章节级隐藏概览**：章节级不显示概览卡片

| Beta.3.5 | 2026-05-10 | `SimpleAINovelApp-Beta.3.5.exe` | `2B8A5160BC790EF5A1A2583D78069F08EC0A7697981823D9D975C7C5F7E58071` |
| v1.0.0-pre | 2026-05-10 | `SimpleAINovelApp-v1.0.0-pre.exe` | `CC6158510540BF1F077DDC86F16EC1606540A2A814C23976DB486F4E6415DC89` |
| Beta.3.4 | 2026-05-07 | `SimpleAINovelApp-Beta.3.4.exe` | `6FC79DF407DDE277F6D6455585740E1A25923F25D2CA68164ECE802175FDE47F` |
| Beta.3.3 | 2026-05-07 | `SimpleAINovelApp-Beta.3.3.exe` | `7FE5BC4C84294B848C7B1CCBE9518AC7A318B4B0B1CCFA7D4C8934FB8CD09CA9` |
| Beta.3.2 | 2026-05-06 | `SimpleAINovelApp-Beta.3.2.exe` | `8042679A9BACC7C56750137932F1EEBD3B0CC8E53F504C54D664990F28C75A42` |
| Beta.3.1 | 2026-05-06 | `SimpleAINovelApp-Beta.3.1.exe` | `592B9A3BF4C4949A71F2D81475ED5AAEC5F40E151AA9F337B6CD16FF1BA44DC9` |
| Beta.3.0 | 2026-05-06 | `SimpleAINovelApp-Beta.3.0.exe` | `4C5A11EBE11A6C0535F5E6099A0D8BCC38CBEE48C00E222BC685C69A6341D6E3` |

## Beta.3.6 — 生成卡片精简版（2026-05-10）

- **生成卡片移除对照布局**：抽屉"生成"标签页移除左右分栏，仅展现章节大纲编辑器
- **标题更新**：从"长篇生成对照"改为"章节生成大纲"

## Beta.3.5 — 修复 + 优化版（2026-05-10）

- **恢复应用图标**：`--icon` 参数 + `--add-data` 打包 `app_icon.ico`，运行时 `setWindowIcon`
- **生成卡片大纲修正**：抽屉"生成"标签页使用章节级大纲（`chapter_outline_editor`），不再混入书籍全局描述
- **删除非 AI 自动提炼**：移除 8 个 `_mock` 方法（摘/Skills/风格/角色/关系/分类），未配置 AI 时直接报错而非产假数据

## v1.0.0-pre — 预发布版（2026-05-10）

首个预发布版本，整合五大开源项目技术架构：

- **真相文件系统** (`novel_app/truth/`)：7 份结构化 Markdown 真相文件 + 伏笔追踪
- **RAG 向量检索** (`novel_app/rag/`)：Qdrant 嵌入式 + 混合检索 + Jina Reranker
- **多 Agent 编排** (`novel_app/agents/`)：AgentGraph 状态图 + Planner/Writer/Auditor/Reviser 四 Agent
- **多维度审计** (`novel_app/audit/`)：12 维审计 + 24 条内置规则 + @DSL 上下文注入 + Pydantic 校验
- **多模型路由** (`novel_app/model_router.py`)：budget/quality 双预设按 Agent 分配模型
- **AI 纠正对话** (`novel_app/qt/correction_dialog.py`)：嵌入式纠错面板
- **103 条自动化测试** 全部通过

### 依赖

```text
PyQt6==6.11.0
python-docx==1.1.2
qdrant-client==1.17.1
jina==3.34.0
```

## Beta.3.4 — AI 任务生命周期重构与交互优化

```text
release/SimpleAINovelApp-Beta.3.4.exe
```

SHA256：

```text
6FC79DF407DDE277F6D6455585740E1A25923F25D2CA68164ECE802175FDE47F
```

### 核心变化

- **AI 任务取消机制重构**：添加 `cancel_requested` 标志位，区分"运行中"和"停止中"状态，`_has_active_write_job` 和 `_find_active_background_job` 均过滤已取消任务。
- **detached_cancelled_jobs 机制**：超时未退出的任务移入 detached 字典，不再阻塞 UI，后台返回结果被忽略。
- **任务面板状态双显示**：状态栏显示"运行中 · N / 停止中 · M"，取消按钮文字动态切换。
- **任务摘要卡片**：新增带动画的任务摘要面板（QPropertyAnimation 220ms），展开显示运行中任务标签列表。
- **ChatDialog 安全关闭**：关闭对话框时先取消 AI 回复再关闭（`event.ignore()`），避免线程泄漏。
- **世界观编辑保存/丢弃/取消**：切换时弹三选一对话框，不再只能丢弃或阻止。
- **专注写作 toggle**：再次点击可退出专注模式，展开侧边栏自动退出。
- **抽屉宽度自适应**：根据窗口大小动态限制抽屉最大宽度（`max(min_width, width - 720)`）。
- **AI 日志路由改进**：日志通过 `_on_ai_log(job_id, message)` 路由，取消后忽略后续日志，避免污染面板。
- **新增 icons.py**：主题感知的树形图标生成器（book/volume/group/template/默认章节 5 种类型）。
- **抽屉面板最小宽度优化**：宽型抽屉（tasks/review）340px，标准抽屉 320px。

### 修改文件

| 文件 | 变更 |
|------|------|
| `novel_app/qt/chat_dialog.py` | 关闭时安全取消 AI 回复 |
| `novel_app/qt/icons.py` | 新增主题感知图标生成器 |
| `novel_app/qt_app.py` | AI 取消机制、任务面板、专注模式、抽屉自适应 |

### 验证情况

- `python -m compileall novel_app` 通过。
- `python -m unittest -v` 40 项通过。

## Beta.3.3 — UI 交互优化版

```text
release/SimpleAINovelApp-Beta.3.3.exe
```

SHA256：

```text
7FE5BC4C84294B848C7B1CCBE9518AC7A318B4B0B1CCFA7D4C8934FB8CD09CA9
```

### 核心变化

- **状态反馈修复**：修复 `_set_status` 消息永远不可见的关键 Bug，改为显示消息 + 5 秒自动淡出。
- **编辑器脏标记可视化**：未保存时编辑器标题加 `●` 前缀，窗口标题加 `*` 前缀。
- **任务运行标识**：状态栏任务运行显示 `⏳ 运行中`，空闲时恢复。
- **`_load_volume` 去重**：不再先调 `_load_book` 再覆盖，直接加载卷数据，消除重复 DB 查询和 UI 刷新。
- **`_refresh_drawer` 懒加载**：仅刷新当前可见 Tab，其余 Tab 标记为 stale，切换时按需刷新。
- **新增 6 个快捷键**：`Ctrl+D` AI检测、`Ctrl+Shift+R` 审查、`Ctrl+Shift+G` 生成、`Ctrl+E` 导出TXT、`Ctrl+Shift+E` 导出DOCX、`Ctrl+L` 折叠导航。
- **AI 快捷操作栏**：编辑区上方新增 5 个快捷按钮（续写/润色/AI检测/审查/生成）。
- **人物编辑脏检测**：切换人物时检测未保存修改，弹确认对话框。
- **世界观编辑脏检测**：切换世界观条目时检测未保存修改，弹确认对话框。
- **目录树符号标识**：章节前缀 `📝`，AI 高风险章节后缀 `🤖`。

### 修改文件

| 文件 | 变更 |
|------|------|
| `novel_app/qt_app.py` | 状态反馈修复、脏标记可视化、性能优化、快捷键、AI操作栏、编辑确认、符号标识 |

### 验证情况

- `python -m compileall novel_app` 通过。
- `python -m unittest -v` 40 项通过。

## Beta.3.2 — 补全 DOCX 依赖版

```text
release/SimpleAINovelApp-Beta.3.2.exe
```

SHA256：

```text
8042679A9BACC7C56750137932F1EEBD3B0CC8E53F504C54D664990F28C75A42
```

### 核心变化

- 修复 DOCX 导入失败：`requirements.txt` 中声明的 `python-docx==1.1.2` 未实际安装到 `vendor` 目录，现已补装 `python-docx` 及其依赖 `lxml`、`typing-extensions`。
- 滚动条玻璃化瘦身：轨道透明化（`background: transparent`），宽度从 `10px` 缩至 `6px`，滑块改用 `muted` 色，增加 `:hover` 悬停高亮反馈。
- 新增 `scrollbar_handle` / `scrollbar_handle_hover` 变量，有背景图时自动切换为半透明模式。
- 水平/垂直滚动条统一风格，圆角微调至 `4px`。

### 修改文件

| 文件 | 变更 |
|------|------|
| `novel_app/qt/theme.py` | 新增玻璃感知滚动条变量，重写 QScrollBar 样式块 |
| `vendor/docx/` | 补装 python-docx 1.1.2 |
| `vendor/lxml/` | 补装 lxml 6.1.0 |

### 验证情况

- `python -m compileall novel_app` 通过。

## Beta.3.1 — 滚动条玻璃化瘦身版

```text
release/SimpleAINovelApp-Beta.3.1.exe
```

SHA256：

```text
592B9A3BF4C4949A71F2D81475ED5AAEC5F40E151AA9F337B6CD16FF1BA44DC9
```

### 核心变化

- 滚动条全局瘦身：轨道透明化（`background: transparent`），宽度从 `10px` 缩至 `6px`，贴合玻璃拟态设计语言。
- 滑块改用 `muted` 色（原 `border` 色对比度低），增加 `:hover` 悬停高亮反馈。
- 新增 `scrollbar_handle` / `scrollbar_handle_hover` 变量，有背景图时自动切换为半透明模式。
- 水平/垂直滚动条统一风格，圆角微调至 `4px`。

### 修改文件

| 文件 | 变更 |
|------|------|
| `novel_app/qt/theme.py` | 新增玻璃感知滚动条变量，重写 QScrollBar 样式块 |

### 验证情况

- 以 `Beta.3.0` 运行时为基线复用打包，构建耗时 ~214s。
- `python -m compileall novel_app` 通过。

## Beta.3.0 — 模块化重构+多智能体生成版

```text
release/SimpleAINovelApp-Beta.3.0.exe
```

SHA256：

```text
4C5A11EBE11A6C0535F5E6099A0D8BCC38CBEE48C00E222BC685C69A6341D6E3
```

### 核心变化

- 删除旧 UI 回退入口、旧 UI 依赖和旧 UI 源码，当前项目只保留 PyQt6 主线。
- `requirements.txt` 移除旧主题依赖，仅保留 PyQt6 与 DOCX 支持依赖。
- `main.py` 简化为直接启动 PyQt6 工作台，不再执行旧界面回退。
- AI 菜单中的旧草稿入口替换为"多智能体生成"。
- 多智能体生成使用 `review` 用途的 AI 配置，流程包含大纲拆解、场景规划、正文写手、剧情审查、连续性审查、文风修订和最终校验。
- 多智能体生成会在写回前创建章节快照，并复用审查安全门：非 approve、空正文、异常缩短、章节被修改或任务取消时只记录，不覆盖正文。
- 多智能体生成结果写入 `review_runs` / `review_findings`，可在右侧"审查"抽屉查看、复制 Truth File 或恢复生成前快照。
- 多智能体审查保留章节、卷、全书批量审查能力，并支持取消后记录未完成章节为 `cancelled`。
- 模块拆分：`qt/workers.py`（AiWorker + FunctionWorker）、`qt/helpers.py`（AI_PROBABILITY_META 等工具函数）、`qt/star_graph.py` 时间轴 QScrollArea 滚动。
- 更新 `项目技术与机制总览.txt` 和 `docs/DEVELOPMENT_GUIDE.md`。

### 修改文件

| 文件 | 变更 |
|------|------|
| `main.py` | -11（移除 Tkinter 回退） |
| `novel_app/qt_app.py` | 重构（引用新模块，多智能体生成入口） |
| `novel_app/qt/workers.py` | 新增（AiWorker, FunctionWorker） |
| `novel_app/qt/helpers.py` | 新增（工具函数提取） |
| `novel_app/qt/star_graph.py` | 时间轴 QScrollArea 滚动 |
| `novel_app/database.py` | review_runs / review_findings 表 |
| `novel_app/ai_service.py` | 多智能体链路支持 |
| `novel_app/theme/__init__.py` | 更新 |
| `novel_app/text_importer.py` | 更新 |
| `requirements.txt` | 精简为 PyQt6 + python-docx |

### 验证情况

- `python -m compileall novel_app` 通过。
- `python -m unittest -v` 通过。

## 旧版历史

旧版完整历史见 `CHANGELOG.md` 的 Git 历史或之前打包的 `功能清单.txt`。
