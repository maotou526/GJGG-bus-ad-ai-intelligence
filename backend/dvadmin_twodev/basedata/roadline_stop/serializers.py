"""
Description: 站点模型序列化器
Version: 1.0
Autor: 王晨
Date: 2025-10-14
LastEditors: 王晨
LastEditTime: 2025-10-14
"""

from rest_framework import serializers
from django.utils import timezone
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.string_util import get_date_object
from dvadmin_twodev.constants.business_constants import STOP_TYPE_MAP
from .models import RoadlineStopModel


class RoadlineStopModelSerializer(CustomModelSerializer):
    """
    站点模型序列化器

    功能说明：
    - 提供站点数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 自动计算显示字段（如状态等）
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer，获得审计字段自动填充功能
    """

    # 计算字段 - 是否过期
    is_expired = serializers.SerializerMethodField()

    # 计算字段 - 是否启用
    is_enabled = serializers.SerializerMethodField()

    class Meta:
        model = RoadlineStopModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            # 日期字段类型配置
            "exec_day": {
                "required": False,
                "allow_null": True,
                "format": "%Y-%m-%d",
                "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]
            },
            "expiry_day": {
                "required": False,
                "allow_null": True,
                "format": "%Y-%m-%d",
                "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]
            },
            # 小数字段类型配置
            "lon02": {
                "required": False,
                "allow_null": True,
                "max_digits": 20,
                "decimal_places": 16
            },
            "lat02": {
                "required": False,
                "allow_null": True,
                "max_digits": 20,
                "decimal_places": 16
            },
            "lon84": {
                "required": False,
                "allow_null": True,
                "max_digits": 20,
                "decimal_places": 16
            },
            "lat84": {
                "required": False,
                "allow_null": True,
                "max_digits": 20,
                "decimal_places": 16
            },
            "sidewalk_width": {
                "required": False,
                "allow_null": True,
                "max_digits": 6,
                "decimal_places": 2
            },
            # 布尔字段类型配置
            "is_main_road": {"required": False, "allow_null": True},
            # 状态字段类型配置
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
        }

    def get_is_expired(self, obj):
        """是否过期"""
        expiry_date = get_date_object(obj.expiry_day)
        if expiry_date:
            return expiry_date < timezone.now().date()
        return False

    def get_is_enabled(self, obj):
        """是否启用"""
        return obj.enabled_mark == 1 and obj.delete_mark == 0

    def validate_stop_name(self, value):
        """验证站点名称"""
        if not value or not value.strip():
            raise serializers.ValidationError("站点名称不能为空")
        return value.strip()

    def validate_stop_code(self, value):
        """验证站点编号唯一性"""
        if not value or not value.strip():
            raise serializers.ValidationError("站点编号不能为空")
        
        value = value.strip()
        
        # 更新时排除当前对象
        if self.instance and self.instance.stop_code == value:
            return value
        
        # 检查唯一性
        if RoadlineStopModel.objects.filter(stop_code=value).exists():
            raise serializers.ValidationError("站点编号已存在")
        
        return value

    def validate_sidewalk_width(self, value):
        """验证人行道宽度"""
        if value is not None and value < 0:
            raise serializers.ValidationError("人行道宽度不能为负数")
        return value

    def validate(self, attrs):
        """整体验证"""
        # 验证启用日期和截止日期
        exec_day = get_date_object(
            attrs.get("exec_day") or (self.instance.exec_day if self.instance else None)
        )
        expiry_day = get_date_object(
            attrs.get("expiry_day") or (self.instance.expiry_day if self.instance else None)
        )

        if exec_day and expiry_day and exec_day > expiry_day:
            raise serializers.ValidationError("启用日期不能晚于截止日期")
        
        # 根据站点类型自动填充站点类型名称
        stop_type = attrs.get("stop_type")
        if stop_type is not None:
            stop_type_name = STOP_TYPE_MAP.get(stop_type, '')
            attrs["stop_type_name"] = stop_type_name
        elif "stop_type" in attrs and attrs["stop_type"] is None:
            # 如果站点类型被清空，也清空站点类型名称
            attrs["stop_type_name"] = None

        return attrs


