"""
IOC基类和接口定义

参考力软 IWorkFlowMethod 接口设计
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class WfMethodParameter:
    """
    IOC方法参数（参考力软 WfMethodParameter）

    包含流程运行时的上下文信息，供IOC方法使用
    """
    process_id: str = None          # 流程实例ID
    task_id: str = None             # 当前任务ID
    node_id: str = None             # 当前节点ID
    node_name: str = None           # 当前节点名称
    user_id: str = None             # 当前用户ID
    user_name: str = None           # 当前用户名称
    company_id: str = None          # 当前用户公司ID
    dept_id: str = None             # 当前用户部门ID
    form_data: Dict[str, Any] = field(default_factory=dict)  # 表单数据
    scheme_code: str = None         # 流程模板编码
    scheme_id: str = None           # 流程模板版本ID
    current_users: List[str] = field(default_factory=list)  # 当前已有的审核人ID列表
    code: str = None                # 操作码（agree/disagree）
    extra: Dict[str, Any] = field(default_factory=dict)  # 扩展参数


class IWorkflowMethod(ABC):
    """
    工作流IOC方法接口

    所有IOC方法都必须实现此接口
    参考力软 IWorkFlowMethod 接口

    使用示例:
        @register_workflow_method
        class MyMethod(IWorkflowMethod):
            @property
            def name(self) -> str:
                return "MyMethod"

            def get_user_ids(self, params: WfMethodParameter) -> List[str]:
                # 实现业务逻辑
                return ["user_id_1", "user_id_2"]
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        IOC方法名称（用于注册和调用）

        这个名称会在流程设计时使用，如 "TestLine1"、"GetLineManager"
        """
        pass

    @property
    def description(self) -> str:
        """
        方法描述（可选）

        用于在前端显示方法说明
        """
        return ""

    def get_user_ids(self, params: WfMethodParameter) -> List[str]:
        """
        获取用户ID列表（审核人来源）

        这是审核人IOC方法的核心方法，用于动态计算审核人
        连线执行类IOC可以不覆盖此方法（默认返回空列表）

        Args:
            params: WfMethodParameter 参数对象，包含流程运行时的上下文信息

        Returns:
            用户ID列表（字符串类型）
        """
        return []

    def execute(self, params: WfMethodParameter) -> bool:
        """
        执行方法（用于节点/连线事件回调）

        除了获取审核人，IOC方法还可以用于执行节点事件
        如：节点进入时通知、连线流转时更新业务数据等

        Args:
            params: WfMethodParameter 参数对象

        Returns:
            执行是否成功
        """
        return True

    def validate(self, params: WfMethodParameter) -> tuple[bool, str]:
        """
        验证方法（可选）

        在执行前验证参数是否合法

        Args:
            params: WfMethodParameter 参数对象

        Returns:
            (是否通过验证, 错误信息)
        """
        return True, ""
