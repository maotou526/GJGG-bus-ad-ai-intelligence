"""
工作流IOC注入模块

提供动态审核人计算机制，支持通过IOC方法名动态获取审核人列表

核心组件:
- IWorkflowMethod: IOC方法接口，所有IOC方法都需要实现此接口
- WfMethodParameter: IOC方法参数，包含流程运行时的上下文信息
- ioc_registry: IOC方法注册表，用于注册和获取IOC方法
- register_workflow_method: 装饰器，用于自动注册IOC方法

使用示例:
    # 1. 定义IOC方法
    from dvadmin_twodev.node_workflow.ioc import (
        IWorkflowMethod, WfMethodParameter, register_workflow_method
    )

    @register_workflow_method
    class MyAuditorMethod(IWorkflowMethod):
        @property
        def name(self) -> str:
            return "MyAuditor"

        def get_user_ids(self, params: WfMethodParameter) -> List[str]:
            # 实现业务逻辑
            return ["user_id_1", "user_id_2"]

    # 2. 在流程设计中配置IOC
    {
        "type": 8,  # 8 = IOC注入类型
        "auditorId": "MyAuditor|1",  # 方法名|过滤类型
        "auditorName": "【MyAuditor】IOC注入"
    }

    # 3. 运行时调用IOC
    from dvadmin_twodev.node_workflow.ioc import ioc_registry, WfMethodParameter

    params = WfMethodParameter(
        process_id="xxx",
        user_id="current_user_id",
        form_data={"amount": 10000}
    )
    user_ids = ioc_registry.get_user_ids_by_ioc("MyAuditor", params)
"""

from .registry import ioc_registry, register_workflow_method
from .base import IWorkflowMethod, WfMethodParameter

# IOC方法由各业务模块自行定义和注册
# 每个模块在自己的 ioc.py 文件中使用 @register_workflow_method 装饰器注册方法
# 模块的 apps.py ready() 方法中导入 ioc 模块触发注册

__all__ = [
    'ioc_registry',
    'register_workflow_method',
    'IWorkflowMethod',
    'WfMethodParameter',
]
