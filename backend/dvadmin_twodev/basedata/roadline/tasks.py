'''
Description: 线路 Celery 任务
Version: 1.0
Autor: 王晨
Date: 2025-12-27
LastEditors: 王晨
LastEditTime: 2025-12-27 16:46:50
'''
from django.db.models import Avg

from application.celery import app
from dvadmin_twodev.basedata.roadline.models import RoadlineModel
from dvadmin_twodev.basedata.roadline_detail.models import RoadlineDetailModel
from dvadmin_twodev.utils.geo.geo_utils import GeoCalculator


@app.task()
def task__calculate_roadline_non_linear_coefficient(roadline_id=None):
    """
    计算线路的非直线系数
    
    参数：
    - roadline_id: 可选，指定要计算的线路ID。如果为None，则计算所有线路
    
    功能说明：
    1. 第一步：计算每个 RoadlineDetailModel 的非直线系数
       - 从坐标数据（lon_lat84 或 lon_lat02）中提取起点和终点
       - 计算起点到终点的直线距离（米）
       - 用实际路径长度（line_length，单位km）除以直线距离（转换为km）得到非直线系数
       - 更新到 RoadlineDetailModel.non_linear_coefficient 字段
    2. 第二步：按线路分组，计算每个线路的平均非直线系数
       - 从 RoadlineDetailModel 中按 roadline 分组，计算平均非直线系数
       - 将平均值更新到 RoadlineModel 的 non_linear_coefficient 字段
    
    返回结果：
    {
        "success": True,
        "step1": {
            "total_details": 200,      # 详情总数
            "calculated_count": 180,   # 成功计算的详情数
            "skipped_count": 20        # 跳过（缺少数据）的详情数
        },
        "step2": {
            "total_roadlines": 100,    # 处理的线路总数
            "updated_count": 95,        # 成功更新的线路数
            "skipped_count": 5          # 跳过（无详情数据）的线路数
        },
        "details": [...]                # 详细信息
    }
    """
    print(f"开始计算线路非直线系数... roadline_id={roadline_id}")
    
    try:
        # ========== 第一步：计算每个 RoadlineDetailModel 的非直线系数 ==========
        print("第一步：开始计算线路详情的非直线系数...")
        
        # 根据 roadline_id 参数过滤数据
        if roadline_id:
            all_details = RoadlineDetailModel.objects.filter(roadline_id=roadline_id)
            print(f"只计算 roadline_id={roadline_id} 的数据")
        else:
            all_details = RoadlineDetailModel.objects.all()
            print("计算所有线路的数据")
        total_details = all_details.count()
        calculated_count = 0
        skipped_count = 0
        detail_calc_errors = []
        
        for detail in all_details:
            try:
                # 优先使用 lon_lat84，如果没有则使用 lon_lat02
                coords_str = detail.lon_lat84 or detail.lon_lat02
                if not coords_str or not coords_str.strip():
                    print(f"详情 ID {detail.id} 缺少坐标数据，跳过")
                    skipped_count += 1
                    continue
                
                # 解析坐标字符串
                try:
                    coords = GeoCalculator.parse_coords_string(coords_str, separator=';')
                except Exception as e:
                    print(f"详情 ID {detail.id} 坐标解析失败: {str(e)}")
                    skipped_count += 1
                    continue
                
                if len(coords) < 2:
                    print(f"详情 ID {detail.id} 坐标点少于2个，无法计算，跳过")
                    skipped_count += 1
                    continue
                
                # 获取起点和终点
                start_point = coords[0]
                end_point = coords[-1]
                
                # 计算起点到终点的直线距离（米）
                try:
                    start_end_distance_m = GeoCalculator.calculate_distance_haversine(
                        start_point, end_point
                    )
                except Exception as e:
                    print(f"详情 ID {detail.id} 距离计算失败: {str(e)}")
                    skipped_count += 1
                    continue
                
                # 判断是否为环线：起点和终点距离小于100米认为是环线
                CIRCULAR_LINE_THRESHOLD = 100.0  # 100米阈值
                is_circular_line = start_end_distance_m < CIRCULAR_LINE_THRESHOLD
                
                if is_circular_line:
                    # 环线：使用线路轨迹上最远两点间的距离作为参考距离（直径）
                    try:
                        max_distance_m = GeoCalculator.calculate_max_distance_in_polyline(coords)
                        straight_distance_km = max_distance_m / 1000.0
                        print(f"详情 ID {detail.id} 检测为环线（起点终点距离={start_end_distance_m:.2f}米），使用最远距离={max_distance_m:.2f}米作为参考")
                    except Exception as e:
                        print(f"详情 ID {detail.id} 计算环线最远距离失败: {str(e)}")
                        skipped_count += 1
                        continue
                else:
                    # 非环线：使用起点到终点的直线距离
                    straight_distance_km = start_end_distance_m / 1000.0
                
                if straight_distance_km <= 0:
                    print(f"详情 ID {detail.id} 参考距离为0或负数，跳过")
                    skipped_count += 1
                    continue
                
                # 获取或计算实际路径长度
                need_calculate_length = not detail.line_length or detail.line_length <= 0
                
                if need_calculate_length:
                    # line_length 为空，通过坐标计算线路总长度
                    try:
                        actual_length_m = GeoCalculator.calculate_polyline_length(coords)
                        actual_length_km = actual_length_m / 1000.0
                        
                        if actual_length_km <= 0:
                            print(f"详情 ID {detail.id} 计算出的线路长度为0或负数，跳过")
                            skipped_count += 1
                            continue
                        
                        # 更新 line_length 字段
                        detail.line_length = round(actual_length_km, 2)
                        print(f"详情 ID {detail.id} line_length 为空，已计算并更新: {actual_length_km:.2f}km")
                    except Exception as e:
                        print(f"详情 ID {detail.id} 计算线路长度失败: {str(e)}")
                        skipped_count += 1
                        continue
                else:
                    # 使用已有的 line_length
                    actual_length_km = float(detail.line_length)
                
                if actual_length_km <= 0:
                    print(f"详情 ID {detail.id} 实际路径长度为0或负数，跳过")
                    skipped_count += 1
                    continue
                
                # 计算非直线系数：实际路径长度 / 直线距离
                non_linear_coeff = actual_length_km / straight_distance_km
                
                # 更新到数据库（保留2位小数）
                old_value = detail.non_linear_coefficient
                detail.non_linear_coefficient = round(non_linear_coeff, 2)
                # 如果 line_length 被计算了，也需要保存
                update_fields = ['non_linear_coefficient']
                if need_calculate_length:
                    update_fields.append('line_length')
                detail.save(update_fields=update_fields)
                
                calculated_count += 1
                
                if calculated_count % 100 == 0:
                    print(f"已计算 {calculated_count} 条详情...")
                
                print(
                    f"详情 ID {detail.id} 非直线系数已计算: "
                    f"实际长度={actual_length_km}km, "
                    f"直线距离={straight_distance_km:.2f}km, "
                    f"系数={detail.non_linear_coefficient}"
                )
                
            except Exception as e:
                error_msg = f"计算详情 ID {detail.id} 时出错: {str(e)}"
                print(error_msg)
                detail_calc_errors.append({
                    "detail_id": detail.id,
                    "error": str(e)
                })
                skipped_count += 1
        
        print(
            f"第一步完成！共处理 {total_details} 条详情，"
            f"成功计算 {calculated_count} 条，跳过 {skipped_count} 条"
        )
        
        # ========== 第二步：按线路分组，计算平均非直线系数 ==========
        print("第二步：开始计算线路平均非直线系数...")
        
        # 从 RoadlineDetailModel 中按 roadline 分组，计算平均非直线系数
        # 只统计有非直线系数值的记录（排除 None）
        detail_stats_query = RoadlineDetailModel.objects.filter(
            non_linear_coefficient__isnull=False
        )
        
        # 如果指定了 roadline_id，则只计算该线路
        if roadline_id:
            detail_stats_query = detail_stats_query.filter(roadline_id=roadline_id)
        
        detail_stats = detail_stats_query.values('roadline_id').annotate(
            avg_coefficient=Avg('non_linear_coefficient')
        )
        
        detail_stats_list = list(detail_stats)
        print(f"找到 {len(detail_stats_list)} 个有非直线系数数据的线路详情")
        
        # 统计信息
        total_roadlines = len(detail_stats_list)
        updated_count = 0
        skipped_count_step2 = 0
        details = []
        
        # 遍历每个线路，更新非直线系数
        for stat in detail_stats_list:
            stat_roadline_id = stat['roadline_id']
            avg_coefficient = stat['avg_coefficient']
            
            if stat_roadline_id is None:
                print(f"跳过 roadline_id 为 None 的记录")
                skipped_count_step2 += 1
                continue
            
            try:
                # 查找对应的线路记录
                roadline = RoadlineModel.objects.filter(id=stat_roadline_id).first()
                
                if not roadline:
                    print(f"线路 ID {stat_roadline_id} 不存在，跳过")
                    skipped_count_step2 += 1
                    details.append({
                        "roadline_id": stat_roadline_id,
                        "status": "skipped",
                        "reason": "线路不存在"
                    })
                    continue
                
                # 更新非直线系数（保留2位小数）
                old_value = roadline.non_linear_coefficient
                roadline.non_linear_coefficient = round(avg_coefficient, 2)
                roadline.save(update_fields=['non_linear_coefficient'])
                
                updated_count += 1
                
                details.append({
                    "roadline_id": stat_roadline_id,
                    "roadline_name": roadline.line_name or "未知",
                    "status": "updated",
                    "old_value": float(old_value) if old_value else None,
                    "new_value": float(roadline.non_linear_coefficient),
                    "detail_count": RoadlineDetailModel.objects.filter(
                        roadline_id=stat_roadline_id,
                        non_linear_coefficient__isnull=False
                    ).count()
                })
                
                print(
                    f"线路 {stat_roadline_id} ({roadline.line_name}) "
                    f"非直线系数已更新: {old_value} -> {roadline.non_linear_coefficient}"
                )
                
            except Exception as e:
                print(f"更新线路 {stat_roadline_id} 时出错: {str(e)}")
                skipped_count_step2 += 1
                details.append({
                    "roadline_id": stat_roadline_id,
                    "status": "error",
                    "error": str(e)
                })
        
        result = {
            "success": True,
            "step1": {
                "total_details": total_details,
                "calculated_count": calculated_count,
                "skipped_count": skipped_count,
                "errors": detail_calc_errors[:50]  # 只返回前50个错误
            },
            "step2": {
                "total_roadlines": total_roadlines,
                "updated_count": updated_count,
                "skipped_count": skipped_count_step2
            },
            "details": details[:100]  # 只返回前100条详情，避免结果过大
        }
        
        print(
            f"计算完成！第一步：成功计算 {calculated_count}/{total_details} 条详情；"
            f"第二步：成功更新 {updated_count}/{total_roadlines} 条线路"
        )
        
        return result
        
    except Exception as e:
        error_msg = f"计算线路非直线系数时出错: {str(e)}"
        print(error_msg)
        import traceback
        print(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }
