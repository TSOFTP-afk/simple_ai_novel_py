from __future__ import annotations

import re
from typing import Any


_PINYIN_FEATURES: dict[str, dict[str, str]] = {
    "在": {"initial": "z", "final": "ai", "tone": "4"},
    "再": {"initial": "z", "final": "ai", "tone": "4"},
    "的": {"initial": "d", "final": "e", "tone": "5"},
    "地": {"initial": "d", "final": "i", "tone": "4"},
    "得": {"initial": "d", "final": "e", "tone": "2"},
    "己": {"initial": "j", "final": "i", "tone": "3"},
    "已": {"initial": "y", "final": "i", "tone": "3"},
    "即": {"initial": "j", "final": "i", "tone": "2"},
    "及": {"initial": "j", "final": "i", "tone": "2"},
    "急": {"initial": "j", "final": "i", "tone": "2"},
    "既": {"initial": "j", "final": "i", "tone": "4"},
    "继": {"initial": "j", "final": "i", "tone": "4"},
    "计": {"initial": "j", "final": "i", "tone": "4"},
    "记": {"initial": "j", "final": "i", "tone": "4"},
    "径": {"initial": "j", "final": "ing", "tone": "4"},
    "胫": {"initial": "j", "final": "ing", "tone": "4"},
    "励": {"initial": "l", "final": "i", "tone": "4"},
    "厉": {"initial": "l", "final": "i", "tone": "4"},
    "霄": {"initial": "x", "final": "iao", "tone": "1"},
    "宵": {"initial": "x", "final": "iao", "tone": "1"},
    "赅": {"initial": "g", "final": "ai", "tone": "1"},
    "骇": {"initial": "h", "final": "ai", "tone": "4"},
    "券": {"initial": "q", "final": "uan", "tone": "4"},
    "卷": {"initial": "j", "final": "uan", "tone": "3"},
    "副": {"initial": "f", "final": "u", "tone": "4"},
    "符": {"initial": "f", "final": "u", "tone": "2"},
    "覆": {"initial": "f", "final": "u", "tone": "4"},
    "复": {"initial": "f", "final": "u", "tone": "4"},
    "辈": {"initial": "b", "final": "ei", "tone": "4"},
    "倍": {"initial": "b", "final": "ei", "tone": "4"},
    "筹": {"initial": "ch", "final": "ou", "tone": "2"},
    "愁": {"initial": "ch", "final": "ou", "tone": "2"},
    "墨": {"initial": "m", "final": "o", "tone": "4"},
    "默": {"initial": "m", "final": "o", "tone": "4"},
    "赖": {"initial": "l", "final": "ai", "tone": "4"},
    "癞": {"initial": "l", "final": "ai", "tone": "4"},
    "省": {"initial": "x", "final": "ing", "tone": "3"},
    "醒": {"initial": "x", "final": "ing", "tone": "3"},
}

_WORD_CONFUSIONS: dict[str, str] = {
    "好象": "好像",
    "在次": "再次",
    "在来": "再来",
    "以经": "已经",
    "以为着": "意味着",
    "坚苦": "艰苦",
    "克苦": "刻苦",
    "刻服": "克服",
    "由其": "尤其",
    "不径而走": "不胫而走",
    "不落巢臼": "不落窠臼",
    "一股作气": "一鼓作气",
    "一如继往": "一如既往",
    "一愁莫展": "一筹莫展",
    "人情事故": "人情世故",
    "入场卷": "入场券",
    "出奇不意": "出其不意",
    "出人投地": "出人头地",
    "灸手可热": "炙手可热",
    "迫不急待": "迫不及待",
    "谈笑风声": "谈笑风生",
    "再接再励": "再接再厉",
    "按步就班": "按部就班",
    "搬门弄斧": "班门弄斧",
    "迫在眉捷": "迫在眉睫",
    "言简意骇": "言简意赅",
    "甘败下风": "甘拜下风",
    "自抱自弃": "自暴自弃",
    "食不裹腹": "食不果腹",
    "不记其数": "不计其数",
    "金榜提名": "金榜题名",
    "死皮癞脸": "死皮赖脸",
    "默守成规": "墨守成规",
    "大声急呼": "大声疾呼",
    "天翻地复": "天翻地覆",
    "婷婷玉立": "亭亭玉立",
    "悬梁刺骨": "悬梁刺股",
    "名符其实": "名副其实",
    "名不符实": "名不副实",
    "心心相映": "心心相印",
    "九宵云外": "九霄云外",
    "沤心沥血": "呕心沥血",
    "功不可抹": "功不可没",
    "不加思索": "不假思索",
    "无可非异": "无可非议",
    "发人深醒": "发人深省",
    "美仑美奂": "美轮美奂",
    "扑溯迷离": "扑朔迷离",
    "一獗不振": "一蹶不振",
    "可望不可及": "可望不可即",
    "忧心重重": "忧心忡忡",
    "关怀倍至": "关怀备至",
    "直接了当": "直截了当",
    "既往不究": "既往不咎",
    "前扑后继": "前仆后继",
}

