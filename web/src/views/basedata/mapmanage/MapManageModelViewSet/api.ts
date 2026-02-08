/*
 * @Description: 地图查询管理API接口
 * @Version: 1.0
 * @Autor: AI Assistant
 * @Date: 2025-01-XX
 * @LastEditors: 
 * @LastEditTime: 2025-01-XX
 * 
 * 接口说明：
 * - 地图查询相关接口
 * - 获取高德地图API Key
 */
import { request } from '/@/utils/service';
import { PageQuery } from '@fast-crud/fast-crud';

// API前缀
export const apiPrefix = '/api/MapManageModelViewSet/';

/**
 * 获取高德地图API Key
 * 从后端env.py中读取AMAP_API_KEY
 * @returns 高德地图API Key
 */
export function getAmapApiKey() {
	return request({
		url: apiPrefix + 'get_amap_api_key/',
		method: 'get',
	});
}

/**
 * 地图查询 - 获取线路列表（用于地图展示）
 * @param query 查询参数
 * @returns 线路列表数据（包含轨迹和站点信息）
 */
export function getMapManageList(query: {
	wd?: string; // 关键词搜索（线路名称）
	lineName?: string; // 线路名称
	company?: string; // 营运公司
	limit?: number; // 返回数量限制
}) {
	return request({
		url: apiPrefix + 'get_manage_list/',
		method: 'get',
		params: query,
	});
}

/**
 * 获取线路详情（包含轨迹点数据）
 * @param id 线路ID
 * @returns 线路详情（包含轨迹坐标）
 */
export function getRoadlineDetail(id: number) {
	return request({
		url: apiPrefix + `get_roadline_detail/${id}/`,
		method: 'get',
	});
}

/**
 * 获取线路站点列表
 * @param query 查询参数
 * @returns 站点列表数据
 */
export function getRoadlineStops(query: {
	roadline_id?: number; // 线路ID
	updown?: number; // 上下行（0-上行，1-下行）
}) {
	return request({
		url: apiPrefix + 'get_roadline_stops/',
		method: 'get',
		params: query,
	});
}
