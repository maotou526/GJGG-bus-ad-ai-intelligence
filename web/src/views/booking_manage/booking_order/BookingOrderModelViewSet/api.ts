/*
 * @Description: 预订订单管理API接口
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
export const apiPrefix = '/api/BookingOrderModelViewSet/';

/**
 * 获取预订订单列表（标准DRF接口）
 * @param query 查询参数
 * @returns 预订订单列表数据
 */
export function GetList(query: PageQuery) {
	return request({
		url: apiPrefix,
		method: 'get',
		params: query,
	});
}

/**
 * 创建预订订单（标准DRF接口）
 * @param obj 预订订单数据
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
 * 更新预订订单（标准DRF接口）
 * @param obj 预订订单数据（必须包含id）
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
 * 删除预订订单（标准DRF接口）
 * @param id 预订订单ID
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
 * 导出预订订单数据
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

// ==================== 审批流程接口 ====================

/** 提交审批（草稿 → 待媒体部初审） */
export function submitForApproval(id: string) {
    return request({ url: apiPrefix + id + '/submit/', method: 'post' });
}

/** 媒体部初审通过 */
export function firstReviewApprove(id: string, data?: { review_comment?: string }) {
    return request({ url: apiPrefix + id + '/first_review_approve/', method: 'post', data });
}

/** 媒体部初审驳回 */
export function firstReviewReject(id: string, data: { reject_reason: string }) {
    return request({ url: apiPrefix + id + '/first_review_reject/', method: 'post', data });
}

/** 营运公司确认车位 */
export function companyConfirmPosition(id: string, data: { position_id: string }) {
    return request({ url: apiPrefix + id + '/company_confirm_position/', method: 'post', data });
}

/** 营运公司剔除车位 */
export function companyExcludePosition(id: string, data: { position_id: string; exclude_reason: string }) {
    return request({ url: apiPrefix + id + '/company_exclude_position/', method: 'post', data });
}

/** 营运公司换车 */
export function companySwapVehicle(id: string, data: { position_id: string; new_vehicle_id: string; swap_reason?: string }) {
    return request({ url: apiPrefix + id + '/company_swap_vehicle/', method: 'post', data });
}

/** 营运公司批量确认 */
export function companyBatchConfirm(id: string, data?: { company_id?: string }) {
    return request({ url: apiPrefix + id + '/company_batch_confirm/', method: 'post', data });
}

/** 营运公司审核完成 */
export function companyReviewComplete(id: string, data?: { review_comment?: string }) {
    return request({ url: apiPrefix + id + '/company_review_complete/', method: 'post', data });
}

/** 媒体部复审通过 */
export function finalReviewApprove(id: string, data?: { review_comment?: string }) {
    return request({ url: apiPrefix + id + '/final_review_approve/', method: 'post', data });
}

/** 媒体部复审驳回 */
export function finalReviewReject(id: string, data: { reject_reason: string }) {
    return request({ url: apiPrefix + id + '/final_review_reject/', method: 'post', data });
}

/** 驳回后重新发起 */
export function resubmit(id: string) {
    return request({ url: apiPrefix + id + '/resubmit/', method: 'post' });
}

/** 取消预订单 */
export function cancelOrder(id: string, data?: { cancel_reason?: string }) {
    return request({ url: apiPrefix + id + '/cancel/', method: 'post', data });
}

/** 获取当前用户可执行操作 */
export function getAvailableActions(id: string) {
    return request({ url: apiPrefix + id + '/get_available_actions/', method: 'get' });
}

/** 审批中新增车位 */
export function reviewAddPosition(id: string, data: { booking_detail_id: string; vehicle_id: string; reason?: string }) {
    return request({ url: apiPrefix + id + '/review_add_position/', method: 'post', data });
}

/** 审批中删除车位 */
export function reviewRemovePosition(id: string, data: { position_id: string; reason?: string }) {
    return request({ url: apiPrefix + id + '/review_remove_position/', method: 'post', data });
}

/** 按营运公司分组获取车位 */
export function getPositionsByCompany(id: string) {
    return request({ url: apiPrefix + id + '/get_positions_by_company/', method: 'get' });
}

