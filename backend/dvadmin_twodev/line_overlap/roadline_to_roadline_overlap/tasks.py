'''
Description: 公交线路复线日常计算 Celery 任务
Version: 2.2
Author: 王晨
Date: 2025-12-03 10:00:00
LastEditors: 王晨
LastEditTime: 2025-12-10 16:54:43
'''
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date as date_class
from typing import List, Tuple, Set

from django.db import transaction
from django.db.models import Q, Max
from django.utils import timezone

from application.celery import app
from dvadmin_twodev.basedata.roadline.models import RoadlineModel
from dvadmin_twodev.basedata.roadline_detail.models import RoadlineDetailModel
from dvadmin_twodev.line_overlap.roadline_to_roadline_overlap.models import (
    RoadlineToRoadlineOverlapModel,
)
from dvadmin_twodev.utils.geo.geo_utils import GeoCalculator

logger = logging.getLogger("celery.task")


def _get_valid_details(target_date: date_class):
    """
    获取指定日期有效的线路走向版本

    Args:
        target_date: 目标日期

    Returns:
        QuerySet[RoadlineDetailModel]: 在 target_date 有效的线路走向
    """
    return (
        RoadlineDetailModel.objects.filter(
            Q(exec_day__isnull=True) | Q(exec_day__lte=target_date),
            Q(expiry_day__isnull=True) | Q(expiry_day__gte=target_date),
        )
        .select_related("roadline")
        .only(
            "id",
            "roadline_id",
            "up_down",
            "lon_lat84",
            "line_length",
            "exec_day",
            "expiry_day",
        )
    )


def _calc_pair_valid_period(
    d1: RoadlineDetailModel,
    d2: RoadlineDetailModel,
    target_date: date_class,
):
    """
    计算一对走向在 target_date 下的共同有效期（exec_day, expiry_day）

    说明:
        - exec_day 取两条线路 exec_day 的最大值（共同生效的开始日）
        - expiry_day 取两条线路 expiry_day 的最小值（共同失效的结束日，任一为空则取非空值，均为空则为 None）
        - 若 target_date 不在 [exec_day, expiry_day] 区间内，则返回 None，表示当天无需计算
    """
    # 将 None 当作 -∞ / +∞ 来处理
    exec1 = d1.exec_day or target_date
    exec2 = d2.exec_day or target_date
    exp1 = d1.expiry_day  # None 视为 +∞
    exp2 = d2.expiry_day

    exec_day = max(exec1, exec2)

    if exp1 and exp2:
        expiry_day = min(exp1, exp2)
    else:
        expiry_day = exp1 or exp2  # 有一个 None 就用另一个；都为 None 时为 None（无限）

    # target_date 要落在 [exec_day, expiry_day] 范围内才认为当天需要计算
    if exec_day and exec_day > target_date:
        return None
    if expiry_day and expiry_day < target_date:
        return None

    return exec_day, expiry_day


def _build_existing_overlap_cache(detail_ids: List[int]) -> Set[Tuple[int, int, date_class, date_class | None]]:
    """
    批量预加载已存在的复线记录，构建内存缓存

    性能优化:
        - 一次性查询所有相关复线记录，避免 N+1 查询问题
        - 使用 set 实现 O(1) 查找性能

    Args:
        detail_ids: 所有有效走向的 ID 列表

    Returns:
        set: 已存在的复线记录键集合，格式为 (main_detail_id, vice_detail_id, exec_day, expiry_day)
    """
    if not detail_ids:
        return set()

    # 一次性查询所有相关的复线记录
    existing_records = RoadlineToRoadlineOverlapModel.objects.filter(
        main_roadline_detail_id__in=detail_ids,
        vice_roadline_detail_id__in=detail_ids,
    ).values_list(
        'main_roadline_detail_id',
        'vice_roadline_detail_id',
        'exec_day',
        'expiry_day',
    )

    # 构建 set 用于 O(1) 查找
    cache = set()
    for main_id, vice_id, exec_day, expiry_day in existing_records:
        # 使用 tuple 作为 key，注意处理 None 值
        cache.add((main_id, vice_id, exec_day, expiry_day))

    return cache


