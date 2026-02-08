/*
 * @Description: OSM节点管理API接口
 * @Version: 1.0
 * @Autor: 系统生成
 * @Date: 2025-10-23
 * 
 * 接口说明：
 * - 标准DRF接口：GetList, GetObj, AddObj, UpdateObj, DelObj
 */
import { request, downloadFile } from '/@/utils/service';
import { PageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

// API前缀
export const apiPrefix = '/api/OsmNodeModelViewSet/';

/**
 * 获取节点列表（标准DRF接口）
 * @param query 查询参数
 * @returns 节点列表数据
 */
export function GetList(query: PageQuery) {
	return request({
		url: apiPrefix,
		method: 'get',
		params: query,
	});
}

/**
 * 获取节点详情（标准DRF接口）
 * @param id 节点ID
 * @returns 节点详情数据
 */
export function GetObj(id: InfoReq) {
	return request({
		url: apiPrefix + id,
		method: 'get',
	});
}

/**
 * 创建节点（标准DRF接口）
 * @param obj 节点数据
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
 * 更新节点（标准DRF接口）
 * @param obj 节点数据（必须包含id）
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
 * 删除节点（标准DRF接口）
 * @param id 节点ID
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
 * 导出节点数据
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

