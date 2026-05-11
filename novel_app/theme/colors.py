from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ColorPalette:
    bg_app: str
    bg_surface: str
    bg_surface_alt: str
    bg_editor: str

    text_primary: str
    text_secondary: str
    text_tertiary: str
    text_inverse: str

    primary: str
    primary_hover: str
    primary_soft: str

    success: str
    warning: str
    danger: str
    info: str

    border: str
    divider: str
    focus_ring: str
    selection: str
    scrollbar: str

    def to_dict(self) -> dict[str, str]:
        return {
            "bg_app": self.bg_app,
            "bg_surface": self.bg_surface,
            "bg_surface_alt": self.bg_surface_alt,
            "bg_editor": self.bg_editor,
            "text_primary": self.text_primary,
            "text_secondary": self.text_secondary,
            "text_tertiary": self.text_tertiary,
            "text_inverse": self.text_inverse,
            "primary": self.primary,
            "primary_hover": self.primary_hover,
            "primary_soft": self.primary_soft,
            "success": self.success,
            "warning": self.warning,
            "danger": self.danger,
            "info": self.info,
            "border": self.border,
            "divider": self.divider,
            "focus_ring": self.focus_ring,
            "selection": self.selection,
            "scrollbar": self.scrollbar,
        }


LIGHT_PALETTE = ColorPalette(
    bg_app="#F0F4F8",
    bg_surface="#FFFFFF",
    bg_surface_alt="#F7F9FC",
    bg_editor="#FCFDFE",
    text_primary="#1A2332",
    text_secondary="#556677",
    text_tertiary="#8899AA",
    text_inverse="#FFFFFF",
    primary="#3366CC",
    primary_hover="#2952A3",
    primary_soft="#EBF0FA",
    success="#2D9D5A",
    warning="#D4A030",
    danger="#D14343",
    info="#3388DD",
    border="#DDE3EA",
    divider="#EEF2F6",
    focus_ring="#99BBEE",
    selection="#D0E0F8",
    scrollbar="#CCD4DD",
)

DARK_PALETTE = ColorPalette(
    bg_app="#0F1419",
    bg_surface="#1A2332",
    bg_surface_alt="#243041",
    bg_editor="#141A21",
    text_primary="#EBF0F8",
    text_secondary="#91A0B5",
    text_tertiary="#6A7788",
    text_inverse="#0F1419",
    primary="#5DA4F5",
    primary_hover="#7FBDF8",
    primary_soft="#1A2838",
    success="#29B67A",
    warning="#E7B547",
    danger="#E7726A",
    info="#5DA4F5",
    border="#2F3E53",
    divider="#243041",
    focus_ring="#5DA4F5",
    selection="#1A3048",
    scrollbar="#3A4A5E",
)


def get_palette(theme_mode: str) -> ColorPalette:
    if theme_mode == "dark":
        return DARK_PALETTE
    return LIGHT_PALETTE
