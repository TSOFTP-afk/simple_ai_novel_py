from __future__ import annotations

from typing import Any


GITHUB_RESEARCH_POOL: list[dict[str, Any]] = [
    {
        "title": "OpenWrite",
        "url": "https://ilrein.github.io/openwrite/",
        "repo_url": "",
        "license": "待确认",
        "reuse_level": "pattern_only",
        "focus": "AI 写作平台、项目工作流、sourcebook/项目级上下文组织。",
        "patterns": [
            "把作品资料、章节任务、AI 辅助入口聚合到项目工作台。",
            "让提示词构建依赖结构化上下文，而不是只依赖正文输入框。",
            "重操作放到专门窗口，正文区保持低噪音。",
        ],
        "risk_note": "未确认仓库和许可前，只做产品模式学习，不做代码复用。",
    },
    {
        "title": "AugmentedQuill",
        "url": "https://github.com/StableLlamaAI/AugmentedQuill",
        "repo_url": "https://github.com/StableLlamaAI/AugmentedQuill",
        "license": "待确认",
        "reuse_level": "pattern_only",
        "focus": "本地优先 AI 写作桌面、隐私友好、可替换模型工作流。",
        "patterns": [
            "把 AI 能力包装成写作桌面里的可选工具，而不是强制接管编辑。",
            "强调本地/私有模型路径，适合离线草稿和隐私敏感设定资料。",
            "将生成、润色、辅助分析拆成清晰任务。",
        ],
        "risk_note": "默认不复制实现；只抽象学习本地优先和任务化 AI 体验。",
    },
    {
        "title": "Writingway2",
        "url": "https://github.com/aomukai/Writingway2",
        "repo_url": "https://github.com/aomukai/Writingway2",
        "license": "待确认",
        "reuse_level": "pattern_only",
        "focus": "轻量 AI 写作辅助、提示词构建、私密写作体验。",
        "patterns": [
            "以较少控件完成写作、提示词、AI 输出之间的切换。",
            "把提示词构建做成用户可理解的中间产物。",
            "保持轻量，不让设置面板挤占正文区。",
        ],
        "risk_note": "许可未确认前不复用代码，只提炼提示词构建体验。",
    },
    {
        "title": "NovelForge",
        "url": "https://github.com/RhythmicWave/NovelForge",
        "repo_url": "https://github.com/RhythmicWave/NovelForge",
        "license": "待确认",
        "reuse_level": "pattern_only",
        "focus": "长篇生成工作流、章节规划、多轮生成与管理。",
        "patterns": [
            "把长篇创作拆成书籍、章节、生成任务和修订结果。",
            "重视生成前的结构化规划，减少一次性自由生成的漂移。",
            "适合提炼章节链路、批量生成和任务监控模式。",
        ],
        "risk_note": "只把长篇流程拆解为 Skills，不导入实现代码。",
    },
    {
        "title": "AI_NovelGenerator",
        "url": "https://github.com/YILING0013/AI_NovelGenerator",
        "repo_url": "https://github.com/YILING0013/AI_NovelGenerator",
        "license": "待确认",
        "reuse_level": "pattern_only",
        "focus": "多章节生成、上下文延续、伏笔和一致性提示。",
        "patterns": [
            "把前文摘要、章节大纲和当前目标同时纳入生成上下文。",
            "针对伏笔、回收和矛盾点做显式检查。",
            "把连续性当成独立辅助任务，而不是生成失败后的补救。",
        ],
        "risk_note": "连续性策略可抽象复用；代码复用需先完成许可审查。",
    },
    {
        "title": "WriteHERE",
        "url": "https://github.com/principia-ai/WriteHERE",
        "repo_url": "https://github.com/principia-ai/WriteHERE",
        "license": "待确认",
        "reuse_level": "pattern_only",
        "focus": "写作助手、编辑体验、AI 辅助检查。",
        "patterns": [
            "围绕编辑器提供低打扰 AI 入口。",
            "把 AI 输出定位为建议或草稿，不覆盖作者判断。",
            "适合提炼检查、改写、辅助分析的按钮层级。",
        ],
        "risk_note": "只学习交互模式；许可明确前不使用源代码。",
    },
    {
        "title": "autonovel",
        "url": "https://github.com/NousResearch/autonovel",
        "repo_url": "https://github.com/NousResearch/autonovel",
        "license": "待确认",
        "reuse_level": "pattern_only",
        "focus": "自动小说生成、agent 化故事流程、长上下文探索。",
        "patterns": [
            "把故事生成拆成计划、写作、检查、迭代几个阶段。",
            "使用明确任务角色降低长篇生成发散。",
            "适合提炼为开发侧的 AI 写作流程 Skill。",
        ],
        "risk_note": "默认只做研究笔记和 workflow Skill，不进入应用代码复用。",
    },
]


def render_research_note(project: dict[str, Any]) -> str:
    patterns = "\n".join(f"- {item}" for item in project["patterns"])
    return (
        f"# {project['title']}\n\n"
        f"- URL: {project['url']}\n"
        f"- Repository: {project.get('repo_url') or '待确认'}\n"
        f"- License: {project['license']}\n"
        f"- Reuse level: {project['reuse_level']}\n\n"
        f"## Focus\n{project['focus']}\n\n"
        f"## Patterns to Distill\n{patterns}\n\n"
        f"## Risk Note\n{project['risk_note']}\n"
    )
