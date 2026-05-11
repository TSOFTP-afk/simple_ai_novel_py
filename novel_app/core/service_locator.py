from __future__ import annotations

from typing import Any, Dict, Optional, Type


class ServiceLocator:
    """服务定位器 - 提供依赖注入和服务管理"""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Any] = {}

    def register(self, name: str, service: Any) -> None:
        """注册服务

        Args:
            name: 服务名称
            service: 服务实例
        """
        self._services[name] = service

    def register_factory(self, name: str, factory: Any) -> None:
        """注册服务工厂

        Args:
            name: 服务名称
            factory: 服务工厂函数
        """
        self._factories[name] = factory

    def get(self, name: str) -> Any:
        """获取服务

        Args:
            name: 服务名称

        Returns:
            服务实例
        """
        if name in self._services:
            return self._services[name]
        elif name in self._factories:
            service = self._factories[name]()
            self._services[name] = service
            return service
        raise KeyError(f"Service '{name}' not found")

    def has(self, name: str) -> bool:
        """检查服务是否存在

        Args:
            name: 服务名称

        Returns:
            是否存在
        """
        return name in self._services or name in self._factories

    def remove(self, name: str) -> None:
        """移除服务

        Args:
            name: 服务名称
        """
        if name in self._services:
            del self._services[name]
        if name in self._factories:
            del self._factories[name]

    def clear(self) -> None:
        """清除所有服务"""
        self._services.clear()
        self._factories.clear()


# 全局服务定位器实例
_service_locator = ServiceLocator()


def get_service_locator() -> ServiceLocator:
    """获取全局服务定位器实例

    Returns:
        服务定位器实例
    """
    return _service_locator


def register_service(name: str, service: Any) -> None:
    """注册服务（全局）

    Args:
        name: 服务名称
        service: 服务实例
    """
    _service_locator.register(name, service)


def register_service_factory(name: str, factory: Any) -> None:
    """注册服务工厂（全局）

    Args:
        name: 服务名称
        factory: 服务工厂函数
    """
    _service_locator.register_factory(name, factory)


def get_service(name: str) -> Any:
    """获取服务（全局）

    Args:
        name: 服务名称

    Returns:
        服务实例
    """
    return _service_locator.get(name)


def has_service(name: str) -> bool:
    """检查服务是否存在（全局）

    Args:
        name: 服务名称

    Returns:
        是否存在
    """
    return _service_locator.has(name)
