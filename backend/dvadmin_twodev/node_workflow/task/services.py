'''
Description: 任务管理业务逻辑服务
Version: 1.0
Author: System
Date: 2026-01-22
LastEditors: Google Antigravity AI
LastEditTime: 2026-01-22
参考: NWFTaskBLL.cs (力软原始实现)
'''
import json
from typing import List, Dict, Any, Optional
from django.db import connection
from django.db.models import Q
from django.utils import timezone

# 导入模型
from dvadmin_twodev.node_workflow.task.models import WorkflowTaskModel
from dvadmin_twodev.node_workflow.taskrelation.models import WorkflowTaskRelationModel
from dvadmin_twodev.node_workflow.process.models import WorkflowProcessModel
from dvadmin_twodev.node_workflow.schemeinfo.models import WorkflowSchemeInfoModel
try:
    from dvadmin.system.models import Users
except ImportError:
    Users = None


class WorkflowTaskService:
    """
    任务管理业务逻辑服务
    
    参考力软NWFTaskBLL实现，包含:
    - get_my_tasks(): 获取我的待办任务
    - get_finished_tasks(): 获取我的已办任务
    - get_all_tasks(): 获取所有任务（监控）
    - get_task_info(): 获取任务详情
    """
    
    @staticmethod
    def get_my_tasks(user, keyword: str = '', scheme_code: str = '',
                    start_time: str = '', end_time: str = '',
                    page: int = 1, limit: int = 20) -> Dict:
        """
        获取我的待办任务（未处理）

        Args:
            user: 当前用户
            keyword: 搜索关键字（流程标题/编号）
            scheme_code: 流程模板编码
            start_time: 开始时间（格式：YYYY-MM-DD HH:MM:SS）
            end_time: 结束时间（格式：YYYY-MM-DD HH:MM:SS）
            page: 页码
            limit: 每页数量

        Returns:
            {'total': 10, 'data': [...]}
        """
        # 1. 查询当前用户需要处理的任务关系
        # mark=0 表示需要处理
        relation_query = WorkflowTaskRelationModel.objects.filter(
            user_id=str(user.id),
            mark=0
        ).values_list('task_id', flat=True)

        # 2. 查询对应的任务
        tasks = WorkflowTaskModel.objects.filter(
            id__in=relation_query,
            is_finished=0  # 任务本身未完成
        )

        # 3. 日期范围过滤
        if start_time:
            tasks = tasks.filter(create_datetime__gte=start_time)
        if end_time:
            tasks = tasks.filter(create_datetime__lte=end_time)

        # 4. 关联流程信息过滤
        if keyword:
            # 先查符合条件的 process_ids
            process_ids = WorkflowProcessModel.objects.filter(
                Q(title__icontains=keyword) | Q(scheme_name__icontains=keyword)
            ).values_list('id', flat=True)
            tasks = tasks.filter(Q(process_id__in=process_ids) | Q(node_name__icontains=keyword))

        if scheme_code:
            process_ids = WorkflowProcessModel.objects.filter(
                scheme_code=scheme_code
            ).values_list('id', flat=True)
            tasks = tasks.filter(process_id__in=process_ids)
            
        # 4. 排序
        tasks = tasks.order_by('-create_datetime')
        
        # 5. 分页
        total = tasks.count()
        start = (page - 1) * limit
        end = start + limit
        page_tasks = tasks[start:end]
        
        # 6. 组装数据
        data = []
        for task in page_tasks:
            # 获取流程信息
            process = WorkflowProcessModel.objects.filter(id=task.process_id).first()
            if not process:
                continue
                
            data.append({
                'id': task.id,
                'taskId': task.id,
                'processId': task.process_id,
                'schemeCode': process.scheme_code,
                'schemeName': process.scheme_name,
                'title': process.title,
                'level': process.level,
                'nodeId': task.node_id,
                'nodeName': task.node_name,
                'createTime': task.create_datetime.strftime('%Y-%m-%d %H:%M:%S') if task.create_datetime else '',
                'creator': process.creator_name,
                'isUrge': task.is_urge,
                'isFinished': process.is_finished,
                'status': 0,  # 待办任务状态为未处理
                'type': task.type  # 1=审批, 2=传阅, 3=加签, 4=子流程, 5=重新创建
            })

        return {
            'total': total,
            'data': data
        }

    @staticmethod
    def get_finished_tasks(user, keyword: str = '', scheme_code: str = '',
                          start_time: str = '', end_time: str = '',
                          page: int = 1, limit: int = 20) -> Dict:
        """
        获取我的已办任务（已处理）

        Args:
            user: 当前用户
            keyword: 搜索关键字
            scheme_code: 流程模板编码
            start_time: 开始时间（格式：YYYY-MM-DD HH:MM:SS）
            end_time: 结束时间（格式：YYYY-MM-DD HH:MM:SS）
            page: 页码
            limit: 每页数量

        Returns:
            {'total': 10, 'data': [...]}
        """
        # 1. 查询当前用户已处理的任务关系
        # mark=1 表示已处理
        relation_query = WorkflowTaskRelationModel.objects.filter(
            user_id=str(user.id),
            mark=1
        ).values_list('task_id', flat=True)

        # 2. 查询对应的任务
        tasks = WorkflowTaskModel.objects.filter(
            id__in=relation_query
        )

        # 3. 日期范围过滤
        if start_time:
            tasks = tasks.filter(create_datetime__gte=start_time)
        if end_time:
            tasks = tasks.filter(create_datetime__lte=end_time)

        # 4. 关联流程信息过滤
        # 注意：这里需要跨表过滤，Django ORM性能可能一般，量大建议优化
        if keyword:
            # 先查符合条件的process_ids
            process_ids = WorkflowProcessModel.objects.filter(
                Q(title__icontains=keyword) | Q(scheme_name__icontains=keyword)
            ).values_list('id', flat=True)
            tasks = tasks.filter(Q(process_id__in=process_ids) | Q(node_name__icontains=keyword))

        if scheme_code:
            scheme_process_ids = WorkflowProcessModel.objects.filter(
                scheme_code=scheme_code
            ).values_list('id', flat=True)
            tasks = tasks.filter(process_id__in=scheme_process_ids)

        # 4. 排序
        tasks = tasks.order_by('-create_datetime')

        # 5. 分页
        total = tasks.count()
        start = (page - 1) * limit
        end = start + limit
        page_tasks = tasks[start:end]

        # 6. 组装数据
        data = []
        for task in page_tasks:
            # 获取流程信息
            process = WorkflowProcessModel.objects.filter(id=task.process_id).first()
            if not process:
                continue

            # 获取我的处理结果
            relation = WorkflowTaskRelationModel.objects.filter(
                task_id=task.id,
                user_id=str(user.id)
            ).first()
            
            data.append({
                'id': task.id,
                'taskId': task.id,
                'processId': task.process_id,
                'schemeCode': process.scheme_code,
                'schemeName': process.scheme_name,
                'title': process.title,
                'level': process.level,
                'nodeId': task.node_id,
                'nodeName': task.node_name,
                'createTime': task.create_datetime.strftime('%Y-%m-%d %H:%M:%S') if task.create_datetime else '',
                'finishTime': relation.time.strftime('%Y-%m-%d %H:%M:%S') if relation and relation.time else '',
                'creator': process.creator_name,
                'isUrge': task.is_urge,
                'isFinished': process.is_finished,
                'status': process.is_finished,  # 流程是否结束
                'type': task.type,
                'result': relation.result if relation else 0  # 我的处理结果
            })

        return {
            'total': total,
            'data': data
        }

    @staticmethod
    def get_my_create_tasks(user, keyword: str = '', scheme_code: str = '',
                           start_time: str = '', end_time: str = '',
                           page: int = 1, limit: int = 20) -> Dict:
        """
        获取我发起的流程
        """
        processes = WorkflowProcessModel.objects.filter(
            creator_id=str(user.id),
            enabled_mark=1  # 正常流程
        )

        # 日期范围过滤
        if start_time:
            processes = processes.filter(create_datetime__gte=start_time)
        if end_time:
            processes = processes.filter(create_datetime__lte=end_time)

        if keyword:
            processes = processes.filter(
                Q(title__icontains=keyword) | Q(scheme_name__icontains=keyword)
            )

        if scheme_code:
            processes = processes.filter(scheme_code=scheme_code)

        processes = processes.order_by('-create_datetime')

        total = processes.count()
        start = (page - 1) * limit
        end = start + limit
        page_processes = processes[start:end]

        data = []
        for p in page_processes:
            # 获取当前节点信息（如果流程未结束）
            current_task = None
            node_name = ''
            is_urge = 0
            if p.is_finished == 0:
                current_task = WorkflowTaskModel.objects.filter(
                    process_id=p.id,
                    is_finished=0
                ).first()
                if current_task:
                    node_name = current_task.node_name
                    is_urge = current_task.is_urge

            data.append({
                'id': p.id,
                'taskId': current_task.id if current_task else '',
                'processId': p.id,
                'schemeCode': p.scheme_code,
                'schemeName': p.scheme_name,
                'title': p.title,
                'level': p.level,
                'nodeId': current_task.node_id if current_task else '',
                'nodeName': node_name,
                'createTime': p.create_datetime.strftime('%Y-%m-%d %H:%M:%S') if p.create_datetime else '',
                'creator': p.creator_name,
                'isUrge': is_urge,
                'isFinished': p.is_finished,
                'isStart': p.is_start,
                'isAgain': p.is_again,
                'status': p.is_finished,
                'type': 0  # 我发起的流程，type=0
            })

        return {
            'total': total,
            'data': data
        }
