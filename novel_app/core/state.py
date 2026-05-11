from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, TypeVar, Generic

from novel_app.core.event_bus import get_event_bus

T = TypeVar('T')


@dataclass
class StateProperty(Generic[T]):
    """状态属性 - 封装状态值和验证逻辑"""
    value: T
    validator: Optional[Callable[[T], bool]] = None
    default: Optional[T] = None

    def validate(self, value: T) -> bool:
        """验证状态值

        Args:
            value: 状态值

        Returns:
            是否有效
        """
        if self.validator:
            try:
                return self.validator(value)
            except Exception:
                return False
        return True


class StateManager:
    """状态管理器 - 提供集中式状态管理和状态变更通知"""

    def __init__(self):
        self._state: Dict[str, StateProperty] = {}
        self._event_bus = get_event_bus()

    def register_property(self, name: str, initial_value: Any, validator: Optional[Callable[[Any], bool]] = None) -> None:
        """注册状态属性

        Args:
            name: 属性名称
            initial_value: 初始值
            validator: 验证函数
        """
        self._state[name] = StateProperty(value=initial_value, validator=validator, default=initial_value)

    def get(self, name: str) -> Any:
        """获取状态值

        Args:
            name: 属性名称

        Returns:
            状态值
        """
        if name in self._state:
            return self._state[name].value
        raise KeyError(f"State property '{name}' not found")

    def set(self, name: str, value: Any) -> bool:
        """设置状态值

        Args:
            name: 属性名称
            value: 新值

        Returns:
            是否设置成功
        """
        if name not in self._state:
            raise KeyError(f"State property '{name}' not found")

        property_obj = self._state[name]
        if not property_obj.validate(value):
            return False

        old_value = property_obj.value
        if old_value == value:
            return True

        property_obj.value = value
        self._event_bus.publish(f"state:{name}", value, old_value)
        self._event_bus.publish("state:changed", name, value, old_value)
        return True

    def reset(self, name: str) -> bool:
        """重置状态值为默认值

        Args:
            name: 属性名称

        Returns:
            是否重置成功
        """
        if name not in self._state:
            raise KeyError(f"State property '{name}' not found")

        property_obj = self._state[name]
        if property_obj.default is not None:
            return self.set(name, property_obj.default)
        return False

    def reset_all(self) -> None:
        """重置所有状态值为默认值"""
        for name in self._state:
            self.reset(name)

    def has_property(self, name: str) -> bool:
        """检查是否存在指定的状态属性

        Args:
            name: 属性名称

        Returns:
            是否存在
        """
        return name in self._state

    def get_all_properties(self) -> Dict[str, Any]:
        """获取所有状态属性

        Returns:
            状态属性字典
        """
        return {name: prop.value for name, prop in self._state.items()}


# 全局状态管理器实例
_state_manager = StateManager()


def get_state_manager() -> StateManager:
    """获取全局状态管理器实例

    Returns:
        状态管理器实例
    """
    return _state_manager


def get_state(name: str) -> Any:
    """获取状态值（全局）

    Args:
        name: 属性名称

    Returns:
        状态值
    """
    return _state_manager.get(name)


def set_state(name: str, value: Any) -> bool:
    """设置状态值（全局）

    Args:
        name: 属性名称
        value: 新值

    Returns:
        是否设置成功
    """
    return _state_manager.set(name, value)


def register_state_property(name: str, initial_value: Any, validator: Optional[Callable[[Any], bool]] = None) -> None:
    """注册状态属性（全局）

    Args:
        name: 属性名称
        initial_value: 初始值
        validator: 验证函数
    """
    _state_manager.register_property(name, initial_value, validator)
