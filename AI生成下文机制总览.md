# AI 生成下文机制总览

> 本文档完整记录项目中所有 AI 生成正文（包括续写、润色、长篇生成、长篇校验等）的触发入口、数据流、代码链路和安全门机制。
> 基线版本：Beta.3.2

---

## 一、架构总览

```
┌─────────────────────────────────────────────────────────┐
│                    UI 层 (qt_app.py)                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │
│  │ 工具栏 AI 菜单 │ │ 抽屉"生成"页签 │ │ 右键上下文菜单    │ │
│  │ (L814-L851)   │ │ (L1157-1158) │ │ (暂无 AI 入口)   │ │
│  └──────┬───────┘ └──────┬───────┘ └────────┬─────────┘ │
│         └────────────────┼──────────────────┘           │
│                          ▼                              │
│  ┌────────────────────────────────────────────────────┐ │
│  │           _start_generation(mode)                   │ │
│  │           _start_multi_agent_generation()           │ │
│  │           _refresh_summary()                        │ │
│  │           _review_current_scope()                   │ │
│  └──────────────────────┬─────────────────────────────┘ │
│                         ▼                               │
│  ┌────────────────────────────────────────────────────┐ │
│  │       _build_sourcebook_context()                  │ │
│  │       _build_review_truth_file()                   │ │
│  │       _build_character_immersion_block()           │ │
│  │       _build_template_context()                    │ │
│  │       _get_previous_chapters_context()             │ │
│  └──────────────────────┬─────────────────────────────┘ │
├─────────────────────────┼───────────────────────────────┤
│                    Worker 层 (qt/workers.py)             │
│  ┌────────────────────┐ ┌─────────────────────────────┐ │
│  │    AiWorker         │ │    FunctionWorker           │ │
│  │   (简单生成/流式)    │ │   (多智能体长篇任务)         │ │
│  └────────┬───────────┘ └──────────────┬──────────────┘ │
├───────────┼────────────────────────────┼─────────────────┤
│                    AI 服务层 (ai_service.py)              │
│  ┌────────┼────────────────────────────┼────────────────┐│
│  │  generate_draft  /  multi_agent_generate_from_outline ││
│  │  continue_writing /  multi_agent_review               ││
│  │  polish_text      /  cross_chapter_check              ││
│  │  stream_generate  /  extract_style_profile            ││
│  │  summarize_chapter / extract_character_voices         ││
│  └────────┼────────────────────────────┼────────────────┘│
│           ▼                            ▼                │
│  ┌────────────────────────────────────────────────────┐ │
│  │              _post_chat_completion                  │ │
│  │              _stream_chat_completion                │ │
│  │                    (HTTP/SSE)                        │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 二、生成模式分类

项目共有 **4 种 AI 生成模式**，按复杂度和入口分为两大类：

### 2.1 简单生成模式（通过 `_start_generation` 触发）

| 模式 | 入口 | AI 用途 | Worker | 输出目标 |
|------|------|---------|--------|----------|
| `draft` | 工具栏 "长篇生成" / 抽屉页签 | `review` | FunctionWorker | `chapters.content` |
| `continue` | 工具栏 | `writing` | AiWorker（流式） | 替换正文 |
| `polish` | 工具栏 "润色" | `writing` | AiWorker（流式） | 替换正文 |
| `summary` | 工具栏 "同步大纲" | `outline` | AiWorker（流式） | `chapters.outline_text` |

### 2.2 长篇多智能体模式（通过专用方法触发）

| 模式 | 入口 | 方法 | Worker | 输出目标 |
|------|------|------|--------|----------|
| 长篇生成 | 工具栏 / 抽屉按钮 | `_start_multi_agent_generation` | FunctionWorker | 覆盖或新建章节 |
| 长篇校验 | 审查页签 | `_review_current_scope` | FunctionWorker | `review_runs` / 可选覆盖正文 |

> 注意：`draft` 模式在 `_start_generation` 中已被重定向到 `_start_multi_agent_generation`，旧版 `generate_draft` 已废弃。

---

## 三、UI 触发入口

### 3.1 工具栏 AI 菜单（qt_app.py L825-L832）

```python
"AI": [
    ("长篇生成",     self._start_multi_agent_generation),
    ("润色",         lambda: self._start_generation("polish")),
    ("同步大纲",     self._refresh_summary),
    ("检测AI概率",   self._detect_current_chapter_ai_probability),
    ("分析全书",     self._analyze_book_full),
    ("清除本章AI标记", self._clear_current_ai_spans),
],
```

### 3.2 抽屉"生成"页签按钮（qt_app.py L1157-L1158）

```python
generate_btn = QPushButton("长篇生成")
generate_btn.clicked.connect(self._start_multi_agent_generation)
```

### 3.3 右键上下文菜单

目前右键菜单**不包含直接 AI 生成入口**。AI 触发全部通过工具栏和抽屉按钮完成。

---

## 四、简单生成模式详细链路

### 4.1 continue / polish 模式

```
工具栏/按钮触发
  → _start_generation("continue" / "polish")
     [qt_app.py L4390-L4440]
     │
     ├─ 校验：章节已选择、正文非空
     ├─ 创建 AI 改写前快照
     │
     └─ _run_ai_worker()  [qt_app.py L4097-L4190]
           │
           ├─ _build_sourcebook_context(book_id)
           ├─ _get_bound_skill_payload(chapter_id)
           │
           ├─ 创建 AiWorker(QThread)
           │     │
           │     └─ run():
           │         a. _generate_by_mode(mode, ..., sourcebook_context, selected_skills)
           │            [ai_service.py L1550-L1586]
           │              │
           │              ├─ require_remote? → _generate_remote()
           │              │   [ai_service.py L1588-L1619]
           │              │     │
           │              │     └─ _post_chat_completion()
           │              │         → POST /chat/completions (timeout=120s)
           │              │
           │              └─ require_remote=False → _generate_mock()
           │                  [ai_service.py L1898-L1942]
           │
           └─ chunk_ready 信号 → _on_ai_chunk()
              finished 信号 → _on_ai_done()
                 │
                 └─ _persist_ai_result_to_target()
                       → database.update_chapter(content)
