from __future__ import annotations

from novel_app.theme.design_tokens import (
    ColorTokens, FontTokens, SpacingTokens, BorderTokens, ShadowTokens, DesignTokens,
    LIGHT_TOKENS, DARK_TOKENS
)


class ThemeCustomizer:
    """主题定制器 - 用于定制和扩展主题"""

    @staticmethod
    def create_custom_theme(
        name: str,
        base_tokens: DesignTokens,
        color_overrides: dict[str, str] = None,
        font_overrides: dict[str, any] = None,
        spacing_overrides: dict[str, int] = None,
        border_overrides: dict[str, int] = None,
        shadow_overrides: dict[str, str] = None
    ) -> DesignTokens:
        """创建自定义主题

        Args:
            name: 主题名称
            base_tokens: 基础设计令牌
            color_overrides: 颜色覆盖
            font_overrides: 字体覆盖
            spacing_overrides: 间距覆盖
            border_overrides: 边框覆盖
            shadow_overrides: 阴影覆盖

        Returns:
            自定义设计令牌
        """
        # 复制基础令牌
        colors = ColorTokens(**{k: v for k, v in base_tokens.colors.__dict__.items()})
        fonts = FontTokens(**{k: v for k, v in base_tokens.fonts.__dict__.items()})
        spacing = SpacingTokens(**{k: v for k, v in base_tokens.spacing.__dict__.items()})
        borders = BorderTokens(**{k: v for k, v in base_tokens.borders.__dict__.items()})
        shadows = ShadowTokens(**{k: v for k, v in base_tokens.shadows.__dict__.items()})

        # 应用覆盖
        if color_overrides:
            for key, value in color_overrides.items():
                if hasattr(colors, key):
                    setattr(colors, key, value)

        if font_overrides:
            for key, value in font_overrides.items():
                if hasattr(fonts, key):
                    setattr(fonts, key, value)

        if spacing_overrides:
            for key, value in spacing_overrides.items():
                if hasattr(spacing, key):
                    setattr(spacing, key, value)

        if border_overrides:
            for key, value in border_overrides.items():
                if hasattr(borders, key):
                    setattr(borders, key, value)

        if shadow_overrides:
            for key, value in shadow_overrides.items():
                if hasattr(shadows, key):
                    setattr(shadows, key, value)

        return DesignTokens(
            colors=colors,
            fonts=fonts,
            spacing=spacing,
            borders=borders,
            shadows=shadows
        )

    @staticmethod
    def create_high_contrast_theme() -> DesignTokens:
        """创建高对比度主题

        Returns:
            高对比度设计令牌
        """
        return ThemeCustomizer.create_custom_theme(
            "high_contrast",
            LIGHT_TOKENS,
            color_overrides={
                "bg_app": "#ffffff",
                "bg_surface": "#f0f0f0",
                "text_primary": "#000000",
                "text_secondary": "#333333",
                "primary": "#0000ff",
                "primary_hover": "#0000cc",
                "border": "#000000",
            }
        )

    @staticmethod
    def create_dark_theme() -> DesignTokens:
        """创建深色主题

        Returns:
            深色设计令牌
        """
        return DARK_TOKENS

    @staticmethod
    def create_light_theme() -> DesignTokens:
        """创建浅色主题

        Returns:
            浅色设计令牌
        """
        return LIGHT_TOKENS


class ComponentThemer:
    """组件主题器 - 用于为组件应用主题"""

    @staticmethod
    def get_component_styles(tokens: DesignTokens, component_type: str) -> dict:
        """获取组件样式

        Args:
            tokens: 设计令牌
            component_type: 组件类型

        Returns:
            组件样式字典
        """
        styles = {
            "button": {
                "primary": {
                    "background": tokens.colors.primary,
                    "foreground": tokens.colors.text_inverse,
                    "hover_background": tokens.colors.primary_hover,
                    "border_radius": tokens.borders.radius_md,
                    "padding": (tokens.spacing.md, tokens.spacing.sm),
                    "font": (tokens.fonts.family_ui, tokens.fonts.size_body_small),
                },
                "secondary": {
                    "background": tokens.colors.bg_surface_alt,
                    "foreground": tokens.colors.text_primary,
                    "hover_background": tokens.colors.primary_soft,
                    "border_radius": tokens.borders.radius_md,
                    "padding": (tokens.spacing.sm, tokens.spacing.xs),
                    "font": (tokens.fonts.family_ui, tokens.fonts.size_body_small),
                },
                "ghost": {
                    "background": "transparent",
                    "foreground": tokens.colors.text_secondary,
                    "hover_background": tokens.colors.bg_surface_alt,
                    "border_radius": tokens.borders.radius_md,
                    "padding": (tokens.spacing.sm, tokens.spacing.xs),
                    "font": (tokens.fonts.family_ui, tokens.fonts.size_body_small),
                },
                "danger": {
                    "background": tokens.colors.bg_surface,
                    "foreground": tokens.colors.danger,
                    "hover_background": tokens.colors.bg_surface_alt,
                    "border_radius": tokens.borders.radius_md,
                    "padding": (tokens.spacing.md, tokens.spacing.sm),
                    "font": (tokens.fonts.family_ui, tokens.fonts.size_body_small),
                },
            },
            "input": {
                "background": tokens.colors.bg_surface,
                "foreground": tokens.colors.text_primary,
                "border": tokens.colors.border,
                "border_radius": tokens.borders.radius_md,
                "padding": (tokens.spacing.sm, tokens.spacing.sm),
                "font": (tokens.fonts.family_ui, tokens.fonts.size_body),
            },
            "text_editor": {
                "background": tokens.colors.bg_editor,
                "foreground": tokens.colors.text_primary,
                "border": tokens.colors.border,
                "border_radius": tokens.borders.radius_md,
                "padding": (tokens.spacing.md, tokens.spacing.md),
                "font": (tokens.fonts.family_ui, tokens.fonts.size_body),
            },
            "panel": {
                "background": tokens.colors.bg_surface,
                "border": tokens.colors.border,
                "border_radius": tokens.borders.radius_md,
                "padding": tokens.spacing.md,
            },
        }
        return styles.get(component_type, {})
