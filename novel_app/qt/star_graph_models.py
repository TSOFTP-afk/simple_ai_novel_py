from dataclasses import dataclass, field
from typing import Optional


@dataclass
class NodeStyle:
    id: Optional[int] = None
    book_id: int = 0
    name: str = "neutral"
    display_name: str = "中立"
    background: str = "#FFFFFF"
    border_color: str = "#D6DFEA"
    border_width: float = 1.5
    text_color: str = "#1F2A36"
    icon_type: str = "default"
    is_preset: bool = True


@dataclass
class RelationshipType:
    id: Optional[int] = None
    book_id: int = 0
    name: str = "unknown"
    display_name: str = "未知"
    color: str = "#5F7088"
    line_style: str = "dotted"
    arrow_type: str = "bi-directional"
    is_directed: bool = False
    is_preset: bool = True


PRESET_NODE_STYLES = [
    NodeStyle(name="protagonist", display_name="主角", background="#DCE8FB", border_color="#2E6FD8", icon_type="hero"),
    NodeStyle(name="antagonist", display_name="反派", background="#FDECEA", border_color="#D83A34", icon_type="villain"),
    NodeStyle(name="supporting", display_name="配角", background="#F6F9FC", border_color="#6A7788", icon_type="npc"),
    NodeStyle(name="minor", display_name="NPC", background="#F3F3F3", border_color="#AAAAAA", icon_type="minor"),
    NodeStyle(name="neutral", display_name="中立", background="#FFFFFF", border_color="#D6DFEA", icon_type="neutral"),
]


PRESET_RELATIONSHIP_TYPES = [
    RelationshipType(name="master_apprentice", display_name="师徒", color="#2E6FD8", line_style="solid", arrow_type="bi-directional"),
    RelationshipType(name="blood", display_name="血缘", color="#E7726A", line_style="solid", arrow_type="bi-directional"),
    RelationshipType(name="hostile", display_name="敌对", color="#D83A34", line_style="dashed", arrow_type="unidirectional"),
    RelationshipType(name="friendly", display_name="友爱", color="#29B67A", line_style="solid", arrow_type="bi-directional"),
    RelationshipType(name="romantic", display_name="恋人", color="#E7B547", line_style="solid", arrow_type="bi-directional"),
    RelationshipType(name="subordinate", display_name="从属", color="#6A7788", line_style="dashed", arrow_type="unidirectional"),
    RelationshipType(name="unknown", display_name="未知", color="#5F7088", line_style="dotted", arrow_type="bi-directional"),
]
