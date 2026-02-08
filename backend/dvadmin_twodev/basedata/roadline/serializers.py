"""
Description: 线路模型序列化器
Version: 1.0
Autor: 王晨
Date: 2025-10-10 09:50:00
LastEditors: 王晨
LastEditTime: 2025-10-10 10:58:38
"""

import uuid
from rest_framework import serializers
from django.utils import timezone
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.string_util import get_date_object
from .models import RoadlineModel


class RoadlineModelSerializer(CustomModelSerializer):
    """
    线路模型序列化器

    功能说明：
    - 提供线路数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 自动计算显示字段（如状态、类型名称等）
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer，获得审计字段自动填充功能
    """


    # 计算字段 - 线路状态
    line_status = serializers.SerializerMethodField()

    # 计算字段 - 是否过期
    is_expired = serializers.SerializerMethodField()

    # 计算字段 - 是否启用
    is_enabled = serializers.SerializerMethodField()

    class Meta:
        model = RoadlineModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "md5_hash": {"write_only": True},  # MD5字段只在写入时使用，不在响应中显示
            # 数字字段类型配置
            "line_type": {"required": False, "allow_null": True},
            "sell_type": {"required": False, "allow_null": True},
            "ticket_price_type": {"required": False, "allow_null": True},
            "yy_type": {"required": False, "allow_null": True},
            "listing_type": {"required": False, "allow_null": True},
            "schedule_type": {"required": False, "allow_null": True},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
            # 整数字段类型配置
            "bus_count": {"required": False, "allow_null": True},
            "ad_bus_count": {"required": False, "allow_null": True},
            # 小数字段类型配置
            "line_length": {"required": False, "allow_null": True, "max_digits": 10, "decimal_places": 2},
            # ticket_price 已改为CharField，不再需要decimal配置
            "ticket_price": {"required": False, "allow_null": True, "allow_blank": True},
            # 日期字段类型配置
            "exec_day": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "expiry_day": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            # 描述字段配置
            "description": {"required": False, "allow_null": True, "allow_blank": True},
            # 文本字段配置
            "covered_population": {"required": False, "allow_null": True, "allow_blank": True},
        }

    def get_line_status(self, obj):
        """计算线路状态"""
        expiry_date = get_date_object(obj.expiry_day)
        if expiry_date and expiry_date < timezone.now().date():
            return "已过期"
        
        if obj.enabled_mark == 0:
            return "已禁用"
        elif obj.delete_mark == 1:
            return "已删除"
        else:
            return "正常运营"

    def get_is_expired(self, obj):
        """是否过期"""
        expiry_date = get_date_object(obj.expiry_day)
        if expiry_date:
            return expiry_date < timezone.now().date()
        return False

    def get_is_enabled(self, obj):
        """是否启用"""
        return obj.enabled_mark == 1 and obj.delete_mark == 0

    def validate_line_name(self, value):
        """验证线路名称"""
        if not value or not value.strip():
            raise serializers.ValidationError("线路名称不能为空")
        return value.strip()

    def validate_ticket_price(self, value):
        """验证票价（字符串类型，支持复杂票价描述）"""
        # ticket_price 已改为CharField，支持 "2-5元"、"起步2元" 等复杂描述
        # 不再进行数值验证
        if value is not None and isinstance(value, str):
            return value.strip()
        return value

    def validate_line_length(self, value):
        """验证线路长度（单位：km）"""
        if value is not None and value < 0:
            raise serializers.ValidationError("线路长度不能为负数")
        return value

    def validate_line_type(self, value):
        """验证线路类型"""
        if value is not None and value not in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
            raise serializers.ValidationError("线路类型只能是0(普通)、1(挂牌线)、2(区间)、3(同名区间)、4(定班线)、5(定制公交)、6(高峰线)、7(夜宵线)或8(低谷定班线)")
        return value

    def validate_sell_type(self, value):
        """验证售票方式"""
        if value is not None and value not in [1, 2]:
            raise serializers.ValidationError("售票方式只能是1(无人)或2(有人)")
        return value

    def validate_ticket_price_type(self, value):
        """验证票价类型"""
        if value is not None and value not in [1, 2]:
            raise serializers.ValidationError("票价类型只能是1(单一)或2(多级)")
        return value

    def validate_yy_type(self, value):
        """验证运营时段分类"""
        if value is not None and value not in [1, 2, 3]:
            raise serializers.ValidationError(
                "运营时段分类只能是1(全日线)、2(高峰线)或3(夜宵线)"
            )
        return value

    def validate_listing_type(self, value):
        """验证挂牌类型"""
        if value is not None and value not in [1, 2, 3]:
            raise serializers.ValidationError(
                "挂牌类型只能是1(无)、2(全日挂牌)或3(高峰挂牌)"
            )
        return value

    def validate_schedule_type(self, value):
        """验证定班类型"""
        if value is not None and value not in [1, 2]:
            raise serializers.ValidationError("定班类型只能是1(无)或2(定班线)")
        return value

    def validate(self, attrs):
        """整体验证"""
        # 验证启用日期和截止日期
        exec_day = attrs.get("exec_day")
        expiry_day = attrs.get("expiry_day")

        if exec_day and expiry_day and exec_day > expiry_day:
            raise serializers.ValidationError("启用日期不能晚于截止日期")

        return attrs