```

### 4.2 summary（同步章节大纲）模式

```
工具栏 "同步大纲"
  → _refresh_summary()  [qt_app.py L4442-L4473]
     │
     ├─ target = "outline"（写入目标是大纲字段）
     │
     └─ _run_ai_worker(mode="summary")
           │
           └─ AiWorker.run()
                → mode == "summary"
                → _summarize_remote() 或 _summarize_mock()
                   [ai_service.py L1662-L1687] / [L1950-L1968]
                   │
                   └─ _post_chat_completion()
                         → 返回 3-5 句章节摘要
```

### 4.3 AI 用途配置路由

```python
# qt_app.py L139-L144
AI_MODE_PURPOSE = {
    "draft":    "writing",
    "continue": "writing",
    "polish":   "writing",
    "summary":  "outline",
}
```

`AiSettingsDialog` 中为 `writing` 和 `outline` 各配置独立的 API Key / Base URL / Model。

---

## 五、长篇多智能体生成模式详细链路

### 5.1 入口：_start_multi_agent_generation

```
工具栏/抽屉 "长篇生成"
  → _start_multi_agent_generation()
     [qt_app.py L4236-L4388]
     │
     ├─ 1. 校验：
     │     - 是否已选择章节
     │     - 章节是否有大纲（无大纲则提示）
     │
     ├─ 2. 创建 pre-generation 快照：
     │     _create_chapter_snapshot(chapter_id)
     │
     ├─ 3. 构建所有上下文（共 7 类）：
     │     ├─ sourcebook_context ← _build_sourcebook_context(book_id)
     │     ├─ truth_file         ← _build_review_truth_file(chapter, scope)
     │     ├─ template_context   ← _build_template_context(book_id, chapter)
     │     ├─ skills             ← _get_bound_skill_payload(chapter_id)
     │     ├─ previous_chapters  ← _get_previous_chapters_context(chapter)
     │     ├─ style_profile      ← extract_style_profile(previous_chapters)
     │     ├─ character_voices   ← extract_character_voices(previous_chapters)
     │     └─ style_voices_block ← format_style_and_voices_block(...)
     │
     ├─ 4. work() 闭包定义：
     │     │
     │     └─ ai_service.multi_agent_generate_from_outline(
     │            book_title, chapter_title, outline,
     │            current_content, truth_file,
     │            selected_skills, sourcebook_context,
     │            require_remote=True, cancel_event,
     │            template_content, previous_chapters, style_voices_block
     │        )
     │
     └─ 5. _run_background_ai_job(label, work, on_done)
           │
           └─ FunctionWorker(work)
                 │
                 └─ on_done = _apply_multi_agent_review_result()
