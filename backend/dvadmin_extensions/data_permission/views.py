"""
数据权限扩展视图

提供自定义规则配置的API接口
"""
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse
from dvadmin.system.models import RoleMenuButtonPermission
from .serializers import (
    RoleMenuButtonPermissionExtSerializer,
    RuleFieldOptionSerializer,
    OperatorOptionSerializer,
    ValueTypeOptionSerializer
)
from .engine import RuleEngine
import logging

logger = logging.getLogger(__name__)


class DataPermissionRuleViewSet(CustomModelViewSet):
    """
    自定义数据权限规则管理视图集
    
    提供：
    1. 获取可用字段列表
    2. 获取操作符列表
    3. 获取值类型列表
    4. 验证规则配置
    5. 预览SQL
    """
    queryset = RoleMenuButtonPermission.objects.all()
    serializer_class = RoleMenuButtonPermissionExtSerializer
    permission_classes = [IsAuthenticated]
    extra_filter_class = []  # 不需要数据权限过滤
    
    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def get_field_options(self, request):
        """
        获取可用字段列表
        
        查询参数：
        - model_name: 模型名称，如 ParkModel
        
        返回：
        [
            {
                "name": "dept_belong_id",
                "label": "部门归属",
                "type": "CharField",
                "help_text": "数据归属部门"
            },
            ...
        ]
        """
        model_name = request.query_params.get('model_name')
        
        if not model_name:
            return DetailResponse(data=[], msg="请提供 model_name 参数")
        
        try:
            # 获取模型的所有字段
            from dvadmin.utils.models import get_custom_app_models
            
            # 查找模型
            target_model = None
            for model_info in get_custom_app_models():
                if model_info['object'].__name__ == model_name:
                    target_model = model_info['object']
                    break
            
            if not target_model:
                return DetailResponse(data=[], msg=f"未找到模型: {model_name}")
            
            # 提取字段信息
            fields = []
            for field in target_model._meta.fields:
                # 排除不适合做过滤的字段
                if field.name in ['id', 'password', 'create_datetime', 'update_datetime']:
                    continue
                
                fields.append({
                    "name": field.name,
                    "label": field.verbose_name or field.name,
                    "type": field.get_internal_type(),
                    "help_text": field.help_text or ""
                })
            
            serializer = RuleFieldOptionSerializer(fields, many=True)
            return DetailResponse(data=serializer.data, msg="获取成功")
        
        except Exception as e:
            logger.error(f"获取字段选项失败: {e}", exc_info=True)
            return DetailResponse(data=[], msg=f"获取失败: {str(e)}")
    
    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def get_operator_options(self, request):
        """
        获取操作符列表
        
        查询参数：
        - field_type: 字段类型（可选），返回适合该类型的操作符
        
        返回：
        [
            {
                "value": "eq",
                "label": "等于 (=)",
                "description": "精确匹配"
            },
            ...
        ]
        """
        field_type = request.query_params.get('field_type')
        
        # 所有操作符
        all_operators = [
            {"value": "eq", "label": "等于 (=)", "description": "精确匹配"},
            {"value": "ne", "label": "不等于 (!=)", "description": "不匹配"},
            {"value": "gt", "label": "大于 (>)", "description": "数值比较"},
            {"value": "gte", "label": "大于等于 (>=)", "description": "数值比较"},
            {"value": "lt", "label": "小于 (<)", "description": "数值比较"},
            {"value": "lte", "label": "小于等于 (<=)", "description": "数值比较"},
            {"value": "in", "label": "包含 (IN)", "description": "在列表中"},
            {"value": "not_in", "label": "不包含 (NOT IN)", "description": "不在列表中"},
            {"value": "contains", "label": "包含字符串", "description": "字符串包含"},
            {"value": "icontains", "label": "包含字符串(忽略大小写)", "description": "字符串包含"},
            {"value": "startswith", "label": "开头匹配", "description": "字符串开头"},
            {"value": "endswith", "label": "结尾匹配", "description": "字符串结尾"},
            {"value": "isnull", "label": "为空", "description": "NULL 检查"},
            {"value": "isnotnull", "label": "不为空", "description": "NOT NULL 检查"},
        ]
        
        # 根据字段类型过滤（可选功能）
        if field_type:
            # 可以根据字段类型返回适合的操作符
            type_operator_map = {
                'IntegerField': ['eq', 'ne', 'gt', 'gte', 'lt', 'lte', 'in', 'not_in'],
                'CharField': ['eq', 'ne', 'in', 'contains', 'icontains', 'startswith', 'endswith'],
                'BooleanField': ['eq', 'ne'],
                'DateTimeField': ['eq', 'gt', 'gte', 'lt', 'lte'],
                'ForeignKey': ['eq', 'in'],
            }
            
            valid_operators = type_operator_map.get(field_type, [op['value'] for op in all_operators])
            operators = [op for op in all_operators if op['value'] in valid_operators]
        else:
            operators = all_operators
        
        serializer = OperatorOptionSerializer(operators, many=True)
        return DetailResponse(data=serializer.data, msg="获取成功")
    
    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def get_value_type_options(self, request):
        """
        获取值类型列表
        
        返回：
        [
            {
                "value": "static",
                "label": "固定值",
                "description": "手动输入的固定值",
                "need_input": true
            },
            ...
        ]
        """
        value_types = [
            {
                "value": "static",
                "label": "固定值 - 手动输入的值",
                "description": "手动输入的值",
                "need_input": True
            },
            {
                "value": "current_user",
                "label": "当前用户 - 当前登录用户的ID",
                "description": "当前登录用户的ID",
                "need_input": False
            },
            {
                "value": "current_company",
                "label": "当前公司 - 当前用户所在公司ID",
                "description": "当前用户所在公司ID",
                "need_input": False
            },
            {
                "value": "company_tree",
                "label": "当前公司树 - 当前公司及所有下级公司ID列表",
                "description": "当前公司及所有下级公司ID列表",
                "need_input": False
            },
            {
                "value": "current_dept",
                "label": "当前部门 - 当前用户所在部门ID",
                "description": "当前用户所在部门ID",
                "need_input": False
            },
            {
                "value": "dept_tree",
                "label": "当前部门树 - 当前部门及所有下级部门ID列表",
                "description": "当前部门及所有下级部门ID列表",
                "need_input": False
            },
        ]
        
        serializer = ValueTypeOptionSerializer(value_types, many=True)
        return DetailResponse(data=serializer.data, msg="获取成功")