_CONTEXT_CHAR_RULES: list[tuple[re.Pattern[str], str, str, float]] = [
    (re.compile(r"(悄悄|慢慢|轻轻|狠狠|缓缓|迅速|认真|小心翼翼)的(?=[\u4e00-\u9fff])"), "的", "地", 0.72),
    (re.compile(r"(?<=[\u4e00-\u9fff])地(脸|手|眼|声音|脚步|影子)"), "地", "的", 0.72),
    (re.compile(r"在(一次|三|见|度|也|不)(?=[\u4e00-\u9fff，。！？、])"), "在", "再", 0.78),
]


def _pinyin_evidence(wrong: str, suggestion: str) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    for wrong_char, suggestion_char in zip(wrong, suggestion, strict=False):
        wrong_feature = _PINYIN_FEATURES.get(wrong_char)
        suggestion_feature = _PINYIN_FEATURES.get(suggestion_char)
        if not wrong_feature or not suggestion_feature:
            continue
        same_initial = wrong_feature.get("initial") == suggestion_feature.get("initial")
        same_final = wrong_feature.get("final") == suggestion_feature.get("final")
        if same_initial or same_final:
            evidence.append(
                {
                    "wrong_char": wrong_char,
                    "suggestion_char": suggestion_char,
                    "wrong_pinyin": _format_pinyin_feature(wrong_feature),
                    "suggestion_pinyin": _format_pinyin_feature(suggestion_feature),
                }
            )
    return evidence


def _format_pinyin_feature(feature: dict[str, str]) -> str:
    return f"{feature.get('initial', '')}-{feature.get('final', '')}-{feature.get('tone', '')}"


def _make_finding(
    *,
    start: int,
    end: int,
    wrong: str,
    suggestion: str,
    rule: str,
    confidence: float,
) -> dict[str, Any]:
    severity = "medium" if confidence >= 0.85 else "low"
    return {
        "start": start,
        "end": end,
        "wrong": wrong,
        "suggestion": suggestion,
        "severity": severity,
        "dimension": "错别字",
        "rule": rule,
        "confidence": round(confidence, 2),
        "pinyin_features": _pinyin_evidence(wrong, suggestion),
    }


def _dedupe_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings.sort(key=lambda item: (int(item["start"]), -float(item.get("confidence", 0))))
    deduped: list[dict[str, Any]] = []
    occupied: list[range] = []
    for item in findings:
        span = range(int(item["start"]), int(item["end"]))
        if any(item["start"] < existing.stop and item["end"] > existing.start for existing in occupied):
            continue
        deduped.append(item)
        occupied.append(span)
    return deduped


def detect_chinese_typos(text: str) -> list[dict[str, Any]]:
    """Return typo candidates for the selected chapter body only.

    The detector is intentionally conservative: it flags known wrong words first,
    then applies a small set of contextual single-character rules backed by the
    built-in pinyin feature table.
    """
    if not str(text or "").strip():
        return []
    content = str(text)
    findings: list[dict[str, Any]] = []

    for wrong, suggestion in _WORD_CONFUSIONS.items():
        if wrong == suggestion:
            continue
        for match in re.finditer(re.escape(wrong), content):
            findings.append(
                _make_finding(
                    start=match.start(),
                    end=match.end(),
                    wrong=wrong,
                    suggestion=suggestion,
                    rule="confusion_word",
                    confidence=0.96,
                )
            )

    for pattern, wrong, suggestion, confidence in _CONTEXT_CHAR_RULES:
        for match in pattern.finditer(content):
            matched_text = match.group(0)
            wrong_offset = matched_text.rfind(wrong)
            if wrong_offset < 0:
                continue
            start = match.start() + wrong_offset
            findings.append(
                _make_finding(
                    start=start,
                    end=start + len(wrong),
                    wrong=wrong,
                    suggestion=suggestion,
                    rule="pinyin_context",
                    confidence=confidence,
                )
            )

    return _dedupe_findings(findings)
