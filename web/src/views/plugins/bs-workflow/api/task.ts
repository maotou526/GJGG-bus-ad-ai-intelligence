import { request } from '/@/utils/service'

export function GetMyTasks(query: any) {
  return request({
    url: '/api/node_workflow/task/my-tasks/',
    method: 'get',
    params: query
  })
}

export function GetFinishedTasks(query: any) {
  return request({
    url: '/api/node_workflow/task/finished-tasks/',
    method: 'get',
    params: query
  })
}

export function GetMyCreateTasks(query: any) {
  return request({
    url: '/api/node_workflow/task/my-create-tasks/',
    method: 'get',
    params: query
  })
}

export function GetTaskLogByProcess(query: any) {
  return request({
    url: '/api/node_workflow/tasklog/by-process/',
    method: 'get',
    params: query
  })
}

export function GetMyMessages(query: any) {
  return request({
    url: '/api/node_workflow/taskmsg/my-messages/',
    method: 'get',
    params: query
  })
}
