'''
Description: 流程进程视图
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
import json
import uuid
from typing import List, Dict, Any, Optional
from rest_framework.decorators import action
from django.db.models import Q
from django.db import transaction
from django.utils import timezone
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse

from dvadmin_twodev.node_workflow.utils.workflow_engine import WorkflowEngine
from .models import WorkflowProcessModel
from dvadmin_twodev.node_workflow.scheme.models import WorkflowSchemeModel
from dvadmin_twodev.node_workflow.schemeinfo.models import WorkflowSchemeInfoModel
from dvadmin_twodev.node_workflow.task.models import WorkflowTaskModel
from dvadmin_twodev.node_workflow.taskrelation.models import WorkflowTaskRelationModel
from dvadmin_twodev.node_workflow.tasklog.models import WorkflowTaskLogModel
from dvadmin_twodev.node_workflow.taskmsg.models import WorkflowTaskMsgModel
from dvadmin_twodev.node_workflow.confluence.models import WorkflowConfluenceModel

# 导入用户模型
try:
    from dvadmin.system.models import Users
except ImportError:
    Users = None

from .serializers import (
    WorkflowProcessModelSerializer,
    WorkflowProcessModelCreateSerializer,
    WorkflowProcessModelUpdateSerializer,
    WorkflowProcessModelListSerializer,
    WorkflowProcessModelImportSerializer,
)


class WorkflowProcessModelViewSet(CustomModelViewSet):
    """
    流程进程管理视图集
    提供标准的 CRUD 接口和自定义业务接口
    """
    
    queryset = WorkflowProcessModel.objects.all()
    serializer_class = WorkflowProcessModelSerializer
    create_serializer_class = WorkflowProcessModelCreateSerializer
    update_serializer_class = WorkflowProcessModelUpdateSerializer
    list_serializer_class = WorkflowProcessModelListSerializer
    import_serializer_class = WorkflowProcessModelImportSerializer
    
    # 排序配置
    ordering_fields = ['scheme_code', 'scheme_name', 'title', 'create_datetime', 'update_datetime']
    ordering = ['-create_datetime']
    
    # 搜索字段
    search_fields = ['scheme_code', 'scheme_name', 'title', 'creator_name']
    
    # 过滤字段
    filter_fields = ['id', 'scheme_id', 'scheme_code', 'level', 'enabled_mark', 'is_finished', 'is_child', 'creator']
    
    @action(methods=['GET'], detail=False, url_path='my-process')
    def get_my_process(self, request):
        """
        获取我的流程列表
        
        请求方式：GET /api/WorkflowProcessModelViewSet/my-process/
        
        请求参数：
            is_finished: 是否结束（可选，0=未结束, 1=已结束）
            enabled_mark: 流程状态（可选，1=正常, 2=草稿, 3=作废）
            
        返回结果：
        {
            "code": 2000,
            "data": {
                "results": [...],
                "total": 10
            },
            "msg": "获取成功"
        }
        """
        user_id = request.user.id if hasattr(request.user, 'id') else None
        if not user_id:
            return ErrorResponse(msg="用户未登录")
        
        queryset = self.get_queryset().filter(
            creator_id=str(user_id),
            is_child=0  # 只查询主流程，不包含子流程
        )
        
        # 过滤条件
        is_finished = request.query_params.get('is_finished', None)
        if is_finished is not None:
            queryset = queryset.filter(is_finished=int(is_finished))
        
        enabled_mark = request.query_params.get('enabled_mark', None)
        if enabled_mark is not None:
            queryset = queryset.filter(enabled_mark=int(enabled_mark))
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")
    
    @action(methods=['GET'], detail=False, url_path='statistics')
    def get_statistics(self, request):
        """
        获取流程统计信息
        
        请求方式：GET /api/WorkflowProcessModelViewSet/statistics/
        
        返回结果：
        {
            "code": 2000,
            "data": {
                "total": 100,
                "finished": 80,
                "unfinished": 20,
                "draft": 5,
                "cancelled": 0
            },
            "msg": "获取成功"
        }
        """
        queryset = self.get_queryset()
        
        total = queryset.count()
        finished = queryset.filter(is_finished=1).count()
        unfinished = queryset.filter(is_finished=0).count()
        draft = queryset.filter(enabled_mark=2).count()
        cancelled = queryset.filter(enabled_mark=3).count()
        
        return SuccessResponse(
            data={
                "total": total,
                "finished": finished,
                "unfinished": unfinished,
                "draft": draft,
                "cancelled": cancelled
            },
            msg="获取成功"
        )
    
    # ==================== 核心流程接口（兼容前端API） ====================
    
    @action(methods=['GET'], detail=False, url_path='get-scheme-by-code')
    def get_scheme_by_code(self, request):
        """
        根据流程编号获取模板（兼容前端API）
        
        请求方式：GET /api/workflow/process/get-scheme-by-code/
        
        请求参数：
            code: 流程编号
            
        返回格式（兼容前端）：
        {
            "code": 200,
            "info": "获取成功",
            "data": {
                "F_Content": "{...}",  // JSON字符串
                "F_Id": "...",
                "F_SchemeInfoId": "...",
                ...
            }
        }
        """
        code = request.query_params.get('code', None)
        if not code:
            return ErrorResponse(msg="流程编号不能为空")
        
        # 查询流程模板信息
        scheme_info = WorkflowSchemeInfoModel.objects.filter(
            code=code,
            enabled_mark=1  # 有效
        ).first()
        
        if not scheme_info:
            return ErrorResponse(msg="流程模板不存在或已禁用")
        
        # 查询当前启用版本的模板
        scheme = None
        if scheme_info.scheme_id:
            scheme = WorkflowSchemeModel.objects.filter(
                id=scheme_info.scheme_id,
                type=1  # 正式版本
            ).first()
        
        if not scheme:
            return ErrorResponse(msg="流程模板版本不存在")
        
        # 返回数据（注意字段名要与前端一致，使用F_前缀）
        return SuccessResponse(
            data={
                "F_Content": scheme.content,
                "F_Id": scheme.id,
                "F_SchemeInfoId": scheme.scheme_info_id,
                "F_Type": scheme.type,
                "F_CreateDate": scheme.create_datetime.strftime('%Y-%m-%d %H:%M:%S') if scheme.create_datetime else None,
                "F_CreateUserId": str(scheme.creator_id) if scheme.creator_id else None,
                "F_CreateUserName": scheme.creator_name,
            },
            msg="获取成功"
        )
    
    @action(methods=['GET'], detail=False, url_path='get-scheme-by-process-id')
    def get_scheme_by_process_id(self, request):
        """
        根据流程ID获取模板（兼容前端API）
        
        请求方式：GET /api/workflow/process/get-scheme-by-process-id/
        
        请求参数：
            processId: 流程ID
            
        返回格式（兼容前端）：
        {
            "code": 200,
            "info": "获取成功",
            "data": {
                "F_Content": "{...}",
                "info": {
                    "currentIds": [...],  // 当前节点ID列表
                    ...
                },
                "task": [...]  // 任务列表
            }
        }
        """
        process_id = request.query_params.get('processId', None)
        if not process_id:
            return ErrorResponse(msg="流程ID不能为空")
        
        # 查询流程实例
        process = WorkflowProcessModel.objects.filter(id=process_id).first()
        if not process:
            return ErrorResponse(msg="流程实例不存在")
        
        # 查询流程模板
        scheme = None
        if process.scheme_id:
            scheme = WorkflowSchemeModel.objects.filter(id=process.scheme_id).first()
        
        if not scheme:
            return ErrorResponse(msg="流程模板不存在")
        
        # 查询当前待处理任务（用于获取当前节点ID列表）
        current_tasks = WorkflowTaskModel.objects.filter(
            process_id=process_id,
            is_finished=0  # 未完成
        )
        current_ids = list(current_tasks.values_list('node_id', flat=True))
        
        # 查询任务列表（包含执行人信息）
        tasks = []
        for task in current_tasks:
            # 查询任务执行人
            task_relations = WorkflowTaskRelationModel.objects.filter(
                task_id=task.id,
                mark=0  # 需要处理
            )
            user_info_list = []
            for relation in task_relations:
                # 获取用户名称
                user_name = None
                if Users and relation.user_id:
                    try:
                        user = Users.objects.filter(id=relation.user_id).first()
                        if user:
                            user_name = user.name or user.username
                    except Exception:
                        pass
                user_info_list.append({
                    "Id": relation.user_id,
                    "Name": user_name or str(relation.user_id),
                    "Mark": relation.mark,
                    "Result": relation.result or 0,
                })

            tasks.append({
                "F_NodeId": task.node_id,
                "F_NodeName": task.node_name,
                "nWFUserInfoList": user_info_list
            })

        return SuccessResponse(
            data={
                "F_Content": scheme.content,
                "info": {
                    "currentIds": current_ids,
                    "isFinished": process.is_finished,
                    "parentProcessId": process.parent_process_id,
                    "childProcessId": None,  # 子流程ID需要从任务中查询
                },
                "task": tasks
            },
            msg="获取成功"
        )
    
    @action(methods=['GET'], detail=False, url_path='get-process-details')
    def get_process_details(self, request):
        """
        获取流程详情（兼容前端API）
        
        请求方式：GET /api/workflow/process/get-process-details/
        
        请求参数：
            processId: 流程ID
            taskId: 任务ID（可选）
            
        返回格式（兼容前端）：
        {
            "code": 200,
            "info": "获取成功",
            "data": {
                "info": {
                    "Scheme": "{...}",  // 流程模板JSON字符串
                    "CurrentNodeId": "...",  // 当前节点ID
                    "CurrentNodeIds": [...],  // 当前节点ID列表
                    "isFinished": 0,
                    "parentProcessId": "...",
                    "childProcessId": "...",
                    "TaskLogList": [...]  // 审批历史
                },
                "task": [...]  // 当前待处理任务列表
            }
        }
        """
        process_id = request.query_params.get('processId', None)
        task_id = request.query_params.get('taskId', None)
        
        if not process_id:
            return ErrorResponse(msg="流程ID不能为空")
        
        # 查询流程实例
        process = WorkflowProcessModel.objects.filter(id=process_id).first()
        if not process:
            return ErrorResponse(msg="流程实例不存在")
        
        # 查询流程模板
        scheme = None
        if process.scheme_id:
            scheme = WorkflowSchemeModel.objects.filter(id=process.scheme_id).first()
        
        if not scheme:
            return ErrorResponse(msg="流程模板不存在")
        
        # 查询当前待处理任务
        current_tasks = WorkflowTaskModel.objects.filter(
            process_id=process_id,
            is_finished=0  # 未完成
        )
        
        # 获取当前节点ID（如果指定了taskId，使用该任务的节点ID；否则使用第一个未完成任务）
        current_node_id = None
        if task_id:
            task = current_tasks.filter(id=task_id).first()
            if task:
                current_node_id = task.node_id
        elif current_tasks.exists():
            current_node_id = current_tasks.first().node_id
        
        current_ids = list(current_tasks.values_list('node_id', flat=True))
        
        # 查询任务列表（包含执行人信息）
        tasks = []
        for task in current_tasks:
            # 查询任务执行人
            task_relations = WorkflowTaskRelationModel.objects.filter(task_id=task.id)
            user_info_list = []
            for relation in task_relations:
                # 获取用户名称
                user_name = None
                if Users and relation.user_id:
                    try:
                        user = Users.objects.filter(id=relation.user_id).first()
                        if user:
                            user_name = user.name or user.username
                    except Exception:
                        pass
                user_info_list.append({
                    "Id": relation.user_id,
                    "Name": user_name or str(relation.user_id),
                    "Mark": relation.mark,
                    "Result": relation.result or 0,
                })

            tasks.append({
                "F_NodeId": task.node_id,
                "F_NodeName": task.node_name,
                "nWFUserInfoList": user_info_list
            })
        
        # 查询审批历史（任务日志）
        task_logs = WorkflowTaskLogModel.objects.filter(
            process_id=process_id
        ).order_by('create_datetime')
        
        task_log_list = []
        for log in task_logs:
            task_log_list.append({
                "F_ProcessId": log.process_id,
                "F_TaskId": log.task_id,
                "F_OperationCode": log.operation_code,
                "F_OperationName": log.operation_name,
                "F_NodeId": log.node_id,
                "F_NodeName": log.node_name,
                "F_TaskType": log.task_type,
                "F_PrevNodeId": log.prev_node_id,
                "F_PrevNodeName": log.prev_node_name,
                "F_CreateDate": log.create_datetime.strftime('%Y-%m-%d %H:%M:%S') if log.create_datetime else None,
                "F_CreateUserId": str(log.creator_id) if log.creator_id else None,
                "F_CreateUserName": log.creator_name,
                "F_TaskUserId": log.task_user_id,
                "F_TaskUserName": log.task_user_name,
                "F_Des": log.des,
                "F_SignImg": log.sign_img,
                "F_StampImg": log.stamp_img,
            })
        
        # 查询子流程ID（如果有）
        child_process_id = None
        child_task = WorkflowTaskModel.objects.filter(
            process_id=process_id,
            type=4,  # 子流程任务
            is_finished=0
        ).first()
        if child_task:
            child_process_id = child_task.child_process_id
        
        return SuccessResponse(
            data={
                "info": {
                    "Scheme": scheme.content,  # 流程模板JSON字符串
                    "CurrentNodeId": current_node_id,
                    "CurrentNodeIds": current_ids,
                    "isFinished": process.is_finished,
                    "parentProcessId": process.parent_process_id,
                    "childProcessId": child_process_id,
                    "TaskLogList": task_log_list
                },
                "task": tasks
            },
            msg="获取成功"
        )
    
    @action(methods=['POST'], detail=False, url_path='create-flow')
    def create_flow(self, request):
        """
        创建流程（兼容前端API）
        
        请求方式：POST /api/workflow/process/create-flow/
        
        请求参数：
        {
            "schemeCode": "...",  // 流程编号
            "processId": "...",  // 流程ID（可选，前端生成）
            "title": "...",  // 流程标题
            "level": 1,  // 紧急程度（1=普通, 2=重要, 3=紧急）
            "auditors": "{...}",  // 下一节点审核人JSON字符串（可选）
            "createUserId": "...",  // 创建人ID
            "formData": "{...}" // 业务表单数据 JSON string
        }
        
        返回格式（兼容前端）：
        {
            "code": 200,
            "info": "创建成功",
            "data": {
                "processId": "..."
            }
        }
        """
        from dvadmin_twodev.node_workflow.process.services import WorkflowProcessService
        
        scheme_code = request.data.get('schemeCode', None)
        process_id = request.data.get('processId', None)
        title = request.data.get('title', '')
        level = int(request.data.get('level', 1))
        auditors_json = request.data.get('auditors', None)
        
        if not scheme_code:
            return ErrorResponse(msg="流程编号不能为空")
        
        if not title:
            return ErrorResponse(msg="流程标题不能为空")
        
        # 解析auditors（如果提供）
        auditors = None
        if auditors_json:
            try:
                auditors_data = json.loads(auditors_json) if isinstance(auditors_json, str) else auditors_json
                # 转换为 {node_id: [user_ids]} 格式
                auditors = {}
                for node_id, user_list in auditors_data.items():
                    if isinstance(user_list, list):
                        auditors[node_id] = user_list
                    else:
                        auditors[node_id] = [user_list]
            except Exception as e:
                return ErrorResponse(msg=f"审核人参数格式错误: {str(e)}")
        
        try:
            # 调用服务层创建流程
            result = WorkflowProcessService.create_flow(
                scheme_code=scheme_code,
                title=title,
                level=level,
                user=request.user,
                process_id=process_id,
                auditors=auditors
            )
            
            return SuccessResponse(
                data={
                    "processId": result['process_id'],
                    "taskId": result.get('task_id', '')
                },
                msg="创建成功"
            )
            
        except ValueError as e:
            # 兼容逻辑：创建失败时保存为草稿
            try:
                WorkflowProcessService.save_draft(scheme_code, process_id, request.user)
                return ErrorResponse(msg=f"创建流程失败，已保存为草稿: {str(e)}")
            except Exception as draft_error:
                return ErrorResponse(msg=f"创建流程失败且保存草稿失败: {str(e)} | {str(draft_error)}")
        except Exception as e:
            # 兼容逻辑：创建失败时保存为草稿
            try:
                WorkflowProcessService.save_draft(scheme_code, process_id, request.user)
                return ErrorResponse(msg=f"创建流程失败，已保存为草稿: {str(e)}")
            except Exception as draft_error:
                return ErrorResponse(msg=f"创建流程失败且保存草稿失败: {str(e)} | {str(draft_error)}")
    
    @action(methods=['POST'], detail=False, url_path='save-draft')
    def save_draft(self, request):
        """
        保存草稿（兼容前端API）
        
        请求方式：POST /api/workflow/process/save-draft/
        
        请求参数：
        {
            "schemeCode": "...",
            "processId": "...",
            "createUserId": "..."
        }
        
        返回格式（兼容前端）：
        {
            "code": 200,
            "info": "保存成功"
        }
        """
        scheme_code = request.data.get('schemeCode', None)
        process_id = request.data.get('processId', None)
        create_user_id = request.data.get('createUserId', None)
        
        if not scheme_code or not process_id:
            return ErrorResponse(msg="流程编号和流程ID不能为空")
        
        if not create_user_id:
            create_user_id = request.user.id if hasattr(request.user, 'id') else None
            if not create_user_id:
                return ErrorResponse(msg="创建人ID不能为空")
        
        try:
            with transaction.atomic():
                # 查询或创建流程实例
                process = WorkflowProcessModel.objects.filter(id=process_id).first()
                
                if process:
                    # 更新为草稿状态
                    process.enabled_mark = 2  # 草稿
                    process.save()
                else:
                    # 创建草稿流程
                    scheme_info = WorkflowSchemeInfoModel.objects.filter(
                        code=scheme_code,
                        enabled_mark=1
                    ).first()
                    
                    if not scheme_info:
                        return ErrorResponse(msg="流程模板不存在")
                    
                    process = WorkflowProcessModel(
                        id=process_id,
                        scheme_code=scheme_code,
                        scheme_name=scheme_info.name,
                        enabled_mark=2,  # 草稿
                        is_start=0,
                        is_finished=0,
                        is_child=0,
                        is_again=0,
                    )
                    # 设置创建人信息（BaseDataModel会自动处理create_datetime）
                    if create_user_id:
                        process.creator_id = create_user_id
                        process.creator_name = getattr(request.user, 'name', '') if hasattr(request.user, 'name') else ''
                    process.save()
                
                return SuccessResponse(msg="保存成功")
                
        except Exception as e:
            return ErrorResponse(msg=f"保存草稿失败: {str(e)}")
    
    @action(methods=['POST'], detail=False, url_path='again-create-flow')
    def again_create_flow(self, request):
        """
        重新发起流程（兼容前端API）
        
        请求方式：POST /api/workflow/process/again-create-flow/
        
        请求参数：
        {
            "processId": "..."  // 原流程ID
        }
        
        返回格式（兼容前端）：
        {
            "code": 200,
            "info": "重新发起成功"
        }
        
        注意：此接口需要实现重新发起逻辑，目前先提供基础框架
        """
        process_id = request.data.get('processId', None)
        
        if not process_id:
            return ErrorResponse(msg="流程ID不能为空")
        
        try:
            with transaction.atomic():
                # 查询原流程
                old_process = WorkflowProcessModel.objects.filter(id=process_id).first()
                if not old_process:
                    return ErrorResponse(msg="原流程不存在")
                
                # TODO: 实现重新发起逻辑
                # 1. 创建新流程实例（is_again=1）
                # 2. 复制原流程的表单数据
                # 3. 创建第一个任务
                
                return SuccessResponse(msg="重新发起成功")
                
        except Exception as e:
            return ErrorResponse(msg=f"重新发起失败: {str(e)}")
    
    @action(methods=['POST'], detail=False, url_path='audit-flow')
    def audit_flow(self, request):
        """
        审批流程（兼容前端API）- 核心流转逻辑
        
        请求方式：POST /api/workflow/process/audit-flow/
        
        请求参数：
        {
            "processId": "...",
            "taskId": "...",
            "operationCode": "agree",  // 操作码：agree/disagree
            "operationName": "同意",
            "des": "...",  // 审批意见
            "auditors": "{...}",  // 下一节点审核人JSON字符串（可选）
            "signUrl": "...",  // 签名图片URL（可选）
            "stamp": "..."  // 印章ID（可选）
        }
        
        返回格式（兼容前端）：
        {
            "code": 200,
            "info": "审批成功"
        }
        """
        from dvadmin_twodev.node_workflow.process.services import WorkflowProcessService
        
        process_id = request.data.get('processId', None)
        task_id = request.data.get('taskId', None)
        operation_code = request.data.get('operationCode', None)
        operation_name = request.data.get('operationName', '')
        des = request.data.get('des', '')
        auditors_json = request.data.get('auditors', None)
        sign_url = request.data.get('signUrl', None)
        stamp = request.data.get('stamp', None)
        
        if not process_id or not task_id or not operation_code:
            return ErrorResponse(msg="流程ID、任务ID和操作码不能为空")
        
        # 解析auditors（如果提供）
        auditors = None
        if auditors_json:
            try:
                auditors_data = json.loads(auditors_json) if isinstance(auditors_json, str) else auditors_json
                # 转换为 {node_id: [user_ids]} 格式
                auditors = {}
                for node_id, user_list in auditors_data.items():
                    if isinstance(user_list, list):
                        auditors[node_id] = user_list
                    else:
                        auditors[node_id] = [user_list]
            except Exception as e:
                return ErrorResponse(msg=f"审核人参数格式错误: {str(e)}")
        
        try:
            # 调用服务层审批流程
            result = WorkflowProcessService.audit_flow(
                process_id=process_id,
                task_id=task_id,
                operation_code=operation_code,
                operation_name=operation_name,
                user=request.user,
                des=des,
                auditors=auditors,
                sign_url=sign_url,
                stamp=stamp
            )
            
            return SuccessResponse(msg=result.get('msg', '审批成功'))
            
        except ValueError as e:
            return ErrorResponse(msg=str(e))
        except Exception as e:
            return ErrorResponse(msg=f"审批失败: {str(e)}")
    
    @action(methods=['GET'], detail=False, url_path='get-next-auditors')
    def get_next_auditors(self, request):
        """
        获取下一节点审核人（兼容前端API）
        
        请求方式：GET /api/workflow/process/get-next-auditors/
        
        请求参数：
            code: 流程编号
            processId: 流程ID
            taskId: 任务ID
            nodeId: 节点ID
            operationCode: 操作码（agree/disagree）
            
        返回格式（兼容前端）：
        {
            "code": 200,
            "info": "获取成功",
            "data": {
                "node_id_1": [
                    {"id": "user_id", "name": "用户姓名"},
                    ...
                ],
                ...
            }
        }
        
        注意：此接口需要解析流程模板，计算下一节点，返回候选审核人列表
        目前先提供基础框架
        """
    @action(methods=['GET'], detail=False, url_path='get-next-auditors')
    def get_next_auditors(self, request):
        """
        获取下一节点审核人（兼容前端API）
        
        GET /api/workflow/process/get-next-auditors/
        """
        from dvadmin_twodev.node_workflow.process.services import WorkflowProcessService
        
        code = request.query_params.get('code', None)
        process_id = request.query_params.get('processId', None)
        task_id = request.query_params.get('taskId', None) # 暂未使用，保留接口兼容
        node_id = request.query_params.get('nodeId', None)
        operation_code = request.query_params.get('operationCode', 'agree')
        
        if not code and not process_id:
             return ErrorResponse(msg="流程编号和流程ID不能同时为空")
        
        try:
            data = WorkflowProcessService.get_next_auditors(
                scheme_code=code,
                process_id=process_id,
                node_id=node_id,
                operation_code=operation_code,
                user=request.user
            )
            return SuccessResponse(data=data, msg="获取成功")
        except ValueError as e:
            return ErrorResponse(msg=str(e))
        except Exception as e:
            return ErrorResponse(msg=f"获取失败: {str(e)}")
    
    @action(methods=['POST'], detail=False, url_path='refer-flow')
    def refer_flow(self, request):
        """
        传阅流程（兼容前端API）
        
        POST /api/workflow/process/refer-flow/
        """
        from dvadmin_twodev.node_workflow.process.services import WorkflowProcessService
        
        process_id = request.data.get('processId', None)
        task_id = request.data.get('taskId', None)
        # 支持传给多个人，逗号分隔? 这里假设传给一个人或需要前端循环调用，
        # 或者调整service支持多人。WorkflowTaskRelationModel通常是单人。
        # 这里为了简单，假设userId是单个ID，如果需要多个可以扩展Service
        user_id = request.data.get('userId', None) # 前端可能传这个参数
        if not user_id:
            # 尝试从users获取 (兼容某些前端可能发数组)
            users = request.data.get('users', None)
            if users and isinstance(users, list):
                user_id = users[0] # 暂时只支持一个?
                pass
        
        des = request.data.get('des', '传阅')
        
        if not process_id or not task_id or not user_id:
            return ErrorResponse(msg="流程ID、任务ID和用户ID不能为空")
        
        try:
            result = WorkflowProcessService.refer_flow(
                process_id=process_id,
                task_id=task_id,
                user_id=user_id,
                des=des,
                user=request.user
            )
            return SuccessResponse(msg=result.get('msg', '传阅成功'))
        except ValueError as e:
            return ErrorResponse(msg=str(e))
        except Exception as e:
            return ErrorResponse(msg=f"传阅失败: {str(e)}")

    @action(methods=['POST'], detail=False, url_path='create-child-flow')
    def create_child_flow(self, request):
        """
        创建子流程
        
        POST /api/workflow/process/create-child-flow/
        """
        from dvadmin_twodev.node_workflow.process.services import WorkflowProcessService
        
        scheme_code = request.data.get('schemeCode', None)
        process_id = request.data.get('processId', None) # 暂未用
        parent_process_id = request.data.get('parentProcessId', None)
        parent_task_id = request.data.get('parentTaskId', None)
        
        if not scheme_code or not parent_process_id or not parent_task_id:
            return ErrorResponse(msg="流程编号、父流程ID和父任务ID不能为空")
        
        try:
            result = WorkflowProcessService.create_child_flow(
                scheme_code=scheme_code,
                parent_process_id=parent_process_id,
                parent_task_id=parent_task_id,
                user=request.user
            )
            return SuccessResponse(data=result)
        except ValueError as e:
            return ErrorResponse(msg=str(e))
        except Exception as e:
            return ErrorResponse(msg=f"创建子流程失败: {str(e)}")
    
    @action(methods=['POST'], detail=False, url_path='sign-flow')
    def sign_flow(self, request):
        """
        加签流程（兼容前端API）
        
        POST /api/workflow/process/sign-flow/
        """
        from dvadmin_twodev.node_workflow.process.services import WorkflowProcessService
        
        process_id = request.data.get('processId', None)
        task_id = request.data.get('taskId', None)
        user_id = request.data.get('userId', None)
        des = request.data.get('des', '')
        
        if not process_id or not task_id or not user_id:
            return ErrorResponse(msg="流程ID、任务ID和用户ID不能为空")
        
        try:
            result = WorkflowProcessService.sign_flow(
                process_id=process_id,
                task_id=task_id,
                user_id=user_id,
                des=des,
                user=request.user
            )
            return SuccessResponse(msg=result.get('msg', '加签成功'))
        except ValueError as e:
            return ErrorResponse(msg=str(e))
        except Exception as e:
            return ErrorResponse(msg=f"加签失败: {str(e)}")

    @action(methods=['POST'], detail=False, url_path='sign-audit-flow')
    def sign_audit_flow(self, request):
        """
        加签审批流程（兼容前端API）
        
        POST /api/workflow/process/sign-audit-flow/
        """
        from dvadmin_twodev.node_workflow.process.services import WorkflowProcessService
        
        process_id = request.data.get('processId', None)
        task_id = request.data.get('taskId', None)
        operation_code = request.data.get('operationCode', 'agree')
        des = request.data.get('des', '')
        
        if not process_id or not task_id:
            return ErrorResponse(msg="流程ID和任务ID不能为空")
        
        try:
            # 直接复用 audit_flow，因为加签任务本质上也是一种任务审批
            result = WorkflowProcessService.audit_flow(
                process_id=process_id,
                task_id=task_id,
                operation_code=operation_code,
                operation_name='加签同意' if operation_code == 'agree' else '加签不同意',
                user=request.user,
                des=des
            )
            return SuccessResponse(msg=result.get('msg', '加签审批成功'))
        except ValueError as e:
            return ErrorResponse(msg=str(e))
        except Exception as e:
            return ErrorResponse(msg=f"加签审批失败: {str(e)}")
    
    @action(methods=['POST'], detail=False, url_path='revoke-flow')
    def revoke_flow(self, request):
        """
        撤销流程（兼容前端API）
        
        请求方式：POST /api/workflow/process/revoke-flow/
        """
        from dvadmin_twodev.node_workflow.process.services import WorkflowProcessService
        
        process_id = request.data.get('processId', None)
        
        if not process_id:
            return ErrorResponse(msg="流程ID不能为空")
        
        try:
            result = WorkflowProcessService.revoke_flow(process_id, request.user)
            return SuccessResponse(msg=result.get('msg', '撤销成功'))
        except ValueError as e:
            return ErrorResponse(msg=str(e))
        except Exception as e:
            return ErrorResponse(msg=f"撤销失败: {str(e)}")

    @action(methods=['POST'], detail=False, url_path='urge-flow')
    def urge_flow(self, request):
        """
        催办流程（兼容前端API）

        请求方式：POST /api/workflow/process/urge-flow/
        """
        from dvadmin_twodev.node_workflow.process.services import WorkflowProcessService

        process_id = request.data.get('processId', None)

        if not process_id:
            return ErrorResponse(msg="流程ID不能为空")

        try:
            result = WorkflowProcessService.urge_flow(process_id, request.user)
            return SuccessResponse(msg=result.get('msg', '催办成功'))
        except ValueError as e:
            return ErrorResponse(msg=str(e))
        except Exception as e:
            return ErrorResponse(msg=f"催办失败: {str(e)}")

    @action(methods=['POST'], detail=False, url_path='revoke-audit')
    def revoke_audit(self, request):
        """
        撤销审核（已办任务中撤销自己的审核）

        请求方式：POST /api/workflow/process/revoke-audit/

        请求参数：
        {
            "processId": "...",  // 流程ID
            "taskId": "..."  // 任务ID
        }

        返回格式：
        {
            "code": 200,
            "info": "撤销审核成功"
        }
        """
        process_id = request.data.get('processId', None)
        task_id = request.data.get('taskId', None)

        if not process_id or not task_id:
            return ErrorResponse(msg="流程ID和任务ID不能为空")

        user_id = str(request.user.id) if hasattr(request.user, 'id') else None
        if not user_id:
            return ErrorResponse(msg="用户未登录")

        try:
            with transaction.atomic():
                # 查询流程实例
                process = WorkflowProcessModel.objects.filter(id=process_id).first()
                if not process:
                    return ErrorResponse(msg="流程实例不存在")

                # 检查流程是否已结束
                if process.is_finished == 1:
                    return ErrorResponse(msg="流程已结束，无法撤销审核")

                # 查询原任务
                task = WorkflowTaskModel.objects.filter(id=task_id, process_id=process_id).first()
                if not task:
                    return ErrorResponse(msg="任务不存在")

                # 检查是否是该用户处理的任务
                task_relation = WorkflowTaskRelationModel.objects.filter(
                    task_id=task_id,
                    user_id=user_id,
                    result__in=[1, 2]  # 已处理（1=同意, 2=不同意）
                ).first()

                if not task_relation:
                    return ErrorResponse(msg="您没有处理过此任务，无法撤销")

                # 检查下一个节点是否已经有人处理
                # 查询该任务之后创建的任务
                next_tasks = WorkflowTaskModel.objects.filter(
                    process_id=process_id,
                    prev_node_id=task.node_id,
                    is_finished__in=[1, 2]  # 已完成或已关闭
                )

                if next_tasks.exists():
                    return ErrorResponse(msg="下一节点已有人处理，无法撤销审核")

                # 撤销审核：
                # 1. 将该任务的 TaskRelation 结果重置
                task_relation.result = 0  # 未处理
                task_relation.time = None
                task_relation.save()

                # 2. 将任务状态重置为未完成
                task.is_finished = 0
                task.save()

                # 3. 删除下一节点的待办任务（如果有）
                WorkflowTaskModel.objects.filter(
                    process_id=process_id,
                    prev_node_id=task.node_id,
                    is_finished=0  # 未完成的
                ).delete()

                # 4. 删除对应的任务日志（可选，保留审计记录则不删除）
                # WorkflowTaskLogModel.objects.filter(task_id=task_id, task_user_id=user_id).delete()

                # 5. 更新流程状态（如果之前被标记为结束，需要重新打开）
                # 这种情况通常不会发生，因为上面已经检查了下一节点是否有人处理

                return SuccessResponse(msg="撤销审核成功")

        except Exception as e:
            return ErrorResponse(msg=f"撤销审核失败: {str(e)}")

    @action(methods=['GET'], detail=False, url_path='ioc-methods')
    def list_ioc_methods(self, request):
        """
        获取所有已注册的IOC方法列表

        请求方式：GET /api/workflow/process/ioc-methods/

        返回格式：
        {
            "code": 200,
            "info": "获取成功",
            "data": [
                {"name": "TestLine1", "description": "测试方法：返回所有超级管理员"},
                {"name": "TestLine3", "description": "测试方法：返回当前用户部门的负责人"},
                ...
            ]
        }

        用于前端在流程设计时显示可用的IOC方法列表
        """
        try:
            from dvadmin_twodev.node_workflow.ioc import ioc_registry

            methods = ioc_registry.list_all_with_info()
            return WorkflowSuccessResponse(data=methods, info="获取成功")
        except ImportError as e:
            return WorkflowErrorResponse(info=f"IOC模块未安装: {e}")
        except Exception as e:
            return WorkflowErrorResponse(info=f"获取IOC方法列表失败: {e}")