```

### 5.2 多智能体生成 — AI 侧

```python
# ai_service.py L576-L629
def multi_agent_generate_from_outline(
    self, *,
    book_title: str,
    chapter_title: str,
    outline: str,
    current_content: str,
    truth_file: str,
    selected_skills: list[dict] | None = None,
    sourcebook_context: str = "",
    require_remote: bool = False,
    cancel_event: Event | None = None,
    template_content: str = "",
    previous_chapters: list[dict] | None = None,
    style_voices_block: str = "",
) -> dict[str, Any]:
```

#### System Prompt（_multi_agent_generate_remote, ai_service.py L658-L693）

```
你是中文长篇小说的长篇生成与 OOC 校验系统，只返回指定 JSON。

请模拟一个长篇小说章节生成流水线：
  大纲拆解员、人物代入员、场景规划员、正文写手、
  剧情校验员、OOC 审查员、连续性审查员、文风修订员、最终校验员

硬性规则：
  不要偏离当前章节大纲；
  不要引入 Truth File 不支持的核心设定；
  不要让角色做出缺少铺垫的 OOC 行为；
  不要输出创作过程；
  正文必须是小说正文而非提纲。
```

#### JSON 输出字段

```json
{
  "summary": "本次生成摘要",
  "overall_score": 0-100,
  "final_verdict": "approve | reject",
  "findings": [
    {
      "agent": "角色名称",
      "severity": "high | medium | low",
      "category": "类别",
      "location_hint": "定位",
      "quote": "引用原文",
      "issue": "问题描述",
      "suggestion": "修改建议"
    }
  ],
  "revised_content": "修订后的完整正文",
  "revised_outline": "修订后的章节大纲",
  "template_comparison": "与模板的对比分析",
  "risk_notes": "覆盖正文前需注意的风险"
}
```

---

## 六、长篇校验（多智能体审查）模式

### 6.1 入口：_review_current_scope

```
审查页签 "校验范围" 按钮
  → _review_current_scope()  [qt_app.py L4775-L4821]
     │
     ├─ 1. _collect_review_targets()
     │     收集 chapter / volume / book 级别审查目标
     │
     ├─ 2. 对每个章节循环：
     │     ├─ _build_review_truth_file(chapter, scope_chapters)
     │     ├─ _build_template_context(book_id)
     │     ├─ _get_review_skill_payload(chapter_id)
     │     ├─ 创建 pre-review 快照
     │     │
     │     └─ work() 闭包循环：
     │           ├─ review_ai_service.multi_agent_review(...)
     │           ├─ review_ai_service.cross_chapter_check(...)（从第2章起）
     │           └─ review_ai_service.extract_character_relationships(...)
     │
     └─ 3. _run_background_ai_job(review_label, work, on_done)
           │
           └─ on_done = _apply_multi_agent_review_result()
```

### 6.2 多智能体审查 — AI 侧

```python
# ai_service.py L538-L574
def multi_agent_review(
    self, *,
    book_title: str,
    chapter_title: str,
    outline: str,
    content: str,
    truth_file: str,
    selected_skills: list[dict] | None = None,
    require_remote: bool = False,
    cancel_event: Event | None = None,
    template_content: str = "",
) -> dict[str, Any]:
```

#### System Prompt（_multi_agent_review_remote, ai_service.py L757-L789）

```
你是中文长篇小说的长篇校验与修订系统，只返回指定 JSON。

请模拟一个多智能体小说审查流水线：
  上下文整理器、剧情审查员、连续性审查员、
  文风审查员、修订智能体、最终校验员

审查规则：
  不改变核心剧情事实；
  不引入 Truth File 无支撑的设定；
  不删除作者独特风格；
  优先修复矛盾/重复/节奏断裂。
