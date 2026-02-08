import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet, compute } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';
import { listPageDefMultiLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';
import { dictionary } from '/@/utils/dictionary';

//此处为crudOptions配置
export default function ({ crudExpose }: { crudExpose: CrudExpose }): CreateCrudOptionsRet {
	// 获取站点列表
	const pageRequest = async (query: any) => {
		// 设置默认排序：按照区属、路名、站名、站址进行排序
		if (!query.ordering) {
			query.ordering = 'district,roadline_name,stop_name,stop_address';
		}
		return await api.GetList(query);
	};

	// 编辑站点
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}

		// 处理日期字段，确保提交纯日期格式
		if (form.exec_day && typeof form.exec_day === 'string') {
			form.exec_day = form.exec_day.split(' ')[0]; // 移除时间部分
		}
		if (form.expiry_day && typeof form.expiry_day === 'string') {
			form.expiry_day = form.expiry_day.split(' ')[0]; // 移除时间部分
		}

		return await api.UpdateObj(form);
	};

	// 删除站点
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加站点
	const addRequest = async ({ form }: AddReq) => {
		// 处理日期字段，确保提交纯日期格式
		if (form.exec_day && typeof form.exec_day === 'string') {
			form.exec_day = form.exec_day.split(' ')[0]; // 移除时间部分
		}
		if (form.expiry_day && typeof form.expiry_day === 'string') {
			form.expiry_day = form.expiry_day.split(' ')[0]; // 移除时间部分
		}

		return await api.AddObj(form);
	};

	// 导出数据
	const exportRequest = async (query: UserPageQuery) => {
		return await api.exportData(query);
	};

	// 启用/禁用站点
	const enableRequest = async (row: any, enabled_mark: 0 | 1) => {
		return await api.enableRoadlineStop({ id: row.id, enabled_mark });
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
				labelWidth: '100px',
				wrapper: {
					is: 'el-dialog',
					width: '900px',
					closeOnClickModal: false, // 禁用点击空白处关闭弹窗
				},
			},
			actionbar: {
				buttons: {
					export: {
						show: auth('RoadlineStopModelViewSet:Export'),
						text: '导出', //按钮文字
						title: '导出', //鼠标停留显示的信息
						click() {
							return exportRequest(crudExpose.getSearchFormData());
						},
					},
				autoFillData: {
					show: false,  // 强制隐藏数据填充按钮
					text: '数据填充',
					title: '自动填充站点数据（调用高德API填充环域、区属、街道、道路、地址）',
					type: 'primary',
					order: -1,
					click() {
						return crudExpose.onAutoFillData();
					},
				},
				convertCoordinates: {
					show: auth('RoadlineStopModelViewSet:Update'),
					text: '坐标转换',
					title: '将GCJ-02坐标（高德坐标系）转换为WGS84坐标（国际标准坐标系）',
					type: 'success',
					order: -2,
					click() {
						return crudExpose.onConvertCoordinates();
					},
				},
				add: {
					show: auth('RoadlineStopModelViewSet:Create'),
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
						show: auth('RoadlineStopModelViewSet:Retrieve'),
					},
					edit: {
						type: 'text',
						order: 2,
						show: auth('RoadlineStopModelViewSet:Update'),
					},
				enable: {
					type: 'text',
					order: 3,
					text: '启用',
					//show: auth('RoadlineStopModelViewSet:Update'),
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
					//show: auth('RoadlineStopModelViewSet:Update'),
					show: false,
					click: async (context: any) => {
						await enableRequest(context.row, 0);
						crudExpose.doRefresh();
					},
				},
					remove: {
						type: 'text',
						order: 5,
						show: auth('RoadlineStopModelViewSet:Delete'),
					},
				},
			},
		columns: {
			// 序号列（跨页连续编号）
			_index: getIndexColumnConfig(crudExpose),
			// 站点编号
			stop_code: {
				title: '站点编号',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 100,
						sortable: 'custom',
					},
					form: {
						rules: [{ required: true, message: '站点编号必填' }],
						component: {
							placeholder: '请输入站点编号',
						},
					},
				},
				// 区属
				district: {
					title: '区属',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 80,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请输入区属',
						},
					},
				},
				// 道路名称
				roadline_name: {
					title: '路名',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 100,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请输入路名',
						},
					},
				},
				// 站点名称
				stop_name: {
					title: '站名',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 150,
						sortable: 'custom',
					},
					form: {
						rules: [{ required: true, message: '站名必填' }],
						component: {
							placeholder: '请输入站名',
						},
					},
				},
				// 站点地址
				stop_address: {
					title: '站址',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 250,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请输入站址',
						},
					},
				},
				// 拼音名称
				pinyin: {
					title: '拼音名称',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 150,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请输入拼音名称',
						},
					},
				},
				// 环域
				area: {
					title: '环域',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 80,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请输入环域',
						},
					},
				},
				// 街道
				street: {
					title: '街道',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 100,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请输入街道',
						},
					},
				},
				// 车向
				path_direction: {
					title: '车向',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 120,
						sortable: 'custom',
						show: true, // 在列表中显示
					},
					form: {
						show: true, // 在表单中显示
						component: {
							placeholder: '请输入车向',
						},
					},
				},
				// 线路列表
				road_line_list: {
					title: '停靠线路',
					type: 'textarea',
					search: { show: false },
					column: {
						minWidth: 200,
						sortable: false,
						show: true, // 在列表中展示
					},
					form: {
						component: {
							placeholder: '请输入停靠线路',
							rows: 3,
						},
					},
				},
				// 经度
				lon02: {
					title: '经度',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 130,
						sortable: 'custom',
						show: false, // 隐藏列
					},
					form: {
						component: {
							placeholder: '请输入经度（GCJ02）',
							precision: 6,
						},
					},
				},
				// 纬度
				lat02: {
					title: '纬度',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 130,
						show: false, // 隐藏列
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请输入纬度（GCJ02）',
							precision: 6,
						},
					},
				},
				// 经度（WGS84）
				lon84: {
					title: '经度(WGS84)',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 130,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入经度（WGS84）',
							precision: 6,
						},
					},
				},
				// 纬度（WGS84）
				lat84: {
					title: '纬度(WGS84)',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 130,
						show: false,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请输入纬度（WGS84）',
							precision: 6,
						},
					},
				},
				// 站点类型
				stop_type: {
					title: '站点类型',
					type: 'dict-select',
					search: { show: false },
					dict: dict({
						data: dictionary('stop_type'),
					}),
					column: {
						minWidth: 120,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请选择站点类型',
							onChange: compute((context: any) => {
								return (value: string) => {
									if(context?.form){
										context.form.stop_type_name = dictionary('stop_type').find((item: any) => item.value === value)?.label ?? '';
									}
								};
							}),
						},
					},
				},
				// 是否主干道
				is_main_road: {
					title: '是否主干道',
					type: 'dict-select',
					search: { show: false }, // 隐藏搜索
					dict: dict({
						data: [
							{ value: true, label: '是' },
							{ value: false, label: '否' },
						],
					}),
					column: {
						minWidth: 120,
						sortable: 'custom',
						show: false, // 隐藏此列
						formatter: (context: any) => {
							return context.value ? '是' : '否';
						},
					},
					form: {
						show: false, // 隐藏表单字段
					},
				},
				// 人行道宽度
				sidewalk_width: {
					title: '人行道宽度(米)',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 140,
						sortable: 'custom',
						show: false, // 隐藏此列
						formatter: (context: any) => {
							const value = context.value;
							return value ? `${value}米` : '-';
						},
					},
					form: {
						show: false, // 隐藏表单字段
					},
				},
				// 接驳地铁道路
				metroline_name: {
					title: '接驳地铁',
					type: 'input',
					search: { show: false }, // 隐藏搜索
					column: {
						minWidth: 150,
						sortable: 'custom',
						show: false, // 隐藏此列
					},
					form: {
						show: false, // 隐藏表单字段
					},
				},
				// 启用日期
				exec_day: {
					title: '启用日期',
					type: 'date',
					search: { show: false },
					form: {
						show: false, // 隐藏表单字段
					},
					column: {
						align: 'center',
						width: 120,
						show: false, // 隐藏列
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
				},
				// 截止日期
				expiry_day: {
					title: '截止日期',
					type: 'date',
					search: { show: false },
					form: {
						show: false, // 隐藏表单字段
					},
					column: {
						align: 'center',
						width: 120,
						show: false, // 隐藏列
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
				},
				// 备注
				remark: {
					title: '备注',
					type: 'textarea',
					search: { show: false },
					column: {
						minWidth: 200,
						sortable: false,
						show: false, // 默认不显示
					},
					form: {
						component: {
							placeholder: '请输入备注信息',
							rows: 3,
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
						show: false, // 隐藏原始字段，使用计算字段
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
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: false,
						formatter: (context: any) => {
							const value = context.value;
							return value ? '是' : '否';
						},
					},
					form: { show: false }, // 表单中不显示
				},
				// 是否过期显示字段
				is_expired: {
					title: '是否过期',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: false,
						show: false, // 隐藏列
						formatter: (context: any) => {
							const value = context.value;
							return value ? '是' : '否';
						},
					},
					form: { show: false }, // 表单中不显示
				},
				// 创建时间
				create_datetime: {
					title: '创建时间',
					type: 'datetime',
					search: { show: false },
					column: {
						show:false,
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
						show:false,
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

