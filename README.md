# Simple AI Novel App

面向长篇小说创作的本地桌面工作台，技术栈 `Python + PyQt6 + SQLite`。

## 核心功能

- **作品目录管理**：书籍 / 卷 / 章节三级树形结构，拖拽排序
- **章节正文编辑**：富文本编辑器，未保存脏标记可视化
- **大纲体系**：书籍 / 卷 / 章节三级大纲，AI 同步生成
- **AI 辅助写作**：续写、润色、AI 概率检测、全书分析
- **多智能体生成**：Planner → Writer → Auditor → Reviser 流水线，支持 budget / quality 双预设
- **多维度审计**：12 维审计框架 + 24 条内置规则 + @DSL 上下文注入 + Pydantic 校验
- **真相文件系统**：7 份结构化 Markdown 真相文件 + 伏笔追踪
- **RAG 向量检索**：Qdrant 嵌入式 + 混合检索 + Jina Reranker
- **人物与世界观设定**：人物卡片、世界观条目编辑，脏检测确认
- **人物关系星图**：可视化关系网络，时间轴历史，样式自定义
- **AI 纠正对话**：嵌入式纠错面板，交互式修正
- **章节快照**：生成 / 审查前自动创建快照，支持恢复
- **智能导入**：TXT / Markdown / DOCX 文件导入与拆章
- **多格式导出**：TXT / Markdown / DOCX
- **Skills 提炼**：从文本中提炼写作技巧
- **DPAPI 安全存储**：Windows 下 API Key 加密存储
- **主题系统**：玻璃拟态设计语言，Design Token 驱动

## 运行

```powershell
python main.py
```

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

## AI 配置

应用优先读取界面中保存的 AI 设置，也支持环境变量作为默认配置：

```powershell
$env:OPENAI_API_KEY = "your_api_key"
$env:OPENAI_BASE_URL = "https://api.openai.com/v1"
$env:OPENAI_MODEL = "your_model_name"
python main.py
```

AI 设置按用途分离：写作生成、同步大纲、AI 概率检测、智能导入、Skills 提炼、全书分析、多智能体审查 / 生成。未配置对应用途时，该功能不可执行。

## 检查

```powershell
python -m compileall novel_app
python -m unittest -v
```

统一健康检查：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\health_check.ps1
```

## 项目结构

```text
simple_ai_novel_py/
├── main.py                          # 入口
├── requirements.txt                 # 依赖声明
├── novel_app/
│   ├── ai_service.py                # AI 服务（多用途路由）
│   ├── model_router.py              # 多模型路由（budget/quality 预设）
│   ├── database.py                  # SQLite 数据层
│   ├── exporter.py                  # TXT/MD/DOCX 导出
│   ├── text_importer.py             # 智能导入
│   ├── secure_storage.py            # DPAPI 安全存储
│   ├── research_sources.py          # 开源研究素材库
│   ├── qt_app.py                    # PyQt6 主窗口
│   ├── agents/                      # 多智能体编排
│   │   ├── graph.py                 # AgentGraph 状态图
│   │   ├── planner.py               # 大纲拆解
│   │   ├── writer.py                # 正文写手
│   │   ├── auditor.py               # 一致性 / 长篇审查
│   │   ├── reviser.py               # 修订润色
│   │   └── prompts.py               # Agent 提示词
│   ├── audit/                       # 多维度审计
│   │   ├── dimensions.py            # 12 维审计框架
│   │   ├── rules.py                 # 24 条内置规则
│   │   ├── dsl_parser.py            # @DSL 上下文注入
│   │   └── validator.py             # Pydantic 校验
│   ├── core/                        # 基础设施
│   │   ├── event_bus.py             # 事件总线
│   │   └── service_locator.py       # 服务定位器
│   ├── qt/                          # UI 组件
│   │   ├── dialogs.py               # 通用对话框
│   │   ├── chat_dialog.py           # AI 对话
│   │   ├── correction_dialog.py     # AI 纠正面板
│   │   ├── star_graph.py            # 人物关系星图
│   │   ├── star_graph_editors.py    # 星图编辑器
│   │   ├── star_graph_history.py    # 星图时间轴
│   │   ├── star_graph_models.py     # 星图数据模型
│   │   ├── star_graph_style.py      # 星图样式管理
│   │   ├── helpers.py               # 工具函数
│   │   ├── icons.py                 # 主题感知图标
│   │   ├── image_utils.py           # 图片处理
│   │   ├── theme.py                 # 玻璃拟态主题
│   │   ├── workers.py               # AI 后台工作线程
│   │   └── state.py                 # Qt 状态管理
│   ├── rag/                         # RAG 向量检索
│   │   ├── embedder.py              # 嵌入器（含 FallbackEmbedder）
│   │   ├── qdrant_client.py         # Qdrant 客户端
│   │   ├── retriever.py             # 混合检索器
│   │   └── reranker.py              # Jina Reranker
│   ├── state/                       # 应用状态
│   │   └── app_state.py             # 全局状态管理
│   ├── theme/                       # 设计系统
│   │   ├── colors.py                # 色彩体系
│   │   ├── design_tokens.py         # Design Token
│   │   ├── spacing.py               # 间距规范
│   │   ├── typography.py            # 字体排版
│   │   └── theme_customization.py   # 主题自定义
│   └── truth/                       # 真相文件系统
│       └── truth_manager.py         # 真相文件管理 + 伏笔追踪
├── tests/                           # 自动化测试
├── docs/                            # 文档
├── packaging/                       # 打包脚本
└── tools/                           # 工具脚本
```

## 打包

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\packaging\build_pyinstaller_exe.ps1
```

## 数据约定

- `data/` 保存本地运行数据与媒体文件
- `data/novels.db` 是默认 SQLite 数据库
- 图片类资源保存为 `data/media/...` 相对路径，便于迁移和打包
- `release/` 保存构建产物，不应在普通开发清理中删除
- API Key 通过 Windows DPAPI 加密存储，不落盘明文

## 依赖

| 依赖 | 用途 |
|------|------|
| PyQt6 | GUI 框架 |
| python-docx | DOCX 导入 / 导出 |
| qdrant-client | RAG 向量检索（可选） |
| jina | Reranker 重排序（可选） |

RAG 系统内置 `FallbackEmbedder`，不安装 qdrant-client 也可运行基础功能。

## 开源协议

本项目采用 **CC BY-NC 4.0**（署名-非商业性使用 4.0 国际）协议开源。

- ✅ **允许**：个人学习、研究、非商业用途的自由使用和修改
- ✅ **要求**：引用或二次分发时**必须注明出处**（项目名称 + 作者 + 仓库链接）
- ❌ **禁止**：将本工具或其衍生作品用于**商业化盈利**目的（包括但不限于付费售卖、SaaS 服务、商业托管等）

详见 [LICENSE](./LICENSE) 文件。