```

#### Temperature

- 长篇生成：**0.65**
- 长篇校验：**0.25**（更保守）

### 6.3 跨章节一致性检查

```python
# ai_service.py L927-L969
def cross_chapter_check(
    self, *,
    current_chapter_title: str,
    current_chapter_content: str,
    previous_chapters: list[dict],
    truth_file: str,
    require_remote: bool = False,
    cancel_event: Event | None = None,
) -> dict[str, Any]:
```

检查三个维度：
- **character** — 人物状态不一致
- **world** — 世界观设定冲突
- **fact** — 剧情事实矛盾

---

## 七、上下文构建函数详解

### 7.1 SourceBook 上下文（_build_sourcebook_context）

[qt_app.py L3809-L3950](file:///f:/项目/simple_ai_novel_py/novel_app/qt_app.py#L3809-L3950)

用于 **简单生成模式**（continue/polish）的轻量参考上下文。

| 内容 | 限制 |
|------|------|
| 书籍全局大纲 | 前 700 字 |
| 当前卷信息 | 前 500 字 |
| 人物设定（name/role/profile_text） | 前 8 人，每人前 180 字 |
| 世界观条目 | 前 8 条，每条前 180 字 |
| 前后章节摘要 | 最多 4 条 |
| 蓝本提炼 Skills | 全部 |
| 总截断 | 无硬截断，自然拼接 |

### 7.2 Truth File（_build_review_truth_file）

[qt_app.py L4996-L5129](file:///f:/项目/simple_ai_novel_py/novel_app/qt_app.py#L4996-L5129)

用于 **多智能体生成和校验**的完整校验上下文。

| 内容 | 限制 |
|------|------|
| 书籍大纲 | 前 1200 字 |
| 章节大纲 | 前 1200 字 |
| 人物卡（name/role/profile_text） | **前 40 人**，每人前 260 字 |
| 人物关系（source→target + 类型 + 描述） | 前 60 条 |
| 世界观条目 | 前 40 条 |
| 章节关键事件 | 全部 |
| 启用 Skills | 全部 |
| AI 标记占比统计 | 百分比统计 |
| 总截断 | **硬截断 14,000 字符** |

### 7.3 人物代入约束块（_build_character_immersion_block）

[qt_app.py L5048-L5095](file:///f:/项目/simple_ai_novel_py/novel_app/qt_app.py#L5048-L5095)

独立构建，被 Truth File 引用，专门用于 OOC 约束。

| 内容 | 限制 |
|------|------|
| 人物设定（含外貌/性格/背景/口头禅） | 前 24 人，每人前 320 字 |
| 人物关系 | 前 60 条，描述前 120 字 |
| 末尾指令 | "生成时必须先代入相关人物的立场、动机、口吻和关系，再输出正文" |

### 7.4 模板上下文（_build_template_context）

[qt_app.py L5131-L5156](file:///f:/项目/simple_ai_novel_py/novel_app/qt_app.py#L5131-L5156)

获取标记为 `template` 的章节作为文风参考（同书最多 3 个模板章节）。

### 7.5 前序章节上下文（_get_previous_chapters_context）

[qt_app.py L5442-L5486](file:///f:/项目/simple_ai_novel_py/novel_app/qt_app.py#L5442-L5486)

获取当前章节之前所有章节的标题 + 正文摘要，用于长篇生成时提供叙事连贯性。

---

## 八、简单生成 Prompt 模板

### 8.1 各模式指令（_build_remote_generation_prompt）

[ai_service.py L2123-L2177](file:///f:/项目/simple_ai_novel_py/novel_app/ai_service.py#L2123-L2177)

**System**: `"你是中文小说写作助手，帮助作者完成草稿生成、续写、润色和摘要提炼。"`

| 模式 | 指令 | 字数要求 |
|------|------|----------|
| `draft` | "请由多智能体流程生成一段新的章节草稿" | 300-500 字 |
| `continue` | "请在现有正文基础上继续写一段新的内容" | 200-400 字，与前文自然衔接 |
| `polish` | "请在不改变剧情核心信息的前提下润色已有正文" | 输出润色后全文 |

### 8.2 摘要 Prompt（_summarize_remote）

[ai_service.py L1662-L1687](file:///f:/项目/simple_ai_novel_py/novel_app/ai_service.py#L1662-L1687)

**System**: `"你擅长为中文小说章节提炼摘要。"`  
**输出**: 3-5 句，提炼剧情推进/人物变化/关键悬念  
**Temperature**: 0.4

---

## 九、风格与人物声音系统

### 9.1 风格特征提取（extract_style_profile）

[ai_service.py L1061-L1125](file:///f:/项目/simple_ai_novel_py/novel_app/ai_service.py#L1061-L1125)

从样本章节中提取：
- 叙事视角（第一/第三人称，全知/限知）
- 句式长度特征（短句/中长句/长句）
- 描写密度（环境/心理/动作比例）
- 对话比例
- 基调情绪（欢快/沉重/紧张/抒情）
- 词汇风格（口语化/书面化）
- 段落节奏（快/中/慢）

### 9.2 人物声音提取（extract_character_voices）

[ai_service.py L1127-L1190](file:///f:/项目/simple_ai_novel_py/novel_app/ai_service.py#L1127-L1190)

从样本中提取每个人物的：
- **speech_style**: 说话风格
- **catchwords**: 口头禅
- **personality_hint**: 性格提示（20 字以内）

### 9.3 格式化输出（format_style_and_voices_block）

[ai_service.py L1192-L1220](file:///f:/项目/simple_ai_novel_py/novel_app/ai_service.py#L1192-L1220)

合并风格特征 + 人物声音卡片 + 人物代入约束块，生成一个总文本块，注入到多智能体生成的 prompt 中。

### 9.4 人物关系提取（extract_character_relationships）

[ai_service.py L506-L536](file:///f:/项目/simple_ai_novel_py/novel_app/ai_service.py#L506-L536)

书籍级人物关系提取，供多智能体审查使用。

---

## 十、Worker 系统

### 10.1 AiWorker（简单生成模式）

[workers.py](file:///f:/项目/simple_ai_novel_py/novel_app/qt/workers.py)

```python
class AiWorker(QThread):
    chunk_ready = Signal(str, str)   # (job_id, text_chunk)
    finished    = Signal(str, str)   # (job_id, message)
    error       = Signal(str, str)   # (job_id, error_message)

    def __init__(self, ai_service, *, mode, book_title, chapter_title,
                 outline, current_content, summary_text,
                 selected_skills, sourcebook_context, cancel_event,
                 require_remote=True):
