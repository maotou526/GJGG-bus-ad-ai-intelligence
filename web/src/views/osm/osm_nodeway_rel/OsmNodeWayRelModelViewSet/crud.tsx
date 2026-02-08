import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';	
import { listPageDefSingleLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';

//此处为crudOptions配置
export default function ({ crudExpose }: { crudExpose: CrudExpose }): CreateCrudOptionsRet {
	// 获取OSM道路节点关联列表
	const pageRequest = async (query: any) => {
		return await api.GetList(query);
	};

	// 编辑OSM道路节点关联
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}
		return await api.UpdateObj(form);
	};

	// 删除OSM道路节点关联
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加OSM道路节点关联
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
					width: '700px',
					closeOnClickModal: false,
				},
			},
			actionbar: {
				buttons: {
					export: {
						show: auth('OsmNodeWayRelModelViewSet:Export'),
						text: '导出',
						title: '导出',
						click() {
							return exportRequest(crudExpose.getSearchFormData());
						},
					},
					add: {
						show: auth('OsmNodeWayRelModelViewSet:Create'),
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
						show: auth('OsmNodeWayRelModelViewSet:Retrieve'),
					},
					edit: {
						type: 'text',
						order: 2,
						show: auth('OsmNodeWayRelModelViewSet:Update'),
					},
					remove: {
						type: 'text',
						order: 3,
						show: auth('OsmNodeWayRelModelViewSet:Delete'),
					},
				},
			},
			columns: {
				_index: getIndexColumnConfig(crudExpose),
				// OSM道路ID
				osm_way_id: {
					title: 'OSM道路ID',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 150,
						sortable: 'custom',
					},
					form: {
						rules: [{ required: true, message: 'OSM道路ID必填' }],
						component: {
							placeholder: '请输入OSM道路ID',
						},
					},
				},
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
				// 排序序号
				sort: {
					title: '排序序号',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请输入排序序号',
							min: 0,
						},
					},
				},
				// 关联关系显示
				relation_display: {
					title: '关联关系',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 250,
						sortable: false,
					},
					form: { show: false },
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

