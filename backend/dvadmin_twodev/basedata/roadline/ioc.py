"""
线路模块IOC方法示例
"""
from typing import List

from dvadmin_twodev.node_workflow.ioc import (
    IWorkflowMethod,
    WfMethodParameter,
    register_workflow_method
)


@register_workflow_method
class GetLineManager(IWorkflowMethod):
    """获取线路负责人（测试用）"""

    @property
    def name(self) -> str:
        return "GetLineManager"

    @property
    def description(self) -> str:
        return "获取线路负责人"

    def get_user_ids(self, params: WfMethodParameter) -> List[str]:
        return ["95062d71-7988-45a8-bdb0-9d5e656e58c5"]


@register_workflow_method
class LineBindingExecutor(IWorkflowMethod):
    """连线绑定执行方法（Demo）"""

    @property
    def name(self) -> str:
        return "LineBindingExecutor"

    def execute(self, params: WfMethodParameter) -> bool:
        """连线流转时执行的业务逻辑"""
        print(f"[LineBindingExecutor] 流程 {params.process_id} 流转到节点 {params.node_name}")
        # TODO: 在这里实现业务逻辑，如更新数据、发送通知等
        return True