```

- 用于 `continue` / `polish` / `summary` 模式
- 由 `_run_ai_worker()` 创建并启动
- `run()` 内部调用 `_generate_by_mode()` → `_generate_remote()` 或 `_generate_mock()`
- 流式模式下通过 `chunk_ready` 逐块推送文本
- 完成后通过 `finished` 信号触发 `_on_ai_done`

### 10.2 FunctionWorker（多智能体长篇任务）

```python
class FunctionWorker(QThread):
    log_message = Signal(str)        # 日志输出
    finished    = Signal(object, str)   # (result, label)
    error       = Signal(str, str)      # (label, error_message)

    def __init__(self, fn, uses_log=False, uses_cancel=False, label=""):
```

- 用于 `multi_agent_generate_from_outline` 和 `multi_agent_review`
- 由 `_run_background_ai_job()` 创建并包装在 `AiWorker` 中
- 执行任意 `Callable`（即 `work()` 闭包）
- 支持 `cancel_event` 中断
- 完成后通过 `finished` 信号触发 `on_done` 回调

### 10.3 任务编排（_run_background_ai_job）

[qt_app.py L5347-L5398](file:///f:/项目/simple_ai_novel_py/novel_app/qt_app.py#L5347-L5398)

```python
def _run_background_ai_job(self, label, callback, on_done,
                            callback_uses_log=False,
                            callback_uses_cancel=False,
                            deliver_result_on_cancel=False):
```

- 创建 `FunctionWorker` 并启动
- 连接 `log_message` → 任务抽屉日志区
- 连接 `finished` → `on_done` 回调
- 连接 `error` → 错误处理
- 所有活跃任务保存在 `self.ai_jobs` 字典中（以 UUID 为键）

---

## 十一、安全门机制

### 11.1 第一层：AI 输出规范化（_normalize_review_payload）

[ai_service.py L842-L925](file:///f:/项目/simple_ai_novel_py/novel_app/ai_service.py#L842-L925)

两个硬性规则，在 AI 返回 JSON 后立即执行：

| 规则 | 触发条件 | 动作 |
|------|----------|------|
| 空正文拦截 | `revised_content` 为空 | 强制 `final_verdict = "reject"`，追加 `safety_gate` finding |
| 异常缩短拦截 | 原正文 ≥ 200 字 且 修订版 < 原长度 40% | 强制 `final_verdict = "reject"`，追加 `safety_gate` finding |

### 11.2 第二层：写入安全门（_apply_multi_agent_review_result）

[qt_app.py L5131-L5281](file:///f:/项目/simple_ai_novel_py/novel_app/qt_app.py#L5131-L5281)

四阶段判断：

```
审查结果到达
  │
  ├─ final_verdict != "approve"？
  │     → reject：只记录审查结果，不覆盖正文
  │
  ├─ revised_content 为空或异常缩短？
  │     → unsafe_skipped：追加 safety_gate finding，不覆盖正文
  │
  ├─ 正文/大纲已被修改 或 编辑器 dirty？
  │     → stale_skipped：跳过自动覆盖
  │
  └─ 全部通过
        → applied：写入数据库
            ├─ update_chapter(content, outline)
            ├─ delete_chapter_ai_spans() + add_chapter_ai_span()
            └─ update_chapter_ai_probability(100, "certain")
