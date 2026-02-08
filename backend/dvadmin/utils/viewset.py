# -*- coding: utf-8 -*-

"""
@author: 猿小天
@contact: QQ:1638245306
@Created on: 2021/6/1 001 22:57
@Remark: 自定义视图集
"""
import copy
from calendar import monthrange
from datetime import date

from django.db import transaction, models
from django.db.models import Q
from django_filters import DateTimeFromToRangeFilter
from django_filters.rest_framework import FilterSet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from dvadmin.utils.filters import DataLevelPermissionsFilter, CoreModelFilterBankend
from dvadmin.utils.import_export_mixin import ExportSerializerMixin, ImportSerializerMixin
from dvadmin.utils.json_response import SuccessResponse, ErrorResponse, DetailResponse
from dvadmin.utils.permission import CustomPermission
from dvadmin.utils.models import get_custom_app_models, CoreModel
from dvadmin.utils.request_util import get_and_validate_date_param
from dvadmin.system.models import FieldPermission, MenuField
from django_restql.mixins import QueryArgumentsMixin
from dvadmin_extensions.table_sharding.utils import get_sharding_proxy_model
from rest_framework.permissions import IsAuthenticated

class CustomModelViewSet(ModelViewSet, ImportSerializerMixin, ExportSerializerMixin, QueryArgumentsMixin):
    """
    自定义的ModelViewSet:
    统一标准的返回格式;新增,查询,修改可使用不同序列化器
    (1)ORM性能优化, 尽可能使用values_queryset形式
    (2)xxx_serializer_class 某个方法下使用的序列化器(xxx=create|update|list|retrieve|destroy)
    (3)filter_fields = '__all__' 默认支持全部model中的字段查询(除json字段外)
    (4)import_field_dict={} 导入时的字段字典 {model值: model的label}
    (5)export_field_label = [] 导出时的字段
    """
    values_queryset = None
    ordering_fields = '__all__'
    create_serializer_class = None
    update_serializer_class = None
    filter_fields = '__all__'
    search_fields = ()
    extra_filter_class = [CoreModelFilterBankend,DataLevelPermissionsFilter]
    # permission_classes = [CustomPermission]
    permission_classes = [IsAuthenticated]
    import_field_dict = {}
    export_field_label = {}

    def filter_queryset(self, queryset):

        # 先让所有过滤器收集 Q 对象（不直接过滤）
        for backend in set(set(self.filter_backends) | set(self.extra_filter_class or [])):
            queryset = backend().filter_queryset(self.request, queryset, self)

        # 统一合并所有数据权限的 Q 对象（OR 逻辑）
        if hasattr(self.request, '_data_permission_q_list') and self.request._data_permission_q_list:
            q_list = self.request._data_permission_q_list

            if len(q_list) == 1:
                queryset = queryset.filter(q_list[0])
            elif len(q_list) > 1:
                # 用 OR 合并所有 Q 对象
                final_q = q_list[0]
                for q_obj in q_list[1:]:
                    final_q |= q_obj
                queryset = queryset.filter(final_q)

            # 清理临时数据
            delattr(self.request, '_data_permission_q_list')

        return queryset

    def get_queryset(self):
        if getattr(self, 'values_queryset', None):
            queryset = self.values_queryset
        else:
            queryset = super().get_queryset()

        # 通用过滤：默认过滤软删除和未启用的数据
        # 如果模型有 delete_mark 和 enabled_mark 字段，且前端未传递这些参数，则应用默认过滤
        model = queryset.model

        # 检查模型是否有 delete_mark 字段（使用更高效的方式）
        if hasattr(model, '_meta'):
            field_names = {f.name for f in model._meta.get_fields()}

            # 如果前端没有传递 delete_mark 参数，默认过滤掉软删除的数据（delete_mark=0）
            if 'delete_mark' in field_names:
                delete_mark_param = self.request.query_params.get('delete_mark')
                if delete_mark_param is None:
                    queryset = queryset.filter(delete_mark=0)

            # 如果前端没有传递 enabled_mark 参数，默认只返回启用的数据（enabled_mark=1）
            # 可通过设置 skip_enabled_mark_filter = True 跳过此过滤
            if 'enabled_mark' in field_names and not getattr(self, 'skip_enabled_mark_filter', False):
                enabled_mark_param = self.request.query_params.get('enabled_mark')
                if enabled_mark_param is None:
                    queryset = queryset.filter(enabled_mark=1)

        # 自动处理所有查询参数中的 __in、__not_in、__gte、__lte、__gt、__lt
        for param_name, param_value in self.request.query_params.items():
            if param_name.endswith('__in') and param_value:
                field_name = param_name.replace('__in', '')
                values = [x.strip() for x in param_value.split(',') if x.strip()]
                if values:
                    # 尝试转换为整数（如果是数字字段）
                    try:
                        field = queryset.model._meta.get_field(field_name)
                        # 跳过 ForeignKey、CharField、TextField 等非数字字段
                        if isinstance(field, (models.ForeignKey, models.CharField, models.TextField, models.UUIDField)):
                            # 这些字段保持字符串格式，不进行类型转换
                            pass
                        elif isinstance(field, (models.IntegerField, models.BigIntegerField, models.PositiveIntegerField)):
                            values = [int(v) for v in values]
                    except:
                        pass
                    queryset = queryset.filter(**{f'{field_name}__in': values})

            elif param_name.endswith('__not_in') and param_value:
                field_name = param_name.replace('__not_in', '')
                values = [x.strip() for x in param_value.split(',') if x.strip()]
                if values:
                    # 尝试转换为整数（如果是数字字段）
                    try:
                        field = queryset.model._meta.get_field(field_name)
                        # 跳过 ForeignKey、CharField、TextField 等非数字字段
                        if isinstance(field, (models.ForeignKey, models.CharField, models.TextField, models.UUIDField)):
                            # 这些字段保持字符串格式，不进行类型转换
                            pass
                        elif isinstance(field, (models.IntegerField, models.BigIntegerField, models.PositiveIntegerField)):
                            values = [int(v) for v in values]
                    except:
                        pass
                    queryset = queryset.exclude(**{f'{field_name}__in': values})
            
            # 处理范围查询：__gte、__lte、__gt、__lt
            elif param_name.endswith(('__gte', '__lte', '__gt', '__lt')) and param_value:
                lookup_expr = param_name.split('__')[-1]  # 获取 gte、lte、gt、lt
                field_name = param_name.replace(f'__{lookup_expr}', '')
                try:
                    # 尝试转换为数字（如果是数字字段）
                    field = queryset.model._meta.get_field(field_name)
                    # 跳过 ForeignKey、CharField、TextField 等非数字字段
                    if isinstance(field, (models.ForeignKey, models.CharField, models.TextField, models.UUIDField)):
                        # 这些字段保持字符串格式，不进行类型转换
                        pass
                    elif isinstance(field, models.DecimalField):
                        from decimal import Decimal
                        param_value = Decimal(str(param_value))
                    elif isinstance(field, models.FloatField):
                        param_value = float(param_value)
                    elif isinstance(field, (models.IntegerField, models.BigIntegerField, models.PositiveIntegerField)):
                        param_value = int(param_value)
                    elif isinstance(field, (models.DateField, models.DateTimeField)):
                        # 日期字段保持字符串格式，让 Django ORM 处理
                        pass
                    # 其他字段保持原样
                    queryset = queryset.filter(**{param_name: param_value})
                except (ValueError, TypeError, models.FieldDoesNotExist):
                    # 转换失败或字段不存在，跳过
                    pass

        # ========== 自动应用有效日期过滤 ==========
        # 如果传递了 date 或 month 参数，且模型支持 valid_period，则自动应用时间过滤
        # 如果不传递参数或模型不支持，行为与之前完全一致（不做任何过滤）
        queryset, error_response = self._apply_valid_period_filter(self.request, queryset)
        if error_response:
            # 如果验证失败（如日期格式错误），记录日志但不影响其他功能
            # import logging
            # logger = logging.getLogger(__name__)
            # logger.warning(f"有效日期过滤验证失败: {error_response}")
            # 返回原查询集，不进行时间过滤
            return queryset

        return queryset

    def _apply_valid_period_filter(self, request, queryset, default_date=None):
        """
        应用有效时间范围过滤到查询集（通用方法）
        
        参数：
        - request: 请求对象
        - queryset: 基础查询集
        - default_date: 可选，默认日期对象（date类型）。如果为None且未传递date/month参数，则不进行时间过滤
        
        返回：
        - (filtered_queryset, error_response): 如果验证失败，error_response 不为 None
        - (filtered_queryset, None): 如果成功，error_response 为 None
        
        支持的查询参数：
        - month: 可选，指定查询月份（格式：YYYY-MM），使用该月最后一天作为查询日期
        - date: 可选，指定查询日期（格式：YYYY-MM-DD），用于过滤有效时间范围
        
        注意：
        - 如果模型没有 valid_period 或 valid_period_by_month 方法，此方法会返回原查询集（不进行过滤）
        - 优先使用 month 参数，如果 month 和 date 都传递，month 优先
        """
        # 获取日期参数
        date_param = request.query_params.get('date', None)
        month_param = request.query_params.get('month', None)

        # 优先使用 month 参数
        if month_param:
            month_date, error_response = get_and_validate_date_param(
                month_param, 
                required=False, 
                date_format='YYYY-MM'
            )
            if error_response:
                return None, error_response
            if month_date:
                # 检查模型是否有 valid_period_by_month 方法
                if hasattr(queryset, 'valid_period_by_month'):
                    queryset = queryset.valid_period_by_month(month_date.year, month_date.month)
                    return queryset, None
                else:
                    # 如果没有该方法，尝试使用 valid_period（使用该月最后一天）
                    last_day = monthrange(month_date.year, month_date.month)[1]
                    query_date = date(month_date.year, month_date.month, last_day)
                    if hasattr(queryset, 'valid_period'):
                        queryset = queryset.valid_period(query_date)
                        return queryset, None
                    else:
                        # 模型不支持时间过滤，返回原查询集
                        return queryset, None
        elif date_param:
            query_date, error_response = get_and_validate_date_param(
                date_param, 
                required=False, 
                date_format='YYYY-MM-DD'
            )
            if error_response:
                return None, error_response
            if query_date:
                if hasattr(queryset, 'valid_period'):
                    queryset = queryset.valid_period(query_date)
                    return queryset, None
                else:
                    # 模型不支持时间过滤，返回原查询集
                    return queryset, None
        elif default_date is not None:
            # 如果指定了默认日期，使用默认日期进行过滤
            if hasattr(queryset, 'valid_period'):
                queryset = queryset.valid_period(default_date)
                return queryset, None
            else:
                # 模型不支持时间过滤，返回原查询集
                return queryset, None

        # 如果都没有传递且没有默认日期，不进行时间过滤（返回所有数据）
        return queryset, None

    def get_serializer_class(self):
        action_serializer_name = f"{self.action}_serializer_class"
        action_serializer_class = getattr(self, action_serializer_name, None)
        if action_serializer_class:
            return action_serializer_class
        return super().get_serializer_class()

    # 通过many=True直接改造原有的API，使其可以批量创建
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        # 全部以可见字段为准
        can_see = self.get_menu_field(serializer_class)
        # 排除掉序列化器级的字段(排除字段权限中未授权的字段)
        # if not self.request.user.is_superuser:
        #     exclude_set = set(serializer_class._declared_fields.keys()) - set(can_see)
        #     for field in exclude_set:
        #         serializer_class._declared_fields.pop(field)
        #     meta = copy.deepcopy(serializer_class.Meta)
        #     meta.fields = list(can_see)
        #     serializer_class.Meta = meta
        # 在分页器中使用
        self.request.permission_fields = can_see
        if isinstance(self.request.data, list):
            with transaction.atomic():
                return serializer_class(many=True, *args, **kwargs)
        else:
            return serializer_class(*args, **kwargs)

    def get_menu_field(self, serializer_class):
        """获取字段权限"""

        if not any(model['object'] is serializer_class.Meta.model for model in get_custom_app_models()):
            return []

        # 匿名用户没有角色
        ret = FieldPermission.objects.filter(field__model=serializer_class.Meta.model.__name__)
        if hasattr(self.request.user, 'role'):
            roles = self.request.user.role.values_list('id', flat=True)
            ret = ret.filter(is_query=True, role__in=roles)

        return ret.values_list('field__field_name', flat=True)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, request=request)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return DetailResponse(data=serializer.data, msg="新增成功")

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())

            if hasattr(request, '_sharding_table_not_exists'):
                sharding_info = request._sharding_table_not_exists
                table_name = sharding_info['table_name']
                date_value = sharding_info.get('date_value')

                formatted_date = None
                if date_value:
                    if isinstance(date_value, str):
                        formatted_date = date_value
                    else:
                        formatted_date = date_value.strftime('%Y-%m-%d')
                else:
                    import re
                    date_match = re.search(r'_(\d{8})$', table_name)
                    if date_match:
                        date_str = date_match.group(1)
                        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

                if formatted_date:
                    return ErrorResponse(
                        msg=f"分表不存在：该日期（{formatted_date}）的数据表尚未创建，请先创建分表或选择其他日期。",
                        code=404
                    )
                return ErrorResponse(
                    msg=f"分表 {table_name} 不存在，请先创建分表。",
                    code=404
                )

            # 支持通过 limit=0 或 no_pagination=true 获取全量数据
            limit_param = request.query_params.get('limit')
            no_pagination = request.query_params.get('no_pagination', '').lower() in ('true', '1', 'yes')

            if limit_param == '0' or no_pagination:
                # 禁用分页，返回全量数据
                serializer = self.get_serializer(queryset, many=True, request=request)
                return SuccessResponse(data=serializer.data, msg="获取成功")

            # 正常分页逻辑
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True, request=request)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True, request=request)
            return SuccessResponse(data=serializer.data, msg="获取成功")
        finally:
            self._restore_sharding_tables(request)

    def retrieve(self, request, *args, **kwargs):
        try:
            # 检查分表操作是否需要日期参数
            if hasattr(request, '_sharding_date_required'):
                info = request._sharding_date_required
                return ErrorResponse(
                    msg=f"查询分表数据需要提供日期参数，请在 URL 中添加 ?{info['date_field']}=YYYY-MM-DD",
                    code=400
                )
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return DetailResponse(data=serializer.data, msg="获取成功")
        finally:
            self._restore_sharding_tables(request)

    def update(self, request, *args, **kwargs):
        try:
            # 处理分表更新：从请求体中获取日期字段，设置目标分表
            if hasattr(request, '_sharding_defer_to_update'):
                self._setup_sharding_for_update(request)

            partial = kwargs.pop('partial', False)

            # 检查是否是分表模型（通过检查 _sharding_model 判断）
            if hasattr(request, '_sharding_model') and request._sharding_model is not None:
                # 使用分表更新逻辑
                return self._perform_sharding_update(request, partial, *args, **kwargs)

            # 普通更新逻辑
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, request=request, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}
            return DetailResponse(data=serializer.data, msg="更新成功")
        finally:
            self._restore_sharding_tables(request)

    def _perform_sharding_update(self, request, partial, *args, **kwargs):
        """
        执行分表更新操作。
        
        使用动态创建的代理模型，每个分表有独立的模型类，彻底避免缓存问题。
        """
        target_table = getattr(request, '_sharding_target_table', None)
        base_table = getattr(request, '_sharding_base_table', None)
        model = getattr(request, '_sharding_model', None)

        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[分表更新] target_table={target_table}, base_table={base_table}, model={model}")

        # 如果没有分表信息，使用普通更新
        if not model or not target_table or not base_table:
            logger.warning("[分表更新] 缺少分表信息，使用普通更新")
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, request=request, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}
            return DetailResponse(data=serializer.data, msg="更新成功")

        # 获取主键
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        pk = self.kwargs.get(lookup_url_kwarg)

        logger.info(f"[分表更新] 使用分表 {target_table} 更新 pk={pk}")

        # ★★★ 关键：为这个分表创建一个独立的模型类 ★★★
        proxy_model = get_sharding_proxy_model(model, target_table)
        logger.info(f"[分表更新] 代理模型 db_table={proxy_model._meta.db_table}")

        try:
            # 使用代理模型查询
            instance = proxy_model.objects.get(pk=pk)
            logger.info(f"[分表更新] 查询成功，instance.__class__={instance.__class__}, _meta.db_table={instance.__class__._meta.db_table}")
        except proxy_model.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound(f"未找到 ID 为 {pk} 的记录")

        # 使用 serializer 验证数据
        serializer = self.get_serializer(instance, data=request.data, request=request, partial=partial)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # ★★★ 关键：直接通过代理模型执行 UPDATE，避免 ORM 缓存表名 ★★★
        if validated_data:
            update_fields = {field: value for field, value in validated_data.items()}
            proxy_model.objects.filter(pk=pk).update(**update_fields)
            logger.info(f"[分表更新] 已更新字段: {list(update_fields.keys())}")
        else:
            logger.info("[分表更新] 无字段需要更新")

        # 重新获取实例用于响应
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        instance = proxy_model.objects.get(pk=pk)
        response_serializer = self.get_serializer(instance)
        return DetailResponse(data=response_serializer.data, msg="更新成功")

    def _setup_sharding_for_update(self, request):
        """
        为 update 操作设置分表信息。
        从请求体中获取日期字段值，确定目标分表。
        """
        date_field = getattr(request, '_sharding_date_field', None)
        config = getattr(request, '_sharding_config', None)

        if not date_field or not config:
            return

        # 从请求体获取日期值
        date_value = request.data.get(date_field)
        if not date_value:
            # 请求体中没有日期字段，使用基础表
            return

        # 调用 mixin 的方法设置分表
        if hasattr(self, '_setup_sharding_table'):
            self._setup_sharding_table(request, date_value, config, date_field)

    def destroy(self, request, *args, **kwargs):
        try:
            # 如果模型启用了分表，则使用分表删除逻辑
            if hasattr(request, '_sharding_model') and request._sharding_model is not None:
                return self._perform_sharding_delete(request, *args, **kwargs)

            instance = self.get_object()
            instance.delete()
            return DetailResponse(data=[], msg="删除成功")
        finally:
            self._restore_sharding_tables(request)
    def _perform_sharding_delete(self, request, *args, **kwargs):
        """
        执行分表删除操作
        """
        target_table = getattr(request, '_sharding_target_table', None)
        base_table = getattr(request, '_sharding_base_table', None)
        model = getattr(request, '_sharding_model', None)

        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[分表删除] target_table={target_table}, base_table={base_table}, model={model}")

        if not model or not target_table or target_table == base_table:
            info = getattr(request, '_sharding_date_field', 'stat_date')
            return ErrorResponse(
                msg=f"删除分表数据需要提供日期参数，请在 URL 中添加 ?{info}=YYYY-MM-DD",
                code=400
            )

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        pk = self.kwargs.get(lookup_url_kwarg)

        proxy_model = get_sharding_proxy_model(model, target_table)
        deleted_count, _ = proxy_model.objects.filter(pk=pk).delete()
        if deleted_count == 0:
            from rest_framework.exceptions import NotFound
            raise NotFound(f"未找到 ID 为 {pk} 的记录")

        logger.info(f"[分表删除] 已删除 pk={pk}，表={target_table}")
        return DetailResponse(data=[], msg="删除成功")

    def destroy(self, request, *args, **kwargs):
        try:
            # 检查分表操作是否需要日期参数
            if hasattr(request, '_sharding_date_required'):
                info = request._sharding_date_required
                return ErrorResponse(
                    msg=f"删除分表数据需要提供日期参数，请在 URL 中添加 ?{info['date_field']}=YYYY-MM-DD",
                    code=400
                )
            instance = self.get_object()
            instance.delete()
            return DetailResponse(data=[], msg="删除成功")
        finally:
            self._restore_sharding_tables(request)

    def _restore_sharding_tables(self, request):
        """恢复分表模型的原始表名"""
        if hasattr(request, '_sharding_original_tables'):
            for model, original_table in request._sharding_original_tables.items():
                model._meta.db_table = original_table
            delattr(request, '_sharding_original_tables')

    keys = openapi.Schema(description='主键列表', type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING))
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['keys'],
        properties={'keys': keys}
    ), operation_summary='批量删除')
    @action(methods=['delete'], detail=False)
    def multiple_delete(self, request, *args, **kwargs):
        request_data = request.data
        keys = request_data.get('keys', None)
        if keys:
            self.get_queryset().filter(id__in=keys).delete()
            return SuccessResponse(data=[], msg="删除成功")
        else:
            return ErrorResponse(msg="未获取到keys字段")

    @action(methods=['post'], detail=False)
    def get_by_ids(self, request):
        """通过IDS列表获取数据"""
        ids = request.data.get('ids', [])
        if ids and ids != ['']:
            queryset = self.get_queryset().filter(id__in=ids)
            serializer = self.get_serializer(queryset, many=True)
            return DetailResponse(data=serializer.data)
        return DetailResponse(data=None)
