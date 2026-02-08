import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';
import { listPageDefSingleLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';
import { ElMessage } from 'element-plus';

//此处为crudOptions配置
export default function ({ crudExpose }: { crudExpose: CrudExpose }): CreateCrudOptionsRet {
	// 获取线路走向详情列表
	const pageRequest = async (query: any) => {
		return await api.GetList(query);
	};

	// 编辑线路走向详情
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

	// 删除线路走向详情
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加线路走向详情
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

	// 启用/禁用线路走向详情
	const enableRequest = async (row: any, enabled_mark: 0 | 1) => {
		return await api.enableRoadlineDetail({ id: row.id, enabled_mark });
	};

	// 批量填充 POI
	const batchFillPoiRequest = async () => {
		try {
			const result = await api.batchFillPoi({
				city: '320585',
				force_update: false,
				batch_size: 100,
				delay: 0.2
			});
			if (result.code === 2000) {
				const data = result.data;
				const msg = `批量填充完成！成功 ${data.success} 条，失败 ${data.failed} 条，跳过 ${data.skipped} 条，共 ${data.total_coordinates} 个坐标点`;
				ElMessage.success(msg);
				crudExpose.doRefresh();
			} else {
				ElMessage.error(result.msg);
			}
		} catch (err) {
			ElMessage.error('批量填充失败');
			console.error(err);
		}
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
					width: '800px',
					closeOnClickModal: false, // 禁用点击空白处关闭弹窗
				},
			},
			actionbar: {
				buttons: {
					export: {
						show: auth('RoadlineDetailModelViewSet:Export'),
						text: '导出', //按钮文字
						title: '导出', //鼠标停留显示的信息
						click() {
							return exportRequest(crudExpose.getSearchFormData());
						},
					},
					add: {
						show: auth('RoadlineDetailModelViewSet:Create'),
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
						show: auth('RoadlineDetailModelViewSet:Retrieve'),
					},
					edit: {
						type: 'text',
						order: 2,
						show: auth('RoadlineDetailModelViewSet:Update'),
					},
				enable: {
					type: 'text',
					order: 3,
					text: '启用',
					//show: auth('RoadlineDetailModelViewSet:Update'),
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
					//show: auth('RoadlineDetailModelViewSet:Update'),
					show: false,
					click: async (context: any) => {
						await enableRequest(context.row, 0);
						crudExpose.doRefresh();
					},
				},
					remove: {
						type: 'text',
						order: 5,
						show: auth('RoadlineDetailModelViewSet:Delete'),
					},
				},
			},
		columns: {
			// 序号列（跨页连续编号）
			_index: getIndexColumnConfig(crudExpose),
			// 关联线路
			roadline: {
				title: '线路名称',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						url: '/api/RoadlineModelViewSet/?limit=1000&enabled_mark=1&delete_mark=0',  // 只显示启用且未删除的线路
						value: 'id',
						label: 'line_name',
					}),
					column: {
						minWidth: 150,
						sortable: 'custom',
						show: false, // 隐藏原始字段
					},
					form: {
						rules: [{ required: true, message: '关联线路必选' }],
						component: {
							placeholder: '请选择关联线路',
							filterable: true,  // 可搜索过滤
						},
					},
				},
			// 关联线路名称显示字段
			roadline_name: {
				title: '线路名称',
				type: 'text',
				search: { show: false },
				column: {
					minWidth: 150,
					sortable: false,
					align: 'left',
				},
				form: { show: false }, // 表单中不显示
			},
				// 上下行
				up_down: {
					title: '上下行',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: 0, label: '上行' },
							{ value: 1, label: '下行' },
						],
					}),
					column: {
						minWidth: 100,
						sortable: 'custom',
						show: false, // 隐藏原始字段
					},
					form: {
						rules: [{ required: true, message: '上下行必选' }],
						component: {
							placeholder: '请选择上下行',
						},
					},
				},
			// 上下行显示字段
			up_down_display: {
				title: '上下行',
				type: 'text',
				search: { show: false },
				column: {
					minWidth: 100,
					sortable: false,
					align: 'left',
				},
				form: { show: false }, // 表单中不显示
			},
			// 起点名称
			start_name: {
				title: '起点名称',
				type: 'input',
				search: { show: true },
				column: {
					minWidth: 150,
					sortable: 'custom',
					align: 'left',
				},
				form: {
					rules: [{ required: true, message: '起点名称必填' }],
					component: {
						placeholder: '请输入起点名称',
					},
				},
			},
			// 开往方向
			to_direction: {
				title: '开往方向',
				type: 'input',
				search: { show: true },
				column: {
					minWidth: 150,
					sortable: 'custom',
					align: 'left',
				},
				form: {
					component: {
						placeholder: '请输入开往方向',
					},
				},
			},
			// 线路走向
			line_direction: {
				title: '线路走向',
				type: 'input',
				search: { show: true },
				column: {
					minWidth: 150,
					sortable: 'custom',
					align: 'left',
				},
				form: {
					component: {
						placeholder: '请输入线路走向',
					},
				},
			},
			// 首末班时间（原始字段，用于表单编辑）
			start_end_time: {
				title: '首末班时间',
				type: 'input',
				search: { show: false },
				column: {
					minWidth: 150,
					sortable: 'custom',
					show: false,  // 列表中隐藏原始字段
				},
				form: {
					component: {
						placeholder: '请输入首末班时间（如：05:30-22:00）',
					},
					helper: '格式：HH:mm-HH:mm（时:分-时:分）',
					rules: [
						{
							pattern: /^([0-1][0-9]|2[0-3]):[0-5][0-9]-([0-1][0-9]|2[0-3]):[0-5][0-9]$/,
							message: '请输入正确的时间格式（如：05:30-22:00）',
						},
					],
				},
			},
			// 首末班时间（格式化显示字段）
			start_end_time_formatted: {
				title: '首末班时间',
				type: 'text',
				search: { show: false },
				column: {
					minWidth: 150,
					sortable: false,
					align: 'left',
				},
				form: { show: false },  // 表单中不显示
			},
			// 线路详情长度
			line_length: {
				title: '线路长度（km）',
				type: 'number',
				search: { show: false },
				column: {
					minWidth: 140,
					sortable: 'custom',
					align: 'left',
					formatter: (context: any) => {
						const value = context.value;
						return value ? `${value}km` : '-';
					},
				},
				form: {
					component: {
						placeholder: '请输入线路长度（单位：km）',
						precision: 2,
					},
					helper: '单位：km',
				},
			},
			// 环域分布
			area: {
				title: '环域分布',
				type: 'input',
				search: { show: true },
				column: {
					minWidth: 150,
					sortable: 'custom',
					show: false,  // 隐藏列
				},
				form: {
					component: {
						placeholder: '请输入环域分布',
					},
				},
			},
				// 途经POI
				poi: {
					title: '途经POI',
					type: 'textarea',
					search: { show: false },
					column: {
						minWidth: 200,
						sortable: false,
						show: false, // 数据量大，列表中隐藏
					},
					form: {
						component: {
							placeholder: '请输入途经POI信息',
							rows: 4,
						},
					},
				},
				// 线路轨迹84坐标
				lon_lat84: {
					title: '轨迹84坐标',
					type: 'textarea',
					search: { show: false },
					column: {
						show: false, // 数据量大，列表中隐藏
					},
					form: {
						component: {
							placeholder: '请输入WGS84坐标系线路轨迹数据',
							rows: 3,
						},
					},
					valueBuilder(context: any) {
						// 查看详情时，如果数据过长，显示前100个字符
						if (context.mode === 'view' && context.row.lon_lat84) {
							const data = context.row.lon_lat84;
							if (data.length > 100) {
								context.row.lon_lat84 = data.substring(0, 100) + '...';
							}
						}
					},
				},
				// 线路轨迹02坐标
				lon_lat02: {
					title: '轨迹02坐标',
					type: 'textarea',
					search: { show: false },
					column: {
						show: false, // 数据量大，列表中隐藏
					},
					form: {
						component: {
							placeholder: '请输入GCJ02坐标系线路轨迹数据',
							rows: 3,
						},
					},
					valueBuilder(context: any) {
						// 查看详情时，如果数据过长，显示前100个字符
						if (context.mode === 'view' && context.row.lon_lat02) {
							const data = context.row.lon_lat02;
							if (data.length > 100) {
								context.row.lon_lat02 = data.substring(0, 100) + '...';
							}
						}
					},
				},
			// 启用日期
			exec_day: {
				title: '启用日期',
				type: 'date',
				search: { show: false },
				form: {
					show: false,  // 表单中隐藏
					component: {
						format: 'YYYY-MM-DD',
						valueFormat: 'YYYY-MM-DD',
						placeholder: '请选择启用日期',
					},
				},
				column: {
					align: 'center',
					width: 120,
					show: false,  // 隐藏列
					component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
				},
			},
			// 截止日期
			expiry_day: {
				title: '截止日期',
				type: 'date',
				search: { show: false },
				form: {
					show: false,  // 表单中隐藏
					component: {
						format: 'YYYY-MM-DD',
						valueFormat: 'YYYY-MM-DD',
						placeholder: '请选择截止日期',
					},
				},
				column: {
					align: 'center',
					width: 120,
					show: false,  // 隐藏列
					component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
				},
			},
			// 启用状态
			enabled_mark: {
				title: '启用状态',
				type: 'dict-select',
				search: { show: false },  // 隐藏搜索
				dict: dict({
					data: [
						{ value: 1, label: '启用' },
						{ value: 0, label: '禁用' },
					],
				}),
				column: {
					minWidth: 120,
					sortable: 'custom',
					show: false, // 隐藏原始字段
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
				dict: dict({
					data: [
						{ value: true, label: '是' },
						{ value: false, label: '否' },
					],
				}),
				search: { show: true },
				column: {
					minWidth: 100,
					sortable: false,
					align: 'left',
				},
				form: {
					value: true, // 默认值：是
					component: {
						placeholder: '请选择是否启用',
					},
				},
			},
			// 是否过期显示字段
			is_expired: {
				title: '是否过期',
				type: 'dict-select',
				dict: dict({
					data: [
						{ value: true, label: '是' },
						{ value: false, label: '否' },
					],
				}),
				search: { show: false },
				column: {
					minWidth: 100,
					sortable: false,
					align: 'left',
					show: false,
				},
				form: {
					show: false,
					value: false, // 默认值：否
					component: {
						placeholder: '请选择是否过期',
					},
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

