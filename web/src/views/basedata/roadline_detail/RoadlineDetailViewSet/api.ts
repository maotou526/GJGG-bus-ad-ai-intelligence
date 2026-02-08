/*

 * 接口说明：
 * - 标准DRF接口：GetList, AddObj, UpdateObj, DelObj
 * - 自定义接口：enableRoadlineDetail（启用/禁用）
 */
import { request, downloadFile } from '/@/utils/service';
import { PageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

// API前缀
export const apiPrefix = '/api/RoadlineDetailViewSet/';

/**
 * 获取线路走向详情列表（标准DRF接口）
 * @param query 查询参数
 * @returns 线路走向详情列表数据
 */
export function GetList(query: PageQuery) {
	return request({
		url: apiPrefix,
		method: 'get',
		params: query,
	});
}

/**
 * 创建线路走向详情（标准DRF接口）
 * @param obj 线路走向详情数据
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
 * 更新线路走向详情（标准DRF接口）
 * @param obj 线路走向详情数据（必须包含id）
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
 * 删除线路走向详情（标准DRF接口）
 * @param id 详情ID
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
 * 导出线路走向详情数据
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
 * 启用/禁用线路走向详情
 * 请求方式：POST /api/RoadlineDetailViewSet/enable_roadline_detail/
 * @param data 启用参数 {id: number, enabled_mark: 0|1}
 * @returns 操作结果
 */
export function enableRoadlineDetail(data: { id: number; enabled_mark: 0 | 1 }) {
	return request({
		url: apiPrefix + 'enable_roadline_detail/',
		method: 'post',
		data: data,
	});
}

/**
 * 批量填充线路 POI 信息
 * 请求方式：POST /api/RoadlineDetailViewSet/batch_fill_poi/
 * @param params 填充参数
 * @returns 填充结果
 */
export function batchFillPoi(params: any = {}) {
	return request({
		url: apiPrefix + 'batch_fill_poi/',
		method: 'post',
		data: params,
	});
}

