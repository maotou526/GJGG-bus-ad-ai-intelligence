import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, CreateCrudOptionsRet, UserPageQuery } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';
import { Ref, ref } from 'vue';
import { listPageDefMultiLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';

// 预订单明细、线路、公司、车辆、资源位 API 前缀
const bookingDetailApiPrefix = '/api/BookingOrderDetailModelViewSet/';
const roadlineApiPrefix = '/api/RoadlineModelViewSet/';
const companyApiPrefix = '/api/CompanyModelViewSet/';
const vehicleApiPrefix = '/api/VehicleModelViewSet/';
const resourceApiPrefix = '/api/VehicleAdResourceModelViewSet/';

// 此处为 crudOptions 配置
export default function ({ crudExpose }: { crudExpose: CrudExpose }): CreateCrudOptionsRet {
	// 下拉选项缓存
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

	// 各业务列表加载
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

	// 编辑请求
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}

		// 处理日期字段，确保提交纯日期格式
		['reserved_start_date', 'reserved_end_date', 'actual_on_date', 'actual_off_date'].forEach((key) => {
			if (form[key] && typeof form[key] === 'string') {
				form[key] = form[key].split(' ')[0];
			}
		});

		return await api.UpdateObj(form);
	};

	// 删除请求
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 新增请求
	const addRequest = async ({ form }: AddReq) => {
		['reserved_start_date', 'reserved_end_date', 'actual_on_date', 'actual_off_date'].forEach((key) => {
			if (form[key] && typeof form[key] === 'string') {
				form[key] = form[key].split(' ')[0];
			}
		});
		return await api.AddObj(form);
	};

	// 导出（预留）
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
						show: auth('VehicleAdPositionModelViewSet:Export'),
						text: '导出',
						title: '导出',
						click() {
							return exportRequest(crudExpose.getSearchFormData());
						},
					},
					add: {
						show: auth('VehicleAdPositionModelViewSet:Create'),
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
						show: auth('VehicleAdPositionModelViewSet:Retrieve'),
					},
					edit: {
						type: 'text',
						order: 2,
						show: auth('VehicleAdPositionModelViewSet:Update'),
					},
					remove: {
						type: 'text',
						order: 3,
						show: auth('VehicleAdPositionModelViewSet:Delete'),
					},
				},
			},
			columns: {
				// 序号列
				_index: getIndexColumnConfig(crudExpose),

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
						minWidth: 120,
						sortable: 'custom',
						show: true,
					},
					form: {
						rules: [{ required: true, message: '预订单明细必选' }],
						component: {
							placeholder: '请选择预订单明细',
							filterable: true,
							clearable: false,
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
						rules: [{ required: true, message: '线路必选' }],
						component: {
							placeholder: '请选择线路',
							filterable: true,
							clearable: false,
						},
					},
				},

				roadline_name: {
					title: '线路名称',
					type: 'text',
					search: { show: false },
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
						minWidth: 160,
						sortable: 'custom',
						show: false,
					},
					form: {
						rules: [{ required: true, message: '营运公司必选' }],
						component: {
							placeholder: '请选择营运公司',
							filterable: true,
							clearable: false,
						},
					},
				},

				roadline_company_name: {
					title: '营运公司名称',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 180,
						sortable: 'custom',
						show: true,
					},
					form: { show: false },
				},

				// 资源位
				resource_id: {
					title: '车辆资源位',
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
						rules: [{ required: true, message: '资源位必选' }],
						component: {
							placeholder: '请选择资源位',
							filterable: true,
							clearable: false,
						},
					},
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
						rules: [{ required: true, message: '车辆必选' }],
						component: {
							placeholder: '请选择车辆',
							filterable: true,
							clearable: false,
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
					form: {
						show: false,
					},
				},

				// 预订开始日期
				reserved_start_date: {
					title: '预订开始日期',
					type: 'date',
					search: { show: false },
					column: {
						align: 'center',
						width: 130,
						show: true,
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: {
						rules: [{ required: true, message: '预订开始日期必填' }],
						component: {
							format: 'YYYY-MM-DD',
							valueFormat: 'YYYY-MM-DD',
							placeholder: '请选择预订开始日期',
						},
					},
				},

				// 预订结束日期
				reserved_end_date: {
					title: '预订结束日期',
					type: 'date',
					search: { show: false },
					column: {
						align: 'center',
						width: 130,
						show: true,
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: {
						rules: [{ required: true, message: '预订结束日期必填' }],
						component: {
							format: 'YYYY-MM-DD',
							valueFormat: 'YYYY-MM-DD',
							placeholder: '请选择预订结束日期',
						},
					},
				},

				// 实际上刊日期
				actual_on_date: {
					title: '实际上刊日期',
					type: 'date',
					search: { show: false },
					column: {
						align: 'center',
						width: 130,
						show: true,
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: {
						component: {
							format: 'YYYY-MM-DD',
							valueFormat: 'YYYY-MM-DD',
							placeholder: '请选择实际上刊日期',
						},
					},
				},

				// 实际下刊日期
				actual_off_date: {
					title: '实际下刊日期',
					type: 'date',
					search: { show: false },
					column: {
						align: 'center',
						width: 130,
						show: true,
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: {
						component: {
							format: 'YYYY-MM-DD',
							valueFormat: 'YYYY-MM-DD',
							placeholder: '请选择实际下刊日期',
						},
					},
				},

				// 分配状态
				allocation_status: {
					title: '分配状态',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: 1, label: '已分配' },
							{ value: 2, label: '已上刊' },
							{ value: 3, label: '已下刊' },
							{ value: 4, label: '已取消' },
						],
					}),
					column: {
						minWidth: 110,
						sortable: 'custom',
						show: false,
					},
					form: {
						value: 1,
						rules: [{ required: true, message: '分配状态必选' }],
						component: {
							placeholder: '请选择分配状态',
						},
					},
				},

				allocation_status_display: {
					title: '分配状态',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 110,
						sortable: false,
						show: true,
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


