from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SpacingScale:
    xs: int = 4
    sm: int = 8
    md: int = 12
    lg: int = 16
    xl: int = 24
    xl2: int = 32
    xl3: int = 48

    def as_dict(self) -> dict[str, int]:
        return {
            "xs": self.xs,
            "sm": self.sm,
            "md": self.md,
            "lg": self.lg,
            "xl": self.xl,
            "xl2": self.xl2,
            "xl3": self.xl3,
        }


class SpacingSystem:
    def __init__(self, scale: SpacingScale | None = None):
        self.scale = scale or SpacingScale()

    @property
    def xs(self) -> int:
        return self.scale.xs

    @property
    def sm(self) -> int:
        return self.scale.sm

    @property
    def md(self) -> int:
        return self.scale.md

    @property
    def lg(self) -> int:
        return self.scale.lg

    @property
    def xl(self) -> int:
        return self.scale.xl

    @property
    def xl2(self) -> int:
        return self.scale.xl2

    @property
    def xl3(self) -> int:
        return self.scale.xl3

    def padx(self, level: str) -> int:
        return getattr(self.scale, level.replace("-", "").replace("2", "2").replace("3", "3"), self.md)

    def pady(self, level: str) -> int:
        return self.padx(level)
