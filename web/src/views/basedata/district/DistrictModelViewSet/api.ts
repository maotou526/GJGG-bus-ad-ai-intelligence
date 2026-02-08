/*
 * @Description: 区属管理API接口
 * @Version: 1.0
 * @Autor: AI Assistant
 * @Date: 2025-10-16
 * @LastEditors: 
 * @LastEditTime: 2025-10-16
 * 
 * 接口说明：
 * - 标准DRF接口：GetList, AddObj, UpdateObj, DelObj
 * - 自定义接口：deleteDistrict（批量删除）, enableDistrict（启用/禁用）, generateFromAmap（从高德地图生成）
 */
import { request, downloadFile } from '/@/utils/service';
import { PageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

// API前缀
export const apiPrefix = '/api/DistrictModelViewSet/';

/**
 * 获取区属列表（标准DRF接口）
 * @param query 查询参数
 * @returns 区属列表数据
 */
export function GetList(query: PageQuery) {
	return request({
		url: apiPrefix,
		method: 'get',
		params: query,
	});
}

/**
 * 创建区属（标准DRF接口）
 * @param obj 区属数据
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
 * 更新区属（标准DRF接口）
 * @param obj 区属数据（必须包含id）
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
 * 删除区属（标准DRF接口）
 * @param id 区属ID
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
 * 导出区属数据
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
 * 删除区属（自定义接口，支持软删除）
 * 请求方式：POST /api/DistrictModelViewSet/delete_district/
 * @param data 删除参数 {id: number} 或 {ids: number[]}
 * @returns 删除结果
 * 
 * 注意：如果区属有子级，不允许删除
 */
export function deleteDistrict(data: { id?: number; ids?: number[] }) {
	return request({
		url: apiPrefix + 'delete_district/',
		method: 'post',
		data: data,
	});
}

/**
 * 启用/禁用区属
 * 请求方式：POST /api/DistrictModelViewSet/enable_district/
 * @param data 启用参数 {id: number, enabled_mark: 0|1}
 * @returns 操作结果
 */
export function enableDistrict(data: { id: number; enabled_mark: 0 | 1 }) {
	return request({
		url: apiPrefix + 'enable_district/',
		method: 'post',
		data: data,
	});
}

/**
 * 从高德地图生成行政区数据
 * 请求方式：POST /api/DistrictModelViewSet/generate_from_amap/
 * @param data 生成参数
 * @returns 生成结果
 * 
 * 请求参数：
 * {
 *   root_keywords: "江苏省",  // 起始区域，默认"中国"
 *   subdistrict: 3           // 层级深度，默认3（省-市-区）
 * }
 * 
 * 返回示例：
 * {
 *   code: 2000,
 *   data: {
 *     deleted_count: 10,
 *     created_count: 100,
 *     root_keywords: "江苏省",
 *     subdistrict: 3
 *   },
 *   msg: "生成成功！删除 10 条，创建 100 条区属数据"
 * }
 */
export function generateFromAmap(data: { root_keywords?: string; subdistrict?: number }) {
	return request({
		url: apiPrefix + 'generate_from_amap/',
		method: 'post',
		data: data,
	});
}

