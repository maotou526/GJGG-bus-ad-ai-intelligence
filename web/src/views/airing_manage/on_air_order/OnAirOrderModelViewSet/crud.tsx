import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';
import { ref, Ref, watch } from 'vue';
// @ts-ignore - defConfig.js 没有类型声明
import { listPageDefSingleLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';

// 预订单API前缀
const bookingOrderApiPrefix = '/api/BookingOrderModelViewSet/';

//此处为crudOptions配置
export default function ({ crudExpose }: { crudExpose: CrudExpose }): CreateCrudOptionsRet {
	// 预订单列表（用于预订单选择）
	const bookingOrderList: Ref<any[]> = ref([]);

	// 加载预订单列表
	const loadBookingOrderList = async () => {
		try {
			const res = await request({
				url: bookingOrderApiPrefix,
				method: 'get',
				params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
			});
			// 兼容两种返回格式
			const data = res?.data?.results || res?.data || [];
			if (Array.isArray(data)) {
				bookingOrderList.value = data.map((item: any) => ({
					value: item.id,
					label: `${item.booking_no || ''} - ${item.customer_name || ''}`.trim() || `订单ID:${item.id}`,
					booking_no: item.booking_no || '',
					customer_name: item.customer_name || '',
					start_date: item.start_date || '',
					end_date: item.end_date || '',
				}));
			}
		} catch (error) {
			console.error('加载预订单列表失败:', error);
		}
	};

	// 获取上刊订单列表
	const pageRequest = async (query: any) => {
		return await api.GetList(query);
	};

	// 编辑上刊订单
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}
		return await api.UpdateObj(form);
	};

	// 删除上刊订单
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加上刊订单
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
						// 注释编号:django-vue3-admin-crud210716:注意这个auth里面的值，最好是使用index.vue文件里面的name值并加上请求动作的单词
						show: auth('OnAirOrderModelViewSet:Export'),
						text: '导出', //按钮文字
						title: '导出', //鼠标停留显示的信息
						click() {
							return exportRequest(crudExpose.getSearchFormData());
						},
					},
					add: {
						show: auth('OnAirOrderModelViewSet:Create'),
					},
				},
			},
			rowHandle: {
				//固定右侧
				fixed: 'right',
				width: 150,
				buttons: {
					view: {
						type: 'text',
						order: 1,
						show: auth('OnAirOrderModelViewSet:Retrieve'),
					},
					edit: {
						type: 'text',
						order: 2,
						show: auth('OnAirOrderModelViewSet:Update'),
					},
					remove: {
						type: 'text',
						order: 3,
						show: auth('OnAirOrderModelViewSet:Delete'),
					},
				},
			},
			columns: {
				// 序号列（跨页连续编号）
				_index: getIndexColumnConfig(crudExpose),
				
				// 订单号
				order_no: {
					title: '订单号',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 180,
						sortable: 'custom',
						align: 'left',
					},
					form: {
						rules: [{ required: true, message: '订单号必填' }],
						component: {
							placeholder: '请输入订单号，格式：ON-YYYYMMDD-XXXX',
						},
						helper: '订单号格式：ON-YYYYMMDD-XXXX',
					},
				},

				// 预订单ID
				booking_order_id: {
					title: '预订单',
					type: 'dict-select',
					search: { 
						show: true,
						component: {
							placeholder: '请选择或搜索预订单',
						},
					},
					dict: dict({
						value: 'value',
						label: 'label',
						getData: async () => {
							if (bookingOrderList.value.length === 0) {
								await loadBookingOrderList();
							}
							return bookingOrderList.value;
						},
					}),
					column: {
						minWidth: 200,
						sortable: 'custom',
						align: 'left',
						formatter: (context: any) => {
							const value = context.value;
							if (!value) {
								return '-';
							}
							// 从bookingOrderList中查找对应的预订单信息
							const bookingOrder = bookingOrderList.value.find((item: any) => item.value === value);
							if (bookingOrder) {
								return bookingOrder.label || `预订单ID:${value}`;
							}
							return `预订单ID:${value}`;
						},
					},
					form: {
						rules: [{ required: true, message: '预订单必填' }],
						component: {
							placeholder: '请选择预订单',
							filterable: true,
							clearable: false,
						},
						// 当选择预订单时，自动填充客户名称和日期
						onChange: ({ form }: any) => {
							const bookingOrderId = form.booking_order_id;
							if (bookingOrderId) {
								const bookingOrder = bookingOrderList.value.find((item: any) => item.value === bookingOrderId);
								if (bookingOrder) {
									// 自动填充客户名称
									if (bookingOrder.customer_name && !form.customer_name) {
										form.customer_name = bookingOrder.customer_name;
									}
									// 自动填充投放开始日期
									if (bookingOrder.start_date && !form.booking_start_date) {
										form.booking_start_date = bookingOrder.start_date;
									}
									// 自动填充投放结束日期
									if (bookingOrder.end_date && !form.booking_end_date) {
										form.booking_end_date = bookingOrder.end_date;
									}
								}
							}
						},
					},
				},

				// 客户名称（冗余字段）
				customer_name: {
					title: '客户名称',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 150,
						sortable: 'custom',
						align: 'left',
					},
					form: {
						rules: [{ required: false, message: '客户名称' }],
						component: {
							placeholder: '客户名称（自动填充）',
						},
						helper: '客户名称，通常从预订单自动填充',
					},
				},

				// 投放开始日期
				booking_start_date: {
					title: '投放开始日期',
					type: 'date',
					search: { 
						show: true,
						component: {
							type: 'date',
							valueFormat: 'YYYY-MM-DD',
						},
					},
					column: {
						minWidth: 130,
						sortable: 'custom',
						align: 'left',
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: {
						rules: [{ required: true, message: '投放开始日期必填' }],
						component: {
							type: 'date',
							valueFormat: 'YYYY-MM-DD',
							placeholder: '请选择投放开始日期',
						},
					},
				},

				// 投放结束日期
				booking_end_date: {
					title: '投放结束日期',
					type: 'date',
					search: { 
						show: true,
						component: {
							type: 'date',
							valueFormat: 'YYYY-MM-DD',
						},
					},
					column: {
						minWidth: 130,
						sortable: 'custom',
						align: 'left',
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: {
						rules: [{ required: true, message: '投放结束日期必填' }],
						component: {
							type: 'date',
							valueFormat: 'YYYY-MM-DD',
							placeholder: '请选择投放结束日期',
						},
					},
				},

				// 订单状态
				order_status: {
					title: '订单状态',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: 1, label: '草稿', color: 'info' },
							{ value: 2, label: '待审批', color: 'warning' },
							{ value: 3, label: '审批中', color: 'primary' },
							{ value: 4, label: '已通过', color: 'success' },
							{ value: 5, label: '施工中', color: 'primary' },
							{ value: 6, label: '已完成', color: 'success' },
							{ value: 7, label: '已驳回', color: 'danger' },
						],
					}),
					column: {
						minWidth: 100,
						sortable: 'custom',
						align: 'left',
						component: {
							name: 'fs-dict-tag',
						},
					},
					form: {
						rules: [{ required: true, message: '订单状态必填' }],
						value: 1, // 默认草稿
						component: {
							placeholder: '请选择订单状态',
						},
					},
				},

				// 订单状态显示字段（从后端返回）
				order_status_display: {
					title: '订单状态',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: false,
						align: 'left',
						show: false, // 隐藏，使用order_status的字典标签
					},
					form: { show: false },
				},

				// 审批完成时间
				approved_time: {
					title: '审批完成时间',
					type: 'datetime',
					search: { show: false },
					column: {
						minWidth: 160,
						sortable: 'custom',
						align: 'left',
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
					},
					form: {
						rules: [{ required: false, message: '审批完成时间' }],
						component: {
							type: 'datetime',
							valueFormat: 'YYYY-MM-DD HH:mm:ss',
							placeholder: '请选择审批完成时间',
						},
						helper: '审批通过时自动填充',
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
						align: 'left',
						formatter: (context: any) => {
							const value = context.value;
							if (!value) return '-';
							// 只显示前50个字符
							return value.length > 50 ? value.substring(0, 50) + '...' : value;
						},
					},
					form: {
						col: { span: 24 }, // 占满整行
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
					search: { show: false },
					dict: dict({
						data: [
							{ value: 1, label: '启用', color: 'success' },
							{ value: 0, label: '禁用', color: 'danger' },
						],
					}),
					column: {
						minWidth: 100,
						sortable: 'custom',
						align: 'left',
						show: false,  // 隐藏列
						component: {
							name: 'fs-dict-tag',
						},
					},
					form: {
						value: 1, // 默认启用
						component: {
							placeholder: '请选择启用状态',
						},
					},
				},

				// 描述
				description: {
					title: '描述',
					type: 'textarea',
					search: { show: false },
					column: {
						minWidth: 200,
						sortable: false,
						align: 'left',
						show: false, // 默认隐藏
						formatter: (context: any) => {
							const value = context.value;
							if (!value) return '-';
							// 只显示前30个字符
							return value.length > 30 ? value.substring(0, 30) + '...' : value;
						},
					},
					form: {
						col: { span: 24 }, // 占满整行
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
						align: 'left',
						show: false,  // 隐藏列
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
						align: 'left',
						show: false, // 默认隐藏
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
						align: 'left',
						width: 160,
						sortable: 'custom',
						show: false, // 隐藏列
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
						align: 'left',
						width: 160,
						sortable: 'custom',
						show: false, // 默认隐藏
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
