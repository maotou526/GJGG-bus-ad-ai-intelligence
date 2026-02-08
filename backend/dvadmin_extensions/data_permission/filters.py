"""
自定义数据权限过滤器

扩展原框架的数据权限功能，支持自定义规则配置。
"""
from rest_framework.filters import BaseFilterBackend
from django.db.models import Q, F
from .engine import RuleEngine
import logging
import re
import json

logger = logging.getLogger(__name__)


class CustomRuleDataPermissionFilter(BaseFilterBackend):
    """
    自定义规则数据权限过滤器
    
    工作流程：
    1. 检查当前接口是否配置了自定义规则（data_range=5）
    2. 如果有，使用规则引擎解析和应用规则
    3. 如果没有，跳过（由原框架的 DataLevelPermissionsFilter 处理）
    
    优先级：
    - 在 extra_filter_class 中排第一位
    - 优先于原框架的 DataLevelPermissionsFilter
    """
    
    def filter_queryset(self, request, queryset, view):
        """
        收集自定义规则的 Q 对象（不直接过滤）
        
        Args:
            request: Django Request 对象
            queryset: Django QuerySet 对象
            view: 视图对象
        
        Returns:
            原始 QuerySet（Q 对象收集到 request._data_permission_q_list）
        """
        # 1. 检查是否启用自定义数据权限
        if not self._is_enabled(request):
            return queryset
        
        # 2. 查找当前请求对应的所有自定义规则配置
        custom_rule_configs = self._get_all_custom_rule_configs(request, queryset, view)
        
        if not custom_rule_configs:
            # 没有自定义规则，让其他过滤器处理
            return queryset
        
        # 3. 使用规则引擎收集所有规则的 Q 对象
        try:
            from django.db.models import Q
            
            # 初始化 Q 对象列表（如果不存在）
            if not hasattr(request, '_data_permission_q_list'):
                request._data_permission_q_list = []
            
            for config in custom_rule_configs:
                rules_list = config.get('rules', [])
                logic_expr = config.get('logic', '')
                
                if not rules_list:
                    continue
                
                engine = RuleEngine(request, queryset)
                rule_q = engine.apply_rules(rules_list, logic_expr)
                
                if rule_q:
                    request._data_permission_q_list.append(rule_q)
                    logger.debug(
                        f"收集自定义规则 Q: 用户={request.user.username}, "
                        f"模型={queryset.model.__name__}, 规则数={len(rules_list)}"
                    )
            
            # 不直接过滤，返回原 queryset（让 ViewSet 统一处理）
            return queryset
        
        except Exception as e:
            logger.error(f"收集自定义规则失败: {e}", exc_info=True)
            # 出错时不过滤，保证系统可用性
            return queryset
    
    def _is_enabled(self, request) -> bool:
        """
        检查是否启用自定义数据权限功能
        
        Returns:
            bool: 是否启用
        """
        # 检查配置开关
        from django.conf import settings
        enabled = getattr(settings, 'ENABLE_CUSTOM_DATA_PERMISSION', True)
        
        if not enabled:
            return False
        
        # 检查用户是否登录
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return False
        
        # 超级管理员跳过自定义规则（查看所有数据）
        if request.user.is_superuser:
            return False
        
        return True
    
    def _get_all_custom_rule_configs(self, request, queryset, view) -> list:
        """
        获取当前请求对应的所有自定义规则配置（支持多个角色）
        
        工作流程：
        1. 根据当前请求的 API + Method 查找 MenuButton
        2. 根据用户角色 + MenuButton 查找所有 RoleMenuButtonPermission
        3. 检查 data_range 是否为 5（自定义规则）
        4. 返回所有角色的 custom_rules 配置列表
        
        Returns:
            list: 规则配置列表，每项格式：{"logic": "...", "rules": [...]}
                  如果没有自定义规则，返回空列表
        """
        try:
            api = request.path
            method = request.method
            
            # 获取 method 对应的数字
            methodList = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
            try:
                method_index = methodList.index(method)
            except ValueError:
                return []
            
            # 处理详情接口（替换ID为占位符）
            re_api = api
            _pk = request.parser_context.get('kwargs', {}).get('pk')
            if _pk:
                re_api = re.sub(str(_pk), '{id}', api)
            
            # 查找对应的 MenuButton
            from dvadmin.system.models import MenuButton
            menu_buttons = MenuButton.objects.filter(
                api=re_api,
                method=method_index
            )
            
            if not menu_buttons.exists():
                logger.debug(f"未找到 MenuButton: api={re_api}, method={method_index}")
                return []
            
            menu_button_ids = menu_buttons.values_list('id', flat=True)
            
            # 查找用户角色的权限配置
            if not hasattr(request.user, 'role'):
                return []
            
            role_ids = request.user.role.values_list('id', flat=True)
            
            from dvadmin.system.models import RoleMenuButtonPermission
            permissions = RoleMenuButtonPermission.objects.filter(
                role__in=role_ids,
                role__status=1,
                menu_button_id__in=menu_button_ids,
                data_range=5  # 只查找自定义规则
            )
            
            # 收集所有角色的自定义规则配置
            config_list = []
            for perm in permissions:
                if perm and perm.custom_rules:
                    logger.debug(
                        f"找到自定义规则配置: "
                        f"role_id={perm.role_id}, "
                        f"menu_button_id={perm.menu_button_id}"
                    )
                    
                    # ⭐ 解析 JSON 字符串（custom_rules 是 TextField）
                    try:
                        if isinstance(perm.custom_rules, str):
                            config = json.loads(perm.custom_rules)
                        else:
                            # 如果已经是 dict（理论上不应该，但做个兼容）
                            config = perm.custom_rules
                        
                        if config:
                            config_list.append(config)
                    except json.JSONDecodeError as e:
                        logger.error(f"解析 custom_rules 失败: {e}, 原始数据: {perm.custom_rules}")
                        continue
            
            return config_list
        
        except Exception as e:
            logger.error(f"获取自定义规则配置失败: {e}", exc_info=True)
            return []

