
from rest_framework import serializers
from django.utils import timezone
from django.db import models
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.string_util import get_date_object
from .models import RoadlineDetailModel
from dvadmin_twodev.basedata.roadline.models import RoadlineModel
from dvadmin_twodev.utils.geo.geo_utils import GeoCalculator


class RoadlineDetailModelSerializer(CustomModelSerializer):
    """
    线路走向详情序列化器

    功能说明：
    - 提供线路走向详情数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 自动计算显示字段（上下行名称、状态等）
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer，获得审计字段自动填充功能
    """

    # 计算字段 - 上下行显示名称
    up_down_display = serializers.SerializerMethodField()

    # 计算字段 - 关联线路名称
    roadline_name = serializers.SerializerMethodField()

    # 计算字段 - 是否过期
    is_expired = serializers.SerializerMethodField()

    # 计算字段 - 是否启用
    is_enabled = serializers.SerializerMethodField()

    # 计算字段 - 首末班时间格式化（时分格式）
    start_end_time_formatted = serializers.SerializerMethodField()

    class Meta:
        model = RoadlineDetailModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            # 外键字段配置
            "roadline": {"required": False, "allow_null": True},
            # 整数字段配置
            "up_down": {"required": False, "allow_null": True},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
            # 字符串字段配置
            "to_direction": {"required": False, "allow_null": True, "allow_blank": True},
            # 小数字段配置
            "line_length": {"required": False, "allow_null": True, "max_digits": 15, "decimal_places": 2},
            # 日期字段配置
            "exec_day": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "expiry_day": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
        }

    def get_up_down_display(self, obj):
        """上下行显示名称"""
        if obj.up_down == 0:
            return "上行"
        elif obj.up_down == 1:
            return "下行"
        else:
            return "未知"

    def get_roadline_name(self, obj):
        """获取关联线路名称"""
        if obj.roadline:
            return obj.roadline.line_name
        return None

    def get_is_expired(self, obj):
        """是否过期"""
        expiry_date = get_date_object(obj.expiry_day)
        if expiry_date:
            return expiry_date < timezone.now().date()
        return False

    def get_is_enabled(self, obj):
        """是否启用"""
        return obj.enabled_mark == 1 and obj.delete_mark == 0

    def get_start_end_time_formatted(self, obj):
        """
        格式化首末班时间为时分格式（HH:mm-HH:mm）
        
        功能说明：
        - 将首末班时间统一格式化为 HH:mm-HH:mm 格式
        - 支持多种输入格式：
          * HH:MM:SS-HH:MM:SS（带秒）
          * HH:MM-HH:MM（不带秒）
          * H:MM-H:MM（小时不补零）
        - 自动去除秒数，保留时分
        - 小时自动补零（如：5:30 -> 05:30）
        
        Returns:
            str: 格式化后的时间字符串（HH:mm-HH:mm）或原值（如果格式无法识别）
        """
        import re
        
        if not obj.start_end_time:
            return None
        
        time_str = str(obj.start_end_time).strip()
        
        if not time_str or '-' not in time_str:
            return time_str
        
        try:
            # 分割开始时间和结束时间
            parts = time_str.split('-')
            if len(parts) != 2:
                return time_str
            
            start_time, end_time = parts[0].strip(), parts[1].strip()
            
            # 处理每个时间部分
            def format_time_part(time_part):
                """格式化单个时间部分"""
                # 分割时、分、秒
                time_components = time_part.split(':')
                
                if len(time_components) >= 2:
                    hour = time_components[0].zfill(2)  # 小时补零
                    minute = time_components[1].zfill(2)  # 分钟补零
                    return f"{hour}:{minute}"
                
                return time_part
            
            # 格式化开始和结束时间
            formatted_start = format_time_part(start_time)
            formatted_end = format_time_part(end_time)
            
            # 验证格式是否正确（HH:mm格式）
            time_pattern = r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$'
            if re.match(time_pattern, formatted_start) and re.match(time_pattern, formatted_end):
                return f"{formatted_start}-{formatted_end}"
            
            # 如果验证失败，返回格式化后的结果（不做严格验证）
            return f"{formatted_start}-{formatted_end}"
            
        except Exception as e:
            # 如果格式化失败，返回原值
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"首末班时间格式化失败: {time_str}, 错误: {str(e)}")
            return time_str

    def validate_roadline(self, value):
        """验证关联线路"""
        if value is None:
            raise serializers.ValidationError("关联线路不能为空")
        
        # 检查线路是否存在且未删除
        if value.delete_mark == 1:
            raise serializers.ValidationError("关联的线路已被删除，无法使用")
        
        return value

    def validate_up_down(self, value):
        """验证上下行"""
        if value is not None and value not in [0, 1]:
            raise serializers.ValidationError("上下行只能是0(上行)或1(下行)")
        return value

    def validate_start_name(self, value):
        """验证起点名称"""
        if value and not value.strip():
            raise serializers.ValidationError("起点名称不能为空字符串")
        return value.strip() if value else value

    def validate_start_end_time(self, value):
        """
        验证并格式化首末班时间
        
        功能：
        - 自动将 HH:mm:ss-HH:mm:ss 格式转换为 HH:mm-HH:mm
        - 自动将 H:mm-H:mm 格式补零为 HH:mm-HH:mm
        - 验证时间格式正确性
        
        支持的输入格式：
        - 06:00:00-18:25:00  →  06:00-18:25
        - 06:00:00-18:25     →  06:00-18:25
        - 6:00-18:25         →  06:00-18:25
        - 06:00-18:25        →  06:00-18:25（不变）
        """
        import re
        
        if not value:
            return value
        
        # 去除首尾空格
        value = value.strip()
        
        # 检查是否包含分隔符
        if '-' not in value:
            raise serializers.ValidationError("首末班时间格式不正确，应为：HH:mm-HH:mm（如：05:30-22:00）")
        
        try:
            # 分割开始时间和结束时间
            parts = value.split('-')
            if len(parts) != 2:
                raise serializers.ValidationError("首末班时间格式不正确，应为：HH:mm-HH:mm（如：05:30-22:00）")
            
            start_time, end_time = parts[0].strip(), parts[1].strip()
            
            # 处理每个时间部分
            def format_time_part(time_part):
                """格式化单个时间部分：去掉秒数，补零"""
                # 分割时、分、秒
                time_components = time_part.split(':')
                
                if len(time_components) < 2:
                    raise ValueError(f"时间格式不正确：{time_part}")
                
                # 提取小时和分钟（忽略秒数）
                hour = int(time_components[0])
                minute = int(time_components[1])
                
                # 验证范围
                if hour < 0 or hour > 23:
                    raise ValueError(f"小时必须在 0-23 之间：{hour}")
                if minute < 0 or minute > 59:
                    raise ValueError(f"分钟必须在 0-59 之间：{minute}")
                
                # 格式化为 HH:mm
                return f"{hour:02d}:{minute:02d}"
            
            # 格式化开始和结束时间
            formatted_start = format_time_part(start_time)
            formatted_end = format_time_part(end_time)
            
            # 返回格式化后的时间
            formatted_time = f"{formatted_start}-{formatted_end}"
            
            return formatted_time
            
        except ValueError as e:
            raise serializers.ValidationError(f"首末班时间格式不正确：{str(e)}。正确格式：HH:mm-HH:mm（如：05:30-22:00）")
        except Exception as e:
            raise serializers.ValidationError(f"首末班时间格式验证失败：{str(e)}")

    

    def validate_line_length(self, value):
        """验证线路长度（单位：公里）"""
        if value is not None and value < 0:
            raise serializers.ValidationError("线路长度不能为负数")
        return value

    def validate(self, attrs):
        """整体验证"""
        # 验证上下行唯一性（同一线路的同一上下行只能有一条记录）
        roadline = attrs.get("roadline") or (self.instance.roadline if self.instance else None)
        up_down = attrs.get("up_down")
        
        if roadline and up_down is not None:
            # 构建查询条件
            existing_query = RoadlineDetailModel.objects.filter(
                roadline=roadline,
                up_down=up_down,
                delete_mark=0  # 只检查未删除的记录
            )
            
            # 如果是更新操作，排除当前实例
            if self.instance:
                existing_query = existing_query.exclude(id=self.instance.id)
            
            if existing_query.exists():
                up_down_text = "上行" if up_down == 0 else "下行"
                raise serializers.ValidationError(
                    f"线路'{roadline.line_name}'的{up_down_text}记录已存在，不能重复创建"
                )

        return attrs


