from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class ColorTokens:
    """色彩设计令牌"""
    # 背景色
    bg_app: str         # 应用背景
    bg_surface: str     # 表面背景
    bg_surface_alt: str # 替代表面背景
    bg_editor: str      # 编辑器背景
    
    # 文本色
    text_primary: str   # 主要文本
    text_secondary: str # 次要文本
    text_tertiary: str  # 第三文本
    text_inverse: str   # 反色文本
    
    # 功能色
    primary: str        # 主色
    primary_hover: str  # 主色悬停
    primary_soft: str   # 主色柔和
    
    # 状态色
    success: str        # 成功
    warning: str        # 警告
    danger: str         # 危险
    info: str           # 信息
    
    # 边框和分割线
    border: str         # 边框
    divider: str        # 分割线
    
    # 其他
    focus_ring: str     # 焦点环
    selection: str      # 选择
    scrollbar: str      # 滚动条


@dataclass(frozen=True)
class FontTokens:
    """字体设计令牌"""
    # 字体家族
    family_ui: str      # UI字体
    family_code: str    # 代码字体
    
    # 字体大小
    size_display: int   # 显示大小
    size_heading1: int  # 标题1大小
    size_heading2: int  # 标题2大小
    size_body: int      # 正文字大小
    size_body_small: int # 小正文字大小
    size_caption: int   # 说明文字大小
    size_code: int      # 代码文字大小
    
    # 字体权重
    weight_light: str   # 轻
    weight_regular: str # 常规
    weight_medium: str  # 中等
    weight_bold: str    # 粗体


@dataclass(frozen=True)
class SpacingTokens:
    """间距设计令牌"""
    xs: int    # 极小
    sm: int    # 小
    md: int    # 中等
    lg: int    # 大
    xl: int    # 极大
    xl2: int   # 超大
    xl3: int   # 特大


@dataclass(frozen=True)
class BorderTokens:
    """边框设计令牌"""
    radius_sm: int      # 小圆角
    radius_md: int      # 中圆角
    radius_lg: int      # 大圆角
    radius_full: int    # 全圆角
    
    width_1: int        # 1px边框
    width_2: int        # 2px边框


@dataclass(frozen=True)
class ShadowTokens:
    """阴影设计令牌"""
    sm: str     # 小阴影
    md: str     # 中阴影
    lg: str     # 大阴影
    xl: str     # 超大阴影


@dataclass(frozen=True)
class DesignTokens:
    """设计令牌集合"""
    colors: ColorTokens
    fonts: FontTokens
    spacing: SpacingTokens
    borders: BorderTokens
    shadows: ShadowTokens


# 亮色主题设计令牌
LIGHT_COLORS = ColorTokens(
    bg_app="#f8f9fa",
    bg_surface="#ffffff",
    bg_surface_alt="#f1f3f5",
    bg_editor="#ffffff",
    text_primary="#212529",
    text_secondary="#6c757d",
    text_tertiary="#adb5bd",
    text_inverse="#ffffff",
    primary="#007bff",
    primary_hover="#0069d9",
    primary_soft="#e3f2fd",
    success="#28a745",
    warning="#ffc107",
    danger="#dc3545",
    info="#17a2b8",
    border="#dee2e6",
    divider="#e9ecef",
    focus_ring="#80bdff",
    selection="#b3d7ff",
    scrollbar="#dee2e6"
)

# 暗色主题设计令牌
DARK_COLORS = ColorTokens(
    bg_app="#1a1a1a",
    bg_surface="#2d2d2d",
    bg_surface_alt="#3d3d3d",
    bg_editor="#1e1e1e",
    text_primary="#e9ecef",
    text_secondary="#adb5bd",
    text_tertiary="#6c757d",
    text_inverse="#212529",
    primary="#17a2b8",
    primary_hover="#138496",
    primary_soft="#1e3a5f",
    success="#28a745",
    warning="#ffc107",
    danger="#dc3545",
    info="#007bff",
    border="#495057",
    divider="#343a40",
    focus_ring="#007bff",
    selection="#007bff",
    scrollbar="#495057"
)

# 字体令牌
FONT_TOKENS = FontTokens(
    family_ui="Segoe UI, Tahoma, Geneva, Verdana, sans-serif",
    family_code="Consolas, Monaco, 'Courier New', monospace",
    size_display=24,
    size_heading1=20,
    size_heading2=16,
    size_body=14,
    size_body_small=12,
    size_caption=11,
    size_code=13,
    weight_light="light",
    weight_regular="normal",
    weight_medium="medium",
    weight_bold="bold"
)

# 间距令牌
SPACING_TOKENS = SpacingTokens(
    xs=4,
    sm=8,
    md=12,
    lg=16,
    xl=24,
    xl2=32,
    xl3=48
)

# 边框令牌
BORDER_TOKENS = BorderTokens(
    radius_sm=4,
    radius_md=8,
    radius_lg=12,
    radius_full=9999,
    width_1=1,
    width_2=2
)

# 阴影令牌
SHADOW_TOKENS = ShadowTokens(
    sm="0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)",
    md="0 4px 6px rgba(0,0,0,0.12), 0 2px 4px rgba(0,0,0,0.24)",
    lg="0 10px 15px rgba(0,0,0,0.12), 0 4px 6px rgba(0,0,0,0.24)",
    xl="0 14px 20px rgba(0,0,0,0.12), 0 8px 10px rgba(0,0,0,0.24)"
)

# 亮色主题设计令牌集合
LIGHT_TOKENS = DesignTokens(
    colors=LIGHT_COLORS,
    fonts=FONT_TOKENS,
    spacing=SPACING_TOKENS,
    borders=BORDER_TOKENS,
    shadows=SHADOW_TOKENS
)

# 暗色主题设计令牌集合
DARK_TOKENS = DesignTokens(
    colors=DARK_COLORS,
    fonts=FONT_TOKENS,
    spacing=SPACING_TOKENS,
    borders=BORDER_TOKENS,
    shadows=SHADOW_TOKENS
)


def get_design_tokens(mode: str = "light") -> DesignTokens:
    """获取设计令牌集合

    Args:
        mode: 主题模式，"light"或"dark"

    Returns:
        设计令牌集合
    """
    if mode == "dark":
        return DARK_TOKENS
    return LIGHT_TOKENS
