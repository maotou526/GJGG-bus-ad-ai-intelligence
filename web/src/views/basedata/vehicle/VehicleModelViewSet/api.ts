/*
 * @Description: 车辆管理API接口
 * @Version: 1.0
 * @Autor: 王晨
 * @Date: 2025-10-18
 * @LastEditors: 王晨
 * @LastEditTime: 2025-10-18
 * 
 * 接口说明：
 * - 标准DRF接口：GetList, AddObj, UpdateObj, DelObj
 * - 自定义接口：enableVehicle（启用/禁用）
 */
import { request, downloadFile } from '/@/utils/service';
import { PageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

// API前缀
export const apiPrefix = '/api/VehicleModelViewSet/';

/**
 * 获取车辆列表（标准DRF接口）
 * @param query 查询参数
 * @returns 车辆列表数据
 */
export function GetList(query: PageQuery) {
	return request({
		url: apiPrefix,
		method: 'get',
		params: query,
	});
}

/**
 * 创建车辆（标准DRF接口）
 * @param obj 车辆数据
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
 * 更新车辆（标准DRF接口）
 * @param obj 车辆数据（必须包含id）
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
 * 删除车辆（标准DRF接口）
 * @param id 车辆ID
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
 * 导出车辆数据
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
 * 启用/禁用车辆
 * 请求方式：POST /api/VehicleModelViewSet/enable_vehicle/
 * @param data 启用参数 {id: number, enabled_mark: 0|1}
 * @returns 操作结果
 */
export function enableVehicle(data: { id: number; enabled_mark: 0 | 1 }) {
	return request({
		url: apiPrefix + 'enable_vehicle/',
		method: 'post',
		data: data,
	});
}

/**
 * 从OD数据填充车辆信息
 * 请求方式：POST /api/VehicleModelViewSet/populate_from_od/
 * @param data 填充参数 {company_name?: string, limit?: number}
 * @returns 填充结果
 */
export function populateFromOd(data?: { company_name?: string; limit?: number }) {
	return request({
		url: apiPrefix + 'populate_from_od/',
		method: 'post',
		data: data || {},
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
		params: { 
			page: 1, 
			limit: 1000,
			enabled_mark: 1,
			delete_mark: 0
		},
	});
}