class RoadlineStopModelCreateSerializer(RoadlineStopModelSerializer):
    """
    站点创建序列化器

    功能说明：
    - 专门用于创建新站点时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(RoadlineStopModelSerializer.Meta):
        # 创建时必填字段
        extra_kwargs = {
            **RoadlineStopModelSerializer.Meta.extra_kwargs,
            "stop_name": {"required": True},
            "stop_code": {"required": True},
        }

    def create(self, validated_data):
        """创建站点"""
        # 调用父类的create方法
        return super().create(validated_data)


class RoadlineStopModelUpdateSerializer(RoadlineStopModelSerializer):
    """
    站点更新序列化器

    功能说明：
    - 专门用于更新现有站点时的数据验证
    - 继承基础序列化器的所有功能
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(RoadlineStopModelSerializer.Meta):
        # 更新时主键不可修改
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class RoadlineStopSimpleSerializer(CustomModelSerializer):
    """
    站点简单序列化器
    只返回核心字段：id、站点编号、站点名称
    """
    
    class Meta:
        model = RoadlineStopModel
        fields = ['id', 'stop_code', 'stop_name']
        read_only_fields = fields


class RoadlineStopModelListSerializer(RoadlineStopModelSerializer):
    """
    站点列表序列化器

    功能说明：
    - 专门用于站点列表显示，优化性能
    - 只包含列表展示需要的核心字段
    - 包含计算字段（状态等）
    - 减少数据传输量，提高响应速度
    - 所有字段为只读，确保数据安全
    """

    class Meta:
        model = RoadlineStopModel
        fields = [
            # 基础信息字段
            "id",
            "stop_code",
            "stop_name",
            "pinyin",
            "area",
            "district",
            "roadline_name",
            "street",
            "path_direction",
            "stop_address",
            
            # 线路和坐标字段
            "road_line_list",
            "lon02",
            "lat02",
            "lon84",
            "lat84",
            
            # 属性字段
            "is_main_road",
            "sidewalk_width",
            "metroline_name",
            
            # 日期字段
            "exec_day",
            "expiry_day",
            
            # 状态字段
            "enabled_mark",
            "delete_mark",
            
            # 计算显示字段
            "is_enabled",
            "is_expired",
            
            # 审计字段
            "create_datetime",
            "update_datetime",
            "creator_name",
            "modifier_name",
            "description",
            "remark",
        ]
        read_only_fields = fields


class RoadlineStopMapSerializer(CustomModelSerializer):
    """
    站点地图序列化器（用于地图展示）
    
    功能说明：
    - 专门用于地图展示，包含WGS84坐标系坐标数据
    - 包含地图展示需要的核心字段
    - 优化数据传输，只包含地图展示必需的字段
    - 所有字段为只读，确保数据安全
    """
    
    class Meta:
        model = RoadlineStopModel
        fields = [
            # 基础信息字段
            "id",
            "stop_code",
            "stop_name",
            "area",
            "district",
            "street",
            "stop_address",
            
            # WGS84坐标字段
            "lon84",
            "lat84",
        ]
        read_only_fields = fields


