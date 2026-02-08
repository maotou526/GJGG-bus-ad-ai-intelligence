'''
Description: 流程模板视图
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework.decorators import action
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from .models import WorkflowSchemeModel
from .serializers import (
    WorkflowSchemeModelSerializer,
    WorkflowSchemeModelCreateSerializer,
    WorkflowSchemeModelUpdateSerializer,
    WorkflowSchemeModelListSerializer,
    WorkflowSchemeModelImportSerializer,
)


class WorkflowSchemeModelViewSet(CustomModelViewSet):
    """
    流程模板管理视图集
    提供标准的 CRUD 接口和自定义业务接口
    """
    
    queryset = WorkflowSchemeModel.objects.select_related('scheme_info').all()
    serializer_class = WorkflowSchemeModelSerializer
    create_serializer_class = WorkflowSchemeModelCreateSerializer
    update_serializer_class = WorkflowSchemeModelUpdateSerializer
    list_serializer_class = WorkflowSchemeModelListSerializer
    import_serializer_class = WorkflowSchemeModelImportSerializer
    
    # 排序配置
    ordering_fields = ['scheme_info_id', 'type', 'create_datetime', 'update_datetime']
    ordering = ['-create_datetime']
    
    # 搜索字段
    search_fields = ['scheme_info_id', 'creator_name']
    
    # 过滤字段
    filter_fields = ['id', 'scheme_info_id', 'type']
    
    @action(methods=['GET'], detail=False, url_path='by-scheme-info')
    def get_by_scheme_info(self, request):
        """
        根据流程信息ID获取模板列表
        
        请求方式：GET /api/WorkflowSchemeModelViewSet/by-scheme-info/
        
        请求参数：
            scheme_info_id: 流程信息ID
            type: 模板类型（可选，1=正式, 2=草稿）
            
        返回结果：
        {
            "code": 2000,
            "data": [
                {
                    "id": "...",
                    "scheme_info_id": "...",
                    "type": 1,
                    "type_display": "正式",
                    ...
                }
            ],
            "msg": "获取成功"
        }
        """
        scheme_info_id = request.query_params.get('scheme_info_id', None)
        if not scheme_info_id:
            return ErrorResponse(msg="scheme_info_id 参数必填")
        
        queryset = self.get_queryset().filter(scheme_info_id=scheme_info_id)
        
        # 过滤类型
        scheme_type = request.query_params.get('type', None)
        if scheme_type is not None:
            queryset = queryset.filter(type=int(scheme_type))
        
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")
    
    @action(methods=['GET'], detail=True, url_path='content')
    def get_content(self, request, pk=None):
        """
        获取流程模板内容
        
        请求方式：GET /api/WorkflowSchemeModelViewSet/{id}/content/
        
        返回结果：
        {
            "code": 2000,
            "data": {
                "id": "...",
                "content": {...}
            },
            "msg": "获取成功"
        }
        """
        instance = self.get_object()
        import json
        content = None
        if instance.content:
            try:
                content = json.loads(instance.content)
            except json.JSONDecodeError:
                content = instance.content
        
        return SuccessResponse(
            data={
                "id": instance.id,
                "content": content
            },
            msg="获取成功"
        )
    
    @action(methods=['GET'], detail=False, url_path='form-data')
    def get_form_data(self, request):
        """
        获取流程模板表单数据（兼容原始力软格式）
        
        请求方式：GET /api/node_workflow/scheme/form-data/?scheme_info_id=xxx
        
        返回结果：
        {
            "code": 2000,
            "data": {
                "info": {...},      # 流程基本信息
                "scheme": {...},    # 流程图数据（已解析）
                "authList": [...]   # 权限列表
            },
            "msg": "获取成功"
        }
        """
        import json
        from dvadmin_twodev.node_workflow.schemeinfo.models import WorkflowSchemeInfoModel
        from dvadmin_twodev.node_workflow.schemeauth.models import WorkflowSchemeAuthModel
        
        scheme_info_id = request.query_params.get('scheme_info_id')
        if not scheme_info_id:
            return ErrorResponse(msg="scheme_info_id 参数必填")
        
        # 获取流程信息
        scheme_info = WorkflowSchemeInfoModel.objects.filter(id=scheme_info_id).first()
        if not scheme_info:
            return ErrorResponse(msg="流程信息不存在")
        
        # 获取关联的 scheme（当前启用的版本）
        scheme = None
        scheme_content = None
        if scheme_info.scheme_id:
            scheme = WorkflowSchemeModel.objects.filter(id=scheme_info.scheme_id).first()
            if scheme and scheme.content:
                # 不解析JSON，直接返回原始字符串
                scheme_content = scheme.content
        
        # 获取权限列表
        auth_list = WorkflowSchemeAuthModel.objects.filter(scheme_info_id=scheme_info_id).all()
        
        # 构造返回数据（小写字段名，无F_前缀）
        info_data = {
            "id": str(scheme_info.id),
            "code": scheme_info.code,
            "name": scheme_info.name,
            "category": scheme_info.category,
            "scheme_id": scheme_info.scheme_id,
            "enabled_mark": scheme_info.enabled_mark,
            "mark": scheme_info.mark,
            "is_in_app": scheme_info.is_in_app,
            "description": scheme_info.description,
            "type": scheme.type if scheme else None,
            "create_datetime": scheme.create_datetime.strftime('%Y-%m-%d %H:%M:%S') if scheme and scheme.create_datetime else None,
            "creator_name": scheme.creator_name if scheme else None
        }
        
        # scheme 返回包含完整字段的对象（小写字段名，无F_前缀）
        scheme_data = {
            "id": str(scheme.id) if scheme else None,
            "scheme_info_id": str(scheme_info.id),
            "type": scheme.type if scheme else None,
            "create_datetime": scheme.create_datetime.strftime('%Y-%m-%d %H:%M:%S') if scheme and scheme.create_datetime else None,
            "creator_id": scheme.creator_id if scheme else None,
            "creator_name": scheme.creator_name if scheme else None,
            "content": scheme_content if scheme_content else "{}"  # 原始JSON字符串
        }
        
        auth_data = []
        for auth in auth_list:
            auth_item = {
                "id": str(auth.id),
                "scheme_info_id": str(auth.scheme_info_id),
                "obj_name": auth.obj_name,
                "obj_id": auth.obj_id,
                "obj_type": auth.obj_type
            }
            auth_data.append(auth_item)
        
        return SuccessResponse(
            data={
                "info": info_data,
                "scheme": scheme_data,
                "authList": auth_data
            },
            msg="获取成功"
        )
    
    @action(methods=['POST'], detail=False, url_path='save-scheme-data')
    def save_scheme_data(self, request):
        """
        保存流程方案数据（完全按照原始力软SaveEntity逻辑）
        
        请求方式：POST /api/node_workflow/scheme/save-scheme-data/
        
        请求参数：
            schemeInfo: JSON字符串，包含流程基本信息
            scheme: JSON字符串，包含流程图数据（nodes, lines, closeDo）
            shcemeAuth: JSON字符串，包含权限人员列表
            type: 模板类型（1=正式, 2=草稿）
            
        返回结果：
        {
            "code": 2000,
            "data": {
                "scheme_info_id": "...",
                "scheme_id": "..."
            },
            "msg": "保存成功"
        }
        """
        import json
        from django.db import transaction
        from dvadmin_twodev.node_workflow.schemeinfo.models import WorkflowSchemeInfoModel
        from dvadmin_twodev.node_workflow.schemeauth.models import WorkflowSchemeAuthModel
        
        try:
            # 1. 解析请求数据
            scheme_info_str = request.data.get('schemeInfo')
            scheme_str = request.data.get('scheme')
            scheme_auth_str = request.data.get('shcemeAuth')
            save_type = request.data.get('type', 1)
            
            if not scheme_info_str or not scheme_str:
                return ErrorResponse(msg="缺少必要参数")
            
            # 解析 JSON 字符串
            scheme_info_data = json.loads(scheme_info_str)
            scheme_data = json.loads(scheme_str)
            scheme_auth_data = json.loads(scheme_auth_str) if scheme_auth_str else []
            
            # 使用事务
            with transaction.atomic():
                # 2. 确定 scheme_info 的 ID（C# 第255-263行）
                key_value = scheme_info_data.get('scheme_id', '')
                
                if not key_value:
                    # 新建：创建新的 scheme_info 实体
                    scheme_info = WorkflowSchemeInfoModel()
                    scheme_info.enabled_mark = 1  # 新建时默认启用（C# 第258行）
                else:
                    # 更新：获取已有的 scheme_info
                    scheme_info = WorkflowSchemeInfoModel.objects.filter(id=key_value).first()
                    if not scheme_info:
                        return ErrorResponse(msg="流程信息不存在")
                
                # 验证流程编码是否重复（C# Controller 第392-396行）
                code = scheme_info_data.get('code')
                existing = WorkflowSchemeInfoModel.objects.filter(code=code).exclude(
                    id=scheme_info.id if scheme_info.id else None
                ).first()
                if existing:
                    return ErrorResponse(msg="流程编码重复")
                
                # 3. 保存流程模板（C# 第265-276行）
                # 创建新的 scheme 实体
                scheme = WorkflowSchemeModel()
                scheme.type = save_type
                
                # ⚠️ 关键！先设置 scheme 属于哪个 scheme_info（C# 第268行）
                # 即使 scheme_info 还没保存，但已经有了 ID
                if scheme_info.id:
                    scheme.scheme_info_id = scheme_info.id
                # 如果是新建，在 scheme_info 保存后会更新
                
                # 保存流程内容
                scheme.content = json.dumps(scheme_data, ensure_ascii=False)
                
                # 设置创建人信息（scheme 每次保存都是新记录）
                if request.user and request.user.is_authenticated:
                    scheme.creator_id = request.user.id
                    scheme.creator_name = request.user.name if hasattr(request.user, 'name') else request.user.username
                
                scheme.save()  # 保存 scheme（C# 第273行）
                
                # 4. 更新 scheme_info 的字段（注意：字段名与模型定义一致）
                scheme_info.code = code
                scheme_info.name = scheme_info_data.get('name')
                scheme_info.category = scheme_info_data.get('category')
                scheme_info.mark = int(scheme_info_data.get('mark', 1))
                scheme_info.is_in_app = int(scheme_info_data.get('is_in_app', 2))
                
                # 注意：WorkflowSchemeInfoModel 没有 close_do_* 字段
                # 这些字段应该在 closeDo 对象中，已经包含在 scheme.content 里了
                
                description = scheme_info_data.get('description', '')
                scheme_info.description = description if description != '&nbsp;' else ''
                
                # ⚠️ 关键！将 scheme 的 ID 赋值给 scheme_info（C# 第274行）
                scheme_info.scheme_id = scheme.id
                
                # 设置创建人/修改人信息
                if request.user and request.user.is_authenticated:
                    if not key_value:
                        # 新建时设置创建人
                        scheme_info.creator_id = request.user.id
                        scheme_info.creator_name = request.user.name if hasattr(request.user, 'name') else request.user.username
                    # 更新时设置修改人（新建时也会设置）
                    scheme_info.modifier_id = request.user.id
                    scheme_info.modifier_name = request.user.name if hasattr(request.user, 'name') else request.user.username
                
                # 5. 保存或更新 scheme_info（C# 第278-286行）
                scheme_info.save()
                
                # 如果是新建，现在需要更新 scheme 的 scheme_info_id
                if not key_value:
                    scheme.scheme_info_id = scheme_info.id
                    scheme.save()
                
                # 6. 保存权限数据（C# 第289-298行）
                # 删除旧的权限数据
                WorkflowSchemeAuthModel.objects.filter(scheme_info_id=scheme_info.id).delete()
                
                # 创建新的权限数据
                for auth_item in scheme_auth_data:
                    auth = WorkflowSchemeAuthModel()
                    auth.scheme_info_id = scheme_info.id
                    auth.obj_type = auth_item.get('obj_type', 4)
                    
                    # 只有指定成员才需要保存具体信息
                    if auth.obj_type != 4:
                        auth.obj_id = auth_item.get('obj_id')
                        auth.obj_name = auth_item.get('obj_name')
                    
                    auth.save()
            
            return SuccessResponse(
                data={
                    "scheme_info_id": str(scheme_info.id),
                    "scheme_id": str(scheme.id)
                },
                msg="保存成功"
            )
            
        except json.JSONDecodeError as e:
            return ErrorResponse(msg=f"JSON解析失败: {str(e)}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            return ErrorResponse(msg=f"保存失败: {str(e)}")

    @action(methods=['POST'], detail=False, url_path='enable')
    def enable_scheme(self, request):
        """
        启用流程模板

        请求方式：POST /api/node_workflow/scheme/enable/

        请求参数：
            id: 流程信息ID (scheme_info_id)

        返回结果：
        {
            "code": 2000,
            "data": null,
            "msg": "启用成功"
        }
        """
        from dvadmin_twodev.node_workflow.schemeinfo.models import WorkflowSchemeInfoModel

        scheme_info_id = request.data.get('id')
        if not scheme_info_id:
            return ErrorResponse(msg="id 参数必填")

        scheme_info = WorkflowSchemeInfoModel.objects.filter(id=scheme_info_id).first()
        if not scheme_info:
            return ErrorResponse(msg="流程信息不存在")

        scheme_info.enabled_mark = 1
        scheme_info.save(update_fields=['enabled_mark'])

        return SuccessResponse(msg="启用成功")

    @action(methods=['POST'], detail=False, url_path='disable')
    def disable_scheme(self, request):
        """
        停用流程模板

        请求方式：POST /api/node_workflow/scheme/disable/

        请求参数：
            id: 流程信息ID (scheme_info_id)

        返回结果：
        {
            "code": 2000,
            "data": null,
            "msg": "停用成功"
        }
        """
        from dvadmin_twodev.node_workflow.schemeinfo.models import WorkflowSchemeInfoModel

        scheme_info_id = request.data.get('id')
        if not scheme_info_id:
            return ErrorResponse(msg="id 参数必填")

        scheme_info = WorkflowSchemeInfoModel.objects.filter(id=scheme_info_id).first()
        if not scheme_info:
            return ErrorResponse(msg="流程信息不存在")

        scheme_info.enabled_mark = 0
        scheme_info.save(update_fields=['enabled_mark'])

        return SuccessResponse(msg="停用成功")



