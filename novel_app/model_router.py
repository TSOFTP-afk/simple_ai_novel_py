from __future__ import annotations

from typing import Any, Callable

MODEL_PRESETS: dict[str, dict[str, Any]] = {
    "default": {
        "label": "默认模型",
        "description": "所有 Agent 使用统一模型",
    },
    "budget": {
        "label": "经济配置",
        "description": "审查类 Agent 使用廉价模型节省成本",
        "mapping": {
            "Planner(大纲拆解)": {"model": "deepseek-chat", "temperature": 0.3, "max_tokens": 4096},
            "Writer(正文写手)": {"model": "deepseek-chat", "temperature": 0.7, "max_tokens": 8192},
            "Auditor(一致性审计)": {"model": "deepseek-chat", "temperature": 0.25, "max_tokens": 4096},
            "Auditor(长篇审查)": {"model": "deepseek-chat", "temperature": 0.25, "max_tokens": 4096},
            "Reviser(修订润色)": {"model": "deepseek-chat", "temperature": 0.4, "max_tokens": 8192},
        },
    },
    "quality": {
        "label": "质量优先",
        "description": "写作和审计使用推理模型，大纲和修订使用普通模型",
        "mapping": {
            "Planner(大纲拆解)": {"model": "deepseek-chat", "temperature": 0.3, "max_tokens": 4096},
            "Writer(正文写手)": {"model": "deepseek-reasoner", "temperature": 0.5, "max_tokens": 8192},
            "Auditor(一致性审计)": {"model": "deepseek-reasoner", "temperature": 0.15, "max_tokens": 4096},
            "Auditor(长篇审查)": {"model": "deepseek-reasoner", "temperature": 0.15, "max_tokens": 4096},
            "Reviser(修订润色)": {"model": "deepseek-chat", "temperature": 0.4, "max_tokens": 8192},
        },
    },
}

DEFAULT_AGENT_OVERRIDES: dict[str, dict[str, Any]] = {
    "Planner(大纲拆解)": {"temperature": 0.3, "max_tokens": 4096},
    "Writer(正文写手)": {"temperature": 0.7, "max_tokens": 8192},
    "Auditor(一致性审计)": {"temperature": 0.25, "max_tokens": 4096},
    "Auditor(长篇审查)": {"temperature": 0.25, "max_tokens": 4096},
    "Reviser(修订润色)": {"temperature": 0.4, "max_tokens": 8192},
}


class ModelRouter:
    def __init__(self, default_model: str = "deepseek-chat", preset: str = "budget") -> None:
        self.default_model = default_model
        self.preset_name = preset
        self._mapping = MODEL_PRESETS.get(preset, MODEL_PRESETS["budget"]).get("mapping", {})
        self._custom_overrides: dict[str, dict[str, Any]] = {}

    @property
    def preset_label(self) -> str:
        return MODEL_PRESETS.get(self.preset_name, {}).get("label", "自定义")

    @property
    def preset_description(self) -> str:
        return MODEL_PRESETS.get(self.preset_name, {}).get("description", "")

    def set_preset(self, preset_name: str) -> None:
        if preset_name not in MODEL_PRESETS:
            raise ValueError(f"Unknown preset: {preset_name}")
        self.preset_name = preset_name
        self._mapping = MODEL_PRESETS[preset_name].get("mapping", {})

    def set_override(self, agent_name: str, model: str | None = None, temperature: float | None = None, max_tokens: int | None = None) -> None:
        override: dict[str, Any] = {}
        if model is not None:
            override["model"] = model
        if temperature is not None:
            override["temperature"] = temperature
        if max_tokens is not None:
            override["max_tokens"] = max_tokens
        self._custom_overrides[agent_name] = override

    def get_config(self, agent_name: str) -> dict[str, Any]:
        base: dict[str, Any] = {
            "model": self.default_model,
            "temperature": 0.7,
            "max_tokens": 4096,
        }
        preset_config = self._mapping.get(agent_name, {})
        base.update(preset_config)
        agent_defaults = DEFAULT_AGENT_OVERRIDES.get(agent_name, {})
        base.update(agent_defaults)
        custom = self._custom_overrides.get(agent_name, {})
        base.update(custom)
        return base

    def get_model(self, agent_name: str) -> str:
        return self.get_config(agent_name).get("model", self.default_model) or self.default_model

    def get_temperature(self, agent_name: str) -> float:
        return float(self.get_config(agent_name).get("temperature", 0.7))

    def get_max_tokens(self, agent_name: str) -> int:
        return int(self.get_config(agent_name).get("max_tokens", 4096))

    def wrap_post_chat(
        self,
        original: Callable[..., dict[str, Any]],
        agent_name: str,
    ) -> Callable[..., dict[str, Any]]:
        config = self.get_config(agent_name)

        def _wrapped(*args: Any, **kwargs: Any) -> dict[str, Any]:
            kwargs.setdefault("model", config.get("model", self.default_model))
            kwargs.setdefault("temperature", config.get("temperature", 0.7))
            kwargs.setdefault("max_tokens", config.get("max_tokens", 4096))
            return original(*args, **kwargs)

        return _wrapped