class RoadlineDetailCreateSerializer(RoadlineDetailModelSerializer):
    """
    线路走向详情创建序列化器

    功能说明：
    - 专门用于创建新的线路走向详情时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(RoadlineDetailModelSerializer.Meta):
        # 创建时必填字段
        extra_kwargs = {
            **RoadlineDetailModelSerializer.Meta.extra_kwargs,
            "roadline": {"required": True},
            "up_down": {"required": True},
            "start_name": {"required": True},
        }

    def create(self, validated_data):
        """创建线路走向详情"""
        # 如果没有设置日期，可以从主线路继承
        if "exec_day" not in validated_data and validated_data.get("roadline"):
            validated_data["exec_day"] = validated_data["roadline"].exec_day
        
        if "expiry_day" not in validated_data and validated_data.get("roadline"):
            validated_data["expiry_day"] = validated_data["roadline"].expiry_day
        
        # 调用父类的create方法
        return super().create(validated_data)


class RoadlineDetailUpdateSerializer(RoadlineDetailModelSerializer):
    """
    线路走向详情更新序列化器

    功能说明：
    - 专门用于更新现有线路走向详情时的数据验证
    - 继承基础序列化器的所有功能
    - 防止修改主键ID、关联线路和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(RoadlineDetailModelSerializer.Meta):
        # 更新时不可修改的字段
        read_only_fields = [
            "id",
            "roadline",  # 不允许更换所属线路
            "create_datetime",
            "update_datetime"
        ]