class RoadlineModelCreateSerializer(RoadlineModelSerializer):
    """
    线路创建序列化器

    功能说明：
    - 专门用于创建新线路时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(RoadlineModelSerializer.Meta):
        # 创建时必填字段
        extra_kwargs = {
            "line_name": {"required": True},
            "company_name": {"required": True},
            "md5_hash": {"write_only": True},
        }

    def create(self, validated_data):
        """创建线路时自动生成GUID"""

        # 调用父类的create方法
        return super().create(validated_data)


class RoadlineModelUpdateSerializer(RoadlineModelSerializer):
    """
    线路更新序列化器

    功能说明：
    - 专门用于更新现有线路时的数据验证
    - 继承基础序列化器的所有功能
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(RoadlineModelSerializer.Meta):
        # 更新时主键不可修改
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class RoadlineModelListSerializer(RoadlineModelSerializer):
    """
    线路列表序列化器

    功能说明：
    - 专门用于线路列表显示
    - 返回所有字段（包括计算字段和显示字段）
    - 包含计算字段（状态、显示名称等）
    - 所有字段为只读，确保数据安全
    """

    class Meta(RoadlineModelSerializer.Meta):
        # 返回所有字段
        fields = "__all__"
        # 继承父类的 read_only_fields
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class RoadlineModelSimpleSerializer(CustomModelSerializer):
    """
    线路简单序列化器
    只返回核心字段：id、线路名称、公司名称、线路编码、生效日期、失效日期
    """
    
    class Meta:
        model = RoadlineModel
        fields = ['id', 'line_name', 'company_name', 'normal_code', 'ygc_code', 'exec_day', 'expiry_day']
        read_only_fields = fields
        extra_kwargs = {
            "exec_day": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "expiry_day": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
        }


