/*
 * @Description: 公交线路复线情况 API 接口
 * @Version: 1.0
 * @Autor: 王晨
 * @Date: 2025-12-01 00:00:00
 * @LastEditors: 王晨
 * @LastEditTime: 2025-12-01 00:00:00
 */
import { request, downloadFile } from '/@/utils/service';
import { PageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

// API 前缀
export const apiPrefix = '/api/RoadlineToRoadlineOverlapModelViewSet/';

/**
 * 获取复线情况列表
 */
export function GetList(query: PageQuery) {
  return request({
    url: apiPrefix,
    method: 'get',
    params: query,
  });
}

/**
 * 获取复线情况详情
 */
export function GetObj(id: InfoReq) {
  return request({
    url: apiPrefix + id,
    method: 'get',
  });
}

/**
 * 创建复线情况
 */
export function AddObj(obj: AddReq) {
  return request({
    url: apiPrefix,
    method: 'post',
    data: obj,
  });
}

/**
 * 更新复线情况
 */
export function UpdateObj(obj: EditReq) {
  return request({
    url: apiPrefix + obj.id + '/',
    method: 'put',
    data: obj,
  });
}

/**
 * 删除复线情况
 */
export function DelObj(id: DelReq) {
  return request({
    url: apiPrefix + id + '/',
    method: 'delete',
    data: { id },
  });
}

/**
 * 导出复线情况数据（如果后端未实现可暂不使用）
 */
export function exportData(params: any) {
  return downloadFile({
    url: apiPrefix + 'export_data/',
    params: params,
    method: 'get',
  });
}


