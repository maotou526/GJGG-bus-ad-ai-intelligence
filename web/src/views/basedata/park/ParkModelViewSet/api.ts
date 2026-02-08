/*
 * @Description: 停车场站管理API接口
 * @Version: 1.0
 * @Autor: 王晨
 * @Date: 2025-10-18
 * @LastEditors: 王晨
 * @LastEditTime: 2025-10-18
 * 
 * 接口说明：
 * - 标准DRF接口：GetList, GetObj, AddObj, UpdateObj, DelObj
 * - 自定义接口：deletePark（批量删除）, enablePark（启用/禁用）
 */
import { request, downloadFile } from '/@/utils/service';
import { PageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

// API前缀
export const apiPrefix = '/api/ParkModelViewSet/';

/**
 * 获取场站列表（标准DRF接口）
 * @param query 查询参数
 * @returns 场站列表数据
 */
export function GetList(query: PageQuery) {
	return request({
		url: apiPrefix,
		method: 'get',
		params: query,
	});
}

/**
 * 获取场站详情（标准DRF接口）
 * @param id 场站ID
 * @returns 场站详情数据
 */
export function GetObj(id: InfoReq) {
	return request({
		url: apiPrefix + id,
		method: 'get',
	});
}

/**
 * 创建场站（标准DRF接口）
 * @param obj 场站数据
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
 * 更新场站（标准DRF接口）
 * @param obj 场站数据（必须包含id）
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
 * 删除场站（标准DRF接口）
 * @param id 场站ID
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
 * 导出场站数据
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

// ==================== 自定义接口方法（只保留必要的业务功能） ====================

/**
 * 删除场站（自定义接口，支持软删除）
 * 请求方式：POST /api/ParkModelViewSet/delete_park/
 * @param data 删除参数 {id: number} 或 {ids: number[]}
 * @returns 删除结果
 */
export function deletePark(data: { id?: number; ids?: number[] }) {
	return request({
		url: apiPrefix + 'delete_park/',
		method: 'post',
		data: data,
	});
}


/**
 * 启用/禁用场站
 * 请求方式：POST /api/ParkModelViewSet/enable_park/
 * @param data 启用参数 {id: number, enabled_mark: 0|1}
 * @returns 操作结果
 */
export function enablePark(data: { id: number; enabled_mark: 0 | 1 }) {
	return request({
		url: apiPrefix + 'enable_park/',
		method: 'post',
		data: data,
	});
}
