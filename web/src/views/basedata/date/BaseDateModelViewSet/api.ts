/*
 * @Description: 基础日期管理API接口
 * @Version: 1.0
 * @Autor: 王晨
 * @Date: 2025-10-23
 * @LastEditors: 王晨
 * @LastEditTime: 2025-10-23
 * 
 * 接口说明：
 * - 标准DRF接口：GetList, GetObj, AddObj, UpdateObj, DelObj
 * - 自定义接口：InitYear（初始化年度数据）
 */
import { request, downloadFile } from '/@/utils/service';
import { PageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

// API前缀
export const apiPrefix = '/api/BaseDateModelViewSet/';

/**
 * 获取日期列表（标准DRF接口）
 * @param query 查询参数
 * @returns 日期列表数据
 */
export function GetList(query: PageQuery) {
	return request({
		url: apiPrefix,
		method: 'get',
		params: query,
	});
}

/**
 * 获取日期详情（标准DRF接口）
 * @param id 日期ID
 * @returns 日期详情数据
 */
export function GetObj(id: InfoReq) {
	return request({
		url: apiPrefix + id,
		method: 'get',
	});
}

/**
 * 创建日期（标准DRF接口）
 * @param obj 日期数据
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
 * 更新日期（标准DRF接口）
 * @param obj 日期数据（必须包含id）
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
 * 删除日期（标准DRF接口）
 * @param id 日期ID
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
 * 导出日期数据
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
 * 初始化年度数据（自定义接口）
 * @param year 年份，不传则使用当前年份
 * @returns 初始化结果
 */
export function InitYear(year?: number) {
	return request({
		url: apiPrefix + 'init_year/',
		method: 'post',
		data: { year },
	});
}

