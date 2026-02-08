import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';
import { ref, Ref, watch } from 'vue';
import { listPageDefMultiLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';

// 预订订单API前缀
const bookingOrderApiPrefix = '/api/BookingOrderModelViewSet/';
// 线路API前缀
const roadlineApiPrefix = '/api/RoadlineModelViewSet/';
// 公司API前缀
const companyApiPrefix = '/api/CompanyModelViewSet/';
// 媒体类型API前缀
const mediaTypeApiPrefix = '/api/AdMediaTypeModelViewSet/';

//此处为crudOptions配置
export default function ({ crudExpose }: { crudExpose: CrudExpose }): CreateCrudOptionsRet {
	// 预订订单列表
	const bookingOrderList: Ref<any[]> = ref([]);

	// 线路列表
	const roadlineList: Ref<any[]> = ref([]);

	// 公司列表
	const companyList: Ref<any[]> = ref([]);

	// 媒体类型列表
	const mediaTypeList: Ref<any[]> = ref([]);

	// 加载预订订单列表
	const loadBookingOrderList = async () => {
		try {
			const res = await request({
				url: bookingOrderApiPrefix,
				method: 'get',
				params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
			});
			if (res && res.data && res.data.results && Array.isArray(res.data.results)) {
				bookingOrderList.value = res.data.results.map((item: any) => ({
					value: item.id,
					label: `${item.booking_no || ''} ${item.customer_name || ''}`.trim() || `订单ID:${item.id}`,
				}));
			}
		} catch (error) {
			console.error('加载预订订单列表失败:', error);
		}
	};

	// 加载线路列表
	const loadRoadlineList = async () => {
		try {
			const res = await request({
				url: roadlineApiPrefix,
				method: 'get',
				params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
			});
			if (res && res.data && res.data.results && Array.isArray(res.data.results)) {
				roadlineList.value = res.data.results.map((item: any) => ({
					value: item.id,
					label: item.line_name || `线路ID:${item.id}`,
				}));
			}
		} catch (error) {
			console.error('加载线路列表失败:', error);
		}
	};

	// 加载公司列表
	const loadCompanyList = async () => {
		try {
			const res = await request({
				url: companyApiPrefix,
				method: 'get',
				params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
			});
			if (res && res.data && res.data.results && Array.isArray(res.data.results)) {
				companyList.value = res.data.results.map((item: any) => ({
					value: item.id,
					label: item.company_name || `公司ID:${item.id}`,
				}));
			}
		} catch (error) {
			console.error('加载公司列表失败:', error);
		}
	};

	// 加载媒体类型列表
	const loadMediaTypeList = async () => {
		try {
			const res = await request({
				url: mediaTypeApiPrefix,
				method: 'get',
				params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
			});
			if (res && res.data && res.data.results && Array.isArray(res.data.results)) {
				mediaTypeList.value = res.data.results.map((item: any) => ({
					value: item.id,
					label: item.media_name || `媒体类型ID:${item.id}`,
					is_composite: item.is_composite || false,
				}));
			}
		} catch (error) {
			console.error('加载媒体类型列表失败:', error);
		}
	};

	// 获取预订订单明细列表
	const pageRequest = async (query: any) => {
		return await api.GetList(query);
	};

	// 编辑预订订单明细
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}

		// 自动计算小计金额
		if (form.unit_price !== undefined && form.quantity !== undefined) {
			const unitPrice = Number(form.unit_price) || 0;
			const quantity = Number(form.quantity) || 0;
			form.subtotal_amount = unitPrice * quantity;
		}

		return await api.UpdateObj(form);
	};

	// 删除预订订单明细
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加预订订单明细
	const addRequest = async ({ form }: AddReq) => {
		// 自动计算小计金额
		if (form.unit_price !== undefined && form.quantity !== undefined) {
			const unitPrice = Number(form.unit_price) || 0;
			const quantity = Number(form.quantity) || 0;
			form.subtotal_amount = unitPrice * quantity;
		}

		return await api.AddObj(form);
	};

	// 导出数据
	const exportRequest = async (query: UserPageQuery) => {
		return await api.exportData(query);
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
				col: { span: 12 }, // 左右各占50%宽度（每列50%）
				labelWidth: '180px', // 统一label宽度（适应最长的label）
				labelAlign: 'left', // label文字左对齐
				wrapper: {
					is: 'el-dialog',
					width: '1300px', // 增加对话框宽度以适应更宽的label
					closeOnClickModal: false,
				},
			},
			actionbar: {
				buttons: {
					export: {
						show: auth('BookingOrderDetailModelViewSet:Export'),
						text: '导出',
						title: '导出',
						click() {
							return exportRequest(crudExpose.getSearchFormData());
						},
					},
					add: {
						show: auth('BookingOrderDetailModelViewSet:Create'),
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
						show: auth('BookingOrderDetailModelViewSet:Retrieve'),
					},
					edit: {
						type: 'text',
						order: 2,
						show: auth('BookingOrderDetailModelViewSet:Update'),
					},
					remove: {
						type: 'text',
						order: 3,
						show: auth('BookingOrderDetailModelViewSet:Delete'),
					},
				},
			},
			columns: {
				// 序号列
				_index: getIndexColumnConfig(crudExpose),
				
				// 预订单ID
				booking_order_id: {
					title: '预订单',
					type: 'dict-select',
					search: { show: true },
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
						show: true,
						formatter: (context: any) => {
							const value = context.value;
							if (!value) {
								return '-';
							}
							const order = bookingOrderList.value.find((item: any) => item.value === value);
							return order ? order.label : `订单ID:${value}`;
						},
					},
					form: {
						rules: [{ required: true, message: '预订单必填' }],
						component: {
							placeholder: '请选择预订单',
							filterable: true,
							clearable: false,
						},
					},
				},

				// 线路ID
				roadline_id: {
					title: '线路',
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
						minWidth: 150,
						sortable: 'custom',
						show: true,
						formatter: (context: any) => {
							const value = context.value;
							if (!value) {
								return '-';
							}
							const roadline = roadlineList.value.find((item: any) => item.value === value);
							return roadline ? roadline.label : `线路ID:${value}`;
						},
					},
					form: {
						rules: [{ required: true, message: '线路必填' }],
						component: {
							placeholder: '请选择线路',
							filterable: true,
							clearable: false,
						},
					},
				},

				// 线路名称（冗余字段）
				roadline_name: {
					title: '线路名称',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 150,
						sortable: 'custom',
						show: true,
					},
					form: {
						show: false, // 表单中不显示，由后端自动填充
					},
				},

				// 营运公司ID
				roadline_company_id: {
					title: '营运公司',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						value: 'value',
						label: 'label',
						getData: async () => {
							if (companyList.value.length === 0) {
								await loadCompanyList();
							}
							return companyList.value;
						},
					}),
					column: {
						minWidth: 150,
						sortable: 'custom',
						show: true,
						formatter: (context: any) => {
							const value = context.value;
							if (!value) {
								return '-';
							}
							const company = companyList.value.find((item: any) => item.value === value);
							return company ? company.label : `公司ID:${value}`;
						},
					},
					form: {
						rules: [{ required: true, message: '营运公司必填' }],
						component: {
							placeholder: '请选择营运公司',
							filterable: true,
							clearable: false,
						},
					},
				},

				// 营运公司名称（冗余字段）
				roadline_company_name: {
					title: '营运公司名称',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 150,
						sortable: 'custom',
						show: false,
					},
					form: {
						show: false, // 表单中不显示，由后端自动填充
					},
				},

				// 媒体类型ID
				media_type_id: {
					title: '媒体类型',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						value: 'value',
						label: 'label',
						getData: async () => {
							if (mediaTypeList.value.length === 0) {
								await loadMediaTypeList();
							}
							return mediaTypeList.value;
						},
					}),
					column: {
						minWidth: 150,
						sortable: 'custom',
						show: true,
						formatter: (context: any) => {
							const value = context.value;
							if (!value) {
								return '-';
							}
							const mediaType = mediaTypeList.value.find((item: any) => item.value === value);
							return mediaType ? mediaType.label : `媒体类型ID:${value}`;
						},
					},
					form: {
						rules: [{ required: true, message: '媒体类型必填' }],
						component: {
							placeholder: '请选择媒体类型',
							filterable: true,
							clearable: false,
						},
						onChange: (context: any) => {
							// 当选择媒体类型时，自动设置是否组合类型
							const mediaTypeId = context.value;
							if (mediaTypeId) {
								const mediaType = mediaTypeList.value.find((item: any) => item.value === mediaTypeId);
								if (mediaType) {
									context.form.is_composite = mediaType.is_composite || false;
								}
							}
						},
					},
				},

				// 媒体类型名称（冗余字段）
				media_type_name: {
					title: '媒体类型名称',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 150,
						sortable: 'custom',
						show: false,
					},
					form: {
						show: false, // 表单中不显示，由后端自动填充
					},
				},

				// 是否组合类型
				is_composite: {
					title: '是否组合类型',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: true, label: '是' },
							{ value: false, label: '否' },
						],
					}),
					column: {
						minWidth: 120,
						sortable: 'custom',
						align: 'center',
						show: true,
						formatter: (context: any) => {
							const value = context.value;
							return value ? '是' : '否';
						},
					},
					form: {
						rules: [{ required: true, message: '是否组合类型必填' }],
						value: false, // 默认值：否
						component: {
							placeholder: '请选择是否组合类型',
						},
					},
				},

				// 预订数量
				quantity: {
					title: '预订数量',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: 'custom',
						align: 'right',
						show: true,
						formatter: (context: any) => {
							const value = context.value;
							return value ? `${value}辆` : '-';
						},
					},
					form: {
						rules: [
							{ required: true, message: '预订数量必填' },
							{ type: 'number', min: 1, message: '预订数量必须大于0' },
						],
						component: {
							placeholder: '请输入预订的车辆数量',
							precision: 0,
							min: 1,
						},
						onChange: (context: any) => {
							// 当数量变化时，自动计算小计金额
							const quantity = Number(context.value) || 0;
							const unitPrice = Number(context.form.unit_price) || 0;
							if (quantity > 0 && unitPrice > 0) {
								context.form.subtotal_amount = quantity * unitPrice;
							}
						},
					},
				},

				// 单价
				unit_price: {
					title: '单价(元)',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: 'custom',
						align: 'right',
						show: true,
						formatter: (context: any) => {
							const value = context.value;
							if (!value) {
								return '-';
							}
							return `¥${Number(value).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
						},
					},
					form: {
						component: {
							placeholder: '请输入单价（元/月或元/年）',
							precision: 2,
							min: 0,
						},
						onChange: (context: any) => {
							// 当单价变化时，自动计算小计金额
							const unitPrice = Number(context.value) || 0;
							const quantity = Number(context.form.quantity) || 0;
							if (unitPrice > 0 && quantity > 0) {
								context.form.subtotal_amount = quantity * unitPrice;
							}
						},
					},
				},

				// 小计金额
				subtotal_amount: {
					title: '小计金额(元)',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 150,
						sortable: 'custom',
						align: 'right',
						show: true,
						formatter: (context: any) => {
							const value = context.value;
							if (!value) {
								return '-';
							}
							return `¥${Number(value).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
						},
					},
					form: {
						show: false, // 表单中不显示，由系统自动计算
					},
				},

				// 资源锁定状态
				lock_status: {
					title: '资源锁定状态',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: 1, label: '未锁定' },
							{ value: 2, label: '已锁定' },
							{ value: 3, label: '已释放' },
						],
					}),
					column: {
						minWidth: 120,
						sortable: 'custom',
						align: 'left',
						show: false, // 隐藏，使用计算字段lock_status_display显示
					},
					form: {
						rules: [{ required: true, message: '资源锁定状态必填' }],
						value: 1, // 默认值：未锁定
						component: {
							placeholder: '请选择资源锁定状态',
						},
					},
				},

				// 资源锁定状态显示字段
				lock_status_display: {
					title: '资源锁定状态',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: false,
						align: 'left',
						show: true,
					},
					form: { show: false },
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
						show: true,
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

