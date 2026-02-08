from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.field_permission import FieldPermissionMixin
from .models import VehicleTypeModel
from .serializers import (
    VehicleTypeModelSerializer,
    VehicleTypeModelCreateSerializer,
    VehicleTypeModelUpdateSerializer,
    VehicleTypeModelListSerializer,
)


class VehicleTypeModelViewSet(CustomModelViewSet, FieldPermissionMixin):
    """
    车型管理视图集
    提供标准的增删改查能力
    """

    queryset = VehicleTypeModel.objects.all()
    serializer_class = VehicleTypeModelSerializer
    list_serializer_class = VehicleTypeModelListSerializer
    create_serializer_class = VehicleTypeModelCreateSerializer
    update_serializer_class = VehicleTypeModelUpdateSerializer

    # Excel 导入字段映射（用于前端导入组件展示）
    import_field_dict = {
        "company_name": "公司名称",
        "company_code": "公司编码",
        "vehicle_model_code": "车型编号",
        "vehicle_model_name": "车型",
        "rated_passenger_capacity": "额定载客量",
        "is_purchased_model": {
            "title": "是否已购车型",
            "choices": {
                "data": {
                    "否": 0,
                    "是": 1,
                }
            },
        },
        "enabled_mark": {
            "title": "启用状态",
            "choices": {
                "data": {
                    "禁用": 0,
                    "启用": 1,
                }
            },
        },
        "description": "描述",
    }

    filter_fields = [
        "company_code",
        "company_name",
        "vehicle_model_code",
        "vehicle_model_name",
        "rated_passenger_capacity",
        "is_purchased_model",
        "enabled_mark",
        "delete_mark",
    ]

    search_fields = [
        "company_name",
        "company_code",
        "vehicle_model_code",
        "vehicle_model_name",
    ]

    ordering_fields = [
        "id",
        "company_code",
        "company_name",
        "vehicle_model_code",
        "vehicle_model_name",
        "rated_passenger_capacity",
        "is_purchased_model",
        "enabled_mark",
        "delete_mark",
        "create_datetime",
        "update_datetime",
    ]

    ordering = ["vehicle_model_name"]
