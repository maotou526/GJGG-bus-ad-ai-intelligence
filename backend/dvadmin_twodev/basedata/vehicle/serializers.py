"""
Description: 车辆序列化器
Version: 1.0
Autor: 王晨
Date: 2025-10-18
LastEditors: 王晨
LastEditTime: 2025-10-18
"""

from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import VehicleModel


class VehicleModelSerializer(CustomModelSerializer):
    """
    车辆序列化器

    功能说明:
    - 提供车辆数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer,获得审计字段自动填充功能
    """

    # 计算字段 - 是否启用
    is_enabled = serializers.SerializerMethodField()
    
    # 计算字段 - 线路名称（从外键关联获取）
    roadline_name = serializers.SerializerMethodField()

    class Meta:
        model = VehicleModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            # 外键字段类型配置
            "roadline": {"required": False, "allow_null": True},
            # 整数字段类型配置
            "is_new_cz": {"required": False, "allow_null": True},
            "has_wheelchair": {"required": False, "allow_null": True},
            "is_share": {"required": False, "allow_null": True},
            "scrap_years": {"required": False, "allow_null": True},
            "plan_scrap_year": {"required": False, "allow_null": True},
            "passenger_number": {"required": False, "allow_null": True},
            "seats_number": {"required": False, "allow_null": True},
            "have_air_condition": {"required": False, "allow_null": True},
            "have_back_camera": {"required": False, "allow_null": True},
            "is_high_grade": {"required": False, "allow_null": True},
            "retirement_time": {"required": False, "allow_null": True},
            "vehicle_door": {"required": False, "allow_null": True},
            "is_baofei": {"required": False, "allow_null": True},
            "voice_card_enabled": {"required": False, "allow_null": True},
            "video_enable": {"required": False, "allow_null": True},
            "has_video": {"required": False, "allow_null": True},
            "is_modified": {"required": False, "allow_null": True},
            "is_new_energy": {"required": False, "allow_null": True},
            "new_flag": {"required": False, "allow_null": True},
            "show_charge": {"required": False, "allow_null": True},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
            # 小数字段类型配置
            "vehicle_size": {"required": False, "allow_null": True, "max_digits": 10, "decimal_places": 2},
            "rated_oil": {"required": False, "allow_null": True, "max_digits": 10, "decimal_places": 2},
            # 日期字段类型配置
            "buy_date": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "actual_scrap_year": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
        }

    def get_is_enabled(self, obj):
        """是否启用"""
        return obj.enabled_mark == 1 and obj.delete_mark == 0
    
    def get_roadline_name(self, obj):
        """获取线路名称"""
        if obj.roadline:
            return obj.roadline.line_name
        return None

    def validate_vehicle_plate(self, value):
        """验证牌照号"""
        if value and not value.strip():
            raise serializers.ValidationError("牌照号不能为空")
        return value.strip() if value else value

    def validate_vehicle_size(self, value):
        """验证车辆长度"""
        if value is not None and value < 0:
            raise serializers.ValidationError("车辆长度不能为负数")
        return value

    def validate_rated_oil(self, value):
        """验证额定耗油"""
        if value is not None and value < 0:
            raise serializers.ValidationError("额定耗油不能为负数")
        return value

    def validate_passenger_number(self, value):
        """验证额定载客人数"""
        if value is not None and value < 0:
            raise serializers.ValidationError("额定载客人数不能为负数")
        return value

    def validate_seats_number(self, value):
        """验证车辆座位数"""
        if value is not None and value < 0:
            raise serializers.ValidationError("车辆座位数不能为负数")
        return value

    def validate(self, attrs):
        """整体验证"""
        # 验证购买日期和报废日期
        buy_date = attrs.get("buy_date")
        actual_scrap_year = attrs.get("actual_scrap_year")

        if buy_date and actual_scrap_year and buy_date > actual_scrap_year:
            raise serializers.ValidationError("购买日期不能晚于报废日期")

        return attrs


