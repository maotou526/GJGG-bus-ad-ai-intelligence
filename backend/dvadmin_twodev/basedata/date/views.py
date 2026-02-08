'''
Description: 基础日期管理视图
Version: 1.0
Autor: 王晨
Date: 2025-10-23
LastEditors: 王晨
LastEditTime: 2025-10-23
'''
import requests
import calendar
from datetime import datetime, timedelta
from rest_framework.decorators import action
from django.db import transaction
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import SuccessResponse, ErrorResponse
from .models import BaseDateModel
from .serializers import (
    BaseDateModelSerializer,
    BaseDateModelListSerializer,
    BaseDateModelImportSerializer
)


class BaseDateModelViewSet(CustomModelViewSet):
    """
    基础日期管理视图集
    """
    queryset = BaseDateModel.objects.all()
    serializer_class = BaseDateModelSerializer
    list_serializer_class = BaseDateModelListSerializer
    import_serializer_class = BaseDateModelImportSerializer
    
    import_field_dict = {
        'date': '日期',
        'month': '当月',
        'date_type': {
            'title': '日期类型（仅填写“工作日”或“休息日”）',
            'choices': {
                'data': {
                    '工作日': 0,
                    '休息日': 1,
                }
            }
        },
        'name': '名称',
        'is_work': {
            'title': '是否上班',
            'choices': {
                'data': {
                    '否': False,
                    '是': True,
                }
            }
        },
    }
    
    filter_fields = ['id', 'date', 'month', 'date_type', 'week', 'is_work']
    search_fields = ['name']
    ordering_fields = ['date', 'create_datetime', 'update_datetime']
    ordering = ['-date']

    @action(methods=['POST'], detail=False, url_path='init_year')
    def init_year(self, request):
        """
        初始化年度数据
        
        请求方式：POST /api/BaseDateModelViewSet/init_year/
        
        请求参数：
        {
            "year": 2025  // 年份，不传则使用当前年份
        }
        
        返回结果：
        {
            "code": 2000,
            "msg": "成功初始化2025年数据，共365天"
        }
        """
        year = request.data.get('year', 0)
        if year == 0:
            year = datetime.now().year
        
        try:
            # 调用第三方API获取节假日数据
            api_url = f"https://date.appworlds.cn/year/{year}"
            print(f"正在请求API: {api_url}")
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            api_data = response.json()
            print(f"API返回数据: {api_data}")
            
            # 兼容code为字符串或数字的情况
            code = str(api_data.get('code', ''))
            msg = api_data.get('msg', '')
            
            if code != '200' or msg != 'ok':
                return ErrorResponse(msg=f"获取节假日数据失败: code={code}, msg={msg}")
            
            holiday_data = api_data.get('data', [])
            
            # 使用事务保证数据一致性
            with transaction.atomic():
                # 删除该年份的所有现有数据
                deleted_count = BaseDateModel.objects.filter(
                    date__year=year
                ).delete()[0]
                
                # 工作日列表（0=Monday到4=Friday）
                # Python weekday: 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday
                workday_list = [0, 1, 2, 3, 4]
                
                # 遍历整年的每一天
                start_date = datetime(year, 1, 1).date()
                end_date = datetime(year, 12, 31).date()
                current_date = start_date
                created_count = 0
                
                while current_date <= end_date:
                    # 创建日期实体
                    date_str = current_date.strftime('%Y-%m-%d')
                    
                    # Python的weekday: 0=Monday, 6=Sunday
                    # 转换为我们的格式: 0=Sunday, 1=Monday
                    python_weekday = current_date.weekday()
                    week = (python_weekday + 1) % 7
                    
                    # 查找API返回的节假日数据
                    holiday_info = next(
                        (item for item in holiday_data if item.get('date') == date_str),
                        None
                    )
                    
                    name = None
                    # 根据星期判断是否上班（周一至周五为工作日）
                    is_work = python_weekday in workday_list
                    
                    if holiday_info:
                        # 存储节假日或特殊日期名称
                        name = holiday_info.get('name') or None
                        is_holiday = holiday_info.get('holiday', False)
                        # 节假日不上班，补班等特殊情况根据holiday字段判断
                        is_work = not is_holiday
                    
                    # 非工作日统一标记为休息日
                    date_type = 0 if is_work else 1
                    
                    # 创建记录
                    BaseDateModel.objects.create(
                        date=current_date,
                        month=current_date.month,
                        count=calendar.monthrange(year, current_date.month)[1],
                        week=week,
                        date_type=date_type,
                        name=name,
                        is_work=is_work
                    )
                    
                    created_count += 1
                    current_date += timedelta(days=1)
                
                print(f"初始化完成: 删除{deleted_count}条，新增{created_count}条")
                return SuccessResponse(
                    msg=f"成功初始化{year}年数据，删除{deleted_count}条，新增{created_count}条"
                )
                
        except requests.Timeout:
            return ErrorResponse(msg="请求节假日API超时，请稍后重试")
        except requests.RequestException as e:
            return ErrorResponse(msg=f"请求节假日API失败: {str(e)}")
        except Exception as e:
            return ErrorResponse(msg=f"初始化失败: {str(e)}")
