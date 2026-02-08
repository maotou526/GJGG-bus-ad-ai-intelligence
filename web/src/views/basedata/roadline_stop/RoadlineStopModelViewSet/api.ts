/*
 * @Description: 站点管理API接口
 * @Version: 1.0
 * @Autor: 王晨
 * @Date: 2025-10-14
 * @LastEditors: 王晨
 * @LastEditTime: 2025-10-14
 * 
 * 接口说明：
 * - 标准DRF接口：GetList, AddObj, UpdateObj, DelObj
 * - 自定义接口：enableRoadlineStop（启用/禁用）
 */
import { request, downloadFile } from '/@/utils/service';
import { PageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

// API前缀
export const apiPrefix = '/api/RoadlineStopModelViewSet/';

/**
 * 获取站点列表（标准DRF接口）
 * @param query 查询参数
 * @returns 站点列表数据
 */
export function GetList(query: PageQuery) {
	return request({
		url: apiPrefix,
		method: 'get',
		params: query,
	});
}

/**
 * 创建站点（标准DRF接口）
 * @param obj 站点数据
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
 * 更新站点（标准DRF接口）
 * @param obj 站点数据（必须包含id）
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
 * 删除站点（标准DRF接口）
 * @param id 站点ID
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
 * 导出站点数据
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
 * 启用/禁用站点
 * 请求方式：POST /api/RoadlineStopViewSet/enable_roadline_stop/
 * @param data 启用参数 {id: number, enabled_mark: 0|1}
 * @returns 操作结果
 */
export function enableRoadlineStop(data: { id: number; enabled_mark: 0 | 1 }) {
	return request({
		url: apiPrefix + 'enable_roadline_stop/',
		method: 'post',
		data: data,
	});
}

/**
 * 自动填充站点数据（调用高德逆地理编码API）
 * 请求方式：POST /api/RoadlineStopModelViewSet/auto_fill_data/
 * 
 * 填充字段：
 * - area（环域）= addressComponent.city
 * - district（区属）= addressComponent.district
 * - roadline_name（道路名称）= addressComponent.streetNumber.street
 * - street（街道）= addressComponent.township
 * - stop_address（站点地址）= regeocode.formatted_address
 * 
 * @param data 参数
 * @returns 操作结果
 */
export function autoFillData(data?: {
	stop_ids?: number[];
	amap_key?: string;
	batch_size?: number;
	delay?: number;
	force_update?: boolean;
}) {
	return request({
		url: apiPrefix + 'auto_fill_data/',
		method: 'post',
		data: data || {},
	});
}

/**
 * 坐标转换：GCJ-02（高德坐标系）→ WGS84（国际标准坐标系）
 * 请求方式：POST /api/RoadlineStopModelViewSet/convert_coordinates/
 * 
 * 功能说明：
 * - 读取数据库中的 lon02 和 lat02 字段（GCJ-02坐标）
 * - 使用坐标转换工具类将其转换为 WGS84 坐标系
 * - 将转换后的坐标存储到 lon84 和 lat84 字段
 * 
 * @param data 参数
 * @returns 操作结果
 */
export function convertCoordinates(data?: {
	stop_ids?: number[];
	force_update?: boolean;
	batch_size?: number;
	delay?: number;
}) {
	return request({
		url: apiPrefix + 'convert_coordinates/',
		method: 'post',
		data: data || {},
	});
}

