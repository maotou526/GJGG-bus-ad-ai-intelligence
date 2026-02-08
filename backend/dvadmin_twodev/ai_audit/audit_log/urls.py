"""
AI审核记录URL配置
Description: AI审核记录的路由配置
Version: 1.0
Date: 2026-02-03
"""
from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import AIAuditLogViewSet

# 创建路由器
router = SimpleRouter()
router.register("api/AIAuditLogViewSet", AIAuditLogViewSet)

urlpatterns = [
    # 路由器自动生成的URL会包含：
    # - GET/POST /ai_audit_log/ - 列表和创建
    # - GET/PUT/PATCH/DELETE /ai_audit_log/{id}/ - 详情、更新、删除
    # - GET /ai_audit_log/statistics/ - 统计
    # - GET /ai_audit_log/by_material/{material_id}/ - 按材料查询
    # - GET /ai_audit_log/by_order/{order_id}/ - 按订单查询
    # - GET /ai_audit_log/get_all/ - 获取全量数据
]

urlpatterns += router.urls
