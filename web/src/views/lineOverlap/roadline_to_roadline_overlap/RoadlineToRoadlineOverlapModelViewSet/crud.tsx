import {
  CrudOptions,
  AddReq,
  DelReq,
  EditReq,
  CrudExpose,
  UserPageQuery,
  CreateCrudOptionsRet,
  dict,
} from '@fast-crud/fast-crud';
import * as api from './api';
import { auth } from '/@/utils/authFunction';
import { listPageDefSingleLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';

// 公交线路复线情况 crud 配置
export default function ({ crudExpose }: { crudExpose: CrudExpose }): CreateCrudOptionsRet {
  // 列表查询
  const pageRequest = async (query: any) => {
    return await api.GetList(query);
  };

  // 新增
  const addRequest = async ({ form }: AddReq) => {
    return await api.AddObj(form);
  };

  // 编辑
  const editRequest = async ({ form, row }: EditReq) => {
    if (row.id) {
      form.id = row.id;
    }
    return await api.UpdateObj(form);
  };

  // 删除
  const delRequest = async ({ row }: DelReq) => {
    return await api.DelObj(row.id);
  };

  // 导出
  const exportRequest = async (query: UserPageQuery) => {
    return await api.exportData(query);
  };

  return {
    crudOptions: {
      ...(listPageDefSingleLineCfg as CrudOptions),
      request: {
        pageRequest,
        addRequest,
        editRequest,
        delRequest,
      },
      form: {
        col: { span: 12 },
        labelWidth: '100px',
        wrapper: {
          is: 'el-dialog',
          width: '900px',
          closeOnClickModal: false,
        },
      },
      actionbar: {
        buttons: {
          export: {
            show: auth('RoadlineToRoadlineOverlapModelViewSet:Export'),
            text: '导出',
            title: '导出',
            click() {
              return exportRequest(crudExpose.getSearchFormData());
            },
          },
          add: {
            show: auth('RoadlineToRoadlineOverlapModelViewSet:Create'),
          },
        },
      },
      rowHandle: {
        fixed: 'right',
        width: 200,
        buttons: {
          view: {
            type: 'text',
            order: 1,
            show: auth('RoadlineToRoadlineOverlapModelViewSet:Retrieve'),
          },
          edit: {
            type: 'text',
            order: 2,
            show: auth('RoadlineToRoadlineOverlapModelViewSet:Update'),
          },
          remove: {
            type: 'text',
            order: 3,
            show: auth('RoadlineToRoadlineOverlapModelViewSet:Delete'),
          },
        },
      },
      columns: {
        _index: getIndexColumnConfig(crudExpose),
        main_roadline_code: {
          title: '主线路编号',
          type: 'input',
          search: { show: true },
          column: {
            minWidth: 140,
          },
          form: {
            component: {
              placeholder: '请输入主线路编号',
            },
          },
        },
        main_roadline_name: {
          title: '主线路名称',
          type: 'input',
          search: { show: true },
          column: {
            minWidth: 160,
          },
          form: {
            component: {
              placeholder: '请输入主线路名称',
            },
          },
        },
        main_roadline_updown: {
          title: '主线路上下行',
          type: 'dict-select',
          dict: dict({
            data: [
              { value: 0, label: '上行' },
              { value: 1, label: '下行' },
            ],
          }),
          search: { show: true },
          column: {
            minWidth: 120,
          },
          form: {
            component: {
              placeholder: '请选择主线路上下行',
            },
          },
        },
        vice_roadline_code: {
          title: '副线路编号',
          type: 'input',
          search: { show: true },
          column: {
            minWidth: 140,
          },
          form: {
            component: {
              placeholder: '请输入副线路编号',
            },
          },
        },
        vice_roadline_name: {
          title: '副线路名称',
          type: 'input',
          search: { show: true },
          column: {
            minWidth: 160,
          },
          form: {
            component: {
              placeholder: '请输入副线路名称',
            },
          },
        },
        vice_roadline_updown: {
          title: '副线路上下行',
          type: 'dict-select',
          dict: dict({
            data: [
              { value: 0, label: '上行' },
              { value: 1, label: '下行' },
            ],
          }),
          search: { show: false },
          column: {
            minWidth: 120,
          },
          form: {
            component: {
              placeholder: '请选择副线路上下行',
            },
          },
        },
        repeat_line_length: {
          title: '复线长度(km)',
          type: 'number',
          search: { show: false },
          column: {
            minWidth: 140,
          },
          form: {
            component: {
              placeholder: '请输入复线长度（km）',
              min: 0,
            },
          },
        },
        main_repeat_rate: {
          title: '主线路复线率',
          type: 'number',
          search: { show: false },
          column: {
            minWidth: 140,
            formatter: (context: any) => {
              const value = context.value;
              if (value === null || value === undefined) {
                return '-';
              }
              return `${(Number(value) * 100).toFixed(2)}%`;
            },
          },
          form: {
            component: {
              placeholder: '请输入主线路复线率（0-1）',
              min: 0,
              max: 1,
            },
          },
        },
        vice_repeat_rate: {
          title: '副线路复线率',
          type: 'number',
          search: { show: false },
          column: {
            minWidth: 140,
            formatter: (context: any) => {
              const value = context.value;
              if (value === null || value === undefined) {
                return '-';
              }
              return `${(Number(value) * 100).toFixed(2)}%`;
            },
          },
          form: {
            component: {
              placeholder: '请输入副线路复线率（0-1）',
              min: 0,
              max: 1,
            },
          },
        },
        exec_day: {
          title: '启用日期',
          type: 'date',
          search: { show: true },
          column: {
            minWidth: 130,
            component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
          },
          form: {
            component: {
              placeholder: '请选择启用日期',
              type: 'date',
              valueFormat: 'YYYY-MM-DD',
            },
          },
        },
        expiry_day: {
          title: '截止日期',
          type: 'date',
          search: { show: false },
          column: {
            minWidth: 130,
            component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
          },
          form: {
            component: {
              placeholder: '请选择截止日期',
              type: 'date',
              valueFormat: 'YYYY-MM-DD',
            },
          },
        },
        is_valid: {
          title: '是否有效',
          type: 'dict-select',
          dict: dict({
            data: [
              { value: true, label: '有效' },
              { value: false, label: '无效' },
            ],
          }),
          search: { show: true },
          column: {
            minWidth: 110,
          },
          form: {
            show: false,
          },
        },
        description: {
          title: '备注',
          type: 'textarea',
          search: { show: false },
          column: {
            minWidth: 180,
            show: false,
          },
          form: {
            component: {
              rows: 3,
              placeholder: '请输入备注',
            },
          },
        },
        creator_name: {
          title: '创建人',
          type: 'text',
          search: { show: false },
          column: {
            minWidth: 100,
            show: false,
          },
          form: { show: false },
        },
        modifier_name: {
          title: '修改人',
          type: 'text',
          search: { show: false },
          column: {
            minWidth: 100,
            show: false,
          },
          form: { show: false },
        },
        create_datetime: {
          title: '创建时间',
          type: 'datetime',
          search: { show: false },
          column: {
            align: 'center',
            width: 160,
            component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
            show: false,
          },
          form: { show: false },
        },
        update_datetime: {
          title: '更新时间',
          type: 'datetime',
          search: { show: false },
          column: {
            align: 'center',
            width: 160,
            component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
            show: false,
          },
          form: { show: false },
        },
      },
    },
  };
}