class RoadlineDetailSimpleSerializer(CustomModelSerializer):
    """
    线路走向详情简单序列化器
    只返回核心字段：id、线路名称、上下行
    """
    roadline_name = serializers.SerializerMethodField()
    up_down_display = serializers.SerializerMethodField()
    
    class Meta:
        model = RoadlineDetailModel
        fields = ['id', 'roadline_name', 'up_down', 'up_down_display']
        read_only_fields = fields
    
    def get_roadline_name(self, obj):
        """获取关联线路名称"""
        if obj.roadline:
            return obj.roadline.line_name
        return None
    
    def get_up_down_display(self, obj):
        """上下行显示名称"""
        if obj.up_down == 0:
            return "上行"
        elif obj.up_down == 1:
            return "下行"
        else:
            return "未知"


class RoadlineDetailListSerializer(RoadlineDetailModelSerializer):
    """
    线路走向详情列表序列化器

    功能说明：
    - 专门用于线路走向详情列表显示，优化性能
    - 只包含列表展示需要的核心字段
    - 包含计算字段（上下行名称、状态等）
    - 减少数据传输量，提高响应速度（不包含大文本字段）
    - 所有字段为只读，确保数据安全
    """

    class Meta:
        model = RoadlineDetailModel
        fields = [
            # 基础信息字段
            "id",
            "roadline",
            "roadline_name",
            "up_down",
            "up_down_display",
            "start_name",
            "to_direction",
            "start_end_time",
            "start_end_time_formatted",  # 格式化的首末班时间
            
            # 线路属性字段
            "line_length",
            "area",
            
            # 日期字段
            "exec_day",
            "expiry_day",
            
            # 状态字段
            "enabled_mark",
            "delete_mark",
            
            # 计算字段
            "is_enabled",
            "is_expired",
            
            # 审计字段
            "create_datetime",
            "update_datetime",
            "creator_name",
            "modifier_name",
            "description",
        ]
        read_only_fields = fields


class RoadlineDetailMapSerializer(CustomModelSerializer):
    """
    线路走向详情地图序列化器（用于地图展示）
    
    功能说明：
    - 专门用于地图展示，包含WGS84坐标系轨迹数据
    - 包含地图展示需要的核心字段
    - 自动解析坐标字符串为坐标数组，方便前端使用
    - 优化数据传输，只包含地图展示必需的字段
    - 只返回解析后的坐标数组，不返回原始字符串，避免数据重复
    - 所有字段为只读，确保数据安全
    """
    
    # 计算字段 - 关联线路名称
    roadline_name = serializers.SerializerMethodField()
    
    # 计算字段 - 上下行显示名称
    up_down_display = serializers.SerializerMethodField()
    
    # 计算字段 - WGS84坐标解析为数组
    coordinates_wgs84 = serializers.SerializerMethodField()
    
    class Meta:
        model = RoadlineDetailModel
        fields = [
            # 基础信息字段
            "id",
            "roadline",
            "roadline_name",
            "up_down",
            "up_down_display",
            "start_name",
            "start_end_time",
            
            # 坐标字段（只返回解析后的数组，不返回原始字符串）
            "coordinates_wgs84",   # 解析后的坐标数组
            
            # 线路属性字段
            "line_length",
        ]
        read_only_fields = fields
    
    def get_roadline_name(self, obj):
        """获取关联线路名称"""
        if obj.roadline:
            return obj.roadline.line_name
        return None
    
    def get_up_down_display(self, obj):
        """上下行显示名称"""
        if obj.up_down == 0:
            return "上行"
        elif obj.up_down == 1:
            return "下行"
        else:
            return "未知"
    
    def get_coordinates_wgs84(self, obj):
        """
        解析WGS84坐标字符串为坐标数组
        
        返回格式：
        [
            {"lng": 120.123, "lat": 30.456},
            {"lng": 120.124, "lat": 30.457},
            ...
        ]
        """
        if not obj.lon_lat84:
            return []

        try:
            # 使用通用工具类解析坐标字符串，保证坐标格式处理的一致性
            points = GeoCalculator.parse_coords_string(obj.lon_lat84, separator=';')
            return [{'lng': lng, 'lat': lat} for lng, lat in points]
        except Exception as e:
            return []


