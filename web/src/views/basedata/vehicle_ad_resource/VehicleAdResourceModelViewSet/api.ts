/*
 * @Description: 车辆广告资源位管理API接口
 * @Version: 1.0
 * @Autor: AI Assistant
 * @Date: 2025-01-XX
 * @LastEditors: 
 * @LastEditTime: 2025-01-XX
 * 
 * 接口说明：
 * - 标准DRF接口：GetList, AddObj, UpdateObj, DelObj
 * - 自定义接口：getByVehicle（根据车辆ID获取资源位列表）、getAvailableResources（获取可用资源位列表）
 */
import { request, downloadFile } from '/@/utils/service';
import { PageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

// API前缀
export const apiPrefix = '/api/VehicleAdResourceModelViewSet/';

/**
 * 获取资源位列表（标准DRF接口）
 * @param query 查询参数
 * @returns 资源位列表数据
 */
export function GetList(query: PageQuery) {
	return request({
		url: apiPrefix,
		method: 'get',
		params: query,
	});
}

/**
 * 创建资源位（标准DRF接口）
 * @param obj 资源位数据
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
 * 批量创建资源位（支持多车辆 + 组合媒体类型自动拆分）
 * 请求方式：POST /api/VehicleAdResourceModelViewSet/bulk_create/
 * @param params { vehicle_ids: number[]|string[], media_type_id: string|number, remark?: string }
 */
export function bulkCreate(params: { vehicle_ids: Array<number | string>; media_type_id: number | string; remark?: string }) {
	return request({
		url: apiPrefix + 'bulk_create/',
		method: 'post',
		data: params,
	});
}

/**
 * 获取某辆车当前媒体类型（组合优先折叠后的展示）
 * GET /api/VehicleAdResourceModelViewSet/get_vehicle_media_types/?vehicle_id=xxx
 */
export function getVehicleMediaTypes(vehicle_id: string) {
	return request({
		url: apiPrefix + 'get_vehicle_media_types/',
		method: 'get',
		params: { vehicle_id },
	});
}

/**
 * 设置某辆车的媒体类型（支持组合类型自动拆分）
 * POST /api/VehicleAdResourceModelViewSet/set_vehicle_media_types/
 */
export function setVehicleMediaTypes(params: { vehicle_id: string; media_type_id: string; remark?: string }) {
	return request({
		url: apiPrefix + 'set_vehicle_media_types/',
		method: 'post',
		data: params,
	});
}

/**
 * 设置某辆车的媒体类型（多选：支持基础/组合混选，后端会取并集并拆分为基础类型集合）
 * POST /api/VehicleAdResourceModelViewSet/set_vehicle_media_types/
 */
export function setVehicleMediaTypesBatch(params: { vehicle_id: string; media_type_ids: string[]; remark?: string }) {
	return request({
		url: apiPrefix + 'set_vehicle_media_types/',
		method: 'post',
		data: params,
	});
}

/**
 * 更新资源位（标准DRF接口）
 * @param obj 资源位数据（必须包含id）
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
 * 删除资源位（标准DRF接口）
 * @param id 资源位ID
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
 * 导出资源位数据
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
 * 根据车辆ID获取资源位列表
 * 请求方式：GET /api/VehicleAdResourceModelViewSet/get_by_vehicle/?vehicle_id=1
 * @param vehicleId 车辆ID
 * @returns 资源位列表
 */
export function getByVehicle(vehicleId: number) {
	return request({
		url: apiPrefix + 'get_by_vehicle/',
		method: 'get',
		params: { vehicle_id: vehicleId },
	});
}

/**
 * 获取可用资源位列表（状态为空闲的资源位）
 * 请求方式：GET /api/VehicleAdResourceModelViewSet/get_available_resources/
 * @returns 可用资源位列表
 */
export function getAvailableResources() {
	return request({
		url: apiPrefix + 'get_available_resources/',
		method: 'get',
	});
}

