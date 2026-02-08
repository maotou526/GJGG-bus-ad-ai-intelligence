"""
Description: 站点关联模型序列化器
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
from .models import RoadlineStopRelModel


class RoadlineStopRelModelSerializer(CustomModelSerializer):
    """
    站点关联模型序列化器

    功能说明：
    - 提供站点关联数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 自动计算显示字段（坐标显示、距离显示、关联名称等）
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer，获得审计字段自动填充功能
    """

    # 计算字段 - 关联线路名称
    roadline_name = serializers.SerializerMethodField()

    # 计算字段 - 关联线路详情名称
    line_detail_name = serializers.SerializerMethodField()
    
    # 计算字段 - 线路方向（用于前端显示）
    up_down = serializers.SerializerMethodField()

    # 计算字段 - 是否启用
    is_enabled = serializers.SerializerMethodField()
    
    # 计算字段 - 从 dwd_roadline_stop 表关联的字段
    stop_area = serializers.SerializerMethodField()  # 环域
    stop_district = serializers.SerializerMethodField()  # 区属
    stop_roadline_name = serializers.SerializerMethodField()  # 路名
    stop_name = serializers.SerializerMethodField()  # 站名
    stop_path_direction = serializers.SerializerMethodField()  # 车向
    stop_address = serializers.SerializerMethodField()  # 站址
    stop_road_line_list = serializers.SerializerMethodField()  # 停靠线路

    class Meta:
        model = RoadlineStopRelModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            # 外键字段配置
            "roadline_id": {"required": False, "allow_null": True},
            "line_dtl_id": {"required": False, "allow_null": True},
            # 整数字段配置
            "level_id": {"required": False, "allow_null": True},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
            # 小数字段配置（高精度坐标）
            "lon02": {"required": False, "allow_null": True, "max_digits": 20, "decimal_places": 16},
            "lat02": {"required": False, "allow_null": True, "max_digits": 20, "decimal_places": 16},
            "to_next_metre": {"required": False, "allow_null": True, "max_digits": 10, "decimal_places": 2},
            "trans_lon02": {"required": False, "allow_null": True, "max_digits": 20, "decimal_places": 16},
            "trans_lat02": {"required": False, "allow_null": True, "max_digits": 20, "decimal_places": 16},
            "lon84": {"required": False, "allow_null": True, "max_digits": 20, "decimal_places": 16},
            "lat84": {"required": False, "allow_null": True, "max_digits": 20, "decimal_places": 16},
            "trans_lon84": {"required": False, "allow_null": True, "max_digits": 20, "decimal_places": 16},
            "trans_lat84": {"required": False, "allow_null": True, "max_digits": 20, "decimal_places": 16},
        }

    def get_roadline_name(self, obj):
        """获取关联线路名称"""
        if obj.roadline_id:
            try:
                return obj.roadline_id.line_name
            except (AttributeError, Exception):
                # 关联的 RoadlineModel 记录不存在，返回 None
                return None
        return None

    def get_line_detail_name(self, obj):
        """获取关联线路详情名称"""
        if obj.line_dtl_id:
            try:
                up_down_text = "上行" if obj.line_dtl_id.up_down == 0 else "下行"
                return f"{obj.line_dtl_id.start_name}({up_down_text})"
            except (AttributeError, Exception):
                # 关联的 RoadlineDetailModel 记录不存在，返回 None
                return None
        return None
    
    def get_up_down(self, obj):
        """获取线路方向"""
        if obj.line_dtl_id:
            try:
                return obj.line_dtl_id.up_down
            except (AttributeError, Exception):
                # 关联的 RoadlineDetailModel 记录不存在，返回 None
                return None
        return None

    def get_is_enabled(self, obj):
        """是否启用"""
        return obj.enabled_mark == 1 and obj.delete_mark == 0
    
    def _get_stop_info(self, obj, field_name):
        """通用方法：根据 stop_code 从 dwd_roadline_stop 表获取字段值"""
        if not obj.stop_code:
            return None
        
        try:
            from dvadmin_twodev.basedata.roadline_stop.models import RoadlineStopModel
            stop = RoadlineStopModel.objects.filter(
                stop_code=obj.stop_code,
                delete_mark=0
            ).first()
            
            if stop:
                return getattr(stop, field_name, None)
        except Exception:
            pass
        
        return None
    
    def get_stop_area(self, obj):
        """获取环域"""
        return self._get_stop_info(obj, 'area')
    
    def get_stop_district(self, obj):
        """获取区属"""
        return self._get_stop_info(obj, 'district')
    
    def get_stop_roadline_name(self, obj):
        """获取路名"""
        return self._get_stop_info(obj, 'roadline_name')
    
    def get_stop_name(self, obj):
        """获取站名"""
        return self._get_stop_info(obj, 'stop_name')
    
    def get_stop_path_direction(self, obj):
        """获取车向"""
        return self._get_stop_info(obj, 'path_direction')
    
    def get_stop_address(self, obj):
        """获取站址"""
        return self._get_stop_info(obj, 'stop_address')
    
    def get_stop_road_line_list(self, obj):
        """获取停靠线路"""
        return self._get_stop_info(obj, 'road_line_list')

    def validate_roadline_id(self, value):
        """验证关联线路"""
        if value and value.delete_mark == 1:
            raise serializers.ValidationError("关联的线路已被删除，无法使用")
        return value

    def validate_line_dtl_id(self, value):
        """验证关联线路详情"""
        if value and value.delete_mark == 1:
            raise serializers.ValidationError("关联的线路详情已被删除，无法使用")
        return value

    def validate_level_id(self, value):
        """验证站序"""
        if value is not None and value < 0:
            raise serializers.ValidationError("站序不能为负数")
        return value

    def validate_stop_code(self, value):
        """验证站点编号"""
        if value and not value.strip():
            raise serializers.ValidationError("站点编号不能为空字符串")
        return value.strip() if value else value

    def validate_to_next_metre(self, value):
        """验证距离"""
        if value is not None and value < 0:
            raise serializers.ValidationError("距离不能为负数")
        return value

    def validate(self, attrs):
        """整体验证"""
        # 验证站序在同一线路详情下的唯一性
        line_dtl_id = attrs.get("line_dtl_id") or (self.instance.line_dtl_id if self.instance else None)
        level_id = attrs.get("level_id")
        
        if line_dtl_id and level_id is not None:
            # 构建查询条件
            existing_query = RoadlineStopRelModel.objects.filter(
                line_dtl_id=line_dtl_id,
                level_id=level_id,
                delete_mark=0  # 只检查未删除的记录
            )
            
            # 如果是更新操作，排除当前实例
            if self.instance:
                existing_query = existing_query.exclude(id=self.instance.id)
            
            if existing_query.exists():
                raise serializers.ValidationError(
                    f"线路详情下的站序{level_id}已存在，不能重复"
                )

        return attrs


class RoadlineStopRelModelCreateSerializer(RoadlineStopRelModelSerializer):
    """
    站点关联创建序列化器

    功能说明：
    - 专门用于创建新的站点关联时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    - 支持通过 up_down 自动查找 line_dtl_id
    """
    
    # 添加 up_down 字段用于接收前端传来的方向
    up_down = serializers.IntegerField(write_only=True, required=True, help_text="线路方向：0-上行，1-下行")

    class Meta(RoadlineStopRelModelSerializer.Meta):
        # 创建时必填字段
        extra_kwargs = {
            **RoadlineStopRelModelSerializer.Meta.extra_kwargs,
            "roadline_id": {"required": True},
            "line_dtl_id": {"required": False},  # 改为非必填，由后端自动查找
            "level_id": {"required": True},
            "stop_code": {"required": True},
        }

    def create(self, validated_data):
        """创建站点关联"""
        from dvadmin_twodev.basedata.roadline_detail.models import RoadlineDetailModel
        
        # 获取并移除 up_down
        up_down = validated_data.pop('up_down')
        roadline_id = validated_data.get('roadline_id')
        
        # 根据 roadline_id 和 up_down 查找 line_dtl_id
        try:
            line_detail = RoadlineDetailModel.objects.get(
                roadline=roadline_id,
                up_down=up_down,
                delete_mark=0,
                enabled_mark=1
            )
            validated_data['line_dtl_id'] = line_detail
        except RoadlineDetailModel.DoesNotExist:
            raise serializers.ValidationError(
                f"未找到线路ID={roadline_id.id}的{'上行' if up_down == 0 else '下行'}记录，请先创建线路详情"
            )
        except RoadlineDetailModel.MultipleObjectsReturned:
            raise serializers.ValidationError(
                f"线路ID={roadline_id.id}的{'上行' if up_down == 0 else '下行'}记录存在多条，数据异常"
            )
        
        # 调用父类的create方法
        return super().create(validated_data)


class RoadlineStopRelModelUpdateSerializer(RoadlineStopRelModelSerializer):
    """
    站点关联更新序列化器

    功能说明：
    - 专门用于更新现有站点关联时的数据验证
    - 继承基础序列化器的所有功能
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(RoadlineStopRelModelSerializer.Meta):
        # 更新时不可修改的字段
        read_only_fields = [
            "id",
            "roadline_id",      # 不允许更换所属线路
            "line_dtl_id",      # 不允许更换所属线路详情
            "create_datetime",
            "update_datetime"
        ]


