"""
数据权限扩展序列化器
"""
from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.system.models import RoleMenuButtonPermission
from .engine import RuleValidator


class CustomRuleConfigSerializer(serializers.Serializer):
    """自定义规则配置序列化器（用于嵌套）"""
    
    logic = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="逻辑表达式，如：(1 OR 2) AND 3"
    )
    
    rules = serializers.ListField(
        child=serializers.DictField(),
        help_text="规则列表"
    )
    
    def validate(self, attrs):
        """验证规则配置"""
        rules = attrs.get('rules', [])
        logic = attrs.get('logic', '')
        
        # 1. 验证规则列表
        is_valid, error_msg = RuleValidator.validate_rules(rules)
        if not is_valid:
            raise serializers.ValidationError({"rules": error_msg})
        
        # 2. 验证逻辑表达式
        rule_ids = {rule.get('id') for rule in rules if 'id' in rule}
        is_valid, error_msg = RuleValidator.validate_logic_expression(logic, rule_ids)
        if not is_valid:
            raise serializers.ValidationError({"logic": error_msg})
        
        return attrs


class RoleMenuButtonPermissionExtSerializer(CustomModelSerializer):
    """
    扩展的角色菜单按钮权限序列化器
    用于保存自定义规则配置
    """
    
    custom_rules = CustomRuleConfigSerializer(
        required=False,
        allow_null=True,
        help_text="自定义规则配置，当data_range=5时使用"
    )
    
    class Meta:
        model = RoleMenuButtonPermission
        fields = ['id', 'data_range', 'custom_rules']
    
    def validate(self, attrs):
        """验证数据"""
        data_range = attrs.get('data_range')
        custom_rules = attrs.get('custom_rules')
        
        # 如果 data_range=5，custom_rules 不能为空
        if data_range == 5 and not custom_rules:
            raise serializers.ValidationError({
                "custom_rules": "当选择自定义规则时，必须配置规则"
            })
        
        # 如果 data_range 不是 5，custom_rules 应该为空
        if data_range != 5 and custom_rules:
            attrs['custom_rules'] = None
        
        return attrs


class RuleFieldOptionSerializer(serializers.Serializer):
    """字段选项序列化器（用于前端下拉列表）"""
    
    name = serializers.CharField(help_text="字段名称")
    label = serializers.CharField(help_text="字段显示名")
    type = serializers.CharField(help_text="字段类型")
    help_text = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="字段说明"
    )


class OperatorOptionSerializer(serializers.Serializer):
    """操作符选项序列化器"""
    
    value = serializers.CharField(help_text="操作符值")
    label = serializers.CharField(help_text="操作符显示名")
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="操作符说明"
    )


class ValueTypeOptionSerializer(serializers.Serializer):
    """值类型选项序列化器"""
    
    value = serializers.CharField(help_text="值类型")
    label = serializers.CharField(help_text="显示名")
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="说明"
    )
    need_input = serializers.BooleanField(
        default=False,
        help_text="是否需要输入值"
    )