class VehicleModelCreateSerializer(VehicleModelSerializer):
    """
    车辆创建序列化器

    功能说明:
    - 专门用于创建新车辆时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(VehicleModelSerializer.Meta):
        # 创建时必填字段
        extra_kwargs = {
            "vehicle_plate": {"required": True},
            "company_name": {"required": True},
        }

    def create(self, validated_data):
        """创建车辆时自动生成GUID"""
        return super().create(validated_data)


class VehicleModelUpdateSerializer(VehicleModelSerializer):
    """
    车辆更新序列化器

    功能说明:
    - 专门用于更新现有车辆时的数据验证
    - 继承基础序列化器的所有功能
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(VehicleModelSerializer.Meta):
        # 更新时主键不可修改
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class VehicleModelListSerializer(VehicleModelSerializer):
    """
    车辆列表序列化器

    功能说明:
    - 专门用于车辆列表显示,优化性能
    - 只包含列表展示需要的核心字段
    - 减少数据传输量,提高响应速度
    - 所有字段为只读,确保数据安全
    """

    class Meta:
        model = VehicleModel
        fields = [
            # 基础信息字段
            "id",
            "vehicle_plate",
            "vehicle_no",
            "company_name",
            "branch",
            "park_name",
            "roadline",
            "roadline_name",
            
            # 车辆基本信息
            "vehicle_brand",
            "vehicle_type",
            "car_type",
            "bus_type",
            "fuel_type",
            "emission_class",
            
            # 车辆参数
            "vehicle_size",
            "passenger_number",
            "seats_number",
            "vehicle_door",
            
            # 日期信息
            "buy_date",
            "scrap_years",
            "plan_scrap_year",
            "actual_scrap_year",
            
            # 特性标记
            "is_new_cz",
            "has_wheelchair",
            "is_share",
            "have_air_condition",
            "have_back_camera",
            "is_high_grade",
            "is_new_energy",
            "is_baofei",
            "new_flag",
            
            # 设备信息
            "have_system",
            "pos_number",
            "mobile_number",
            "sn",
            "manufacturer",
            
            # 状态字段
            "vehicle_condition",
            "realtime_condition",
            "vehicle_status",
            "enabled_mark",
            "delete_mark",
            
            # 计算显示字段
            "is_enabled",
            
            # 审计字段
            "create_datetime",
            "update_datetime",
            "creator_name",
            "modifier_name",
            "description",
        ]
        read_only_fields = fields