```

### 11.3 取消安全门

任务被取消的章节：
- 创建 `status="cancelled"` 的 `review_run`
- 不覆盖正文
- 在审查记录中保存取消状态

---

## 十二、数据库写回路径

```
┌──────────────────────────────────────────────────┐
│  简单模式 (continue / polish / summary)           │
│                                                   │
│  _on_ai_done()                                    │
│    → _persist_ai_result_to_target()               │
│      → database.update_chapter()                  │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  长篇多智能体模式 (generate / review)              │
│                                                   │
│  _apply_multi_agent_review_result()               │
│    ├─ database.create_review_run()                │
│    ├─ database.replace_review_findings()          │
│    ├─ [if applied] database.update_chapter()      │
│    ├─ [if applied] database.delete_chapter_ai_spans()
│    ├─ [if applied] database.add_chapter_ai_span() │
│    └─ [if applied] database.update_chapter_ai_probability(100, "certain") │
└──────────────────────────────────────────────────┘
```

### AI 概率标记

多智能体生成/校验写入正文后，该章节自动标记为：

```python
database.update_chapter_ai_probability(chapter_id, 100, "certain")
```

对应 UI 徽章显示为 "AI 100%"。

---

## 十三、Mock 兜底机制

所有 `*_remote` 方法在 API 不可用时自动回退到 `*_mock` 方法：

| Remote | Mock | 模式 |
|--------|------|------|
| `_generate_remote` | `_generate_mock` | 简单生成 |
| `_summarize_remote` | `_summarize_mock` | 章节摘要 |
| `_multi_agent_generate_remote` | `_multi_agent_generate_mock` | 长篇生成 |
| `_multi_agent_review_remote` | `_multi_agent_review_mock` | 长篇校验 |
| `_cross_chapter_check_remote` | `_cross_chapter_check_mock` | 跨章节检查 |
| 风格/声音/关系提取 | 均有对应 mock 变体 | |

所有 mock 方法返回带有 `"本地 Mock"` 标记的内容和固定 low/medium severity findings。

回退条件：`_remote` 方法抛出异常且 `require_remote=False`。

---

## 十四、底层 API 通信

### 14.1 同步请求（_post_chat_completion）

[ai_service.py L1784-L1806](file:///f:/项目/simple_ai_novel_py/novel_app/ai_service.py#L1784-L1806)

```python
def _post_chat_completion(self, messages, temperature, purpose):
    # POST /chat/completions
    # Headers: Authorization, Content-Type
    # Timeout: 120s
    # 返回: response["choices"][0]["message"]["content"]
```

### 14.2 流式请求（_stream_chat_completion）

[ai_service.py L1808-L1844](file:///f:/项目/simple_ai_novel_py/novel_app/ai_service.py#L1808-L1844)

```python
def _stream_chat_completion(self, messages, temperature, purpose, cancel_event=None):
    # POST /chat/completions (stream=True)
    # SSE 逐行读取
    # 检查 cancel_event.is_set()
    # 返回: Iterator[str]
```

---

## 十五、文件索引

| 文件 | 核心内容 |
|------|----------|
| [qt_app.py](file:///f:/项目/simple_ai_novel_py/novel_app/qt_app.py) | UI 触发入口、上下文构建函数、安全门、回调处理 |
| [ai_service.py](file:///f:/项目/simple_ai_novel_py/novel_app/ai_service.py) | 所有 AI 生成方法、Prompt 模板、JSON 解析、Mock 兜底 |
| [qt/workers.py](file:///f:/项目/simple_ai_novel_py/novel_app/qt/workers.py) | AiWorker / FunctionWorker 线程类 |
| [qt/helpers.py](file:///f:/项目/simple_ai_novel_py/novel_app/qt/helpers.py) | AI_PROBABILITY_META、概率归一化 |
| [qt/dialogs.py](file:///f:/项目/simple_ai_novel_py/novel_app/qt/dialogs.py) | AiSettingsDialog（AI API 配置） |
| [database.py](file:///f:/项目/simple_ai_novel_py/novel_app/database.py) | chapters / review_runs / review_findings 表操作 |