class RoadlineStopRelSimpleSerializer(CustomModelSerializer):
    """
    站点关联简单序列化器
    只返回核心字段：id、线路名称、站点名称、站序
    """
    roadline_name = serializers.SerializerMethodField()

    roadline_updown = serializers.SerializerMethodField()

    class Meta:
        model = RoadlineStopRelModel
        fields = [
            "id",
            "roadline_id",
            "line_dtl_id",
            "roadline_name",
            "roadline_updown",
            "stop_id",
            "stop_code",
            "level_name",
            "level_id",
        ]
        read_only_fields = fields

    def get_roadline_name(self, obj):
        """获取关联线路名称"""
        if obj.roadline_id:
            try:
                return obj.roadline_id.line_name
            except (AttributeError, Exception):
                # 关联的 RoadlineModel 记录不存在，返回 None
                return None
        return None
    
    def get_roadline_updown(self, obj):
        """获取关联线路上下行"""
        if obj.line_dtl_id:
            try:
                return obj.line_dtl_id.up_down
            except (AttributeError, Exception):
                # 关联的 RoadlineDetailModel 记录不存在，返回 None
                return None
        return None


class RoadlineStopRelModelListSerializer(RoadlineStopRelModelSerializer):
    """
    站点关联列表序列化器

    功能说明：
    - 专门用于站点关联列表显示，优化性能
    - 只包含列表展示需要的核心字段
    - 包含计算字段（关联名称、坐标显示等）
    - 减少数据传输量，提高响应速度
    - 所有字段为只读，确保数据安全
    """
    
    def _get_stop_info(self, obj, field_name):
        """重写父类方法，优先使用 context 中的缓存"""
        if not obj.stop_code:
            return None
        
        # 尝试从 context 中获取缓存
        stop_cache = None
        if hasattr(self, 'context') and self.context:
            stop_cache = self.context.get('stop_cache', {})
        
        # 如果缓存中有数据，使用缓存
        if stop_cache and obj.stop_code in stop_cache:
            stop = stop_cache[obj.stop_code]
            return getattr(stop, field_name, None)
        
        # 否则使用父类方法（单次查询）
        return super()._get_stop_info(obj, field_name)

    class Meta:
        model = RoadlineStopRelModel
        fields = [
            # 基础信息字段
            "id",
            "roadline_id",
            "roadline_name",
            "line_dtl_id",
            "line_detail_name",
            "up_down",  # 线路方向
            "level_id",
            "level_name",
            "stop_code",
            "zone",
            
            # 从 dwd_roadline_stop 表关联的字段
            "stop_area",  # 环域
            "stop_district",  # 区属
            "stop_roadline_name",  # 路名
            "stop_name",  # 站名
            "stop_path_direction",  # 车向
            "stop_address",  # 站址
            "stop_road_line_list",  # 停靠线路
            
            # 坐标字段
            "lon02",
            "lat02",
            "lon84",
            "lat84",
            
            # 距离字段
            "to_next_metre",
            
            # 网格转换坐标字段
            "trans_lon02",
            "trans_lat02",
            "trans_lon84",
            "trans_lat84",
            
            # 状态字段
            "enabled_mark",
            "delete_mark",
            
            # 计算字段
            "is_enabled",
            
            # 审计字段
            "create_datetime",
            "update_datetime",
            "creator_name",
            "modifier_name",
            "description",
        ]
        read_only_fields = fields