class RoadlineDetailImportSerializer(CustomModelSerializer):
    """
    线路走向详情导入序列化器
    
    功能说明：
    - 专门用于Excel导入功能
    - 包含导入字段：
      * 线路名称（必填）
      * 上下行（0=上行，1=下行，必填）
      * 起点名称（可选）
      * 首末班时间（可选，如：05:30-22:00）
      * 线路长度（公里，可选）
    - 自动根据线路名称查找关联的 RoadlineModel
    - 自动去重：所有导入字段完全相同的数据将被跳过
    - 去重逻辑：线路名称+上下行+起点名称+首末班时间+线路长度都相同才认为是重复数据
    """
    
    # 使用字符串字段接收线路名称
    line_name = serializers.CharField(
        max_length=100,
        required=True,
        write_only=True,
        help_text="线路名称"
    )
    
    class Meta:
        model = RoadlineDetailModel
        fields = [
            'line_name',         # 线路名称
            'up_down',           # 上下行
            'start_name',        # 起点名称
            'start_end_time',    # 首末班时间
            'line_length',       # 线路长度（km）
        ]
        extra_kwargs = {
            'up_down': {'required': True},  # 上下行必填
            'start_name': {'required': False, 'allow_null': True, 'allow_blank': True},
            'start_end_time': {'required': False, 'allow_null': True, 'allow_blank': True},
            'line_length': {'required': False, 'allow_null': True},
        }
    
    def validate_line_name(self, value):
        """验证线路名称并查找对应的线路记录"""
        if not value or not value.strip():
            raise serializers.ValidationError("线路名称不能为空")
        
        value = value.strip()
        
        # 查找对应的线路记录
        try:
            roadline = RoadlineModel.objects.get(
                line_name=value,
                delete_mark=0,      # 只查找未删除的线路
                enabled_mark=1      # 只查找启用的线路
            )
            return roadline
        except RoadlineModel.DoesNotExist:
            raise serializers.ValidationError(
                f"线路'{value}'不存在或未启用，请先在线路主表中创建该线路"
            )
        except RoadlineModel.MultipleObjectsReturned:
            raise serializers.ValidationError(
                f"存在多个名为'{value}'的线路，请联系管理员处理数据冲突"
            )
    
    def validate_up_down(self, value):
        """验证上下行"""
        if value not in [0, 1]:
            raise serializers.ValidationError("上下行只能是0(上行)或1(下行)")
        return value
    
    def validate_start_name(self, value):
        """验证起点名称（允许为空）"""
        # 允许 None 或空字符串
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            # 如果去除空格后为空字符串，返回 None
            if not value:
                return None
            return value
        return value
    
    def validate_start_end_time(self, value):
        """
        验证并格式化首末班时间（允许为空）
        
        功能：
        - 自动将 HH:mm:ss-HH:mm:ss 格式转换为 HH:mm-HH:mm
        - 自动将 H:mm-H:mm 格式补零为 HH:mm-HH:mm
        - 验证时间格式正确性
        - 支持空值
        """
        # 允许 None 或空字符串
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            # 如果去除空格后为空字符串，返回 None
            if not value:
                return None
            
            # 检查是否包含分隔符
            if '-' not in value:
                raise serializers.ValidationError("首末班时间格式不正确，应为：HH:mm-HH:mm（如：05:30-22:00）")
            
            try:
                # 分割开始时间和结束时间
                parts = value.split('-')
                if len(parts) != 2:
                    raise serializers.ValidationError("首末班时间格式不正确，应为：HH:mm-HH:mm（如：05:30-22:00）")
                
                start_time, end_time = parts[0].strip(), parts[1].strip()
                
                # 处理每个时间部分
                def format_time_part(time_part):
                    """格式化单个时间部分：去掉秒数，补零"""
                    # 分割时、分、秒
                    time_components = time_part.split(':')
                    
                    if len(time_components) < 2:
                        raise ValueError(f"时间格式不正确：{time_part}")
                    
                    # 提取小时和分钟（忽略秒数）
                    hour = int(time_components[0])
                    minute = int(time_components[1])
                    
                    # 验证范围
                    if hour < 0 or hour > 23:
                        raise ValueError(f"小时必须在 0-23 之间：{hour}")
                    if minute < 0 or minute > 59:
                        raise ValueError(f"分钟必须在 0-59 之间：{minute}")
                    
                    # 格式化为 HH:mm
                    return f"{hour:02d}:{minute:02d}"
                
                # 格式化开始和结束时间
                formatted_start = format_time_part(start_time)
                formatted_end = format_time_part(end_time)
                
                # 返回格式化后的时间
                return f"{formatted_start}-{formatted_end}"
                
            except ValueError as e:
                raise serializers.ValidationError(f"首末班时间格式不正确：{str(e)}。正确格式：HH:mm-HH:mm（如：05:30-22:00）")
            except Exception as e:
                raise serializers.ValidationError(f"首末班时间格式验证失败：{str(e)}")
        
        return value
    
    def validate_line_length(self, value):
        """验证线路长度（单位：公里）"""
        if value is not None and value < 0:
            raise serializers.ValidationError("线路长度不能为负数")
        return value
    
    def validate(self, attrs):
        """整体验证：基本数据验证，去重检查在 create() 方法中进行"""
        return attrs
    
    def create(self, validated_data):
        """
        创建线路走向详情 - 带去重逻辑
        
        去重规则：
        检查所有导入字段（线路+上下行+起点+时间+长度）是否完全相同
        如果相同则返回现有记录（不创建新记录）
        """
        # 将 line_name（实际是 roadline 对象）重命名为 roadline
        roadline = validated_data.pop('line_name')
        
        # 提取所有导入字段用于去重检查
        up_down = validated_data.get('up_down')
        start_name = validated_data.get('start_name')
        start_end_time = validated_data.get('start_end_time')
        line_length = validated_data.get('line_length')
        
        # 构建查询条件（所有导入字段）
        from django.db import models as django_models
        
        query_filter = {
            'roadline': roadline,
            'up_down': up_down,
            'delete_mark': 0
        }
        
        # 处理可能为 None 的字段
        if start_name:
            query_filter['start_name'] = start_name
        else:
            # start_name 为空时，需要特殊处理
            existing = RoadlineDetailModel.objects.filter(
                roadline=roadline,
                up_down=up_down,
                delete_mark=0
            ).filter(
                django_models.Q(start_name__isnull=True) | django_models.Q(start_name='')
            )
            
            # 继续检查其他字段
            if start_end_time:
                existing = existing.filter(start_end_time=start_end_time)
            else:
                existing = existing.filter(
                    django_models.Q(start_end_time__isnull=True) | django_models.Q(start_end_time='')
                )
            
            if line_length is not None:
                existing = existing.filter(line_length=line_length)
            else:
                existing = existing.filter(line_length__isnull=True)
            
            if existing.exists():
                # 数据已存在，返回现有记录
                return existing.first()
        
        # 如果 start_name 有值，继续添加其他条件
        if start_name:
            if start_end_time:
                query_filter['start_end_time'] = start_end_time
            if line_length is not None:
                query_filter['line_length'] = line_length
            
            # 查询现有记录
            existing = RoadlineDetailModel.objects.filter(**query_filter)
            
            # 还需要检查 start_end_time 和 line_length 的 None 情况
            if not start_end_time:
                existing = existing.filter(
                    django_models.Q(start_end_time__isnull=True) | django_models.Q(start_end_time='')
                )
            if line_length is None:
                existing = existing.filter(line_length__isnull=True)
            
            if existing.exists():
                # 数据已存在，返回现有记录
                return existing.first()
        
        # 数据不存在，创建新记录
        validated_data['roadline'] = roadline
        
        # 从关联的线路继承日期
        if roadline:
            if roadline.exec_day:
                validated_data['exec_day'] = roadline.exec_day
            if roadline.expiry_day:
                validated_data['expiry_day'] = roadline.expiry_day
        
        # 设置默认的enabled_mark和delete_mark
        if 'enabled_mark' not in validated_data:
            validated_data['enabled_mark'] = 1
        if 'delete_mark' not in validated_data:
            validated_data['delete_mark'] = 0
        
        return RoadlineDetailModel.objects.create(**validated_data)