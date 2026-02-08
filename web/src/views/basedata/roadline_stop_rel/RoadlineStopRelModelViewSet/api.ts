/*
 * 接口说明：
 * - 标准DRF接口：GetList, AddObj, UpdateObj, DelObj
 * - 自定义接口：enableRoadlineStopRel（启用/禁用）
 * - 辅助接口：getRoadlineList, getRoadlineDetailList（下拉选择）
 */
import { request, downloadFile } from '/@/utils/service';
import { PageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

// API前缀
export const apiPrefix = '/api/RoadlineStopRelModelViewSet/';

/**
 * 获取站点关联列表（标准DRF接口）
 * @param query 查询参数
 * @returns 站点关联列表数据
 */
export function GetList(query: PageQuery) {
	return request({
		url: apiPrefix,
		method: 'get',
		params: query,
	});
}

/**
 * 创建站点关联（标准DRF接口）
 * @param obj 站点关联数据
 * @returns 创建结果
 */
export function AddObj(obj: AddReq) {
	return request({
		url: apiPrefix,
		method: 'post',
		data: obj,
	});
}

/**
 * 更新站点关联（标准DRF接口）
 * @param obj 站点关联数据（必须包含id）
 * @returns 更新结果
 */
export function UpdateObj(obj: EditReq) {
	return request({
		url: apiPrefix + obj.id + '/',
		method: 'put',
		data: obj,
	});
}

/**
 * 删除站点关联（标准DRF接口）
 * @param id 站点关联ID
 * @returns 删除结果
 */
export function DelObj(id: DelReq) {
	return request({
		url: apiPrefix + id + '/',
		method: 'delete',
		data: { id },
	});
}

/**
 * 导出站点关联数据
 * @param params 导出参数
 * @returns 导出文件
 */
export function exportData(params: any) {
    return downloadFile({
        url: apiPrefix + 'export_data/',
        params: params,
        method: 'get'
    });
}

// ==================== 自定义接口方法 ====================

/**
 * 启用/禁用站点关联
 * 请求方式：POST /api/RoadlineStopRelModelViewSet/enable_roadline_stop_rel/
 * @param data 启用参数 {id: number, enabled_mark: 0|1}
 * @returns 操作结果
 */
export function enableRoadlineStopRel(data: { id: number; enabled_mark: 0 | 1 }) {
	return request({
		url: apiPrefix + 'enable_roadline_stop_rel/',
		method: 'post',
		data: data,
	});
}

/**
 * 获取线路列表（用于下拉选择）
 * @returns 线路列表
 */
export function getRoadlineList() {
	return request({
		url: '/api/RoadlineModelViewSet/',
		method: 'get',
		params: { page: 1, limit: 1000 },
	});
}

/**
 * 获取线路详情列表（用于下拉选择）
 * @param roadline_id 线路ID
 * @returns 线路详情列表
 */
export function getRoadlineDetailList(roadline_id?: number) {
	return request({
		url: '/api/RoadlineDetailViewSet/',
		method: 'get',
		params: { page: 1, limit: 1000, roadline_id },
	});
}

