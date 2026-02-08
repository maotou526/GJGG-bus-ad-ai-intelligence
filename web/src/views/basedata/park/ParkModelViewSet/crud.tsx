import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';
// @ts-ignore
import { listPageDefMultiLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';

//此处为crudOptions配置
export default function ({ crudExpose }: { crudExpose: CrudExpose }): CreateCrudOptionsRet {
	// 获取场站列表
	const pageRequest = async (query: any) => {
		return await api.GetList(query);
	};

	// 编辑场站
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}

		// 处理时间字段，确保提交正确格式
		if (form.oper_start_time && typeof form.oper_start_time === 'string') {
			// 只保留时间部分 HH:mm:ss
			const timePart = form.oper_start_time.split(' ')[1] || form.oper_start_time;
			form.oper_start_time = timePart;
		}
		if (form.oper_end_time && typeof form.oper_end_time === 'string') {
			const timePart = form.oper_end_time.split(' ')[1] || form.oper_end_time;
			form.oper_end_time = timePart;
		}

		return await api.UpdateObj(form);
	};

	// 删除场站
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加场站
	const addRequest = async ({ form }: AddReq) => {
		// 处理时间字段
		if (form.oper_start_time && typeof form.oper_start_time === 'string') {
			const timePart = form.oper_start_time.split(' ')[1] || form.oper_start_time;
			form.oper_start_time = timePart;
		}
		if (form.oper_end_time && typeof form.oper_end_time === 'string') {
			const timePart = form.oper_end_time.split(' ')[1] || form.oper_end_time;
			form.oper_end_time = timePart;
		}

		return await api.AddObj(form);
	};

	// 导出数据
	const exportRequest = async (query: UserPageQuery) => {
		return await api.exportData(query);
	};

	// // 启用/禁用场站
	// const enableRequest = async (row: any, enabled_mark: 0 | 1) => {
	// 	return await api.enablePark({ id: row.id, enabled_mark });
	// };

	// 获取公司树形数据
	const getCompanyTree = async () => {
		const res = await request({
			url: '/api/CompanyModelViewSet/all_company/',
			method: 'get',
		});
		const data = res.data || [];
		
		// 构建树形结构（用于 dict-tree）
		const buildTree = (items: any[], parentId: any = null): any[] => {
			const result: any[] = [];
			const children = items.filter(item => item.parentid === parentId);
			
			children.forEach(item => {
				const node: any = {
					id: item.id,
					label: item.shortname, // tree-select 使用 label 作为显示字段
					value: item.shortname, // 保存到数据库的值
					shortname: item.shortname,
					parentid: item.parentid,
				};
				
				// 递归构建子节点
				const subChildren = buildTree(items, item.id);
				if (subChildren.length > 0) {
					node.children = subChildren;
				}
				
				result.push(node);
			});
			
			return result;
		};
		
		return buildTree(data);
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
			form: {
				col: { span: 12 },
				labelWidth: '120px',
				wrapper: {
					is: 'el-dialog',
					width: '900px',
					closeOnClickModal: false,
				},
			},
			actionbar: {
				buttons: {
					export: {
						show: auth('ParkModelViewSet:Export'),
						text: '导出',
						title: '导出',
						click() {
							return exportRequest(crudExpose.getSearchFormData());
						},
					},
					add: {
						show: auth('ParkModelViewSet:Create'),
					},
				},
			},
			rowHandle: {
				fixed: 'right',
				width: 380,
				buttons: {
					view: {
						type: 'text',
						order: 1,
						show: auth('ParkModelViewSet:Retrieve'),
					},
					edit: {
						type: 'text',
						order: 2,
						show: auth('ParkModelViewSet:Update'),
					},
					remove: {
						type: 'text',
						order: 5,
						show: auth('ParkModelViewSet:Delete'),
					},
				},
			},
			toolbar: {
				buttons: {
					add: { show: auth('ParkModelViewSet:Create') },
					edit: { show: false },
					remove: { show: false },
				},
			},
			columns: {
		// 序号列（跨页连续编号）
		_index: getIndexColumnConfig(crudExpose),
		// ========== 基础信息 ==========
		// 场站名称
		park_name: {
			title: '场站名称',
			type: 'input',
			search: { show: true },
			column: {
				minWidth: 100,
				sortable: 'custom',
				align: 'left',
				order: 1,
			},
			form: {
				rules: [{ required: true, message: '场站名称必填' }],
				component: {
					placeholder: '请输入场站名称',
				},
			},
		},
		// 公司名称
		company_name: {
			title: '公司名称',
			type: 'dict-tree',
			search: { show: true },
			dict: dict({
				getData: getCompanyTree,
				value: 'value',
				label: 'label',
				isTree: true,
				children: 'children',
			}),
			column: {
				minWidth: 170,
				sortable: 'custom',
				show: false,
			},
			form: {
				rules: [{ required: true, message: '公司名称必填' }],
				component: {
					placeholder: '请选择公司名称',
					filterable: true,
					clearable: true,
					checkStrictly: false,
					expandOnClickNode: true,
					props: {
						label: 'label',
						value: 'value',
						children: 'children',
					},
				},
			},
		},
		// 场地编码
		park_code: {
			title: '场地编码',
			type: 'input',
			search: { show: true },
			column: {
				minWidth: 100,
				sortable: 'custom',
				align: 'left',
				show: false,
			},
			form: {
				component: {
					placeholder: '请输入场地编码',
				},
			},
		},
		// 场地地址
		park_address: {
			title: '场地地址',
			type: 'input',
			search: { show: true },
			column: {
				minWidth: 100,
				sortable: 'custom',
				align: 'left',
				show: false,
			},
			form: {
				component: {
					placeholder: '请输入场地地址',
				},
			},
		},
		// 场地类型
		park_type: {
			title: '场地类型',
			type: 'dict-select',
			search: { show: true },
			dict: dict({
				data: [
					{ value: 0, label: '场内' },
					{ value: 1, label: '外停点' },
					{ value: 2, label: '终点站' },
				],
			}),
			column: {
				minWidth: 100,
				sortable: 'custom',
				align: 'left',
				show: false,
			},
			form: {
				component: {
					placeholder: '请选择场地类型',
				},
			},
		},
		// 场站类型
		station_type: {
			title: '场站类型',
			type: 'dict-select',
			search: { show: true },
			dict: dict({
				data: [
					{ value: 0, label: '总站' },
					{ value: 1, label: '分站' },
					{ value: 2, label: '停车场' },
					{ value: 3, label: '维修中心' },
				],
			}),
			column: {
				minWidth: 100,
				sortable: 'custom',
				align: 'left',
				order: 2,
			},
			form: {
				component: {
					placeholder: '请选择场站类型',
				},
			},
		},
		// 停车场状态
		park_status: {
			title: '停车场状态',
			type: 'dict-select',
			search: { show: true },
			dict: dict({
				data: [
					{ value: 0, label: '停用' },
					{ value: 1, label: '建设中' },
					{ value: 2, label: '运营中' },
				],
			}),
			column: {
				minWidth: 110,
				align: 'left',
				sortable: 'custom',
				order: 6,
			},
			form: {
				component: {
					placeholder: '请选择停车场状态',
				},
			},
		},
		// 总面积
		total_area: {
			title: '总面积(㎡)',
			type: 'number',
			search: { show: false },
			column: {
				minWidth: 110,
				sortable: 'custom',
				align: 'left',
				order: 3,
				formatter: (context: any) => {
					const value = context.value;
					return value ? `${value}㎡` : '-';
				},
			},
			form: {
				component: {
					placeholder: '请输入总面积',
					precision: 2,
				},
			},
		},
		// 建筑面积
		building_area: {
			title: '建筑面积(㎡)',
			type: 'number',
			search: { show: false },
			column: {
				minWidth: 120,
				sortable: 'custom',
				align: 'left',
				show: false,
				formatter: (context: any) => {
					const value = context.value;
					return value ? `${value}㎡` : '-';
				},
			},
			form: {
				component: {
					placeholder: '请输入建筑面积',
					precision: 2,
				},
			},
		},
		// 停车位数量
		parking_space: {
			title: '停车位数',
			type: 'number',
			search: { show: false },
			column: {
				minWidth: 100,
				sortable: 'custom',
				align: 'left',
				order: 4,
				formatter: (context: any) => {
					return context.value || 0;
				},
			},
			form: {
				component: {
					placeholder: '请输入停车位数量',
					precision: 0,
				},
			},
		},
		// 维修工位数量
		repair_space: {
			title: '维修工位数',
			type: 'number',
			search: { show: false },
			column: {
				minWidth: 110,
				sortable: 'custom',
				align: 'left',
				show: false,
				formatter: (context: any) => {
					return context.value || 0;
				},
			},
			form: {
				component: {
					placeholder: '请输入维修工位数量',
					precision: 0,
				},
			},
		},
		// 加油站数量
		gas_station_count: {
			title: '加油站数量',
			type: 'number',
			search: { show: false },
			column: {
				minWidth: 110,
				align: 'left',
				sortable: 'custom',
				show: false,
			},
			form: {
				component: {
					placeholder: '请输入加油站数量',
					precision: 0,
				},
			},
		},
		// 充电桩数量
		charging_pile_count: {
			title: '充电桩数量',
			type: 'number',
			search: { show: false },
			column: {
				minWidth: 120,
				sortable: 'custom',
				order: 5,
			},
			form: {
				component: {
					placeholder: '请输入充电桩数量',
					precision: 0,
				},
			},
		},
		// 洗车位数量
		car_wash_count: {
			title: '洗车位数量',
			type: 'number',
			search: { show: false },
			column: {
				minWidth: 120,
				sortable: 'custom',
				show: false,
			},
			form: {
				component: {
					placeholder: '请输入洗车位数量',
					precision: 0,
				},
			},
		},
		// 维修功能
		repair_flag: {
			title: '维修功能',
			type: 'dict-radio',
			dict: dict({
				data: [
					{ value: 0, label: '无' },
					{ value: 1, label: '有' },
				],
			}),
			search: { show: false },
			column: {
				minWidth: 100,
				sortable: 'custom',
				show: false,
				formatter: (context: any) => {
					return context.value === 1 ? '有' : '无';
				},
			},
			form: {
				value: 0,
				component: {
					placeholder: '是否有维修功能',
				},
			},
		},
		// 报到设备
		report_flag: {
			title: '报到设备',
			type: 'dict-radio',
			dict: dict({
				data: [
					{ value: 0, label: '无' },
					{ value: 1, label: '有' },
				],
			}),
			search: { show: false },
			column: {
				minWidth: 100,
				sortable: 'custom',
				align: 'left',
				show: false,
				formatter: (context: any) => {
					return context.value === 1 ? '有' : '无';
				},
			},
			form: {
				value: 0,
				component: {
					placeholder: '是否有报到设备',
				},
			},
		},
		// 办公楼
		office_flag: {
			title: '办公楼',
			type: 'dict-radio',
			dict: dict({
				data: [
					{ value: 0, label: '无' },
					{ value: 1, label: '有' },
				],
			}),
			search: { show: false },
			column: {
				minWidth: 80,
				sortable: 'custom',
				align: 'left',
				show: false,
				formatter: (context: any) => {
					return context.value === 1 ? '有' : '无';
				},
			},
			form: {
				value: 0,
			},
		},
		// 食堂
		canteen_flag: {
			title: '食堂',
			type: 'dict-radio',
			dict: dict({
				data: [
					{ value: 0, label: '无' },
					{ value: 1, label: '有' },
				],
			}),
			search: { show: false },
			column: {
				minWidth: 70,
				sortable: 'custom',
				align: 'left',
				show: false,
				formatter: (context: any) => {
					return context.value === 1 ? '有' : '无';
				},
			},
			form: {
				value: 0,
			},
		},
		// 宿舍
		dormitory_flag: {
			title: '宿舍',
			type: 'dict-radio',
			dict: dict({
				data: [
					{ value: 0, label: '无' },
					{ value: 1, label: '有' },
				],
			}),
			search: { show: false },
			column: {
				minWidth: 70,
				sortable: 'custom',
				align: 'left',
				show: false,
				formatter: (context: any) => {
					return context.value === 1 ? '有' : '无';
				},
			},
			form: {
				value: 0,
			},
		},
		// 保安室
		security_room_flag: {
			title: '保安室',
			type: 'dict-radio',
			dict: dict({
				data: [
					{ value: 0, label: '无' },
					{ value: 1, label: '有' },
				],
			}),
			search: { show: false },
			column: {
				minWidth: 80,
				sortable: 'custom',
				align: 'left',
				show: false,
				formatter: (context: any) => {
					return context.value === 1 ? '有' : '无';
				},
			},
			form: {
				value: 0,
			},
		},
		// 仓库
		warehouse_flag: {
			title: '仓库',
			type: 'dict-radio',
			dict: dict({
				data: [
					{ value: 0, label: '无' },
					{ value: 1, label: '有' },
				],
			}),
			search: { show: false },
			column: {
				minWidth: 70,
				sortable: 'custom',
				align: 'left',
				show: false,
				formatter: (context: any) => {
					return context.value === 1 ? '有' : '无';
				},
			},
			form: {
				value: 0,
			},
		},
		// 培训室
		training_room_flag: {
			title: '培训室',
			type: 'dict-radio',
			dict: dict({
				data: [
					{ value: 0, label: '无' },
					{ value: 1, label: '有' },
				],
			}),
			search: { show: false },
			column: {
				minWidth: 80,
				sortable: 'custom',
				align: 'left',
				show: false,
				formatter: (context: any) => {
					return context.value === 1 ? '有' : '无';
				},
			},
			form: {
				value: 0,
			},
		},
		// 运营开始时间
		oper_start_time: {
			title: '运营开始时间',
			type: 'time',
			search: { show: false },
			column: {
				width: 120,
				sortable: 'custom',
				align: 'left',
				show: false,
			},
			form: {
				component: {
					format: 'HH:mm',
					valueFormat: 'HH:mm',
					placeholder: '请选择运营开始时间',
				},
			},
		},
		// 运营结束时间
		oper_end_time: {
			title: '运营结束时间',
			type: 'time',
			search: { show: false },
			column: {
				width: 120,
				sortable: 'custom',
				align: 'left',
				show: false,
			},
			form: {
				component: {
					format: 'HH:mm',
					valueFormat: 'HH:mm',
					placeholder: '请选择运营结束时间',
				},
			},
		},
		// 负责人
		principal: {
			title: '负责人',
			type: 'input',
			search: { show: true },
			column: {
				minWidth: 80,
				sortable: 'custom',
				align: 'left',
				show: false,
			},
			form: {
				component: {
					placeholder: '请输入负责人',
				},
			},
		},
		// 联系电话
		contact_phone: {
			title: '联系电话',
			type: 'input',
			search: { show: false },
			column: {
				minWidth: 100,
				sortable: 'custom',
				align: 'left',
				show: false,
			},
			form: {
				component: {
					placeholder: '请输入联系电话',
				},
			},
		},
		// 电子邮箱
		contact_email: {
			title: '电子邮箱',
			type: 'input',
			search: { show: false },
			column: {
				minWidth: 100,
				sortable: 'custom',
				align: 'left',
				show: false,
			},
			form: {
				component: {
					placeholder: '请输入电子邮箱',
					type: 'email',
				},
			},
		},
		// 停车场围栏
		park_fence: {
			title: '停车场围栏',
			type: 'textarea',
			search: { show: false },
			column: {
				minWidth: 120,
				sortable: 'custom',
				align: 'left',
				show: false,
			},
			form: {
				component: {
					placeholder: '请输入停车场围栏坐标数据',
					rows: 4,
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
				minWidth: 100,
				sortable: 'custom',
				align: 'left',
				show: false,
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
				show: false,
				formatter: (context: any) => {
					const value = context.value;
					return value ? '是' : '否';
				},
			},
			form: { show: false },
		},
		// 创建时间
		create_datetime: {
			title: '创建时间',
			type: 'datetime',
			search: { show: false },
			column: {
				align: 'center',
				width: 180,
				component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
				show: false,
			},
			form: {
				align: 'left',
			},
		},
		// 更新时间
		update_datetime: {
			type: 'datetime',
			search: { show: false },
			column: {
				align: 'center',
				width: 180,
				component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
				show: false,
			},
			form: {
				show: false,
			},
		},
			},
		},
	};
}
