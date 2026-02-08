import { CrudOptions, AddReq, DelReq, EditReq, CrudExpose, CreateCrudOptionsRet, dict } from '@fast-crud/fast-crud';
import * as api from './api';
import { listPageDefSingleLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';
import { auth } from '/@/utils/authFunction';

export default function ({ crudExpose }: { crudExpose: CrudExpose }): CreateCrudOptionsRet {
	const pageRequest = async (query: any) => {
		return await api.GetList(query);
	};

	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}
		return await api.UpdateObj(form);
	};

	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	const addRequest = async ({ form }: AddReq) => {
		return await api.AddObj(form);
	};

	const exportRequest = async (query: any) => {
		return await api.exportData(query);
	};

	return {
		crudOptions: {
			...listPageDefSingleLineCfg,
			request: {
				pageRequest,
				addRequest,
				editRequest,
				delRequest,
			},
			form: {
				col: { span: 12 },
				labelWidth: '120px',
				wrapper: {
					is: 'el-dialog',
					width: '800px',
					closeOnClickModal: false,
				},
			},
			actionbar: {
				buttons: {
					export: {
						show: auth('VehicleTypeModelViewSet:Export'),
						text: '导出',
						title: '导出',
						click() {
							return exportRequest(crudExpose.getSearchFormData());
						},
					},
					add: {
						show: auth('VehicleTypeModelViewSet:Create'),
					},
				},
			},
			rowHandle: {
				fixed: 'right',
				width: 160,
				buttons: {
					view: {
						type: 'text',
						order: 1,
						show: auth('VehicleTypeModelViewSet:Retrieve'),
					},
					edit: {
						type: 'text',
						order: 2,
						show: auth('VehicleTypeModelViewSet:Update'),
					},
					remove: {
						type: 'text',
						order: 3,
						show: auth('VehicleTypeModelViewSet:Delete'),
					},
				},
			},
			columns: {
				_index: getIndexColumnConfig(crudExpose),
				company_name: {
					title: '公司名称',
					type: 'input',
					search: { show: true },
					column: { minWidth: 160, sortable: 'custom' },
					form: { component: { placeholder: '请输入公司名称' } },
				},
				company_code: {
					title: '公司编码',
					type: 'input',
					search: { show: true },
					column: { minWidth: 120, sortable: 'custom', show: false },
					form: { component: { placeholder: '请输入公司编码' } },
				},
				vehicle_model_code: {
					title: '车型编号',
					type: 'input',
					search: { show: true },
					column: { minWidth: 120, sortable: 'custom' },
					form: { component: { placeholder: '请输入车型编号' } },
				},
				vehicle_model_name: {
					title: '车型',
					type: 'input',
					search: { show: true },
					column: { minWidth: 140, sortable: 'custom' },
					form: {
						rules: [{ required: true, message: '车型必填' }],
						component: { placeholder: '请输入车型名称' },
					},
				},
				rated_passenger_capacity: {
					title: '额定载客量(人)',
					type: 'number',
					search: { show: false },
					column: { minWidth: 140, sortable: 'custom' },
					form: { component: { placeholder: '请输入额定载客量', precision: 0, min: 0 } },
				},
				is_purchased_model: {
					title: '是否已购车型',
					type: 'dict-select',
					search: { show: true },
					dict: dict({ data: [{ value: 1, label: '是' }, { value: 0, label: '否' }] }),
					column: { minWidth: 120, sortable: 'custom' },
					form: { component: { placeholder: '请选择是否已购' } },
				},
				enabled_mark: {
					title: '启用状态',
					type: 'dict-select',
					search: { show: true },
					dict: dict({ data: [{ value: 1, label: '启用' }, { value: 0, label: '禁用' }] }),
					column: { minWidth: 100, sortable: 'custom', show: false },
					form: { component: { placeholder: '请选择启用状态' } },
				},
				description: {
					title: '描述',
					type: 'textarea',
					search: { show: false },
					column: { minWidth: 180, show: false },
					form: { component: { placeholder: '请输入描述', rows: 3 } },
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
					},
					form: { show: false },
				},
			},
		},
	};
}

