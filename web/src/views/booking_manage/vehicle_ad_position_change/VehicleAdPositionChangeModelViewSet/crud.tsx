import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';
import { ref, Ref } from 'vue';
import { listPageDefMultiLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';

// 预订单、预订单明细、线路、公司、车辆、资源位 API 前缀
const bookingOrderApiPrefix = '/api/BookingOrderModelViewSet/';
const bookingDetailApiPrefix = '/api/BookingOrderDetailModelViewSet/';
const roadlineApiPrefix = '/api/RoadlineModelViewSet/';
const companyApiPrefix = '/api/CompanyModelViewSet/';
const vehicleApiPrefix = '/api/VehicleModelViewSet/';
const resourceApiPrefix = '/api/VehicleAdResourceModelViewSet/';

// 此处为 crudOptions 配置
export default function ({ crudExpose }: { crudExpose: CrudExpose }): CreateCrudOptionsRet {
	// 下拉选项缓存
	const bookingOrderList: Ref<any[]> = ref([]);
	const bookingDetailList: Ref<any[]> = ref([]);
	const roadlineList: Ref<any[]> = ref([]);
	const companyList: Ref<any[]> = ref([]);
	const vehicleList: Ref<any[]> = ref([]);
	const resourceList: Ref<any[]> = ref([]);

	// 通用加载列表方法
	const loadSimpleList = async (url: string, target: Ref<any[]>, labelBuilder: (item: any) => string) => {
		try {
			const res = await request({
				url,
				method: 'get',
				params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
			});
			if (res && res.data && res.data.results && Array.isArray(res.data.results)) {
				target.value = res.data.results.map((item: any) => ({
					value: item.id,
					label: labelBuilder(item),
					raw: item,
				}));
			}
		} catch (error) {
			console.error('加载下拉数据失败:', url, error);
		}
	};

	const loadBookingOrderList = () =>
		loadSimpleList(
			bookingOrderApiPrefix,
			bookingOrderList,
			(item) => `${item.booking_no || ''} ${item.customer_name || ''}`.trim() || `预订单ID:${item.id}`,
		);
	const loadBookingDetailList = () =>
		loadSimpleList(bookingDetailApiPrefix, bookingDetailList, (item) => `明细ID:${item.id}`);
	const loadRoadlineList = () =>
		loadSimpleList(roadlineApiPrefix, roadlineList, (item) => item.line_name || `线路ID:${item.id}`);
	const loadCompanyList = () =>
		loadSimpleList(companyApiPrefix, companyList, (item) => item.company_name || `公司ID:${item.id}`);
	const loadVehicleList = () =>
		loadSimpleList(
			vehicleApiPrefix,
			vehicleList,
			(item) => `${item.vehicle_no || ''} ${item.vehicle_plate || ''}`.trim() || `车辆ID:${item.id}`,
		);
	const loadResourceList = () =>
		loadSimpleList(resourceApiPrefix, resourceList, (item) => item.resource_code || `资源ID:${item.id}`);

	// 列表请求
	const pageRequest = async (query: any) => {
		return await api.GetList(query);
	};

	// 编辑请求（一般不需要修改历史，仅预留）
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}
		// 处理时间字段
		if (form.operation_time && typeof form.operation_time === 'string') {
			form.operation_time = form.operation_time.replace('T', ' ').split('.')[0];
		}
		return await api.UpdateObj(form);
	};

	// 删除请求（不建议大量使用，仅预留）
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加请求（主要通过后端业务写入，界面新增仅作为辅助）
	const addRequest = async ({ form }: AddReq) => {
		if (form.operation_time && typeof form.operation_time === 'string') {
			form.operation_time = form.operation_time.replace('T', ' ').split('.')[0];
		}
		return await api.AddObj(form);
	};

	// 导出数据（预留）
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
				col: { span: 12 },
				labelWidth: '180px',
				labelAlign: 'left',
				wrapper: {
					is: 'el-dialog',
					width: '1300px',
					closeOnClickModal: false,
				},
			},
			actionbar: {
				buttons: {
					export: {
						show: auth('VehicleAdPositionChangeModelViewSet:Export'),
						text: '导出',
						title: '导出',
						click() {
							return exportRequest(crudExpose.getSearchFormData());
						},
					},
					add: {
						show: auth('VehicleAdPositionChangeModelViewSet:Create'),
					},
				},
			},
			rowHandle: {
				fixed: 'right',
				width: 220,
				buttons: {
					view: {
						type: 'text',
						order: 1,
						show: auth('VehicleAdPositionChangeModelViewSet:Retrieve'),
					},
					edit: {
						type: 'text',
						order: 2,
						show: auth('VehicleAdPositionChangeModelViewSet:Update'),
					},
					remove: {
						type: 'text',
						order: 3,
						show: auth('VehicleAdPositionChangeModelViewSet:Delete'),
					},
				},
			},
			columns: {
				// 序号列
				_index: getIndexColumnConfig(crudExpose),

				// 预订单
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
					},
					form: {
						rules: [{ required: true, message: '预订单必选' }],
						component: {
							placeholder: '请选择预订单',
							filterable: true,
							clearable: false,
						},
					},
				},

				// 预订单明细
				booking_detail_id: {
					title: '预订单明细',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						value: 'value',
						label: 'label',
						getData: async () => {
							if (bookingDetailList.value.length === 0) {
								await loadBookingDetailList();
							}
							return bookingDetailList.value;
						},
					}),
					column: {
						minWidth: 140,
						sortable: 'custom',
						show: true,
					},
					form: {
						component: {
							placeholder: '可选：请选择预订单明细',
							filterable: true,
							clearable: true,
						},
					},
				},

				// 操作类型
				action_type: {
					title: '操作类型',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: 1, label: '新增车位' },
							{ value: 2, label: '删除车位' },
							{ value: 3, label: '修改车位' },
						],
					}),
					column: {
						minWidth: 110,
						sortable: 'custom',
						show: true,
					},
					form: {
						rules: [{ required: true, message: '操作类型必选' }],
						component: {
							placeholder: '请选择操作类型',
						},
					},
				},

				// 线路
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
						minWidth: 160,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '可选：请选择线路',
							filterable: true,
							clearable: true,
						},
					},
				},

				roadline_name: {
					title: '线路名称',
					type: 'text',
					search: { show: true },
					column: {
						minWidth: 160,
						sortable: 'custom',
						show: true,
					},
					form: { show: false },
				},

				// 营运公司
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
						minWidth: 180,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '可选：请选择营运公司',
							filterable: true,
							clearable: true,
						},
					},
				},

				roadline_company_name: {
					title: '营运公司名称',
					type: 'text',
					search: { show: true },
					column: {
						minWidth: 180,
						sortable: 'custom',
						show: true,
					},
					form: { show: false },
				},

				// 车辆
				vehicle_id: {
					title: '车辆',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						value: 'value',
						label: 'label',
						getData: async () => {
							if (vehicleList.value.length === 0) {
								await loadVehicleList();
							}
							return vehicleList.value;
						},
					}),
					column: {
						minWidth: 180,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '可选：请选择车辆',
							filterable: true,
							clearable: true,
						},
					},
				},

				vehicle_no: {
					title: '车辆自编号',
					type: 'text',
					search: { show: true },
					column: {
						minWidth: 140,
						sortable: 'custom',
						show: true,
					},
					form: { show: false },
				},

				// 资源位
				resource_id: {
					title: '资源位',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						value: 'value',
						label: 'label',
						getData: async () => {
							if (resourceList.value.length === 0) {
								await loadResourceList();
							}
							return resourceList.value;
						},
					}),
					column: {
						minWidth: 160,
						sortable: 'custom',
						show: true,
					},
					form: {
						component: {
							placeholder: '可选：请选择资源位',
							filterable: true,
							clearable: true,
						},
					},
				},

				// 变更节点
				change_node: {
					title: '变更节点',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: '1', label: '媒体部初审' },
							{ value: '2', label: '营运公司审核' },
							{ value: '3', label: '媒体部复审' },
						],
					}),
					column: {
						minWidth: 140,
						sortable: 'custom',
						show: true,
					},
					form: {
						rules: [{ required: true, message: '变更节点必选' }],
						component: {
							placeholder: '请选择变更节点',
						},
					},
				},

				// 变更原因
				change_reason: {
					title: '变更原因',
					type: 'textarea',
					search: { show: false },
					column: {
						minWidth: 220,
						sortable: 'custom',
						show: true,
					},
					form: {
						component: {
							placeholder: '请输入变更原因说明',
							rows: 3,
						},
					},
				},

				// 操作时间
				operation_time: {
					title: '操作时间',
					type: 'datetime',
					search: { show: true },
					column: {
						align: 'center',
						width: 180,
						show: true,
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
					},
					form: {
						rules: [{ required: true, message: '操作时间必填' }],
						component: {
							format: 'YYYY-MM-DD HH:mm:ss',
							valueFormat: 'YYYY-MM-DD HH:mm:ss',
							placeholder: '请选择操作时间',
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