class RoadlineStopImportSerializer(CustomModelSerializer):
    """
    站点导入序列化器
    
    功能说明：
    - 专门用于Excel导入功能
    - 包含所有表单字段，与添加页面保持一致
    - 自动去重：站点名称+经度+纬度完全相同的数据将被跳过
    - 去重逻辑：只有三个字段都相同才认为是重复数据
    - 提供完整的数据验证功能
    """
    
    class Meta:
        model = RoadlineStopModel
        fields = [
            'stop_code',
            'district',
            'roadline_name',
            'stop_name',
            'stop_address',
            'pinyin',
            'area',
            'street',
            'path_direction',
            'road_line_list',
            'lon02',
            'lat02',
            'lon84',
            'lat84',
            'stop_type',
            'stop_type_name',
            'enabled_mark',
            'remark',
        ]
        extra_kwargs = {
            # 必填字段 - 在导入时允许为空，通过验证方法处理
            'stop_code': {'required': False, 'allow_null': True, 'allow_blank': True},
            'stop_name': {'required': True},
            # 可选字段
            'district': {'required': False, 'allow_null': True, 'allow_blank': True},
            'roadline_name': {'required': False, 'allow_null': True, 'allow_blank': True},
            'stop_address': {'required': False, 'allow_null': True, 'allow_blank': True},
            'pinyin': {'required': False, 'allow_null': True, 'allow_blank': True},
            'area': {'required': False, 'allow_null': True, 'allow_blank': True},
            'street': {'required': False, 'allow_null': True, 'allow_blank': True},
            'path_direction': {'required': False, 'allow_null': True, 'allow_blank': True},
            'road_line_list': {'required': False, 'allow_null': True, 'allow_blank': True},
            'lon02': {'required': False, 'allow_null': True, 'max_digits': 20, 'decimal_places': 16},
            'lat02': {'required': False, 'allow_null': True, 'max_digits': 20, 'decimal_places': 16},
            'lon84': {'required': False, 'allow_null': True, 'max_digits': 20, 'decimal_places': 16},
            'lat84': {'required': False, 'allow_null': True, 'max_digits': 20, 'decimal_places': 16},
            'stop_type': {'required': False, 'allow_null': True},
            'stop_type_name': {'required': False, 'allow_null': True, 'allow_blank': True},
            'enabled_mark': {'required': False, 'allow_null': True},
            'remark': {'required': False, 'allow_null': True, 'allow_blank': True},
        }
    
    def validate_stop_code(self, value):
        """验证站点编号 - 如果为空则返回None，允许后续自动生成"""
        if value:
            return value.strip() if isinstance(value, str) else value
        return None
    
    def validate_street(self, value):
        """验证街道字段 - 确保正确处理字符串类型"""
        if value is None:
            return None
        # 如果是数字类型（Excel可能误识别），转换为字符串
        if isinstance(value, (int, float)):
            return str(value)
        # 如果是字符串，去除首尾空格
        if isinstance(value, str):
            return value.strip()
        return value
    
    def validate(self, attrs):
        """
        整体验证
        
        基本数据格式验证，不进行去重检查
        去重检查在 create() 方法中进行
        """
        # 如果站点编号为空，尝试使用站名生成一个临时编号
        # 注意：这里不强制要求站点编号，因为导入时可能为空
        stop_code = attrs.get('stop_code')
        stop_name = attrs.get('stop_name')
        
        # 如果站点编号为空但站名不为空，可以允许继续（在create中处理）
        # 如果站名为空，则必须报错
        if not stop_name or (isinstance(stop_name, str) and not stop_name.strip()):
            raise serializers.ValidationError({"stop_name": "站名不能为空"})
        
        # 根据站点类型自动填充站点类型名称
        stop_type = attrs.get("stop_type")
        if stop_type is not None:
            stop_type_name = STOP_TYPE_MAP.get(stop_type, '')
            attrs["stop_type_name"] = stop_type_name
        elif "stop_type" in attrs and attrs["stop_type"] is None:
            # 如果站点类型被清空，也清空站点类型名称
            attrs["stop_type_name"] = None
        
        return attrs
    
    def validate_stop_name(self, value):
        """验证站点名称"""
        if not value or not value.strip():
            raise serializers.ValidationError("站点名称不能为空")
        return value.strip()
    
    def validate_lon02(self, value):
        """验证经度（GCJ02）"""
        if value is not None:
            # 验证经度范围（中国范围大约在73-135之间）
            if not (73 <= float(value) <= 135):
                raise serializers.ValidationError("经度超出有效范围(73-135)")
        return value
    
    def validate_lat02(self, value):
        """验证纬度（GCJ02）"""
        if value is not None:
            # 验证纬度范围（中国范围大约在3-53之间）
            if not (3 <= float(value) <= 53):
                raise serializers.ValidationError("纬度超出有效范围(3-53)")
        return value
    
    def validate_lon84(self, value):
        """验证经度（WGS84）"""
        if value is not None:
            # 验证经度范围（中国范围大约在73-135之间）
            if not (73 <= float(value) <= 135):
                raise serializers.ValidationError("经度(WGS84)超出有效范围(73-135)")
        return value
    
    def validate_lat84(self, value):
        """验证纬度（WGS84）"""
        if value is not None:
            # 验证纬度范围（中国范围大约在3-53之间）
            if not (3 <= float(value) <= 53):
                raise serializers.ValidationError("纬度(WGS84)超出有效范围(3-53)")
        return value
    
    def validate(self, attrs):
        """
        整体验证
        
        基本数据格式验证，不进行去重检查
        去重检查在 create() 方法中进行
        """
        # 如果站点编号为空，尝试使用站名生成一个临时编号
        # 注意：这里不强制要求站点编号，因为导入时可能为空
        stop_code = attrs.get('stop_code')
        stop_name = attrs.get('stop_name')
        
        # 如果站点编号为空但站名不为空，可以允许继续（在create中处理）
        # 如果站名为空，则必须报错
        if not stop_name or (isinstance(stop_name, str) and not stop_name.strip()):
            raise serializers.ValidationError({"stop_name": "站名不能为空"})
        
        return attrs
    
    def create(self, validated_data):
        """
        创建站点 - 带去重逻辑
        
        去重规则：
        1. 优先使用站点编号（stop_code）进行去重检查
        2. 如果站点编号相同，则认为是重复数据，返回现有记录（不创建新记录）
        3. 如果没有站点编号，则检查站点名称+经度+纬度是否完全相同
        4. 只要有一个不同，就创建新记录
        
        这样设计的好处：
        - 不会抛出异常中断导入流程
        - 返回现有记录而不是 None，确保返回值一致性
        - 导入框架可以正常统计（重复的会被识别为已存在）
        """
        import uuid
        
        stop_code = validated_data.get('stop_code')
        stop_name = validated_data.get('stop_name')
        lon02 = validated_data.get('lon02')
        lat02 = validated_data.get('lat02')
        
        # 如果站点编号为空，尝试使用站名+经纬度生成一个临时编号用于去重
        # 但实际保存时，如果站点编号为空，允许保存为空（模型字段允许null）
        if not stop_code or (isinstance(stop_code, str) and not stop_code.strip()):
            # 站点编号为空，使用站点名称+经纬度进行去重检查
            if stop_name and lon02 is not None and lat02 is not None:
                existing = RoadlineStopModel.objects.filter(
                    stop_name=stop_name,
                    lon02=lon02,
                    lat02=lat02,
                    delete_mark=0  # 只检查未删除的记录
                ).first()
                
                if existing:
                    # 数据已存在，返回现有记录（不创建新记录）
                    return existing
            # 如果站点编号为空且没有重复，允许创建（站点编号字段允许null）
        else:
            # 有站点编号，优先使用站点编号进行去重检查
            existing = RoadlineStopModel.objects.filter(
                stop_code=stop_code,
                delete_mark=0  # 只检查未删除的记录
            ).first()
            
            if existing:
                # 数据已存在，返回现有记录（不创建新记录）
                return existing
        
        # 数据不存在，创建新记录
        # 注意：如果 stop_code 为空字符串，转换为 None（因为模型字段允许 null）
        if stop_code and isinstance(stop_code, str) and not stop_code.strip():
            validated_data['stop_code'] = None
        
        return RoadlineStopModel.objects.create(**validated_data)
