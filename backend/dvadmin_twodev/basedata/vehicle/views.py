'''
Description: 车辆视图
Version: 1.0
Autor: 王晨
Date: 2025-10-18
LastEditors: 王晨
LastEditTime: 2026-01-20 17:06:44
'''
from rest_framework.decorators import action
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from .models import VehicleModel
from .serializers import (
    VehicleModelSerializer,
    VehicleModelCreateSerializer,
    VehicleModelUpdateSerializer,
    VehicleModelListSerializer,
    VehicleModelImportSerializer
)
from dvadmin_twodev.basedata.vehicle_type.models import VehicleTypeModel
from django.db.models import Q
import random
from datetime import datetime, timedelta
from decimal import Decimal


class VehicleModelViewSet(CustomModelViewSet):
    """
    车辆管理视图集
    
    功能说明:
    - 提供车辆的增删改查功能(使用DRF标准接口)
    - 自动处理分页、过滤、排序等功能
    - 支持批量删除和启用/禁用操作
    
    标准DRF接口:
    - GET /api/VehicleModelViewSet/ - 获取车辆列表
    - POST /api/VehicleModelViewSet/ - 创建车辆
    - PUT /api/VehicleModelViewSet/{id}/ - 更新车辆
    - DELETE /api/VehicleModelViewSet/{id}/ - 删除车辆
    
    自定义接口:
    - POST /api/VehicleModelViewSet/enable_vehicle/ - 启用/禁用车辆
    """
    # 查询集（使用select_related优化外键查询）
    queryset = VehicleModel.objects.select_related('roadline').all()
    
    # 默认序列化器(用于查询详情)
    serializer_class = VehicleModelSerializer
    
    # 列表序列化器(用于列表展示)
    list_serializer_class = VehicleModelListSerializer
    
    # 创建序列化器
    create_serializer_class = VehicleModelCreateSerializer
    
    # 更新序列化器
    update_serializer_class = VehicleModelUpdateSerializer
    
    # 导入序列化器
    import_serializer_class = VehicleModelImportSerializer
    
    # 导出序列化器
    export_serializer_class = VehicleModelListSerializer
    
    # 导出字段配置
    export_field_label = {
        'id': 'ID',
        'vehicle_plate': '牌照号',
        'vehicle_no': '自编号',
        'company_name': '公司名称',
        'branch': '车队',
        'roadline': '所属线路ID',
        'vehicle_brand': '车辆品牌',
        'vehicle_type': '车辆型号',
        'bus_type': '客车类型',
        'fuel_type': '燃料种类',
        'emission_class': '排放等级',
        'vehicle_size': '车辆长度（米）',
        'size': '车辆尺寸',
        'passenger_number': '额定载客人数',
        'seats_number': '车辆座位数',
        'vehicle_door': '车辆门数',
        'rated_oil': '额定耗油（升/百公里）',
        'engine_position': '发动机位置',
        'engine_type': '发动机型号',
        'buy_date': '购买日期',
        'scrap_years': '报废年限（年）',
        'retirement_time': '报废年限（年）',
        'plan_scrap_year': '计划报废年份',
        'actual_scrap_year': '实际报废日期',
        'is_new_cz': '是否新车载',
        'has_wheelchair': '是否无障碍',
        'is_share': '是否共营车辆',
        'have_air_condition': '有无空调',
        'have_back_camera': '有无后置摄像头',
        'is_high_grade': '高等级车',
        'is_new_energy': '是否新能源车',
        'is_baofei': '是否报废',
        'new_flag': '是否是新车',
        'show_charge': '是否显示充电状态',
        'have_system': '智能化终端',
        'pos_number': 'POS机编号',
        'mobile_number': '车载手机号',
        'sn': '序列号',
        'manufacturer': '车载GPS供应商',
        'vehicle_condition': '车辆状态',
        'realtime_condition': '实时状况',
        'vehicle_status': '状态',
        'electronic_lupai': '电子路牌',
        'voice_card_enabled': '是否开通通话功能',
        'video_enable': '是否开通视频功能',
        'has_video': '是否有视频功能',
        'is_modified': '是否改装过',
        'enabled_mark': '启用状态',
        'delete_mark': '删除状态',
        'description': '描述',
        'create_datetime': '创建时间',
        'update_datetime': '更新时间',
    }
    
    # 导入字段配置（与列表展示字段保持一致）
    import_field_dict = {
        'vehicle_plate': '牌照号',
        'vehicle_no': '自编号',
        'company_name': '公司名称',
        'branch': '车队',
        'roadline': '所属线路ID',
        'vehicle_brand': '车辆品牌',
        'vehicle_type': '车辆型号',
        'bus_type': '客车类型',
        'fuel_type': '燃料种类',
        'emission_class': '排放等级',
        'vehicle_size': '车辆长度（米）',
        'size': '车辆尺寸',
        'passenger_number': '额定载客人数',
        'seats_number': '车辆座位数',
        'vehicle_door': '车辆门数',
        'rated_oil': '额定耗油（升/百公里）',
        'engine_position': '发动机位置',
        'engine_type': '发动机型号',
        'buy_date': '购买日期',
        'scrap_years': '报废年限（年）',
        'retirement_time': '报废年限（年）',
        'plan_scrap_year': '计划报废年份',
        'actual_scrap_year': '实际报废日期',
        'is_new_cz': {
            'title': '是否新车载',
            'choices': {
                'data': {
                    '否': 0,
                    '是': 1,
                }
            }
        },
        'has_wheelchair': {
            'title': '是否无障碍',
            'choices': {
                'data': {
                    '否': 0,
                    '是': 1,
                }
            }
        },
        'is_share': {
            'title': '是否共营车辆',
            'choices': {
                'data': {
                    '否': 0,
                    '是': 1,
                }
            }
        },
        'have_air_condition': {
            'title': '有无空调',
            'choices': {
                'data': {
                    '无': 0,
                    '有': 1,
                }
            }
        },
        'have_back_camera': {
            'title': '有无后置摄像头',
            'choices': {
                'data': {
                    '无': 0,
                    '有': 1,
                }
            }
        },
        'is_high_grade': {
            'title': '高等级车',
            'choices': {
                'data': {
                    '否': 0,
                    '是': 1,
                }
            }
        },
        'is_new_energy': {
            'title': '是否新能源车',
            'choices': {
                'data': {
                    '否': 0,
                    '是': 1,
                }
            }
        },
        'is_baofei': {
            'title': '是否报废',
            'choices': {
                'data': {
                    '否': 0,
                    '是': 1,
                }
            }
        },
        'new_flag': {
            'title': '是否是新车',
            'choices': {
                'data': {
                    '否': 0,
                    '是': 1,
                }
            }
        },
        'show_charge': {
            'title': '是否显示充电状态',
            'choices': {
                'data': {
                    '否': 0,
                    '是': 1,
                }
            }
        },
        'have_system': '智能化终端',
        'pos_number': 'POS机编号',
        'mobile_number': '车载手机号',
        'sn': '序列号',
        'manufacturer': '车载GPS供应商',
        'vehicle_condition': '车辆状态',
        'realtime_condition': '实时状况',
        'vehicle_status': '状态',
        'electronic_lupai': '电子路牌',
        'voice_card_enabled': {
            'title': '是否开通通话功能',
            'choices': {
                'data': {
                    '否': 0,
                    '是': 1,
                }
            }
        },
        'video_enable': {
            'title': '是否开通视频功能',
            'choices': {
                'data': {
                    '否': 0,
                    '是': 1,
                }
            }
        },
        'has_video': {
            'title': '是否有视频功能',
            'choices': {
                'data': {
                    '否': 0,
                    '是': 1,
                }
            }
        },
        'is_modified': {
            'title': '是否改装过',
            'choices': {
                'data': {
                    '否': 0,
                    '是': 1,
                }
            }
        },
        'enabled_mark': {
            'title': '启用状态',
            'choices': {
                'data': {
                    '禁用': 0,
                    '启用': 1,
                }
            }
        },
        'description': '描述',
    }
    
    # 过滤字段(支持精确查询)
    filter_fields = [
        'id', 'company_name', 'branch', 'roadline',
        'vehicle_plate', 'vehicle_no', 'vehicle_brand',
        'vehicle_type', 'bus_type', 'fuel_type',
        'is_new_energy', 'is_baofei', 'new_flag',
        'enabled_mark', 'delete_mark'
    ]
    
    # filterset_fields 用于 DRF 的过滤后端（确保外键字段可以正常过滤）
    filterset_fields = [
        'id', 'company_name', 'branch', 'roadline',
        'vehicle_plate', 'vehicle_no', 'vehicle_brand',
        'vehicle_type', 'bus_type', 'fuel_type',
        'is_new_energy', 'is_baofei', 'new_flag',
        'enabled_mark', 'delete_mark'
    ]
    
    # 搜索字段(支持模糊查询)
    search_fields = ['vehicle_plate', 'vehicle_no', 'company_name', 'branch', 'vehicle_brand', 'vehicle_type']
    
    # 排序字段
    ordering_fields = ['company_name', 'vehicle_no', 'vehicle_plate', 'create_datetime', 'update_datetime', 'buy_date']
    
    # 默认排序（按公司名称和车辆编号排序）
    ordering = ['company_name', 'vehicle_no']