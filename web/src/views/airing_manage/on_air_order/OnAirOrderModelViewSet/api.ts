/*
 * @Description: 上刊订单管理API接口
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
import { PageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

// API前缀
export const apiPrefix = '/api/OnAirOrderModelViewSet/';

/**
 * 获取上刊订单列表（标准DRF接口）
 * @param query 查询参数
 * @returns 上刊订单列表数据
 */
export function GetList(query: PageQuery) {
	return request({
		url: apiPrefix,
		method: 'get',
		params: query,
	});
}

/**
 * 创建上刊订单（标准DRF接口）
 * @param obj 上刊订单数据
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
 * 更新上刊订单（标准DRF接口）
 * @param obj 上刊订单数据（必须包含id）
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
 * 删除上刊订单（标准DRF接口）
 * @param id 上刊订单ID
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
 * 导出上刊订单数据
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
