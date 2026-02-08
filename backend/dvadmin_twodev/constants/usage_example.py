# -*- coding: utf-8 -*-

"""
常量使用示例
展示如何使用系统常量和业务常量

@author: 王晨
@Created on: 2025-10-17 11:20:53
@Remark: 常量使用示例，展示新的模块结构
"""

# 方式1：导入整个常量模块
from dvadmin_twodev.constants import system_constants, business_constants

# 方式2：导入具体常量
from dvadmin_twodev.constants.system_constants import SYSTEM_TITLE, STATUS_CHOICES
from dvadmin_twodev.constants.business_constants import PROJECT_TITLE

def example_usage():
    """使用示例"""
    print("=== 常量使用示例 ===")
    
    # 使用系统常量
    print(f"系统标题: {system_constants.SYSTEM_TITLE}")
    print(f"系统版本: {system_constants.SYSTEM_VERSION}")
    print(f"状态选择: {system_constants.STATUS_CHOICES}")
    
    # 使用业务常量
    print(f"项目标题: {business_constants.PROJECT_TITLE}")
    print(f"项目副标题: {business_constants.PROJECT_SUBTITLE}")
    print(f"交通工具类型: {business_constants.VEHICLE_TYPES}")
    
    # 使用直接导入的常量
    print(f"系统标题（直接导入）: {SYSTEM_TITLE}")
    print(f"项目标题（直接导入）: {PROJECT_TITLE}")
    
    # 使用地理信息常量
    print(f"太仓市中心坐标: {business_constants.TAICANG_CENTER}")
    print(f"太仓市边界: {business_constants.TAICANG_BOUNDS}")
    
    # 使用网格配置常量
    print(f"网格大小选择: {business_constants.GRID_SIZE_OPTIONS}")
    print(f"默认网格大小: {business_constants.DEFAULT_GRID_SIZE}米")
    
    print("所有常量正常工作！")

def example_in_django_model():
    """在Django模型中使用常量的示例"""
    print("\n=== Django模型中使用常量示例 ===")
    
    # 模拟Django模型字段定义
    print("class GridModel(models.Model):")
    print("    grid_id = models.CharField(")
    print("        max_length=50,")
    print(f"        verbose_name='网格ID',")
    print("        help_text='网格唯一标识'")
    print("    )")
    print("    ")
    print("    grid_size = models.IntegerField(")
    print("        choices=business_constants.GRID_SIZE_OPTIONS,")
    print(f"        default={business_constants.DEFAULT_GRID_SIZE},")
    print("        verbose_name='网格大小',")
    print("        help_text='网格边长（米）'")
    print("    )")
    print("    ")
    print("    status = models.BooleanField(")
    print("        choices=system_constants.STATUS_CHOICES,")
    print("        default=True,")
    print("        verbose_name='状态',")
    print("        help_text='网格状态'")
    print("    )")

def example_in_django_view():
    """在Django视图中使用常量的示例"""
    print("\n=== Django视图中使用常量示例 ===")
    
    print("def get_grid_list(request):")
    print("    \"\"\"获取网格列表\"\"\"")
    print("    # 使用分页常量")
    print(f"    page_size = request.GET.get('page_size', {system_constants.DEFAULT_PAGE_SIZE})")
    print(f"    max_page_size = {system_constants.MAX_PAGE_SIZE}")
    print("    ")
    print("    # 使用状态常量")
    print("    status = request.GET.get('status')")
    print("    if status is not None:")
    print("        status = status.lower() == 'true'")
    print("    ")
    print("    # 使用业务常量")
    print(f"    grid_size_options = {business_constants.GRID_SIZE_OPTIONS}")
    print("    ")
    print("    return JsonResponse({")
    print("        'code': system_constants.STATUS_SUCCESS,")
    print("        'msg': '获取成功',")
    print("        'data': grid_list")
    print("    })")

if __name__ == "__main__":
    example_usage()
    example_in_django_model()
    example_in_django_view()
