'''
Description: 车辆广告资源位视图
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from rest_framework.decorators import action
from django.db import transaction
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from .models import VehicleAdResourceModel
from .serializers import (
    VehicleAdResourceModelSerializer,
    VehicleAdResourceModelCreateSerializer,
    VehicleAdResourceModelUpdateSerializer,
    VehicleAdResourceModelListSerializer
)
from django.db.models import Q
from dvadmin_twodev.booking_manage.vehicle_ad_position.models import VehicleAdPositionModel
from dvadmin_twodev.basedata.media_type.models import AdMediaTypeModel
from dvadmin_twodev.basedata.media_type_composition.models import AdMediaTypeCompositionModel
from django.db.models import Count
import logging

logger = logging.getLogger(__name__)
from django.db.models import Q as DjangoQ


class VehicleAdResourceModelViewSet(CustomModelViewSet):
    """
    车辆广告资源位管理视图集
    
    功能说明:
    - 提供资源位的增删改查功能(使用DRF标准接口)
    - 自动处理分页、过滤、排序等功能
    - 支持批量删除和启用/禁用操作
    
    标准DRF接口:
    - GET /api/VehicleAdResourceModelViewSet/ - 获取资源位列表
    - POST /api/VehicleAdResourceModelViewSet/ - 创建资源位
    - PUT /api/VehicleAdResourceModelViewSet/{id}/ - 更新资源位
    - DELETE /api/VehicleAdResourceModelViewSet/{id}/ - 删除资源位
    
    自定义接口:
    - POST /api/VehicleAdResourceModelViewSet/enable_resource/ - 启用/禁用资源位
    - GET /api/VehicleAdResourceModelViewSet/get_by_vehicle/ - 根据车辆ID获取资源位列表
    """
    # 查询集
    queryset = VehicleAdResourceModel.objects.all()
    
    # 默认序列化器(用于查询详情)
    serializer_class = VehicleAdResourceModelSerializer
    
    # 列表序列化器(用于列表展示)
    list_serializer_class = VehicleAdResourceModelListSerializer
    
    # 创建序列化器
    create_serializer_class = VehicleAdResourceModelCreateSerializer
    
    # 更新序列化器
    update_serializer_class = VehicleAdResourceModelUpdateSerializer
    
    # 过滤字段(支持精确查询)
    filter_fields = [
        'id', 'resource_code', 'vehicle_id', 'base_media_type_id',
        'resource_status', 'current_order_id', 'enabled_mark', 'delete_mark'
    ]
    
    # filterset_fields 用于 DRF 的过滤后端
    filterset_fields = [
        'id', 'resource_code', 'vehicle_id', 'base_media_type_id',
        'resource_status', 'current_order_id', 'enabled_mark', 'delete_mark'
    ]
    
    # 搜索字段(支持模糊查询)
    search_fields = ['resource_code', 'remark']
    
    # 排序字段
    ordering_fields = ['resource_code', 'create_datetime', 'update_datetime', 'on_air_date', 'off_air_date']
    
    # 默认排序
    ordering = ['vehicle_id', 'base_media_type_id']

    def get_queryset(self):
        """
        自定义查询集
        优化查询性能，预加载关联对象
        支持通过 roadline_id 过滤（通过车辆表的 roadline 字段）
        支持通过 vehicle_id__in 过滤（多个车辆ID）
        在列表接口中只显示 resource_status=1（空闲）的数据
        支持通过 include_all_status=true 参数来包含所有状态的数据
        支持通过 exclude_resource_status 参数来排除指定状态的数据
        """
        queryset = super().get_queryset()
        
        # 使用 select_related 预加载关联对象，提高查询性能
        # 避免 N+1 查询问题
        queryset = queryset.select_related('vehicle_id', 'vehicle_id__roadline', 'base_media_type_id')
        
        # 只在列表接口中应用过滤：只显示 resource_status=1（空闲）的数据
        # 但可以通过查询参数来控制是否应用此过滤
        if self.action == 'list':
            # 检查是否包含所有状态（用于日历视图等场景）
            include_all_status = self.request.query_params.get('include_all_status', '').lower() in ('true', '1', 'yes')
            # 检查是否排除指定状态（用于排除空闲状态等场景）
            exclude_resource_status = self.request.query_params.get('exclude_resource_status')
            
            if not include_all_status and not exclude_resource_status:
                # 默认行为：只显示 resource_status=1（空闲）的数据
                queryset = queryset.filter(resource_status=1)
            elif exclude_resource_status:
                # 排除指定状态的数据
                try:
                    exclude_status = int(exclude_resource_status)
                    queryset = queryset.exclude(resource_status=exclude_status)
                except (ValueError, TypeError):
                    # 如果参数无效，使用默认行为
                    queryset = queryset.filter(resource_status=1)
            # 如果 include_all_status=true，则不应用任何 resource_status 过滤
        
        # 支持通过 vehicle_id__in 过滤（多个车辆ID，逗号分隔）
        vehicle_id_in = self.request.query_params.get('vehicle_id__in')
        if vehicle_id_in:
            try:
                # 解析逗号分隔的车辆ID列表
                vehicle_ids = [int(vid.strip()) for vid in str(vehicle_id_in).split(',') if vid.strip()]
                if vehicle_ids:
                    queryset = queryset.filter(vehicle_id__in=vehicle_ids)
            except (ValueError, TypeError):
                pass
        
        # 支持通过 roadline_id 过滤（通过车辆表的 roadline 字段）
        # 注意：如果同时有 vehicle_id__in，优先使用 vehicle_id__in
        if not vehicle_id_in:
            roadline_id = self.request.query_params.get('roadline_id')
            if roadline_id:
                queryset = queryset.filter(vehicle_id__roadline_id=roadline_id)
        
        return queryset

    def list(self, request, *args, **kwargs):
        """
        列表展示增强：
        - 当筛选到单一车辆（vehicle_id=xxx）时，优先折叠展示组合媒体类型
          若某组合类型的所有基础组件在该车资源位中都存在，则列表只返回“代表行”，并显示组合媒体类型名称；
          若无任何组合成立，则正常展示基础媒体类型。
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            # NOTE: 为排查线上/开发环境日志等级过滤，临时使用 print 打印关键调试信息
            # 用于确认 list 是否被调用、是否携带 vehicle_id 参数
            try:
                print(
                    "[VehicleAdResource.list][debug]",
                    "vehicle_id=",
                    request.query_params.get("vehicle_id"),
                    "roadline_id=",
                    request.query_params.get("roadline_id"),
                    "vehicle_id__in=",
                    request.query_params.get("vehicle_id__in"),
                )
            except Exception:
                pass

            # 仅在“单一车辆过滤”场景启用折叠
            vehicle_id = request.query_params.get("vehicle_id")
            vehicle_id_in = request.query_params.get("vehicle_id__in")

            # 这份 mapping 的 key 统一用 vehicle_id|base_type_id
            base_type_to_composite_name = {}

            # 支持 vehicle_id__in（多车）时，也分别对每辆车做折叠。
            # 若未指定车辆筛选（页面刚打开），则只对“当前页会出现的车辆”做折叠，避免全表扫描。
            vehicle_ids = []
            if vehicle_id:
                vehicle_ids = [str(vehicle_id)]
            elif vehicle_id_in:
                vehicle_ids = [x.strip() for x in str(vehicle_id_in).split(",") if x.strip()]
            else:
                # 未筛选车辆：从当前分页窗口中提取涉及到的 vehicle_id 列表
                try:
                    limit_param = request.query_params.get("limit")
                    page_param = request.query_params.get("page")
                    limit = int(limit_param) if limit_param else 20
                    page_no = int(page_param) if page_param else 1
                    if limit > 0 and page_no > 0:
                        offset = (page_no - 1) * limit
                        vehicle_ids = list(
                            queryset.values_list("vehicle_id", flat=True).distinct()[offset : offset + limit]
                        )
                        vehicle_ids = [str(x) for x in vehicle_ids if x is not None]
                except Exception:
                    vehicle_ids = []

            if vehicle_ids:
                # 从组合配置表构建 composite -> components（按 sort_order 排序）
                comp_rows = (
                    AdMediaTypeCompositionModel.objects.filter(delete_mark=0, enabled_mark=1)
                    .order_by("composite_type_id", "sort_order", "id")
                    .values_list("composite_type_id", "component_type_id")
                )
                comp_to_components = {}
                for comp_id, comp_base_id in comp_rows:
                    comp_id = str(comp_id)
                    comp_base_id = str(comp_base_id)
                    comp_to_components.setdefault(comp_id, []).append(comp_base_id)

                # 每辆车要排除的基础类型（非代表行）
                drop_map = {}  # vehicle_id -> set(base_type_id)
                chosen_composite_ids_all = set()
                reps_map = {}  # (vehicle_id, composite_id) -> rep_base_type_id

                for vid in vehicle_ids:
                    # 当前车空闲基础类型集合（当前 queryset 已经是 resource_status=1 的过滤结果）
                    base_ids = list(
                        queryset.filter(vehicle_id=vid).values_list("base_media_type_id", flat=True).distinct()
                    )
                    available_base_set = {str(x) for x in base_ids if x is not None}
                    if not available_base_set:
                        continue

                    # 满足条件：组件集合 ⊆ 空闲集合
                    satisfied = []
                    for comp_id, comps in comp_to_components.items():
                        comp_set = set(comps)
                        if comp_set and comp_set.issubset(available_base_set):
                            satisfied.append((comp_id, comps))

                    if not satisfied:
                        continue

                    # 贪心选择：组件数多的优先，避免重复占用
                    satisfied.sort(key=lambda x: (-len(set(x[1])), x[0]))
                    remaining = set(available_base_set)
                    chosen = []
                    for comp_id, comps in satisfied:
                        comp_set = set(comps)
                        if comp_set.issubset(remaining):
                            chosen.append((comp_id, comps))
                            remaining -= comp_set

                    if not chosen:
                        continue

                    # 代表行：取该组合 components 排序后的第一个基础类型
                    all_component_ids = {base_id for _, comps in chosen for base_id in set(comps)}
                    reps = {cid: comps[0] for cid, comps in chosen if comps}

                    rep_base_ids = set(reps.values())
                    drop_ids = set(all_component_ids - rep_base_ids)
                    if drop_ids:
                        drop_map[vid] = drop_ids

                    for comp_id, rep_base_id in reps.items():
                        reps_map[(vid, str(comp_id))] = str(rep_base_id)
                        chosen_composite_ids_all.add(str(comp_id))

                if chosen_composite_ids_all:
                    # 组合名称
                    composite_name_map = dict(
                        AdMediaTypeModel.objects.filter(id__in=list(chosen_composite_ids_all), delete_mark=0)
                        .values_list("id", "media_name")
                    )
                    # 构建 vehicle_id|rep_base_id -> composite_name
                    for (vid, comp_id), rep_base_id in reps_map.items():
                        name = composite_name_map.get(str(comp_id))
                        if name:
                            base_type_to_composite_name[f"{vid}|{rep_base_id}"] = name

                # 应用排除：按车排除非代表基础类型
                if drop_map:
                    exclude_q = DjangoQ()
                    for vid, drop_ids in drop_map.items():
                        exclude_q |= DjangoQ(vehicle_id=vid, base_media_type_id__in=list(drop_ids))
                    queryset = queryset.exclude(exclude_q)

            # ====== 下面基本复用 CustomModelViewSet.list 的分页/返回逻辑 ======
            limit_param = request.query_params.get("limit")
            no_pagination = request.query_params.get("no_pagination", "").lower() in ("true", "1", "yes")

            serializer_context = {"request": request}
            if base_type_to_composite_name:
                serializer_context["base_type_to_composite_name"] = base_type_to_composite_name

            if limit_param == "0" or no_pagination:
                serializer = self.get_serializer(queryset, many=True, context=serializer_context)
                return SuccessResponse(data=serializer.data, msg="获取成功")

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True, context=serializer_context)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True, context=serializer_context)
            return SuccessResponse(data=serializer.data, msg="获取成功")
        finally:
            self._restore_sharding_tables(request)

    @action(detail=False, methods=["get"], url_path="get_vehicle_media_types")
    def get_vehicle_media_types(self, request):
        """
        获取某辆车当前已配置的媒体类型（展示用）：
        - 基于该车 resource_status=1 的基础类型集合，反推能组成的组合类型（组合优先）
        - 返回组合名称列表 + 剩余基础类型名称列表 + 展示字符串
        """
        vehicle_id = request.query_params.get("vehicle_id")
        if not vehicle_id:
            return ErrorResponse(msg="vehicle_id 不能为空")

        qs = self.queryset.filter(vehicle_id=vehicle_id, delete_mark=0, enabled_mark=1, resource_status=1)
        base_ids = list(qs.values_list("base_media_type_id", flat=True).distinct())
        available_base_set = {str(x) for x in base_ids if x is not None}

        if not available_base_set:
            return SuccessResponse(
                data={
                    "vehicle_id": str(vehicle_id),
                    "composites": [],
                    "bases": [],
                    "display": "",
                },
                msg="获取成功",
            )

        # composite -> components
        comp_rows = (
            AdMediaTypeCompositionModel.objects.filter(delete_mark=0, enabled_mark=1)
            .order_by("composite_type_id", "sort_order", "id")
            .values_list("composite_type_id", "component_type_id")
        )
        comp_to_components = {}
        for comp_id, comp_base_id in comp_rows:
            comp_id = str(comp_id)
            comp_base_id = str(comp_base_id)
            comp_to_components.setdefault(comp_id, []).append(comp_base_id)

        satisfied = []
        for comp_id, comps in comp_to_components.items():
            comp_set = set(comps)
            if comp_set and comp_set.issubset(available_base_set):
                satisfied.append((comp_id, comps))
        satisfied.sort(key=lambda x: (-len(set(x[1])), x[0]))

        remaining = set(available_base_set)
        chosen = []
        for comp_id, comps in satisfied:
            comp_set = set(comps)
            if comp_set.issubset(remaining):
                chosen.append((comp_id, comps))
                remaining -= comp_set

        composite_ids = [cid for cid, _ in chosen]
        composite_name_map = dict(
            AdMediaTypeModel.objects.filter(id__in=composite_ids, delete_mark=0).values_list("id", "media_name")
        )
        composites = [{"id": cid, "name": composite_name_map.get(cid, cid)} for cid in composite_ids]

        # 剩余基础类型名称
        base_name_map = dict(
            AdMediaTypeModel.objects.filter(id__in=list(remaining), delete_mark=0).values_list("id", "media_name")
        )
        bases = [{"id": bid, "name": base_name_map.get(bid, bid)} for bid in sorted(list(remaining))]

        display_parts = [c["name"] for c in composites] + [b["name"] for b in bases]
        display = "、".join([x for x in display_parts if x])

        return SuccessResponse(
            data={
                "vehicle_id": str(vehicle_id),
                "composites": composites,
                "bases": bases,
                "display": display,
            },
            msg="获取成功",
        )

    @action(detail=False, methods=["post"], url_path="set_vehicle_media_types")
    def set_vehicle_media_types(self, request):
        """
        编辑某辆车的媒体类型配置：
        - 入参支持：
          - media_type_id: 单个组合/基础类型
          - media_type_ids: 多个组合/基础类型（取并集）
        - 组合类型自动拆分成基础类型集合，并对多个输入取并集
        - 对该车资源位进行"覆盖式更新"：先删除该车辆下所有 resource_status=1 的数据，然后添加新的数据，使用事务确保原子性
        """
        vehicle_id = request.data.get("vehicle_id")
        media_type_id = request.data.get("media_type_id") or request.data.get("base_media_type_id")
        media_type_ids = request.data.get("media_type_ids")
        remark = request.data.get("remark")

        if not vehicle_id:
            return ErrorResponse(msg="vehicle_id 不能为空")
        # 兼容单选与多选
        input_ids = []
        if media_type_ids:
            if isinstance(media_type_ids, (list, tuple)):
                input_ids = [str(x) for x in media_type_ids if str(x)]
            else:
                # 兼容前端误传字符串逗号分隔
                input_ids = [x.strip() for x in str(media_type_ids).split(",") if x.strip()]
        elif media_type_id:
            input_ids = [str(media_type_id)]
        else:
            return ErrorResponse(msg="media_type_id 或 media_type_ids 不能为空")

        media_types = list(AdMediaTypeModel.objects.filter(id__in=input_ids, delete_mark=0).only("id", "is_composite", "media_name"))
        media_type_map = {str(x.id): x for x in media_types}
        missing_input = [mid for mid in input_ids if mid not in media_type_map]
        if missing_input:
            return ErrorResponse(msg=f"媒体类型不存在或已删除：{missing_input}")

        # 目标基础类型集合
        target_base_ids = []
        for mt_id in input_ids:
            mt = media_type_map.get(str(mt_id))
            if not mt:
                continue
            if mt.is_composite:
                comps = AdMediaTypeCompositionModel.objects.filter(
                    composite_type_id=str(mt.id),
                    delete_mark=0,
                    enabled_mark=1,
                ).order_by("sort_order", "id")
                if not comps.exists():
                    return ErrorResponse(msg=f"组合类型【{mt.media_name}】未配置基础类型")
                target_base_ids.extend([str(c.component_type_id) for c in comps])
            else:
                target_base_ids.append(str(mt.id))

        # 校验目标都是基础类型
        # 去重保持稳定
        target_base_ids = list(dict.fromkeys([x for x in target_base_ids if x]))
        base_types = AdMediaTypeModel.objects.filter(id__in=target_base_ids, delete_mark=0).only("id", "is_composite")
        base_type_map = {str(x.id): x for x in base_types}
        missing = [tid for tid in target_base_ids if tid not in base_type_map]
        if missing:
            return ErrorResponse(msg=f"基础媒体类型不存在或已删除：{missing}")
        invalid = [tid for tid, obj in base_type_map.items() if obj.is_composite]
        if invalid:
            return ErrorResponse(msg=f"组合类型拆分结果包含非基础类型：{invalid}")

        with transaction.atomic():
            # 先删除该车辆下所有 resource_status=1 的数据（物理删除）
            VehicleAdResourceModel.objects.filter(
                vehicle_id=vehicle_id,
                resource_status=1,
            ).delete()

            # 然后为所有目标基础类型创建新记录
            created_ids = []
            for base_id in target_base_ids:
                payload = {
                    "vehicle_id": vehicle_id,
                    "base_media_type_id": base_id,
                    "remark": remark,
                    "resource_status": 1,
                    "scheduled_start_date": None,
                    "scheduled_end_date": None,
                }
                ser = VehicleAdResourceModelCreateSerializer(data=payload, request=request)
                ser.is_valid(raise_exception=True)
                obj = ser.save()
                created_ids.append(str(obj.id))

        return SuccessResponse(
            data={"vehicle_id": str(vehicle_id), "created_ids": created_ids, "created_count": len(created_ids)},
            msg="编辑成功",
        )

    @action(detail=False, methods=["post"], url_path="bulk_create")
    def bulk_create(self, request):
        """
        批量创建资源位：
        - 支持多车辆 + 单一媒体类型
        - 若媒体类型为组合类型(is_composite=True)，自动拆分为基础类型并批量插入
        - 对每个车辆，先删除该车辆下所有 resource_status=1 的数据，然后添加新的数据，使用事务确保原子性

        请求体示例：
        {
            "vehicle_ids": [1,2,3],
            "media_type_id": "xxx",   # AdMediaTypeModel.id
            "remark": "..."
        }
        """
        vehicle_ids = request.data.get("vehicle_ids") or []
        media_type_id = request.data.get("media_type_id") or request.data.get("base_media_type_id")
        remark = request.data.get("remark")

        if not isinstance(vehicle_ids, (list, tuple)) or len(vehicle_ids) == 0:
            return ErrorResponse(msg="vehicle_ids 不能为空，且必须为数组")
        if not media_type_id:
            return ErrorResponse(msg="media_type_id 不能为空")

        # 获取媒体类型
        try:
            media_type = AdMediaTypeModel.objects.get(id=str(media_type_id), delete_mark=0)
        except AdMediaTypeModel.DoesNotExist:
            return ErrorResponse(msg="媒体类型不存在或已删除")

        # 解析基础媒体类型列表
        base_type_ids = []
        if media_type.is_composite:
            compositions = AdMediaTypeCompositionModel.objects.filter(
                composite_type_id=str(media_type.id),
                delete_mark=0,
                enabled_mark=1,
            ).order_by("sort_order", "id")
            if not compositions.exists():
                return ErrorResponse(msg=f"组合类型【{media_type.media_name}】未配置基础类型")
            base_type_ids = [str(c.component_type_id) for c in compositions]
        else:
            base_type_ids = [str(media_type.id)]

        # 校验基础类型都存在且为基础类型
        base_types = AdMediaTypeModel.objects.filter(id__in=base_type_ids, delete_mark=0).only("id", "is_composite")
        base_type_map = {str(x.id): x for x in base_types}
        missing = [tid for tid in base_type_ids if tid not in base_type_map]
        if missing:
            return ErrorResponse(msg=f"基础媒体类型不存在或已删除：{missing}")
        invalid = [tid for tid, obj in base_type_map.items() if obj.is_composite]
        if invalid:
            return ErrorResponse(msg=f"组合类型拆分结果包含非基础类型：{invalid}")

        created = []
        errors = []

        try:
            with transaction.atomic():
                for vehicle_id in vehicle_ids:
                    # 先删除该车辆下所有 resource_status=1 的数据（物理删除）
                    VehicleAdResourceModel.objects.filter(
                        vehicle_id=vehicle_id,
                        resource_status=1,
                    ).delete()

                    # 然后为该车辆创建新的资源位
                    for base_id in base_type_ids:
                        payload = {
                            "vehicle_id": vehicle_id,
                            "base_media_type_id": base_id,
                            "remark": remark,
                            "resource_status": 1,
                            # 明确传空，避免某些序列化器/前端约定把"缺失字段"当必填
                            "scheduled_start_date": None,
                            "scheduled_end_date": None,
                        }
                        # 显式使用创建序列化器，并传入 request（CustomModelSerializer 支持 request 参数）
                        ser = VehicleAdResourceModelCreateSerializer(data=payload, request=request)
                        if ser.is_valid():
                            obj = ser.save()
                            created.append(str(obj.id))
                        else:
                            errors.append({"vehicle_id": vehicle_id, "base_media_type_id": base_id, "errors": ser.errors})

                if errors:
                    # 触发回滚
                    raise ValueError("validation_error")
        except ValueError:
            # 前端通常只展示 msg，这里补充一个简短摘要，便于直接定位失败原因
            summary_parts = []
            for item in errors[:3]:
                vid = item.get("vehicle_id")
                mid = item.get("base_media_type_id")
                err_obj = item.get("errors") or {}
                # err_obj 可能是 dict(field -> [ErrorDetail...])
                first_field = None
                first_msg = None
                if isinstance(err_obj, dict) and err_obj:
                    first_field = next(iter(err_obj.keys()))
                    try:
                        first_msg = str(err_obj[first_field][0])
                    except Exception:
                        first_msg = str(err_obj[first_field])
                if first_field:
                    summary_parts.append(f"[vehicle_id={vid}, media_type_id={mid}] {first_field}: {first_msg}")
                else:
                    summary_parts.append(f"[vehicle_id={vid}, media_type_id={mid}] 校验失败")

            summary = "；".join(summary_parts)
            return ErrorResponse(
                msg=f"批量新增失败：存在校验错误（已回滚）。示例：{summary}",
                data={"errors": errors, "error_count": len(errors)},
            )

        return SuccessResponse(
            data={"created_ids": created, "created_count": len(created)},
            msg=f"批量新增成功：{len(created)} 条",
        )

    @action(detail=False, methods=['get'])
    def get_by_vehicle(self, request):
        """
        根据车辆ID获取资源位列表
        GET /api/VehicleAdResourceModelViewSet/get_by_vehicle/?vehicle_id=<uuid>
        注意：vehicle_id 是 UUID 字符串，不是整数
        """
        vehicle_id = request.query_params.get('vehicle_id')
        if not vehicle_id:
            return ErrorResponse(message="车辆ID不能为空")
        
        # vehicle_id 是 UUID 字符串，不需要转换为整数
        queryset = self.queryset.filter(vehicle_id=vehicle_id, delete_mark=0)
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")

    @action(detail=False, methods=['get'])
    def get_available_resources(self, request):
        """
        获取可用资源位列表（状态为空闲的资源位）
        GET /api/VehicleAdResourceModelViewSet/get_available_resources/
        """
        queryset = self.queryset.filter(
            resource_status=1,  # 空闲
            delete_mark=0,
            enabled_mark=1
        )
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")

    @action(detail=False, methods=['get'])
    def get_gantt_by_booking_order(self, request):
        """
        获取甘特图数据（按预订单聚合）
        
        按预订单的广告内容聚合数据，返回每辆车上的广告投放信息。
        
        数据关联路径：
        VehicleAdPositionModel.resource_id → VehicleAdResourceModel
        VehicleAdPositionModel.booking_detail_id → BookingOrderDetailModel.booking_order_id → BookingOrderModel.ad_content
        
        GET /api/VehicleAdResourceModelViewSet/get_gantt_by_booking_order/
        
        查询参数：
        - roadline_id: 线路ID（可选）
        - vehicle_id: 车辆ID（可选）
        - booking_order_id: 预订单ID（可选，用于查看详情）
        - reserved_start_date__gte: 预订开始日期（可选，格式：YYYY-MM-DD）
        - reserved_end_date__lte: 预订结束日期（可选，格式：YYYY-MM-DD）
        
        日期筛选说明：
        显示所有在指定日期范围内有排期的数据（排期与筛选范围有重叠即显示）
        
        返回格式：
        {
            "code": 2000,
            "data": {
                "vehicles": [
                    {"id": "车辆ID", "plateNumber": "车牌号", "route": "线路名称"}
                ],
                "schedules": [
                    {
                        "id": "预订单ID",
                        "vehicleId": "车辆ID",
                        "advertiser": "广告内容",
                        "adType": "媒体类型",
                        "status": "reserved|active|finished",
                        "startDate": "2025-01-01",
                        "endDate": "2025-01-31",
                        "bookingOrderId": "预订单ID",
                        "customerName": "客户名称",
                        "positionCount": 3
                    }
                ]
            },
            "msg": "获取成功"
        }
        """
        # 获取查询参数
        roadline_id = request.query_params.get('roadline_id')
        vehicle_id = request.query_params.get('vehicle_id')
        booking_order_id = request.query_params.get('booking_order_id')
        
        # 日期筛选参数（VehicleAdPositionModel 使用 reserved_start_date 和 reserved_end_date）
        reserved_start_date_gte = request.query_params.get('reserved_start_date__gte')
        reserved_end_date_lte = request.query_params.get('reserved_end_date__lte')
        
        # 构建查询条件
        position_filters = Q(delete_mark=0, enabled_mark=1)
        
        if roadline_id:
            position_filters &= Q(roadline_id=roadline_id)
        if vehicle_id:
            position_filters &= Q(vehicle_id=vehicle_id)
        if booking_order_id:
            position_filters &= Q(booking_detail_id__booking_order_id=booking_order_id)
        
        # 日期范围筛选：显示所有在指定日期范围内有排期的数据
        # 条件：reserved_start_date <= end_date AND reserved_end_date >= start_date
        from datetime import datetime
        if reserved_start_date_gte:
            try:
                start_date_obj = datetime.strptime(reserved_start_date_gte, '%Y-%m-%d').date()
                position_filters &= Q(reserved_end_date__gte=start_date_obj)
            except (ValueError, TypeError):
                pass
        if reserved_end_date_lte:
            try:
                end_date_obj = datetime.strptime(reserved_end_date_lte, '%Y-%m-%d').date()
                position_filters &= Q(reserved_start_date__lte=end_date_obj)
            except (ValueError, TypeError):
                pass
        
        # 查询车位广告数据，预加载关联对象
        positions = VehicleAdPositionModel.objects.filter(
            position_filters
        ).select_related(
            'vehicle_id',
            'vehicle_id__roadline',
            'roadline_id',
            'booking_detail_id',
            'booking_detail_id__booking_order_id',
            'booking_detail_id__media_type_id',
            'resource_id',  # 关联资源位，用于获取 off_air_date 和 scheduled_end_date
        ).order_by('vehicle_id', 'reserved_start_date')
        
        # 收集车辆信息
        vehicle_map = {}
        # 按 车辆+预订单 聚合排期数据
        schedule_map = {}  # key: (vehicle_id, booking_order_id)
        
        for pos in positions:
            # 获取车辆信息
            vehicle = pos.vehicle_id
            if vehicle and vehicle.id not in vehicle_map:
                vehicle_map[vehicle.id] = {
                    'id': str(vehicle.id),
                    'plateNumber': vehicle.vehicle_plate or f'车辆ID:{vehicle.id}',
                    'route': pos.roadline_name or (vehicle.roadline.line_name if vehicle.roadline else ''),
                }
            
            # 获取预订单信息
            booking_detail = pos.booking_detail_id
            if not booking_detail:
                continue
            
            booking_order = booking_detail.booking_order_id
            if not booking_order:
                continue
            
            # 构建聚合 key
            agg_key = (str(vehicle.id), str(booking_order.id))
            
            if agg_key not in schedule_map:
                # 确定状态
                status = 'finished'
                if pos.allocation_status == 1:
                    status = 'reserved'  # 已分配 = 预约中
                elif pos.allocation_status == 2:
                    status = 'active'  # 已上刊 = 已上线
                elif pos.allocation_status == 3:
                    status = 'finished'  # 已下刊 = 已结束
                
                # 获取资源位的 off_air_date 和 scheduled_end_date
                off_air_date = None
                scheduled_end_date = None
                if pos.resource_id:
                    resource = pos.resource_id
                    off_air_date = str(resource.off_air_date) if resource.off_air_date else None
                    scheduled_end_date = str(resource.scheduled_end_date) if resource.scheduled_end_date else None
                
                schedule_map[agg_key] = {
                    'id': f'{vehicle.id}_{booking_order.id}',  # 组合ID
                    'vehicleId': str(vehicle.id),
                    'advertiser': booking_order.ad_content or booking_order.booking_no or '广告内容',
                    'adType': booking_detail.media_type_name or '',
                    'status': status,
                    'startDate': str(pos.reserved_start_date) if pos.reserved_start_date else None,
                    'endDate': str(pos.reserved_end_date) if pos.reserved_end_date else None,
                    'bookingOrderId': str(booking_order.id),
                    'bookingNo': booking_order.booking_no,
                    'customerName': booking_order.customer_name or '',
                    'positionCount': 1,
                    # 记录该预订单在该车辆上的所有资源位ID
                    'positionIds': [str(pos.id)],
                    # 用于判断到期未下刊的字段
                    'off_air_date': off_air_date,
                    'scheduled_end_date': scheduled_end_date,
                }
            else:
                # 已存在，更新日期范围和资源位计数
                existing = schedule_map[agg_key]
                existing['positionCount'] += 1
                existing['positionIds'].append(str(pos.id))
                
                # 更新开始日期（取最早）
                if pos.reserved_start_date:
                    start_str = str(pos.reserved_start_date)
                    if not existing['startDate'] or start_str < existing['startDate']:
                        existing['startDate'] = start_str
                
                # 更新结束日期（取最晚）
                if pos.reserved_end_date:
                    end_str = str(pos.reserved_end_date)
                    if not existing['endDate'] or end_str > existing['endDate']:
                        existing['endDate'] = end_str
        
        return SuccessResponse(
            data={
                'vehicles': list(vehicle_map.values()),
                'schedules': list(schedule_map.values()),
            },
            msg="获取成功"
        )

    @action(detail=False, methods=['get'])
    def get_positions_by_booking(self, request):
        """
        获取指定车辆+预订单的所有车位资源详情
        
        用于点击甘特图广告条后显示详情。
        
        GET /api/VehicleAdResourceModelViewSet/get_positions_by_booking/
        
        查询参数：
        - vehicle_id: 车辆ID（必填）
        - booking_order_id: 预订单ID（必填）
        
        返回格式：
        {
            "code": 2000,
            "data": {
                "bookingOrder": {
                    "id": "预订单ID",
                    "bookingNo": "BK-20250101-0001",
                    "adContent": "广告内容",
                    "customerName": "客户名称",
                    "startDate": "2025-01-01",
                    "endDate": "2025-01-31"
                },
                "positions": [
                    {
                        "id": "车位ID",
                        "resourceCode": "资源编码",
                        "mediaTypeName": "媒体类型",
                        "reservedStartDate": "2025-01-01",
                        "reservedEndDate": "2025-01-31",
                        "allocationStatus": 1,
                        "allocationStatusDisplay": "已分配"
                    }
                ]
            },
            "msg": "获取成功"
        }
        """
        vehicle_id = request.query_params.get('vehicle_id')
        booking_order_id = request.query_params.get('booking_order_id')
        
        if not vehicle_id or not booking_order_id:
            return ErrorResponse(msg="车辆ID和预订单ID不能为空")
        
        # 查询车位广告数据
        positions = VehicleAdPositionModel.objects.filter(
            vehicle_id=vehicle_id,
            booking_detail_id__booking_order_id=booking_order_id,
            delete_mark=0,
            enabled_mark=1,
        ).select_related(
            'resource_id',
            'booking_detail_id',
            'booking_detail_id__booking_order_id',
            'booking_detail_id__media_type_id',
        ).order_by('reserved_start_date')
        
        if not positions.exists():
            return ErrorResponse(msg="未找到相关数据")
        
        # 获取预订单信息
        first_pos = positions.first()
        booking_order = first_pos.booking_detail_id.booking_order_id
        
        # 资源状态显示映射（来自 dwd_vehicle_ad_resource.resource_status）
        resource_status_map = {
            1: '空闲',
            2: '预订',
            3: '在刊',
            4: '下刊',
            5: '维修中',
            6: '不可用',
            7: '到期未下刊',
        }
        
        # 构建返回数据
        position_list = []
        for pos in positions:
            resource = pos.resource_id
            detail = pos.booking_detail_id
            vehicle = pos.vehicle_id

            # 媒体类型：优先使用资源位关联的“基础媒体类型”名称，兜底为预订单明细上的媒体类型名称
            base_media_type_name = ''
            try:
                if resource and getattr(resource, "base_media_type_id", None):
                    media_obj = resource.base_media_type_id
                    if media_obj and getattr(media_obj, "media_name", None):
                        base_media_type_name = media_obj.media_name or ''
            except Exception:
                # 安全兜底，避免因个别数据问题导致接口整体失败
                base_media_type_name = ''

            # 资源状态：从车辆资源位表（dwd_vehicle_ad_resource）读取
            resource_status = getattr(resource, "resource_status", None) if resource else None

            position_list.append({
                'id': str(pos.id),
                'resourceId': str(resource.id) if resource else None,
                'resourceCode': resource.resource_code if resource else '',
                # 前端“媒体类型”列：只展示基础类型名称，若获取失败则回退到明细上的媒体类型名称
                'mediaTypeName': base_media_type_name or (detail.media_type_name if detail else ''),
                'roadlineName': pos.roadline_name or '',
                'roadlineCompanyName': pos.roadline_company_name or '',
                'vehicleNo': pos.vehicle_no or (vehicle.vehicle_plate if vehicle else ''),
                'vehiclePlate': vehicle.vehicle_plate if vehicle else '',
                'reservedStartDate': str(pos.reserved_start_date) if pos.reserved_start_date else None,
                'reservedEndDate': str(pos.reserved_end_date) if pos.reserved_end_date else None,
                'actualOnDate': str(pos.actual_on_date) if pos.actual_on_date else None,
                'actualOffDate': str(pos.actual_off_date) if pos.actual_off_date else None,
                # 分配状态列改为展示资源状态
                'resourceStatus': resource_status,
                'resourceStatusDisplay': resource_status_map.get(resource_status, '未知') if resource_status is not None else '未知',
            })
        
        # 预订单状态映射
        booking_status_map = {
            1: '草稿',
            2: '待审批',
            3: '审批中',
            4: '已通过',
            5: '已完成',
            6: '已取消',
            7: '已驳回',
        }
        
        return SuccessResponse(
            data={
                'bookingOrder': {
                    'id': str(booking_order.id),
                    'bookingNo': booking_order.booking_no,
                    'adContent': booking_order.ad_content or '',
                    'customerName': booking_order.customer_name or '',
                    'startDate': str(booking_order.start_date) if booking_order.start_date else None,
                    'endDate': str(booking_order.end_date) if booking_order.end_date else None,
                    'durationDays': booking_order.duration_days,
                    'totalAmount': str(booking_order.total_amount) if booking_order.total_amount else None,
                    'paidAmount': str(booking_order.paid_amount) if booking_order.paid_amount else None,
                    'bookingStatus': booking_order.booking_status,
                    'bookingStatusDisplay': booking_status_map.get(booking_order.booking_status, '未知'),
                    'remark': booking_order.remark or '',
                    'createDatetime': str(booking_order.create_datetime) if booking_order.create_datetime else None,
                },
                'positions': position_list,
            },
            msg="获取成功"
        )
