from __future__ import annotations

from typing import Any

AUDIT_DIMENSIONS: list[dict[str, Any]] = [
    {
        "id": "plot_structure",
        "name": "情节结构",
        "description": "检查章节是否有完整起承转合，推进主线发展",
        "check_prompt": "分析本章的情节结构：1) 是否有明确的开场和收尾 2) 是否推进了主线 3) 是否有高潮或转折",
        "weight": 1.2,
    },
    {
        "id": "character_continuity",
        "name": "人物连续性",
        "description": "检查人物行为、对话风格、关系状态是否与设定一致",
        "check_prompt": "检查所有出场角色：1) 言行是否符合设定 2) 关系状态是否连贯 3) 是否有未声明的能力或知识",
        "weight": 1.5,
    },
    {
        "id": "world_consistency",
        "name": "世界观一致性",
        "description": "检查设定、规则、地理、时间线是否无冲突",
        "check_prompt": "验证世界观：1) 设定/规则是否被遵循 2) 时间线是否合理 3) 地理/空间描述是否一致",
        "weight": 1.3,
    },
    {
        "id": "logic_coherence",
        "name": "逻辑连贯性",
        "description": "检查事件因果链条是否合理，是否存在逻辑跳跃",
        "check_prompt": "检查逻辑：1) 事件因果是否合理 2) 是否有信息缺失导致理解困难 3) 角色决策是否有合理动机",
        "weight": 1.2,
    },
    {
        "id": "style_stability",
        "name": "风格稳定性",
        "description": "检查叙事风格、节奏、语调是否前后一致",
        "check_prompt": "检查风格：1) 叙事风格是否与全书一致 2) 节奏是否恰当 3) 语调是否稳定",
        "weight": 0.8,
    },
    {
        "id": "ooc_detection",
        "name": "OOC 检测",
        "description": "检查角色言行是否超出设定范围（Out of Character）",
        "check_prompt": "OOC 检测：逐一检查每个角色的言行是否超出其设定中的性格、能力、知识范围",
        "weight": 1.5,
    },
    {
        "id": "ai_flavor",
        "name": "AI 痕迹检测",
        "description": "检测是否有明显的 AI 生成模式（重复句式、模板化表达等）",
        "check_prompt": "AI 痕迹检测：1) 是否有重复句式 2) 是否有模板化概括 3) 是否有突兀的抒情/总结",
        "weight": 1.0,
    },
    {
        "id": "hook_tracking",
        "name": "伏笔追踪",
        "description": "检查已有伏笔是否被适当引用或推进",
        "check_prompt": "伏笔检查：1) Truth File 中的未回收伏笔是否被提及或推进 2) 是否新增了伏笔",
        "weight": 0.9,
    },
    {
        "id": "emotion_arc",
        "name": "情感弧光",
        "description": "检查角色情感变化是否自然、有层次",
        "check_prompt": "情感检查：1) 角色情感是否有变化 2) 情感转变是否有铺垫 3) 情感表达是否恰当",
        "weight": 0.7,
    },
    {
        "id": "pacing",
        "name": "节奏控制",
        "description": "检查叙事节奏是否合适（快慢分布、场景切换频率）",
        "check_prompt": "节奏检查：1) 场景切换是否流畅 2) 快慢节奏分布是否合理 3) 是否有拖沓或仓促段落",
        "weight": 0.8,
    },
    {
        "id": "dialogue_quality",
        "name": "对话质量",
        "description": "检查对话的自然度和角色辨识度",
        "check_prompt": "对话检查：1) 对话是否自然 2) 不同角色的说话方式是否有区分 3) 对话是否推动情节",
        "weight": 0.8,
    },
    {
        "id": "template_alignment",
        "name": "模板对齐",
        "description": "检查与指定对照模板的风格相似度",
        "check_prompt": "模板对比：当前章节的叙事风格、结构、节奏与对照模板的相似度和偏离点",
        "weight": 0.6,
    },
]

AUDIT_DIMENSION_MAP: dict[str, dict[str, Any]] = {d["id"]: d for d in AUDIT_DIMENSIONS}

DEFAULT_AUDIT_WEIGHTS = {d["id"]: d["weight"] for d in AUDIT_DIMENSIONS}


def get_dimension_label(dim_id: str) -> str:
    dim = AUDIT_DIMENSION_MAP.get(dim_id)
    return dim["name"] if dim else dim_id


def get_active_dimensions(selected: list[str] | None = None) -> list[dict[str, Any]]:
    if not selected:
        return AUDIT_DIMENSIONS
    return [d for d in AUDIT_DIMENSIONS if d["id"] in selected]