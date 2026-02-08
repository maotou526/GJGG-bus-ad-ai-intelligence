/*
 * @Description: AI审核记录管理API接口
 * @Version: 1.0
 * @Date: 2026-02-04
 *
 * 接口说明：
 * - 标准DRF接口：GetList, GetObj, AddObj, UpdateObj, DelObj
 * - 自定义接口：Statistics（审核统计）
 */
import { request, downloadFile } from '/@/utils/service';
import { PageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

// API前缀
export const apiPrefix = '/api/AIAuditLogViewSet/';

/**
 * 获取AI审核记录列表（标准DRF接口）
 * @param query 查询参数
 * @returns AI审核记录列表数据
 */
export function GetList(query: any) {
	return request({
		url: apiPrefix,
		method: 'get',
		params: query,
	});
}

/**
 * 获取AI审核记录详情（标准DRF接口）
 * @param id AI审核记录ID
 * @returns AI审核记录详情数据
 */
export function GetObj(id: any) {
	return request({
		url: apiPrefix + id + '/',
		method: 'get',
	});
}

/**
 * 创建AI审核记录（标准DRF接口）
 * @param obj AI审核记录数据
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
 * 更新AI审核记录（标准DRF接口）
 * @param obj AI审核记录数据（必须包含id）
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
 * 删除AI审核记录（标准DRF接口）
 * @param id AI审核记录ID
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
 * 导出AI审核记录数据
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
 * 审核统计
 * @returns 统计数据
 */
export function getStatistics() {
	return request({
		url: apiPrefix + 'statistics/',
		method: 'get'
	});
}

/**
 * 上传文件并触发AI审核
 * @param data FormData对象
 * @returns 审核结果
 */
export function uploadAndAudit(data: FormData) {
	return request({
		url: apiPrefix + 'upload_and_audit/',
		method: 'post',
		data: data,
		headers: {
			'Content-Type': 'multipart/form-data'
		}
	});
}