"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from application import dispatch
from application import settings
from application.sse_views import sse_view
from dvadmin.system.views.dictionary import InitDictionaryViewSet
from dvadmin.system.views.login import (
    LoginView,
    CaptchaView,
    ApiLogin,
    LogoutView,
    LoginTokenView
)
from dvadmin.system.views.system_config import InitSettingsViewSet
from dvadmin.utils.swagger import CustomOpenAPISchemaGenerator

# =========== 初始化系统配置 =================
dispatch.init_system_config()
dispatch.init_dictionary()
# =========== 初始化系统配置 =================

# Swagger 配置 - 根据 DEBUG 环境控制
if settings.DEBUG:
    # 开发环境才启用 Swagger
    permission_classes = [permissions.AllowAny]
    schema_view = get_schema_view(
        openapi.Info(
            title="Snippets API",
            default_version="v1",
            description="Test description",
            terms_of_service="https://www.google.com/policies/terms/",
            contact=openapi.Contact(email="contact@snippets.local"),
            license=openapi.License(name="BSD License"),
        ),
        public=True,
        permission_classes=permission_classes,
        generator_class=CustomOpenAPISchemaGenerator,
    )
    
    # Swagger 路由配置
    swagger_urlpatterns = [
        re_path(
            r"^swagger(?P<format>\.json|\.yaml)$",
            schema_view.without_ui(cache_timeout=0),
            name="schema-json",
        ),
        path(
            "",  # 根路径显示 Swagger（仅在开发环境 DEBUG=True）
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        path(
            "redoc/",
            schema_view.with_ui("redoc", cache_timeout=0),
            name="schema-redoc",
        ),
    ]
else:
    # 生产环境：完全禁用 Swagger
    swagger_urlpatterns = []
# 前端页面映射
from django.http import Http404, HttpResponse
from django.shortcuts import render
import mimetypes
import os


def web_view(request):
    return render(request, 'web/index.html')


def serve_web_files(request, filename):
    # 设定文件路径
    filepath = os.path.join(settings.BASE_DIR, 'templates', 'web', filename)

    # 检查文件是否存在
    if not os.path.exists(filepath):
        raise Http404("File does not exist")

    # 根据文件扩展名，确定 MIME 类型
    mime_type, _ = mimetypes.guess_type(filepath)

    # 打开文件并读取内容
    with open(filepath, 'rb') as f:
        response = HttpResponse(f.read(), content_type=mime_type)
        return response


urlpatterns = (
        swagger_urlpatterns +  # 根据 DEBUG 动态添加 Swagger 路由
        [
            path("api/system/", include("dvadmin.system.urls")),
            path("api/login/", LoginView.as_view(), name="token_obtain_pair"),
            path("api/logout/", LogoutView.as_view(), name="token_obtain_pair"),
            path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
            re_path(
                r"^api-auth/", include("rest_framework.urls", namespace="rest_framework")
            ),
            path("api/captcha/", CaptchaView.as_view()),
            path("api/init/dictionary/", InitDictionaryViewSet.as_view()),
            path("api/init/settings/", InitSettingsViewSet.as_view()),
            path("apiLogin/", ApiLogin.as_view()),

            # 仅用于开发，上线需关闭
            path("api/token/", LoginTokenView.as_view()),
            # 前端页面映射
            path('web/', web_view, name='web_view'),
            path('web/<path:filename>', serve_web_files, name='serve_web_files'),
            # sse
            path('sse/', sse_view, name='sse'),
        ]
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        + static(settings.STATIC_URL, document_root=settings.STATIC_URL)
        + [re_path(ele.get('re_path'), include(ele.get('include'))) for ele in settings.PLUGINS_URL_PATTERNS]
)

# 添加自定义路由（业务模块）
My_Urls = (
    # 基础数据模块
    path('', include('dvadmin_twodev.basedata.roadline.urls')),
    path('', include('dvadmin_twodev.basedata.company.urls')),
    path('', include('dvadmin_twodev.basedata.vehicle_type.urls')),
    path('', include('dvadmin_twodev.basedata.district.urls')),
    path('', include('dvadmin_twodev.basedata.media_type.urls')),
    path('', include('dvadmin_twodev.basedata.media_type_composition.urls')),
    path('', include('dvadmin_twodev.basedata.roadline_detail.urls')),
    path('', include('dvadmin_twodev.basedata.roadline_stop.urls')),
    path('', include('dvadmin_twodev.basedata.roadline_stop_rel.urls')),
    path('', include('dvadmin_twodev.basedata.mapmanage.urls')),
    path('', include('dvadmin_twodev.basedata.park.urls')),
    path('', include('dvadmin_twodev.basedata.vehicle.urls')),
    path('', include('dvadmin_twodev.basedata.vehicle_ad_resource.urls')),
    path('', include('dvadmin_twodev.basedata.date.urls')),
    # 预订管理模块
    path('', include('dvadmin_twodev.booking_manage.agent.urls')),
    path('', include('dvadmin_twodev.booking_manage.agent_resource_auth.urls')),
    path('', include('dvadmin_twodev.booking_manage.customer.urls')),
    path('', include('dvadmin_twodev.booking_manage.booking_order.urls')),
    path('', include('dvadmin_twodev.booking_manage.booking_order_detail.urls')),
    path('', include('dvadmin_twodev.booking_manage.vehicle_ad_position.urls')),
    path('', include('dvadmin_twodev.booking_manage.vehicle_ad_position_change.urls')),
    #上下刊执行模块
    path('', include('dvadmin_twodev.airing_manage.on_air_order.urls')),
    path('', include('dvadmin_twodev.airing_manage.on_air_order_detail.urls')),
    path('', include('dvadmin_twodev.airing_manage.on_air_material.urls')),
    path('', include('dvadmin_twodev.airing_manage.construction_team.urls')),
    path('', include('dvadmin_twodev.airing_manage.construction_team_member.urls')),
    path('', include('dvadmin_twodev.airing_manage.construction_team_vehicle.urls')),
    path('', include('dvadmin_twodev.airing_manage.on_air_worker.urls')),
    path('', include('dvadmin_twodev.airing_manage.on_air_file.urls')),
    path('', include('dvadmin_twodev.airing_manage.entry_reg.urls')),
    # OSM 模块
    path('', include('dvadmin_twodev.osm.osm_node.urls')),
    path('', include('dvadmin_twodev.osm.osm_way.urls')),
    path('', include('dvadmin_twodev.osm.osm_nodeway_rel.urls')),
    # 线路复线分析
    path('', include('dvadmin_twodev.line_overlap.roadline_to_roadline_overlap.urls')),
    # 工作流模块
    path('', include('dvadmin_twodev.node_workflow.schemeinfo.urls')),
    path('', include('dvadmin_twodev.node_workflow.scheme.urls')),
    path('', include('dvadmin_twodev.node_workflow.schemeauth.urls')),
    path('', include('dvadmin_twodev.node_workflow.process.urls')),
    path('', include('dvadmin_twodev.node_workflow.task.urls')),
    path('', include('dvadmin_twodev.node_workflow.taskrelation.urls')),
    path('', include('dvadmin_twodev.node_workflow.tasklog.urls')),
    path('', include('dvadmin_twodev.node_workflow.taskmsg.urls')),
    path('', include('dvadmin_twodev.node_workflow.confluence.urls')),
    # AI审核模块
    path('', include('dvadmin_twodev.ai_audit.audit_log.urls')),
    path('', include('dvadmin_twodev.ai_audit.audit_feedback.urls')),
)
# ========== 扩展模块路由（扩展功能） ==========
Extension_Urls = (
    path("api/ext/data_permission/", include("dvadmin_extensions.data_permission.urls")),
    path("api/ext/table_sharding/", include("dvadmin_extensions.table_sharding.urls")),
)

# 合并所有路由
urlpatterns += My_Urls + Extension_Urls

