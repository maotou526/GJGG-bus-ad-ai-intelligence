"""
IOC方法注册表

实现IOC方法的注册、获取和调用
参考力软 IocManager 设计
"""

import os
import importlib
import logging
from pathlib import Path
from typing import Dict, Type, Optional, List
from .base import IWorkflowMethod, WfMethodParameter

logger = logging.getLogger(__name__)


class WorkflowMethodRegistry:
    """
    工作流IOC方法注册表（单例模式）

    用于注册和获取IOC方法实现
    支持自动扫描 dvadmin_twodev 下所有 ioc.py 文件

    使用示例:
        # 注册方法
        ioc_registry.register(MyMethod())

        # 获取方法
        method = ioc_registry.get("MyMethod")

        # 调用方法获取用户
        user_ids = ioc_registry.get_user_ids_by_ioc("MyMethod", params)
    """
    _instance = None
    _methods: Dict[str, IWorkflowMethod] = {}
    _auto_discovered: bool = False  # 标记是否已自动扫描

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._methods = {}
            cls._instance._auto_discovered = False
        return cls._instance

    def _auto_discover(self) -> None:
        """
        自动扫描并加载 dvadmin_twodev 下所有 ioc.py 文件

        扫描规则：
        - 扫描 backend/dvadmin_twodev/**/ioc.py
        - 排除 node_workflow/ioc 目录（核心模块）
        - 只在首次调用时执行一次
        """
        if self._auto_discovered:
            return

        self._auto_discovered = True
        print("[IOC] 开始自动扫描 ioc.py 模块...")

        # 获取 dvadmin_twodev 目录路径
        current_file = Path(__file__)  # registry.py
        ioc_dir = current_file.parent  # node_workflow/ioc
        node_workflow_dir = ioc_dir.parent  # node_workflow
        dvadmin_twodev_dir = node_workflow_dir.parent  # dvadmin_twodev

        if not dvadmin_twodev_dir.exists():
            print(f"[IOC] dvadmin_twodev 目录不存在: {dvadmin_twodev_dir}")
            return

        print(f"[IOC] 扫描目录: {dvadmin_twodev_dir}")

        # 扫描所有 ioc.py 文件
        ioc_files = list(dvadmin_twodev_dir.glob("**/ioc.py"))
        print(f"[IOC] 找到 {len(ioc_files)} 个 ioc.py 文件: {[str(f) for f in ioc_files]}")

        for ioc_file in ioc_files:
            # 排除 node_workflow/ioc 目录下的文件
            if "node_workflow" in str(ioc_file) and "ioc" in ioc_file.parent.name:
                continue

            # 构造模块路径: dvadmin_twodev.xxx.yyy.ioc
            relative_path = ioc_file.relative_to(dvadmin_twodev_dir.parent)
            module_path = str(relative_path).replace(os.sep, ".").replace(".py", "")

            try:
                print(f"[IOC] 正在加载模块: {module_path}")
                importlib.import_module(module_path)
                print(f"[IOC] 已加载模块: {module_path}")
            except Exception as e:
                print(f"[IOC] 加载模块失败 {module_path}: {e}")

    def register(self, method: IWorkflowMethod) -> None:
        """
        注册IOC方法

        Args:
            method: IWorkflowMethod 实现类实例
        """
        name = method.name
        if name in self._methods:
            print(f"[IOC] 方法 {name} 已存在，将被覆盖")
        self._methods[name] = method
        print(f"[IOC] 已注册方法: {name}")

    def unregister(self, name: str) -> bool:
        """
        注销IOC方法

        Args:
            name: 方法名称

        Returns:
            是否成功注销
        """
        if name in self._methods:
            del self._methods[name]
            logger.info(f"已注销IOC方法: {name}")
            return True
        return False

    def get(self, name: str) -> Optional[IWorkflowMethod]:
        """
        获取IOC方法

        Args:
            name: 方法名称

        Returns:
            IWorkflowMethod 实例，如果不存在则返回 None
        """
        # 首次调用时自动扫描
        self._auto_discover()
        return self._methods.get(name)

    def is_registered(self, name: str) -> bool:
        """
        检查方法是否已注册

        Args:
            name: 方法名称

        Returns:
            是否已注册
        """
        print(f"[IOC] is_registered 被调用: {name}, _auto_discovered={self._auto_discovered}, _methods={list(self._methods.keys())}")
        # 首次调用时自动扫描
        self._auto_discover()
        return name in self._methods

    def list_all(self) -> List[str]:
        """
        列出所有已注册的方法名

        Returns:
            方法名列表
        """
        self._auto_discover()
        return list(self._methods.keys())

    def list_all_with_info(self) -> List[Dict[str, str]]:
        """
        列出所有已注册的方法（包含描述信息）

        Returns:
            方法信息列表 [{"name": "...", "description": "..."}, ...]
        """
        self._auto_discover()
        result = []
        for name, method in self._methods.items():
            result.append({
                "name": method.name,
                "description": method.description
            })
        return result

    def get_user_ids_by_ioc(self, method_name: str, params: WfMethodParameter) -> List[str]:
        """
        通过IOC方法名获取用户ID列表

        这是调用IOC方法的主要入口

        Args:
            method_name: IOC方法名
            params: 参数对象

        Returns:
            用户ID列表
        """
        method = self.get(method_name)
        if method is None:
            logger.error(f"IOC方法 {method_name} 未注册")
            return []

        try:
            # 先验证参数
            is_valid, error_msg = method.validate(params)
            if not is_valid:
                logger.warning(f"IOC方法 {method_name} 参数验证失败: {error_msg}")
                return []

            # 调用方法获取用户ID
            return method.get_user_ids(params)
        except Exception as e:
            logger.error(f"IOC方法 {method_name} 执行失败: {e}")
            return []

    def execute_method(self, method_name: str, params: WfMethodParameter) -> bool:
        """
        执行IOC方法（用于事件回调）

        Args:
            method_name: IOC方法名
            params: 参数对象

        Returns:
            执行是否成功
        """
        method = self.get(method_name)
        if method is None:
            logger.error(f"IOC方法 {method_name} 未注册")
            return False

        try:
            return method.execute(params)
        except Exception as e:
            logger.error(f"IOC方法 {method_name} 执行失败: {e}")
            return False

    def clear(self) -> None:
        """
        清空所有已注册的方法（主要用于测试）
        """
        self._methods.clear()
        logger.info("已清空所有IOC方法")


# 全局注册表实例
ioc_registry = WorkflowMethodRegistry()


def register_workflow_method(method_class: Type[IWorkflowMethod]) -> Type[IWorkflowMethod]:
    """
    装饰器：自动注册IOC方法

    使用示例:
        @register_workflow_method
        class TestLine1Method(IWorkflowMethod):
            @property
            def name(self) -> str:
                return "TestLine1"

            def get_user_ids(self, params: WfMethodParameter) -> List[str]:
                return ["user_id_1"]
    """
    instance = method_class()
    ioc_registry.register(instance)
    return method_class