def _exists_overlap_record_cached(
    d1: RoadlineDetailModel,
    d2: RoadlineDetailModel,
    exec_day: date_class,
    expiry_day: date_class | None,
    cache: Set[Tuple[int, int, date_class, date_class | None]],
) -> bool:
    """
    从内存缓存中判断复线记录是否已存在（优化版本）

    性能优化:
        - 使用内存缓存替代数据库查询，避免 N+1 问题
        - O(1) 查找时间复杂度

    Args:
        d1: 主线路走向
        d2: 副线路走向
        exec_day: 共同生效日期
        expiry_day: 共同失效日期
        cache: 预加载的缓存集合

    Returns:
        bool: 是否存在
    """
    key = (d1.id, d2.id, exec_day, expiry_day)
    return key in cache


def _compute_overlap_geometry_and_length(
    d1: RoadlineDetailModel,
    d2: RoadlineDetailModel,
):
    """
    计算两条线路走向之间的复线轨迹与长度

    说明:
        - 使用 GeoCalculator.calculate_polyline_overlap 对 84 坐标轨迹进行计算
        - 若其中一条线路缺少 84 轨迹，直接返回 0

    Returns:
        tuple:
            repeat_length_m (float): 复线长度（米）
            main_repeat_rate (float): 主线路复线率
            vice_repeat_rate (float): 副线路复线率
            repeat_lon_lat84 (str): 复线轨迹（WGS84 坐标，多段用 '|' 分隔）
    """
    if not d1.lon_lat84 or not d2.lon_lat84:
        return 0.0, 0.0, 0.0, ""

    repeat_len_m, main_rate, vice_rate, repeat_lon_lat84 = (
        GeoCalculator.calculate_polyline_overlap(
            main_coord_str=d1.lon_lat84,
            vice_coord_str=d2.lon_lat84,
            sample_interval=10.0,
            match_threshold=15.0,
            separator=";",
            precision=6,
        )
    )

    # 直接返回米，不转换为公里
    repeat_len_m = repeat_len_m if repeat_len_m and repeat_len_m > 0 else 0.0
    return repeat_len_m, main_rate, vice_rate, repeat_lon_lat84