class RoadlineModelImportSerializer(CustomModelSerializer):
    """
    线路导入序列化器
    
    功能说明：
    - 专门用于Excel导入功能
    - 包含导入字段：
      * 线路名称（必填）
      * 公司名称（可选）
      * 线路长度（km）
      * 线路类型（0=普通，1=挂牌线，2=区间，3=同名区间，4=定班线，5=定制公交，6=高峰线，7=夜宵线，8=低谷定班线）
      * 售票方式（1=无人售票，2=有人售票）
      * 票价类型（1=单一票价，2=多级票价）
      * 票价（元）
      * 启用状态（1=启用，0=禁用）
      * 描述（可选）
    - 自动去重：所有导入字段完全相同的数据将被跳过
    - 去重逻辑：只导入字段都相同才认为是重复数据
    """
    
    class Meta:
        model = RoadlineModel
        fields = [
            'id',                 # 主键ID（用于批量更新模板）
            'company_name',       # 公司名称
            'branch',             # 车队
            'line_name',          # 线路名称
            'normal_code',        # 企业线路编码
            'ygc_code',           # 行业线路编号
            'line_length',        # 线路长度（km）
            'line_type',          # 线路类型
            'sell_type',          # 售票方式
            'ticket_price_type',  # 票价类型
            'ticket_price',       # 票价（元）
            'yy_type',            # 运营时段分类
            'listing_type',       # 挂牌类型
            'schedule_type',      # 定班类型
            'enabled_mark',       # 启用状态
            'bus_count',          # 配车数
            'ad_bus_count',       # 广告车辆数
            'exec_day',           # 启用日期
            'expiry_day',         # 截止日期
            'description',        # 描述
        ]
        extra_kwargs = {
            'line_name': {'required': True},  # 线路名称必填
            'company_name': {'required': False, 'allow_null': True, 'allow_blank': True},
            'branch': {'required': False, 'allow_null': True, 'allow_blank': True},
            'normal_code': {'required': False, 'allow_null': True, 'allow_blank': True},
            'ygc_code': {'required': False, 'allow_null': True, 'allow_blank': True},
            'line_length': {'required': False, 'allow_null': True},
            'line_type': {'required': False, 'allow_null': True},
            'sell_type': {'required': False, 'allow_null': True},
            'ticket_price_type': {'required': False, 'allow_null': True},
            'ticket_price': {'required': False, 'allow_null': True, 'allow_blank': True},
            'yy_type': {'required': False, 'allow_null': True},
            'listing_type': {'required': False, 'allow_null': True},
            'schedule_type': {'required': False, 'allow_null': True},
            'enabled_mark': {'required': False, 'allow_null': True},
            'bus_count': {'required': False, 'allow_null': True},
            'ad_bus_count': {'required': False, 'allow_null': True},
            'exec_day': {'required': False, 'allow_null': True, 'format': '%Y-%m-%d', 'input_formats': ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']},
            'expiry_day': {'required': False, 'allow_null': True, 'format': '%Y-%m-%d', 'input_formats': ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']},
            'description': {'required': False, 'allow_null': True, 'allow_blank': True},
        }
    
    def validate_line_name(self, value):
        """验证线路名称（必填）"""
        if not value or not value.strip():
            raise serializers.ValidationError("线路名称不能为空")
        return value.strip()
    
    def validate_company_name(self, value):
        """验证公司名称（允许为空）"""
        if value and isinstance(value, str):
            value = value.strip()
            # 如果去除空格后为空字符串，返回 None
            if not value:
                return None
            return value
        return value
    
    def validate_line_length(self, value):
        """验证线路长度（单位：km）"""
        if value is not None and value < 0:
            raise serializers.ValidationError("线路长度不能为负数")
        return value
    
    def validate_line_type(self, value):
        """验证线路类型"""
        if value is not None and value not in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
            raise serializers.ValidationError("线路类型只能是0(普通)、1(挂牌线)、2(区间)、3(同名区间)、4(定班线)、5(定制公交)、6(高峰线)、7(夜宵线)或8(低谷定班线)")
        return value
    
    def validate_sell_type(self, value):
        """验证售票方式"""
        if value is not None and value not in [1, 2]:
            raise serializers.ValidationError("售票方式只能是1(无人)或2(有人)")
        return value
    
    def validate_ticket_price_type(self, value):
        """验证票价类型"""
        if value is not None and value not in [1, 2]:
            raise serializers.ValidationError("票价类型只能是1(单一)或2(多级)")
        return value
    
    def validate_ticket_price(self, value):
        """验证票价（字符串类型，支持复杂票价描述）"""
        # ticket_price 已改为CharField，支持 "2-5元"、"起步2元" 等复杂描述
        # 不再进行数值验证
        if value is not None and isinstance(value, str):
            return value.strip()
        return value
    
    def validate_enabled_mark(self, value):
        """验证线路状态"""
        if value is not None and value not in [0, 1]:
            raise serializers.ValidationError("线路状态只能是0(禁用)或1(启用)")
        return value
    
    def validate_description(self, value):
        """验证描述（允许为空）"""
        if value and isinstance(value, str):
            value = value.strip()
            # 如果去除空格后为空字符串，返回 None
            if not value:
                return None
            return value
        return value
    
    def create(self, validated_data):
        """
        创建新线路 - 带去重逻辑
        
        去重规则：
        检查所有导入字段是否完全相同，如果相同则返回现有记录（不创建新记录）
        """
        # 提取所有导入字段用于去重检查
        line_name = validated_data.get('line_name')
        company_name = validated_data.get('company_name')
        line_length = validated_data.get('line_length')
        line_type = validated_data.get('line_type')
        sell_type = validated_data.get('sell_type')
        ticket_price_type = validated_data.get('ticket_price_type')
        ticket_price = validated_data.get('ticket_price')
        enabled_mark = validated_data.get('enabled_mark', 1)
        description = validated_data.get('description')
        
        # 构建查询条件（所有导入字段）
        query_filter = {
            'line_name': line_name,
            'company_name': company_name,
            'line_length': line_length,
            'line_type': line_type,
            'sell_type': sell_type,
            'ticket_price_type': ticket_price_type,
            'ticket_price': ticket_price,
            'enabled_mark': enabled_mark,
            'description': description,
            'delete_mark': 0  # 只检查未删除的记录
        }
        
        # 去重检查：查询是否存在完全相同的记录
        existing = RoadlineModel.objects.filter(**query_filter).first()
        
        if existing:
            # 数据已存在，返回现有记录（不创建新记录）
            return existing
        
        # 数据不存在，创建新记录
        # 如果没有指定线路状态，默认为启用
        if 'enabled_mark' not in validated_data:
            validated_data['enabled_mark'] = 1
        
        # 如果没有指定delete_mark，默认为0（未删除）
        if 'delete_mark' not in validated_data:
            validated_data['delete_mark'] = 0
        
        return RoadlineModel.objects.create(**validated_data)