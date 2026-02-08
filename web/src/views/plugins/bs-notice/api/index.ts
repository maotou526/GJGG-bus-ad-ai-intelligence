import { request } from '/@/utils/service';
import { PageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

export const apiPrefix = '/api/bs_notice/notice_user/';
export const noticeApiPrefix = '/api/bs_notice/notice/';

/**
 * 获取用户消息列表（标准DRF接口）
 */
export function GetList(query: PageQuery) {
	return request({
		url: apiPrefix,
		method: 'get',
		params: query,
	});
}

/**
 * 获取消息详情（标准DRF接口）
 */
export function GetObj(id: InfoReq) {
	return request({
		url: apiPrefix + id + '/',
		method: 'get',
	});
}

/**
 * 获取未读消息数量
 */
export function getUnreadCount() {
	return request({
		url: apiPrefix + 'unread_count/',
		method: 'get',
	});
}

/**
 * 标记消息为已读
 */
export function markAsRead(id: string) {
	return request({
		url: apiPrefix + id + '/mark_read/',
		method: 'post',
	});
}

/**
 * 标记消息为已处理
 */
export function markAsHandled(id: string) {
	return request({
		url: apiPrefix + id + '/mark_handled/',
		method: 'post',
	});
}

/**
 * 标记消息为已忽略
 */
export function markAsIgnored(id: string) {
	return request({
		url: apiPrefix + id + '/mark_ignored/',
		method: 'post',
	});
}

/**
 * 删除消息（软删除）
 */
export function deleteNotice(id: string) {
	return request({
		url: apiPrefix + id + '/delete_notice/',
		method: 'post',
	});
}

/**
 * 批量标记已读
 */
export function batchMarkRead(ids: string[]) {
	return request({
		url: apiPrefix + 'batch_mark_read/',
		method: 'post',
		data: { ids },
	});
}

/**
 * 批量删除
 */
export function batchDelete(ids: string[]) {
	return request({
		url: apiPrefix + 'batch_delete/',
		method: 'post',
		data: { ids },
	});
}

/**
 * 获取当前用户的消息列表（按用户过滤，权限安全）
 */
export function getMyNotices(params?: Record<string, any>) {
	return request({
		url: apiPrefix + 'my_notices/',
		method: 'get',
		params,
	});
}

/**
 * 发送通知（管理端）
 */
export function sendNotification(data: any) {
	return request({
		url: noticeApiPrefix + 'send_notification/',
		method: 'post',
		data,
	});
}
