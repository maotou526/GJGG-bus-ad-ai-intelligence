/*
 * @Description: AI审核反馈管理API接口
 * @Version: 1.0
 * @Date: 2026-02-04
 *
 * 接口说明：
 * - 标准DRF接口：GetList, GetObj, AddObj, UpdateObj, DelObj
 * - 自定义接口：AccuracyAnalysis（准确性分析）
 */
import { request, downloadFile } from '/@/utils/service';
import { PageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

// API前缀
export const apiPrefix = '/api/AIAuditFeedbackViewSet/';

/**
 * 获取AI审核反馈列表（标准DRF接口）
 * @param query 查询参数
 * @returns AI审核反馈列表数据
 */
export function GetList(query: PageQuery) {
	return request({
		url: apiPrefix,
		method: 'get',
		params: query,
	});
}

/**
 * 获取AI审核反馈详情（标准DRF接口）
 * @param id AI审核反馈ID
 * @returns AI审核反馈详情数据
 */
export function GetObj(id: InfoReq) {
	return request({
		url: apiPrefix + id + '/',
		method: 'get',
	});
}

/**
 * 创建AI审核反馈（标准DRF接口）
 * @param obj AI审核反馈数据
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
 * 更新AI审核反馈（标准DRF接口）
 * @param obj AI审核反馈数据（必须包含id）
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
 * 删除AI审核反馈（标准DRF接口）
 * @param id AI审核反馈ID
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
 * 导出AI审核反馈数据
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
 * 获取AI准确性分析（自定义接口）
 * @param params 分析参数（时间范围、审核员等）
 * @returns 准确性分析数据
 */
export function GetAccuracyAnalysis(params?: any) {
	return request({
		url: apiPrefix + 'accuracy_analysis/',
		method: 'get',
		params: params,
	});
}
