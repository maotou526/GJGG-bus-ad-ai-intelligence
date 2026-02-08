/*
 * @Description: 媒体类型管理API接口
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
export const apiPrefix = '/api/AdMediaTypeModelViewSet/';

/**
 * 获取媒体类型列表（标准DRF接口）
 * @param query 查询参数
 * @returns 媒体类型列表数据
 */
export function GetList(query: PageQuery) {
	return request({
		url: apiPrefix,
		method: 'get',
		params: query,
	});
}

/**
 * 创建媒体类型（标准DRF接口）
 * @param obj 媒体类型数据
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
 * 更新媒体类型（标准DRF接口）
 * @param obj 媒体类型数据（必须包含id）
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
 * 删除媒体类型（标准DRF接口）
 * @param id 媒体类型ID
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
 * 导出媒体类型数据
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

/**
 * 获取基础类型列表（用于组合类型选择）
 * @param params 查询参数
 * @returns 基础类型列表
 */
export function GetBaseTypes(params: any) {
	return request({
		url: apiPrefix,
		method: 'get',
		params: params,
	});
}

/**
 * 保存组合关系
 * @param compositeTypeId 组合类型ID
 * @param compositions 组合关系数据数组
 * @returns 保存结果
 */
export function SaveCompositions(compositeTypeId: string, compositions: any[]) {
	return request({
		url: '/api/AdMediaTypeCompositionModelViewSet/batch_save/',
		method: 'post',
		data: {
			composite_type_id: compositeTypeId,
			compositions: compositions,
		},
	});
}

/**
 * 获取组合关系列表
 * @param compositeTypeId 组合类型ID
 * @returns 组合关系列表
 */
export function GetCompositions(compositeTypeId: string) {
	return request({
		url: '/api/AdMediaTypeCompositionModelViewSet/',
		method: 'get',
		params: {
			composite_type_id: compositeTypeId,
		},
	});
}
