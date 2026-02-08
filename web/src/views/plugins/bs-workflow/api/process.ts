import { request } from '/@/utils/service'

export function CreateFlow(data: any) {
  return request({
    url: '/api/node_workflow/process/create-flow/',
    method: 'post',
    data: data
  })
}

export function AuditFlow(data: any) {
  return request({
    url: '/api/node_workflow/process/audit-flow/',
    method: 'post',
    data: data
  })
}

export function SignFlow(data: any) {
  return request({
    url: '/api/node_workflow/process/sign-flow/',
    method: 'post',
    data: data
  })
}

export function RevokeFlow(data: any) {
  return request({
    url: '/api/node_workflow/process/revoke-flow/',
    method: 'post',
    data: data
  })
}

export function UrgeFlow(data: any) {
  return request({
    url: '/api/node_workflow/process/urge-flow/',
    method: 'post',
    data: data
  })
}

export function ReferFlow(data: any) {
  return request({
    url: '/api/node_workflow/process/refer-flow/',
    method: 'post',
    data: data
  })
}

export function GetNextAuditors(query: any) {
  return request({
    url: '/api/node_workflow/process/get-next-auditors/',
    method: 'get',
    params: query
  })
}

export function GetProcessDetails(query: any) {
  return request({
    url: '/api/node_workflow/process/get-process-details/',
    method: 'get',
    params: query
  })
}

export function GetSchemeByCode(query: any) {
    return request({
      url: '/api/node_workflow/process/get-scheme-by-code/',
      method: 'get',
      params: query
    })
  }

export function GetTaskPageList(query: any) {
  let url = '/api/node_workflow/task/my-todo/' // 默认待办
  if (query.categoryId === '1') {
    url = '/api/node_workflow/task/my-create/'
  } else if (query.categoryId === '3') {
    url = '/api/node_workflow/task/my-done/'
  }
  return request({
    url: url,
    method: 'get',
    params: query
  })
}

export function DeleteDraft(data: any) {
    return request({
        url: `/api/node_workflow/process/${data.processId}/`,
        method: 'delete',
        data: data
    })
}

export function RevokeAudit(data: any) {
    return request({
        url: '/api/node_workflow/process/revoke-audit/',
        method: 'post',
        data: data
    })
}
