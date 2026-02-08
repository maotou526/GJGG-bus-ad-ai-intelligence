/*
 * @Description: 车位广告变更历史管理API接口
 * @Version: 1.0
 * @Autor: AI Assistant
 * @Date: 2025-01-XX
 * @LastEditors:
 * @LastEditTime: 2025-01-XX
 *
 * 接口说明：
 * - 标准DRF接口：GetList, AddObj, UpdateObj, DelObj
 */
import { request, downloadFile } from '/@/utils/service';
import { PageQuery, AddReq, DelReq, EditReq } from '@fast-crud/fast-crud';

// API前缀
export const apiPrefix = '/api/VehicleAdPositionChangeModelViewSet/';

/**
 * 获取车位广告变更历史列表（标准DRF接口）
 * @param query 查询参数
 * @returns 车位广告变更历史列表数据
 */
export function GetList(query: PageQuery) {
	return request({
		url: apiPrefix,
		method: 'get',
		params: query,
	});
}

/**
 * 创建车位广告变更历史记录（标准DRF接口）
 * @param obj 变更历史数据
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
 * 更新车位广告变更历史记录（一般不常用，仅预留）
 * @param obj 变更历史数据（必须包含id）
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
 * 删除车位广告变更历史记录（一般不建议物理删除，仅预留）
 * @param id 记录ID
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
 * 导出车位广告变更历史数据（预留，当前后端未实现时可不使用）
 * @param params 导出参数
 * @returns 导出文件
 */
export function exportData(params: any) {
	return downloadFile({
		url: apiPrefix + 'export_data/',
		params: params,
		method: 'get',
	});
}