class RoadlineStopRelImportSerializer(CustomModelSerializer):
    """
    站点关联导入序列化器
    
    功能说明：
    - 专门用于Excel导入功能
    - 包含导入字段：线路名称、站点名称、站序、线路方向（上下行）、经度、纬度
    - 自动根据线路名称和上下行查找关联的 RoadlineModel 和 RoadlineDetailModel
    - 自动去重：所有导入字段完全相同的数据将被跳过
    - 去重逻辑：线路名称+上下行+站点名称+站序+经纬度都相同才认为是重复数据
    - 经纬度为可选字段，使用GCJ02坐标系（火星坐标系，高德地图坐标系）
    """
    
    # 使用字符串字段接收线路名称
    line_name = serializers.CharField(
        max_length=100,
        required=True,
        write_only=True,
        help_text="线路名称"
    )
    
    # 接收线路方向（上下行）
    up_down = serializers.IntegerField(
        required=True,
        write_only=True,
        help_text="线路方向：0-上行，1-下行"
    )
    
    class Meta:
        model = RoadlineStopRelModel
        fields = ['line_name', 'level_name', 'level_id', 'up_down', 'lon02', 'lat02']
        extra_kwargs = {
            'level_name': {'required': True},
            'level_id': {'required': True},
            'lon02': {'required': False, 'allow_null': True},
            'lat02': {'required': False, 'allow_null': True},
        }
    
    def validate_line_name(self, value):
        """验证线路名称"""
        if not value or not value.strip():
            raise serializers.ValidationError("线路名称不能为空")
        return value.strip()
    
    def validate_level_name(self, value):
        """验证站点名称"""
        if not value or not value.strip():
            raise serializers.ValidationError("站点名称不能为空")
        return value.strip()
    
    def validate_level_id(self, value):
        """验证站序"""
        if value is None:
            raise serializers.ValidationError("站序不能为空")
        if value < 0:
            raise serializers.ValidationError("站序不能为负数")
        return value
    
    def validate_up_down(self, value):
        """验证上下行"""
        if value not in [0, 1]:
            raise serializers.ValidationError("线路方向只能是0(上行)或1(下行)")
        return value
    
    def validate_lon02(self, value):
        """验证经度（GCJ02坐标系）"""
        if value is None:
            return value
        # 中国经度范围大约在 73°-135°
        if not (73 <= float(value) <= 135):
            raise serializers.ValidationError("经度值超出有效范围（73-135°）")
        return value
    
    def validate_lat02(self, value):
        """验证纬度（GCJ02坐标系）"""
        if value is None:
            return value
        # 中国纬度范围大约在 3°-54°
        if not (3 <= float(value) <= 54):
            raise serializers.ValidationError("纬度值超出有效范围（3-54°）")
        return value
    
    def validate(self, attrs):
        """整体验证：查找关联记录，去重检查在 create() 方法中进行"""
        from dvadmin_twodev.basedata.roadline.models import RoadlineModel
        from dvadmin_twodev.basedata.roadline_detail.models import RoadlineDetailModel
        
        line_name = attrs.get('line_name')
        up_down = attrs.get('up_down')
        
        # 1. 查找线路主表记录
        try:
            roadline = RoadlineModel.objects.get(
                line_name=line_name,
                delete_mark=0
            )
            attrs['roadline'] = roadline
        except RoadlineModel.DoesNotExist:
            raise serializers.ValidationError(f"线路'{line_name}'不存在，请先在线路主表中创建该线路")
        except RoadlineModel.MultipleObjectsReturned:
            raise serializers.ValidationError(f"存在多个名为'{line_name}'的线路，无法确定导入哪个")
        
        # 2. 查找线路详情记录
        try:
            line_detail = RoadlineDetailModel.objects.get(
                roadline=roadline,
                up_down=up_down,
                delete_mark=0
            )
            attrs['line_detail'] = line_detail
        except RoadlineDetailModel.DoesNotExist:
            up_down_text = "上行" if up_down == 0 else "下行"
            raise serializers.ValidationError(
                f"线路'{line_name}'的{up_down_text}记录不存在，请先在线路详情表中创建"
            )
        except RoadlineDetailModel.MultipleObjectsReturned:
            up_down_text = "上行" if up_down == 0 else "下行"
            raise serializers.ValidationError(
                f"线路'{line_name}'的{up_down_text}记录存在多条，数据异常"
            )
        
        return attrs
    
    def create(self, validated_data):
        """
        创建站点关联 - 带去重逻辑
        
        去重规则：
        检查所有导入字段（线路详情+站点名称+站序+经纬度）是否完全相同
        如果相同则返回现有记录（不创建新记录）
        """
        # 移除辅助字段
        line_name = validated_data.pop('line_name')
        up_down = validated_data.pop('up_down')
        roadline = validated_data.pop('roadline')
        line_detail = validated_data.pop('line_detail')
        
        # 提取导入字段用于去重检查
        level_name = validated_data.get('level_name')
        level_id = validated_data.get('level_id')
        lon02 = validated_data.get('lon02')
        lat02 = validated_data.get('lat02')
        
        # 去重检查：查询是否存在完全相同的记录
        # 构建查询条件
        query_filter = {
            'line_dtl_id': line_detail,
            'level_name': level_name,
            'level_id': level_id,
            'delete_mark': 0
        }
        
        # 如果经纬度有值，则加入去重条件
        if lon02 is not None:
            query_filter['lon02'] = lon02
        if lat02 is not None:
            query_filter['lat02'] = lat02
        
        existing = RoadlineStopRelModel.objects.filter(**query_filter).first()
        
        if existing:
            # 数据已存在，返回现有记录（不创建新记录）
            return existing
        
        # 数据不存在，创建新记录
        # 设置外键字段
        validated_data['roadline_id'] = roadline
        validated_data['line_dtl_id'] = line_detail
        
        return RoadlineStopRelModel.objects.create(**validated_data)
