from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FontScale:
    family_ui: str
    family_code: str
    size_display: int
    size_heading1: int
    size_heading2: int
    size_body: int
    size_body_small: int
    size_caption: int
    size_code: int

    @staticmethod
    def default() -> FontScale:
        return FontScale(
            family_ui="Microsoft YaHei UI",
            family_code="Cascadia Code",
            size_display=20,
            size_heading1=16,
            size_heading2=12,
            size_body=11,
            size_body_small=10,
            size_caption=9,
            size_code=10,
        )

    def display(self) -> tuple[str, int, str]:
        return (self.family_ui, self.size_display, "bold")

    def heading1(self) -> tuple[str, int, str]:
        return (self.family_ui, self.size_heading1, "bold")

    def heading2(self) -> tuple[str, int, str]:
        return (self.family_ui, self.size_heading2, "bold")

    def body(self) -> tuple[str, int]:
        return (self.family_ui, self.size_body)

    def body_bold(self) -> tuple[str, int, str]:
        return (self.family_ui, self.size_body, "bold")

    def body_small(self) -> tuple[str, int]:
        return (self.family_ui, self.size_body_small)

    def caption(self) -> tuple[str, int]:
        return (self.family_ui, self.size_caption)

    def code(self) -> tuple[str, int]:
        return (self.family_code, self.size_code)

    def as_kwargs(self) -> dict[str, Any]:
        return {
            "family_ui": self.family_ui,
            "family_code": self.family_code,
            "size_display": self.size_display,
            "size_heading1": self.size_heading1,
            "size_heading2": self.size_heading2,
            "size_body": self.size_body,
            "size_body_small": self.size_body_small,
            "size_caption": self.size_caption,
            "size_code": self.size_code,
        }

    def scaled(self, factor: float) -> FontScale:
        return FontScale(
            family_ui=self.family_ui,
            family_code=self.family_code,
            size_display=int(self.size_display * factor),
            size_heading1=int(self.size_heading1 * factor),
            size_heading2=int(self.size_heading2 * factor),
            size_body=int(self.size_body * factor),
            size_body_small=int(self.size_body_small * factor),
            size_caption=int(self.size_caption * factor),
            size_code=int(self.size_code * factor),
        )


class FontSystem:
    def __init__(self, scale: FontScale | None = None):
        self.scale = scale or FontScale.default()

    def display(self) -> tuple[str, int, str]:
        return self.scale.display()

    def heading1(self) -> tuple[str, int, str]:
        return self.scale.heading1()

    def heading2(self) -> tuple[str, int, str]:
        return self.scale.heading2()

    def body(self) -> tuple[str, int]:
        return self.scale.body()

    def body_bold(self) -> tuple[str, int, str]:
        return self.scale.body_bold()

    def body_small(self) -> tuple[str, int]:
        return self.scale.body_small()

    def caption(self) -> tuple[str, int]:
        return self.scale.caption()

    def code(self) -> tuple[str, int]:
        return self.scale.code()
