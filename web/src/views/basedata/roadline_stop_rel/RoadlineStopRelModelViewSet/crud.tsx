import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';
import { ref, Ref } from 'vue';
import { listPageDefMultiLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';

//此处为crudOptions配置
export default function ({ crudExpose }: { crudExpose: CrudExpose }): CreateCrudOptionsRet {
	// 线路列表
	const roadlineList: Ref<any[]> = ref([]);

	// 加载线路列表
	const loadRoadlineList = async () => {
		try {
			const res = await api.getRoadlineList();
			if (res && res.data && Array.isArray(res.data)) {
				roadlineList.value = res.data.map((item: any) => ({
					value: item.id,
					label: item.line_name,
				}));
			}
		} catch (error) {
			console.error('加载线路列表失败:', error);
		}
	};

	// 固定的上下行选项
	const upDownOptions = [
		{ value: 0, label: '上行' },
		{ value: 1, label: '下行' },
	];

	// 初始化时加载线路列表
	loadRoadlineList();

	// 获取站点关联列表
	const pageRequest = async (query: any) => {
		// 🔥 字段映射：前端 up_down -> 后端 line_dtl_id__up_down
		const mappedQuery = { ...query };
		
		// 处理搜索过滤字段
		if (mappedQuery.up_down !== undefined) {
			mappedQuery['line_dtl_id__up_down'] = mappedQuery.up_down;
			delete mappedQuery.up_down;
		}
		
		// 处理排序字段
		if (mappedQuery.ordering) {
			mappedQuery.ordering = mappedQuery.ordering.replace(/^-?up_down$/, (match: string) => {
				return match.startsWith('-') ? '-line_dtl_id__up_down' : 'line_dtl_id__up_down';
			});
		}
		
		return await api.GetList(mappedQuery);
	};

	// 编辑站点关联
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}
		return await api.UpdateObj(form);
	};
	// 删除站点关联
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加站点关联
	const addRequest = async ({ form }: AddReq) => {
		return await api.AddObj(form);
	};

	// 导出数据
	const exportRequest = async (query: UserPageQuery) => {
		return await api.exportData(query);
	};

	// 启用/禁用站点关联
	const enableRequest = async (row: any, enabled_mark: 0 | 1) => {
		return await api.enableRoadlineStopRel({ id: row.id, enabled_mark });
	};

	return {
		crudOptions: {
			...listPageDefMultiLineCfg,
			request: {
				pageRequest,
				addRequest,
				editRequest,
				delRequest,
			},
			// 搜索配置
			// search: {
			// 	container: {
			// 		collapse: true, //是否展开，你布局组件中定义的props
			// 		action: {
			// 			label: '操作', //查询按钮前缀
			// 			col: { span: 4 }, //查询按钮所占格子宽度
			// 		},
			// 		col: { span: 4 }, // 默认列宽度配置
			// 		collapseButton: {
			// 			//展开按钮配置
			// 			// fs-button 属性
			// 		},
			// 	},
			// },
			form: {
				col: { span: 12 },
				labelWidth: '120px',
				wrapper: {
					is: 'el-dialog',
					width: '900px',
					closeOnClickModal: false, // 禁用点击空白处关闭弹窗
				},
			},
			actionbar: {
				buttons: {
					export: {
						show: auth('RoadlineStopRelModelViewSet:Export'),
						text: '导出', //按钮文字
						title: '导出', //鼠标停留显示的信息
						click() {
							return exportRequest(crudExpose.getSearchFormData());
							// return exportRequest(crudExpose!.getSearchFormData())    // 注意这个crudExpose!.getSearchFormData()，一些低版本的环境是需要添加!的
						},
					},
					add: {
						show: auth('RoadlineStopRelModelViewSet:Create'),
					},
				},
			},
			rowHandle: {
				//固定右侧
				fixed: 'right',
				width: 280,
				buttons: {
					view: {
						type: 'text',
						order: 1,
						show: auth('RoadlineStopRelModelViewSet:Retrieve'),
					},
					edit: {
						type: 'text',
						order: 2,
						show: auth('RoadlineStopRelModelViewSet:Update'),
					},
				enable: {
					type: 'text',
					order: 3,
					text: '启用',
					//show: auth('RoadlineStopRelModelViewSet:Update'),
					show: false,
					click: async (context: any) => {
						await enableRequest(context.row, 1);
						crudExpose.doRefresh();
					},
				},
				disable: {
					type: 'text',
					order: 4,
					text: '禁用',
					//show: auth('RoadlineStopRelModelViewSet:Update'),
					show: false,
					click: async (context: any) => {
						await enableRequest(context.row, 0);
						crudExpose.doRefresh();
					},
				},
					remove: {
						type: 'text',
						order: 5,
						show: auth('RoadlineStopRelModelViewSet:Delete'),
					},
				},
			},
		columns: {
			// 序号列（跨页连续编号）
			_index: getIndexColumnConfig(crudExpose),
			// 关联线路ID（表单使用）
			roadline_id: {
				title: '线路名称',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						value: 'value',
						label: 'label',
						getData: async () => {
							if (roadlineList.value.length === 0) {
								await loadRoadlineList();
							}
							return roadlineList.value;
						},
					}),
					column: {
						minWidth: 170,
						sortable: 'custom',
						show: false, // 隐藏，使用计算字段roadline_name显示
					},
					form: {
						rules: [{ required: true, message: '关联线路必填' }],
						component: {
							placeholder: '请选择关联线路',
							filterable: true,
						},
					},
					editForm: {
						// 编辑时禁用（因为后端不允许修改所属线路）
						component: {
							disabled: true,
						},
					},
				},
			// 关联线路名称显示字段
			roadline_name: {
				title: '线路名称',
				type: 'text',
				search: { show: false },
				column: {
					minWidth: 170,
					sortable: false,
					align: 'left',
				},
				form: { show: false }, // 表单中不显示
			},
			// 上下行方向（用于后端查找line_dtl_id）
			up_down: {
				title: '线路方向',
				type: 'dict-select',
				search: { show: true },  // 🔥 字段映射在 pageRequest 中完成
				dict: dict({
					data: upDownOptions,
				}),
				column: {
					minWidth: 120,
					sortable: 'custom',
					align: 'left',
				},
				form: {
					rules: [{ required: true, message: '线路方向必填' }],
					component: {
						placeholder: '请选择线路方向',
					},
				},
				editForm: {
					// 编辑时禁用（因为后端不允许修改线路方向）
					component: {
						disabled: true,
					},
				},
			},
			// 站级序号
			level_id: {
				title: '站级序号',
				type: 'number',
				search: { show: true },
				column: {
					minWidth: 100,
					sortable: 'custom',
					align: 'left',
				},
				form: {
					rules: [{ required: true, message: '站级序号必填' }],
					component: {
						placeholder: '请输入站级序号',
						min: 0,
					},
				},
			},
			// 站级名称
			level_name: {
				title: '站级名称',
				type: 'input',
				search: { show: true },
				column: {
					minWidth: 140,
					sortable: 'custom',
					align: 'left',
				},
				form: {
					component: {
						placeholder: '请输入站级名称',
					},
				},
			},
			// 站点编号
			stop_code: {
				title: '站点编号',
				type: 'input',
				search: { show: true },
				column: {
					minWidth: 140,
					sortable: 'custom',
					show: true,  // 显示列
					align: 'left',
				},
				form: {
					component: {
						placeholder: '请输入站点编号',
					},
				},
			},
			// 环域（从 dwd_roadline_stop 表关联）
			stop_area: {
				title: '环域',
				type: 'text',
				search: { show: false },
				column: {
					minWidth: 120,
					sortable: false,
					align: 'left',
					show: true,
				},
				form: { show: false }, // 表单中不显示
			},
			// 区属（从 dwd_roadline_stop 表关联）
			stop_district: {
				title: '区属',
				type: 'text',
				search: { show: false },
				column: {
					minWidth: 120,
					sortable: false,
					align: 'left',
					show: true,
				},
				form: { show: false }, // 表单中不显示
			},
			// 路名（从 dwd_roadline_stop 表关联）
			stop_roadline_name: {
				title: '路名',
				type: 'text',
				search: { show: false },
				column: {
					minWidth: 140,
					sortable: false,
					align: 'left',
					show: true,
				},
				form: { show: false }, // 表单中不显示
			},
			// 站名（从 dwd_roadline_stop 表关联）
			stop_name: {
				title: '站名',
				type: 'text',
				search: { show: false },
				column: {
					minWidth: 140,
					sortable: false,
					align: 'left',
					show: true,
				},
				form: { show: false }, // 表单中不显示
			},
			// 车向（从 dwd_roadline_stop 表关联）
			stop_path_direction: {
				title: '车向',
				type: 'text',
				search: { show: false },
				column: {
					minWidth: 120,
					sortable: false,
					align: 'left',
					show: true,
				},
				form: { show: false }, // 表单中不显示
			},
			// 站址（从 dwd_roadline_stop 表关联）
			stop_address: {
				title: '站址',
				type: 'text',
				search: { show: false },
				column: {
					minWidth: 200,
					sortable: false,
					align: 'left',
					show: true,
				},
				form: { show: false }, // 表单中不显示
			},
			// 停靠线路（从 dwd_roadline_stop 表关联）
			stop_road_line_list: {
				title: '停靠线路',
				type: 'text',
				search: { show: false },
				column: {
					minWidth: 200,
					sortable: false,
					align: 'left',
					show: true,
				},
				form: { show: false }, // 表单中不显示
			},
			// 区属（隐藏字段）
			zone: {
				title: '区属',
				type: 'input',
				search: { show: false }, // 隐藏筛选条件
				column: {
					minWidth: 120,
					sortable: 'custom',
					show: false, // 隐藏列表列
					align: 'left',
				},
				form: {
					show: false, // 隐藏表单字段（添加和编辑）
					component: {
						placeholder: '请输入区属',
					},
				},
			},
			// 经度02
			lon02: {
				title: '经度(GCJ02)',
				type: 'number',
				search: { show: false },
				column: {
					minWidth: 140,
					sortable: 'custom',
					show: false,  // 隐藏列
				},
				form: {
					component: {
						placeholder: '请输入经度（GCJ02）',
						precision: 8,
					},
				},
			},
			// 纬度02
			lat02: {
				title: '纬度(GCJ02)',
				type: 'number',
				search: { show: false },
				column: {
					minWidth: 140,
					sortable: 'custom',
					show: false,  // 隐藏列
				},
				form: {
					component: {
						placeholder: '请输入纬度（GCJ02）',
						precision: 8,
					},
				},
			},
			// 距上一站距离
			to_next_metre: {
				title: '距上站距离(米)',
				type: 'number',
				search: { show: false },
				column: {
					minWidth: 140,
					sortable: 'custom',
					show: false,  // 隐藏列
					formatter: (context: any) => {
						const value = context.value;
						return value ? `${value}米` : '-';
					},
				},
				form: {
					component: {
						placeholder: '请输入距上一站距离',
						precision: 2,
						min: 0,
					},
				},
			},
				// 网格转换经度02
				trans_lon02: {
					title: '网格转换经度',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 140,
						sortable: 'custom',
						show: false, // 默认不显示
					},
					form: {
						component: {
							placeholder: '请输入网格转换经度',
							precision: 8,
						},
					},
				},
				// 网格转换纬度02
				trans_lat02: {
					title: '网格转换纬度',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 140,
						sortable: 'custom',
						show: false, // 默认不显示
					},
					form: {
						component: {
							placeholder: '请输入网格转换纬度',
							precision: 8,
						},
					},
				},
				// 启用状态
				enabled_mark: {
					title: '启用状态',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: 1, label: '启用' },
							{ value: 0, label: '禁用' },
						],
					}),
					column: {
						minWidth: 120,
						sortable: 'custom',
						show: false, // 隐藏原始字段，使用显示字段
					},
					form: {
						component: {
							placeholder: '请选择启用状态',
						},
					},
				},
			// 是否启用显示字段
			is_enabled: {
				title: '是否启用',
				type: 'dict-select',
				search: { show: true },
				dict: dict({
					data: [
						{ value: true, label: '是' },
						{ value: false, label: '否' },
					],
				}),
				column: {
					minWidth: 100,
					sortable: false,
					align: 'left',
				},
				form: { show: false }, // 表单中不显示
			},
				// 描述
				description: {
					title: '描述',
					type: 'textarea',
					search: { show: false },
					column: {
						minWidth: 200,
						sortable: false,
						show: false, // 默认不显示
					},
					form: {
						component: {
							placeholder: '请输入描述信息',
							rows: 3,
						},
					},
				},
				// 创建人
				creator_name: {
					title: '创建人',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: false,
						show: false, // 默认不显示
					},
					form: {
						show: false,
					},
				},
				// 修改人
				modifier_name: {
					title: '修改人',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: false,
						show: false, // 默认不显示
					},
					form: {
						show: false,
					},
				},
				// 创建时间
				create_datetime: {
					title: '创建时间',
					type: 'datetime',
					search: { show: false },
					column: {
						align: 'center',
						width: 160,
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
						show:false,
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
						align: 'center',
						width: 160,
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
						show:false,
					},
					form: {
						show: false,
					},
				},
			},
		},
	};
}