def _calc_roadline_overlap_batch(
    date_str: str,
    detail_id_list: List[int],
    pair_index_list: List[Tuple[int, int]],
) -> dict:
    """
    批处理函数：计算一批线路走向组合的复线情况

    设计目的:
        - 将大量计算任务拆分成多个批次，支持并行处理
        - 每个批次独立执行，互不干扰
        - 在批次内部重新构建缓存，避免序列化大对象

    Args:
        date_str: 目标日期字符串（YYYY-MM-DD）
        detail_id_list: 所有有效走向的 ID 列表（按索引顺序）
        pair_index_list: 需要计算的组合索引列表，格式为 [(i, j), ...]

    Returns:
        dict: 本批次的运行结果统计信息
    """
    batch_start_time = time.time()
    target_date = date_class.fromisoformat(date_str)
    
    total_pairs = len(pair_index_list)
    logger.info(f"[roadline_overlap] 批次开始处理 {total_pairs} 对组合")

    # 批量加载 detail 对象（避免在循环中查询）
    load_start_time = time.time()
    detail_dict = {
        detail.id: detail
        for detail in RoadlineDetailModel.objects.filter(id__in=detail_id_list).select_related("roadline")
    }
    load_elapsed = time.time() - load_start_time
    logger.debug(f"[roadline_overlap] 批次加载 {len(detail_dict)} 条走向数据，耗时: {load_elapsed:.2f}秒")

    # 在批次内部重新构建缓存（避免序列化大对象，且每个批次独立）
    cache_start_time = time.time()
    existing_cache = _build_existing_overlap_cache(detail_id_list)
    cache_elapsed = time.time() - cache_start_time
    logger.debug(f"[roadline_overlap] 批次构建缓存 {len(existing_cache)} 条记录，耗时: {cache_elapsed:.2f}秒")

    created_count = 0
    skipped_count = 0
    created_records = []
    calc_count = 0  # 实际执行几何计算的次数
    last_log_time = batch_start_time

    for pair_idx, (i, j) in enumerate(pair_index_list):
        # 每处理10%或每10秒输出一次进度
        current_time = time.time()
        if pair_idx > 0 and (
            pair_idx % max(1, total_pairs // 10) == 0 or 
            current_time - last_log_time >= 10
        ):
            elapsed = current_time - batch_start_time
            progress = pair_idx * 100 // total_pairs if total_pairs > 0 else 0
            avg_time = elapsed / pair_idx if pair_idx > 0 else 0
            remaining_pairs = total_pairs - pair_idx
            est_remaining = avg_time * remaining_pairs if avg_time > 0 else 0
            logger.info(
                f"[roadline_overlap] 批次进度: {pair_idx}/{total_pairs} ({progress}%), "
                f"已用时: {elapsed:.1f}秒, 预计剩余: {est_remaining:.1f}秒, "
                f"新建: {created_count}, 跳过: {skipped_count}, 计算: {calc_count}"
            )
            last_log_time = current_time
        # 从 detail_id_list 获取对应的 detail 对象
        if i >= len(detail_id_list) or j >= len(detail_id_list):
            continue

        detail_id_i = detail_id_list[i]
        detail_id_j = detail_id_list[j]

        if detail_id_i not in detail_dict or detail_id_j not in detail_dict:
            continue

        d1 = detail_dict[detail_id_i]
        d2 = detail_dict[detail_id_j]

        # roadline 一样的组合不参与复线计算
        if d1.roadline_id == d2.roadline_id:
            continue

        # 计算当天下两条走向的共同有效期
        period = _calc_pair_valid_period(d1, d2, target_date)
        if not period:
            continue
        exec_day, expiry_day = period

        # 使用内存缓存判断是否已存在
        if _exists_overlap_record_cached(d1, d2, exec_day, expiry_day, existing_cache):
            skipped_count += 1
            continue

        # 计算复线轨迹和长度（这里可能很耗时）
        calc_start_time = time.time()
        try:
            repeat_len_m, main_rate, vice_rate, repeat_lon_lat84 = (
                _compute_overlap_geometry_and_length(d1, d2)
            )
            calc_elapsed = time.time() - calc_start_time
            calc_count += 1
            
            # 如果单对计算超过5秒，记录警告
            if calc_elapsed > 5:
                logger.warning(
                    f"[roadline_overlap] 单对组合计算耗时 {calc_elapsed:.1f}秒: "
                    f"detail_{d1.id}(roadline_{d1.roadline_id}) vs "
                    f"detail_{d2.id}(roadline_{d2.roadline_id})"
                )
        except Exception as e:
            calc_elapsed = time.time() - calc_start_time
            logger.error(
                f"[roadline_overlap] 计算复线失败 (耗时 {calc_elapsed:.1f}秒): "
                f"detail_{d1.id} vs detail_{d2.id}, 错误: {e}"
            )
            continue

        # 没有复线（长度为 0）则无需写入
        if repeat_len_m <= 0:
            continue

        # 准备批量写入的数据
        created_records.append(
            RoadlineToRoadlineOverlapModel(
                main_roadline=d1.roadline,
                main_roadline_detail=d1,
                main_roadline_updown=d1.up_down,
                vice_roadline=d2.roadline,
                vice_roadline_detail=d2,
                vice_roadline_updown=d2.up_down,
                repeat_line_length=repeat_len_m,
                main_repeat_rate=main_rate,
                vice_repeat_rate=vice_rate,
                repeat_lon_lat84=repeat_lon_lat84,
                exec_day=exec_day,
                expiry_day=expiry_day,
            )
        )

        # 更新缓存，避免同一批次内重复计算
        existing_cache.add((d1.id, d2.id, exec_day, expiry_day))
        created_count += 1

    # 批量写入数据库
    if created_records:
        write_start_time = time.time()
        try:
            with transaction.atomic():
                RoadlineToRoadlineOverlapModel.objects.bulk_create(
                    created_records,
                    ignore_conflicts=True,  # 忽略唯一约束冲突
                )
            write_elapsed = time.time() - write_start_time
            logger.debug(
                f"[roadline_overlap] 批次批量写入 {len(created_records)} 条记录，耗时: {write_elapsed:.2f}秒"
            )
        except Exception as e:
            logger.error(f"[roadline_overlap] 批次批量写入失败: {e}")
            # 如果批量写入失败，尝试逐条写入
            write_start_time = time.time()
            success_count = 0
            for record in created_records:
                try:
                    with transaction.atomic():
                        record.save()
                    success_count += 1
                except Exception as e2:
                    logger.warning(f"[roadline_overlap] 单条记录写入失败: {e2}")
            write_elapsed = time.time() - write_start_time
            logger.info(
                f"[roadline_overlap] 批次逐条写入完成: {success_count}/{len(created_records)} 条成功，耗时: {write_elapsed:.2f}秒"
            )

    batch_elapsed = time.time() - batch_start_time
    logger.info(
        f"[roadline_overlap] 批次完成: 处理 {total_pairs} 对组合，"
        f"新建 {created_count} 条，跳过 {skipped_count} 对，计算 {calc_count} 次，"
        f"总耗时: {batch_elapsed:.1f}秒，平均每对: {batch_elapsed/total_pairs:.2f}秒"
    )

    return {
        "date": date_str,
        "created": created_count,
        "skipped": skipped_count,
        "batch_size": len(pair_index_list),
    }


@app.task()
def task__calc_roadline_overlap_for_date(date_str: str | None = None, batch_size: int = 10) -> dict:
    """
    按指定日期（默认今天）增量计算公交线路复线情况（优化版 - 支持并行处理）

    业务规则:
        1. 每日调度一次（可由定时任务调用），对当天有效的所有线路走向进行两两组合计算复线；
        2. 同一条线路（roadline 一样）的组合不参与计算；
        3. 一对走向在当天的共同有效期 (exec_day, expiry_day) 若与历史一致，则不重新计算；
        4. 一旦线路走向的 exec_day / expiry_day 变化，产生新的有效期组合，就会生成新的复线记录；
        5. 旧的复线记录不删除，从而可以查询历史任意日期的复线情况。

    性能优化:
        1. 批量预加载已存在的复线记录，构建内存缓存，避免 N+1 查询
        2. 将计算任务拆分成多个批次，使用线程池并行处理
        3. 使用批量写入（bulk_create）提高数据库写入性能
        4. 完成一个批次后立即补充新的批次，保持并发数稳定

    Args:
        date_str: 目标日期字符串（YYYY-MM-DD），为空则使用当前日期
        batch_size: 每批处理的组合数量，默认 100

    Returns:
        dict: 运行结果统计信息
    """
    if date_str:
        target_date = date_class.fromisoformat(date_str)
    else:
        target_date = timezone.now().date()

    logger.info(f"[roadline_overlap] 开始计算 {target_date} 的公交线路复线情况")

    details = list(_get_valid_details(target_date))
    n = len(details)
    if n <= 1:
        logger.info(f"[roadline_overlap] {target_date} 有效走向数量为 {n}，无需计算")
        return {"date": target_date.isoformat(), "created": 0, "skipped": 0, "batches": 0}

    # ========== 性能优化：批量预加载已存在的复线记录 ==========
    detail_ids = [d.id for d in details]
    logger.info(f"[roadline_overlap] 预加载 {len(detail_ids)} 条走向的已存在复线记录...")
    existing_cache = _build_existing_overlap_cache(detail_ids)
    logger.info(f"[roadline_overlap] 预加载完成，已存在 {len(existing_cache)} 条复线记录")

    # ========== 生成所有需要计算的组合对 ==========
    all_pairs = []
    for i in range(n):
        d1 = details[i]
        for j in range(i + 1, n):
            d2 = details[j]
            # roadline 一样的组合不参与复线计算
            if d1.roadline_id != d2.roadline_id:
                all_pairs.append((i, j))

    total_pairs = len(all_pairs)
    logger.info(f"[roadline_overlap] 共需计算 {total_pairs} 对组合，将拆分为多个批次并行处理")

    if total_pairs == 0:
        logger.info(f"[roadline_overlap] {target_date} 没有需要计算的组合")
        return {"date": target_date.isoformat(), "created": 0, "skipped": 0, "batches": 0}

    # ========== 将组合对拆分成多个批次 ==========
    batches = []
    for k in range(0, total_pairs, batch_size):
        batch_pairs = all_pairs[k : k + batch_size]
        batches.append(batch_pairs)

    logger.info(f"[roadline_overlap] 拆分为 {len(batches)} 个批次，每批约 {batch_size} 对组合")

    # ========== 控制并发数并行执行批次任务 ==========
    # 使用 ThreadPoolExecutor 并行处理批次任务
    # 并发数策略：
    # - 至少2个线程
    # - 不超过批次数量
    # - 最多10个线程（避免过多线程导致资源竞争和数据库连接池耗尽）
    max_workers = max(2, min(len(batches), 10))
    
    total_created = 0
    total_skipped = 0

    logger.info(
        f"[roadline_overlap] 开始并行执行 {len(batches)} 个批次（并发数：{max_workers}）"
    )

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有批次任务到线程池
        future_to_batch = {
            executor.submit(
                _calc_roadline_overlap_batch,
                date_str=target_date.isoformat(),
                detail_id_list=detail_ids,
                pair_index_list=batch_pairs,
            ): batch_idx
            for batch_idx, batch_pairs in enumerate(batches)
        }

        # 收集所有批次的结果（按完成顺序）
        completed_batches = 0
        for future in as_completed(future_to_batch):
            batch_idx = future_to_batch[future]
            try:
                result = future.result()
                batch_created = result.get("created", 0)
                batch_skipped = result.get("skipped", 0)
                total_created += batch_created
                total_skipped += batch_skipped
                completed_batches += 1
                logger.info(
                    f"[roadline_overlap] 批次 {batch_idx + 1}/{len(batches)} 完成："
                    f"新建 {batch_created} 条，跳过 {batch_skipped} 对"
                )
            except Exception as e:
                logger.error(f"[roadline_overlap] 批次 {batch_idx + 1} 执行失败: {e}")

    logger.info(
        f"[roadline_overlap] {target_date} 所有批次执行完成，"
        f"总计新建 {total_created} 条记录，跳过 {total_skipped} 对组合"
    )

    # ========== 计算每个 detail 和 roadline 的最大复线率 ==========
    try:
        calc_start_time = time.time()
        detail_max_rates = _calc_detail_max_overlap_rates(target_date, detail_ids)
        roadline_max_rates = _calc_roadline_max_overlap_rates(target_date, detail_max_rates)
        calc_elapsed = time.time() - calc_start_time
        logger.info(
            f"[roadline_overlap] 最大复线率计算完成，"
            f"更新 {len(detail_max_rates)} 个 detail，{len(roadline_max_rates)} 个 roadline，"
            f"耗时: {calc_elapsed:.2f}秒"
        )
    except Exception as e:
        logger.error(f"[roadline_overlap] 计算最大复线率失败: {e}")

    return {
        "date": target_date.isoformat(),
        "total_pairs": total_pairs,
        "batches": len(batches),
        "batch_size": batch_size,
        "created": total_created,
        "skipped": total_skipped,
    }


def _calc_detail_max_overlap_rates(target_date: date_class, detail_ids: List[int]) -> dict:
    """
    计算每个线路走向详情（detail）的最大复线率
    
    业务逻辑:
        1. 对于每个 detail，查找所有以它为 main 或 vice 的复线记录
        2. 取 main_repeat_rate 和 vice_repeat_rate 的最大值
        3. 批量更新 detail 的 max_roadline_overlap_rate 字段
    
    Args:
        target_date: 目标日期
        detail_ids: 所有有效走向的 ID 列表
    
    Returns:
        dict: {detail_id: max_rate, ...} 每个 detail 的最大复线率字典
    """
    if not detail_ids:
        return {}
    
    logger.info(f"[roadline_overlap] 开始计算 {len(detail_ids)} 个 detail 的最大复线率")
    
    # 查询所有相关的复线记录（以这些 detail 为主或副的）
    overlaps = RoadlineToRoadlineOverlapModel.objects.filter(
        Q(main_roadline_detail_id__in=detail_ids) | Q(vice_roadline_detail_id__in=detail_ids),
        Q(exec_day__isnull=True) | Q(exec_day__lte=target_date),
        Q(expiry_day__isnull=True) | Q(expiry_day__gte=target_date),
        delete_mark=0,
    ).values(
        'main_roadline_detail_id',
        'vice_roadline_detail_id',
        'main_repeat_rate',
        'vice_repeat_rate',
    )
    
    # 计算每个 detail 的最大复线率
    detail_max_rates = {}
    for overlap in overlaps:
        main_detail_id = overlap['main_roadline_detail_id']
        vice_detail_id = overlap['vice_roadline_detail_id']
        main_rate = overlap['main_repeat_rate']
        vice_rate = overlap['vice_repeat_rate']
        
        # 处理主线路的复线率
        if main_detail_id and main_rate is not None:
            if main_detail_id not in detail_max_rates:
                detail_max_rates[main_detail_id] = 0.0
            detail_max_rates[main_detail_id] = max(detail_max_rates[main_detail_id], float(main_rate))
        
        # 处理副线路的复线率
        if vice_detail_id and vice_rate is not None:
            if vice_detail_id not in detail_max_rates:
                detail_max_rates[vice_detail_id] = 0.0
            detail_max_rates[vice_detail_id] = max(detail_max_rates[vice_detail_id], float(vice_rate))
    
    # 批量更新 detail 的 max_roadline_overlap_rate
    update_count = 0
    with transaction.atomic():
        for detail_id, max_rate in detail_max_rates.items():
            try:
                RoadlineDetailModel.objects.filter(id=detail_id).update(
                    max_roadline_overlap_rate=max_rate
                )
                update_count += 1
            except Exception as e:
                logger.warning(f"[roadline_overlap] 更新 detail {detail_id} 最大复线率失败: {e}")
    
    logger.info(f"[roadline_overlap] 完成计算，更新了 {update_count} 个 detail 的最大复线率")
    
    return detail_max_rates


def _calc_roadline_max_overlap_rates(target_date: date_class, detail_max_rates: dict) -> dict:
    """
    基于 detail 的最大复线率，计算每个线路（roadline）的最大复线率
    
    业务逻辑:
        1. 对于每个 roadline，查找它所有 detail 的最大复线率
        2. 取这些 detail 的最大复线率的最大值
        3. 批量更新 roadline 的 max_roadline_overlap_rate 字段
    
    Args:
        target_date: 目标日期
        detail_max_rates: detail 的最大复线率字典 {detail_id: max_rate, ...}
    
    Returns:
        dict: {roadline_id: max_rate, ...} 每个 roadline 的最大复线率字典
    """
    if not detail_max_rates:
        return {}
    
    logger.info(f"[roadline_overlap] 开始计算 roadline 的最大复线率（基于 {len(detail_max_rates)} 个 detail）")
    
    # 获取所有相关的 detail，并关联到 roadline
    detail_ids = list(detail_max_rates.keys())
    details = RoadlineDetailModel.objects.filter(
        Q(exec_day__isnull=True) | Q(exec_day__lte=target_date),
        Q(expiry_day__isnull=True) | Q(expiry_day__gte=target_date),
        id__in=detail_ids,
        delete_mark=0,
    ).values('id', 'roadline_id')
    
    # 计算每个 roadline 的最大复线率
    roadline_max_rates = {}
    for detail in details:
        detail_id = detail['id']
        roadline_id = detail['roadline_id']
        
        if not roadline_id or detail_id not in detail_max_rates:
            continue
        
        detail_rate = detail_max_rates[detail_id]
        
        if roadline_id not in roadline_max_rates:
            roadline_max_rates[roadline_id] = 0.0
        
        roadline_max_rates[roadline_id] = max(roadline_max_rates[roadline_id], detail_rate)
    
    # 批量更新 roadline 的 max_roadline_overlap_rate
    update_count = 0
    with transaction.atomic():
        for roadline_id, max_rate in roadline_max_rates.items():
            try:
                RoadlineModel.objects.filter(id=roadline_id).update(
                    max_roadline_overlap_rate=max_rate
                )
                update_count += 1
            except Exception as e:
                logger.warning(f"[roadline_overlap] 更新 roadline {roadline_id} 最大复线率失败: {e}")
    
    logger.info(f"[roadline_overlap] 完成计算，更新了 {update_count} 个 roadline 的最大复线率")
    
    return roadline_max_rates