class VehicleModelImportSerializer(CustomModelSerializer):
    """
    车辆导入序列化器
    
    功能说明：
    - 专门用于Excel导入功能
    - 包含导入字段：牌照号、自编号、公司名称、车队、所属线路、车辆品牌、车辆型号等
    - 自动去重：所有导入字段完全相同的数据将被跳过
    - 去重逻辑：只导入字段都相同才认为是重复数据
    """
    
    class Meta:
        model = VehicleModel
        fields = [
            'id',                 # 主键ID（用于批量更新模板）
            'vehicle_plate',      # 牌照号（必填）
            'vehicle_no',         # 自编号
            'company_name',       # 公司名称（必填）
            'branch',            # 车队
            'roadline',          # 所属线路（外键ID）
            'vehicle_brand',     # 车辆品牌
            'vehicle_type',      # 车辆型号
            'bus_type',          # 客车类型
            'fuel_type',         # 燃料种类
            'emission_class',    # 排放等级
            'vehicle_size',      # 车辆长度（米）
            'size',              # 车辆尺寸
            'passenger_number',  # 额定载客人数
            'seats_number',      # 车辆座位数
            'vehicle_door',      # 车辆门数
            'rated_oil',         # 额定耗油（升/百公里）
            'engine_position',   # 发动机位置
            'engine_type',       # 发动机型号
            'buy_date',          # 购买日期
            'scrap_years',       # 报废年限（年）
            'retirement_time',   # 报废年限（年）
            'plan_scrap_year',   # 计划报废年份
            'actual_scrap_year', # 实际报废日期
            'is_new_cz',         # 是否新车载（0否，1是）
            'has_wheelchair',    # 是否无障碍（0否，1是）
            'is_share',          # 是否共营车辆（0否，1是）
            'have_air_condition', # 有无空调（0无，1有）
            'have_back_camera',  # 有无后置摄像头（0无，1有）
            'is_high_grade',     # 高等级车（0否，1是）
            'is_new_energy',     # 是否新能源车（0否，1是）
            'is_baofei',         # 是否报废（0否，1是）
            'new_flag',          # 是否是新车（0否，1是）
            'show_charge',       # 是否显示充电状态（0否，1是）
            'have_system',       # 智能化终端
            'pos_number',        # POS机编号
            'mobile_number',     # 车载手机号
            'sn',                # 序列号
            'manufacturer',      # 车载GPS供应商
            'vehicle_condition', # 车辆状态
            'realtime_condition', # 实时状况
            'vehicle_status',    # 状态
            'electronic_lupai',  # 电子路牌
            'voice_card_enabled', # 是否开通通话功能（0否，1是）
            'video_enable',      # 是否开通视频功能（0否，1是）
            'has_video',         # 是否有视频功能（0否，1是）
            'is_modified',       # 是否改装过（0否，1是）
            'enabled_mark',      # 启用状态（0禁用，1启用）
            'description',      # 描述
        ]
        extra_kwargs = {
            'vehicle_plate': {'required': True},  # 牌照号必填
            'company_name': {'required': True},   # 公司名称必填
            'vehicle_no': {'required': False, 'allow_null': True, 'allow_blank': True},
            'branch': {'required': False, 'allow_null': True, 'allow_blank': True},
            'roadline': {'required': False, 'allow_null': True},
            'vehicle_brand': {'required': False, 'allow_null': True, 'allow_blank': True},
            'vehicle_type': {'required': False, 'allow_null': True, 'allow_blank': True},
            'bus_type': {'required': False, 'allow_null': True, 'allow_blank': True},
            'fuel_type': {'required': False, 'allow_null': True, 'allow_blank': True},
            'emission_class': {'required': False, 'allow_null': True, 'allow_blank': True},
            'vehicle_size': {'required': False, 'allow_null': True},
            'size': {'required': False, 'allow_null': True, 'allow_blank': True},
            'passenger_number': {'required': False, 'allow_null': True},
            'seats_number': {'required': False, 'allow_null': True},
            'vehicle_door': {'required': False, 'allow_null': True},
            'rated_oil': {'required': False, 'allow_null': True},
            'engine_position': {'required': False, 'allow_null': True, 'allow_blank': True},
            'engine_type': {'required': False, 'allow_null': True, 'allow_blank': True},
            'buy_date': {'required': False, 'allow_null': True, 'format': '%Y-%m-%d', 'input_formats': ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']},
            'scrap_years': {'required': False, 'allow_null': True},
            'retirement_time': {'required': False, 'allow_null': True},
            'plan_scrap_year': {'required': False, 'allow_null': True},
            'actual_scrap_year': {'required': False, 'allow_null': True, 'format': '%Y-%m-%d', 'input_formats': ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']},
            'is_new_cz': {'required': False, 'allow_null': True},
            'has_wheelchair': {'required': False, 'allow_null': True},
            'is_share': {'required': False, 'allow_null': True},
            'have_air_condition': {'required': False, 'allow_null': True},
            'have_back_camera': {'required': False, 'allow_null': True},
            'is_high_grade': {'required': False, 'allow_null': True},
            'is_new_energy': {'required': False, 'allow_null': True},
            'is_baofei': {'required': False, 'allow_null': True},
            'new_flag': {'required': False, 'allow_null': True},
            'show_charge': {'required': False, 'allow_null': True},
            'have_system': {'required': False, 'allow_null': True, 'allow_blank': True},
            'pos_number': {'required': False, 'allow_null': True, 'allow_blank': True},
            'mobile_number': {'required': False, 'allow_null': True, 'allow_blank': True},
            'sn': {'required': False, 'allow_null': True, 'allow_blank': True},
            'manufacturer': {'required': False, 'allow_null': True, 'allow_blank': True},
            'vehicle_condition': {'required': False, 'allow_null': True, 'allow_blank': True},
            'realtime_condition': {'required': False, 'allow_null': True, 'allow_blank': True},
            'vehicle_status': {'required': False, 'allow_null': True, 'allow_blank': True},
            'electronic_lupai': {'required': False, 'allow_null': True, 'allow_blank': True},
            'voice_card_enabled': {'required': False, 'allow_null': True},
            'video_enable': {'required': False, 'allow_null': True},
            'has_video': {'required': False, 'allow_null': True},
            'is_modified': {'required': False, 'allow_null': True},
            'enabled_mark': {'required': False, 'allow_null': True},
            'description': {'required': False, 'allow_null': True, 'allow_blank': True},
        }
    
    def validate_vehicle_plate(self, value):
        """验证牌照号（必填）"""
        if not value or not value.strip():
            raise serializers.ValidationError("牌照号不能为空")
        return value.strip()
    
    def validate_company_name(self, value):
        """验证公司名称（必填）"""
        if not value or not value.strip():
            raise serializers.ValidationError("公司名称不能为空")
        return value.strip()
    
    def validate_vehicle_size(self, value):
        """验证车辆长度"""
        if value is not None and value < 0:
            raise serializers.ValidationError("车辆长度不能为负数")
        return value
    
    def validate_rated_oil(self, value):
        """验证额定耗油"""
        if value is not None and value < 0:
            raise serializers.ValidationError("额定耗油不能为负数")
        return value
    
    def validate_passenger_number(self, value):
        """验证额定载客人数"""
        if value is not None and value < 0:
            raise serializers.ValidationError("额定载客人数不能为负数")
        return value
    
    def validate_seats_number(self, value):
        """验证车辆座位数"""
        if value is not None and value < 0:
            raise serializers.ValidationError("车辆座位数不能为负数")
        return value
    
    def validate_enabled_mark(self, value):
        """验证启用状态"""
        if value is not None and value not in [0, 1]:
            raise serializers.ValidationError("启用状态只能是0(禁用)或1(启用)")
        return value
    
    def create(self, validated_data):
        """
        创建新车辆 - 带去重逻辑
        
        去重规则：
        检查所有导入字段是否完全相同，如果相同则返回现有记录（不创建新记录）
        """
        # 提取关键字段用于去重检查（牌照号+公司名称作为唯一标识）
        vehicle_plate = validated_data.get('vehicle_plate')
        company_name = validated_data.get('company_name')
        
        # 构建查询条件
        query_filter = {
            'vehicle_plate': vehicle_plate,
            'company_name': company_name,
            'delete_mark': 0  # 只检查未删除的记录
        }
        
        # 去重检查：查询是否存在完全相同的记录
        existing = VehicleModel.objects.filter(**query_filter).first()
        
        if existing:
            # 数据已存在，返回现有记录（不创建新记录）
            return existing
        
        # 数据不存在，创建新记录
        # 如果没有指定启用状态，默认为启用
        if 'enabled_mark' not in validated_data:
            validated_data['enabled_mark'] = 1
        
        # 如果没有指定delete_mark，默认为0（未删除）
        if 'delete_mark' not in validated_data:
            validated_data['delete_mark'] = 0
        
        return VehicleModel.objects.create(**validated_data)
