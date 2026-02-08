/*
 * @Description: 代理商资源授权管理API接口
 * @Version: 1.0
 * @Autor: AI Assistant
 * @Date: 2025-01-XX
 * @LastEditors: 
 * @LastEditTime: 2025-01-XX
 * 
 * 接口说明：
 * - 标准DRF接口：GetList, AddObj, UpdateObj, DelObj
 * - 自定义接口：getByAgent（根据代理商ID获取授权列表）
 */
import { request, downloadFile } from '/@/utils/service';
import { PageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

// API前缀
export const apiPrefix = '/api/AgentResourceAuthModelViewSet/';

/**
 * 获取授权列表（标准DRF接口）
 * @param query 查询参数
 * @returns 授权列表数据
 */
export function GetList(query: PageQuery) {
	return request({
		url: apiPrefix,
		method: 'get',
		params: query,
	});
}

/**
 * 创建授权（标准DRF接口）
 * @param obj 授权数据
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
 * 更新授权（标准DRF接口）
 * @param obj 授权数据（必须包含id）
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
 * 删除授权（标准DRF接口）
 * @param id 授权ID
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
 * 导出授权数据
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
 * 根据代理商ID获取授权列表
 * 请求方式：GET /api/AgentResourceAuthModelViewSet/get_by_agent/?agent_id=1
 * @param agentId 代理商ID
 * @returns 授权列表
 */
export function getByAgent(agentId: number) {
	return request({
		url: apiPrefix + 'get_by_agent/',
		method: 'get',
		params: { agent_id: agentId },
	});
}

