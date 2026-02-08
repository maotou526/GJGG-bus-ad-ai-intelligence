import { request } from '/@/utils/service'

export function GetList(query: any) {
  return request({
    url: '/api/node_workflow/schemeinfo/',
    method: 'get',
    params: query
  })
}

export function GetObj(id: any) {
  return request({
    url: '/api/node_workflow/scheme/' + id + '/',
    method: 'get'
  })
}

export function AddObj(obj: any) {
  return request({
    url: '/api/node_workflow/scheme/',
    method: 'post',
    data: obj
  })
}

export function UpdateObj(obj: any) {
  return request({
    url: '/api/node_workflow/scheme/' + obj.id + '/',
    method: 'patch',
    data: obj
  })
}

// 新的保存方法（兼容原始力软数据格式）
export function SaveSchemeData(data: any) {
  return request({
    url: '/api/node_workflow/scheme/save-scheme-data/',
    method: 'post',
    data: data
  })
}

export function DelObj(id: any) {
  return request({
    url: '/api/node_workflow/schemeinfo/' + id + '/',
    method: 'delete'
  })
}

export function GetBySchemeInfo(query: any) {
  return request({
    url: '/api/node_workflow/scheme/by-scheme-info/',
    method: 'get',
    params: query
  })
}

export function GetContent(id: any) {
  return request({
    url: '/api/node_workflow/scheme/' + id + '/content/',
    method: 'get'
  })
}

// 获取流程模板表单数据（用于编辑）
export function GetFormData(schemeInfoId: any) {
  return request({
    url: '/api/node_workflow/scheme/form-data/',
    method: 'get',
    params: { scheme_info_id: schemeInfoId }
  })
}

// Scheme Auth API
export function GetAuthList(query: any) {
  return request({
    url: '/api/node_workflow/scheme_auth/by-scheme-info/',
    method: 'get',
    params: query
  })
}

export function SaveAuthList(data: any) {
  return request({
    url: '/api/node_workflow/scheme_auth/batch-save/',
    method: 'post',
    data: data
  })
}

// 启用流程模板
export function EnableScheme(id: any) {
  return request({
    url: '/api/node_workflow/scheme/enable/',
    method: 'post',
    data: { id }
  })
}

// 停用流程模板
export function DisableScheme(id: any) {
  return request({
    url: '/api/node_workflow/scheme/disable/',
    method: 'post',
    data: { id }
  })
}
