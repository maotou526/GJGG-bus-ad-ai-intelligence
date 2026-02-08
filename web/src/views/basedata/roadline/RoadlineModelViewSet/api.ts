/*
 * @Description: 线路管理API接口
 * @Version: 1.0
 * @Autor: 王晨
 * @Date: 2025-10-10 11:19:29
 * @LastEditors: 王晨
 * @LastEditTime: 2025-10-23 15:48:59
 * 
 * 接口说明：
 * - 标准DRF接口：GetList, GetObj, AddObj, UpdateObj, DelObj
 * - 自定义接口：deleteRoadline（批量删除）, enableRoadline（启用/禁用）
 */
import { request, downloadFile } from '/@/utils/service';
import { PageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

// API前缀
export const apiPrefix = '/api/RoadlineModelViewSet/';

/**
 * 获取线路列表（标准DRF接口）
 * @param query 查询参数
 * @returns 线路列表数据
 */
export function GetList(query: PageQuery) {
	return request({
		url: apiPrefix,
		method: 'get',
		params: query,
	});
}

/**
 * 获取线路详情（标准DRF接口）
 * @param id 线路ID
 * @returns 线路详情数据
 */
export function GetObj(id: InfoReq) {
	return request({
		url: apiPrefix + id,
		method: 'get',
	});
}

/**
 * 创建线路（标准DRF接口）
 * @param obj 线路数据
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
 * 更新线路（标准DRF接口）
 * @param obj 线路数据（必须包含id）
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
 * 删除线路（标准DRF接口）
 * @param id 线路ID
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
 * 导出线路数据
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
 * 删除线路（自定义接口，支持软删除）
 * 请求方式：POST /api/RoadlineModelViewSet/delete_roadline/
 * @param data 删除参数 {id: number} 或 {ids: number[]}
 * @returns 删除结果
 */
export function deleteRoadline(data: { id?: number; ids?: number[] }) {
	return request({
		url: apiPrefix + 'delete_roadline/',
		method: 'post',
		data: data,
	});
}

export function GetPermission() {
    return request({
        url: apiPrefix + 'field_permission/',
        method: 'get',
    });
}