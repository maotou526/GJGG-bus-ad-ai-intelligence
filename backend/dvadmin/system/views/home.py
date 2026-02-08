'''
Description: 首页接口，包含首页所需的数据卡片和热门线路信息
Version: 1.0
Autor: 王晨
Date: 2025-12-11
LastEditors: 王晨
LastEditTime: 2026-01-20 17:05:39
'''
# 标准库导入
from datetime import datetime, timedelta

# 第三方库导入
from django.db.models import Sum, Avg, F, Count, Q, Case, When, IntegerField
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


# 本地应用导入 - dvadmin
from dvadmin.utils.json_response import SuccessResponse, DetailResponse, ErrorResponse

# 本地应用导入 - dvadmin_twodev (按模块分组)
from dvadmin_twodev.basedata.company.models import CompanyModel
from dvadmin_twodev.basedata.roadline.models import RoadlineModel
from dvadmin_twodev.basedata.roadline_stop.models import RoadlineStopModel
from dvadmin_twodev.basedata.roadline_stop_rel.models import RoadlineStopRelModel

# 本地应用导入 - dvadmin_extensions
from dvadmin_extensions.table_sharding.utils import get_sharding_proxy_model
from dvadmin.utils.request_util import get_and_validate_date_param

# 本地应用导入 - 工具类
from dvadmin_twodev.utils.math.calculation_utils import calculate_change_percentage
