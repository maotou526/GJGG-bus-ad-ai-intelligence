import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';
import { listPageDefSingleLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';

//此处为crudOptions配置
export default function ({ crudExpose }: { crudExpose: CrudExpose }): CreateCrudOptionsRet {
	// 获取OSM节点列表
	const pageRequest = async (query: any) => {
		return await api.GetList(query);
	};

	// 编辑OSM节点
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}
		return await api.UpdateObj(form);
	};

	// 删除OSM节点
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加OSM节点
	const addRequest = async ({ form }: AddReq) => {
		return await api.AddObj(form);
	};

	// 导出数据
	const exportRequest = async (query: UserPageQuery) => {
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
			// 搜索配置
			// search: {
			// 	container: {
			// 		collapse: true,
			// 		action: {
			// 			label: '操作',
			// 			col: { span: 4 },
			// 		},
			// 		col: { span: 4 },
			// 		collapseButton: {},
			// 	},
			// },
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
						show: auth('OsmNodeModelViewSet:Export'),
						text: '导出',
						title: '导出',
						click() {
							return exportRequest(crudExpose.getSearchFormData());
						},
					},
					add: {
						show: auth('OsmNodeModelViewSet:Create'),
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
						show: auth('OsmNodeModelViewSet:Retrieve'),
					},
					edit: {
						type: 'text',
						order: 2,
						show: auth('OsmNodeModelViewSet:Update'),
					},
					remove: {
						type: 'text',
						order: 3,
						show: auth('OsmNodeModelViewSet:Delete'),
					},
				},
			},
			columns: {
				_index: getIndexColumnConfig(crudExpose),
				// OSM节点ID
				osm_node_id: {
					title: 'OSM节点ID',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 150,
						sortable: 'custom',
					},
					form: {
						rules: [{ required: true, message: 'OSM节点ID必填' }],
						component: {
							placeholder: '请输入OSM节点ID',
						},
					},
				},
				// 经度
				str_lon: {
					title: '经度',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请输入经度',
							step: 0.00000001,
						},
					},
				},
				// 纬度
				str_lat: {
					title: '纬度',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请输入纬度',
							step: 0.00000001,
						},
					},
				},
				// 坐标显示
				coordinate_display: {
					title: '坐标',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 180,
						sortable: false,
					},
					form: { show: false },
				},
				// 标签JSON
				tag_json: {
					title: '标签JSON',
					type: 'textarea',
					search: { show: false },
					column: {
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入标签数据（JSON格式）',
							rows: 5,
						},
					},
				},
				// 创建时间
				create_datetime: {
					title: '创建时间',
					type: 'datetime',
					search: { show: false },
					column: {
						show: false,
						align: 'center',
						width: 160,
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
					},
					form: {
						show: false,
					},
				},
				// 更新时间
				update_datetime: {
					title: '更新时间',
					type: 'datetime',
					search: { show: false },
					column: {
						show: false,
						align: 'center',
						width: 160,
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
					},
					form: {
						show: false,
					},
				},
			},
		},
	};
}

