import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';
import { ref, Ref } from 'vue';
// @ts-ignore - defConfig.js 没有类型声明
import { listPageDefSingleLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';

// API前缀
const onAirOrderApiPrefix = '/api/OnAirOrderModelViewSet/';
const vehicleAdPositionApiPrefix = '/api/VehicleAdPositionModelViewSet/';
const roadlineApiPrefix = '/api/RoadlineModelViewSet/';
const companyApiPrefix = '/api/CompanyModelViewSet/';
const vehicleApiPrefix = '/api/VehicleModelViewSet/';
const mediaTypeApiPrefix = '/api/AdMediaTypeModelViewSet/';

//此处为crudOptions配置
export default function ({ crudExpose }: { crudExpose: CrudExpose }): CreateCrudOptionsRet {
	// 上刊订单列表
	const onAirOrderList: Ref<any[]> = ref([]);
	// 车位广告列表
	const vehicleAdPositionList: Ref<any[]> = ref([]);
	// 线路列表
	const roadlineList: Ref<any[]> = ref([]);
	// 营运公司列表
	const companyList: Ref<any[]> = ref([]);
	// 车辆列表
	const vehicleList: Ref<any[]> = ref([]);
	// 基础媒体类型列表
	const baseMediaTypeList: Ref<any[]> = ref([]);
	// 组合媒体类型列表
	const compositeMediaTypeList: Ref<any[]> = ref([]);

	// 兼容两种返回格式
	const getListData = (resp: any): any[] => {
		const data = resp?.data;
		if (Array.isArray(data)) return data;
		if (data && Array.isArray(data.results)) return data.results;
		return [];
	};

	// 加载上刊订单列表
	const loadOnAirOrderList = async () => {
		try {
			const res = await request({
				url: onAirOrderApiPrefix,
				method: 'get',
				params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
			});
			const list = getListData(res);
			if (list.length > 0) {
				onAirOrderList.value = list.map((item: any) => ({
					value: item.id,
					label: `${item.order_no || ''} - ${item.customer_name || ''}`.trim() || `订单ID:${item.id}`,
					order_no: item.order_no || '',
				}));
			}
		} catch (error) {
			console.error('加载上刊订单列表失败:', error);
		}
	};

	// 加载车位广告列表
	const loadVehicleAdPositionList = async () => {
		try {
			const res = await request({
				url: vehicleAdPositionApiPrefix,
				method: 'get',
				params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
			});
			const list = getListData(res);
			if (list.length > 0) {
				vehicleAdPositionList.value = list.map((item: any) => ({
					value: item.id,
					label: `${item.roadline_name || ''} - ${item.vehicle_no || ''} - ${item.base_media_type_name || ''}`.trim() || `车位ID:${item.id}`,
					roadline_id: item.roadline_id,
					roadline_name: item.roadline_name,
					roadline_company_id: item.roadline_company_id,
					roadline_company_name: item.roadline_company_name,
					vehicle_id: item.vehicle_id,
					vehicle_no: item.vehicle_no,
					base_media_type_id: item.base_media_type_id,
					base_media_type_name: item.base_media_type_name,
				}));
			}
		} catch (error) {
			console.error('加载车位广告列表失败:', error);
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
			const list = getListData(res);
			if (list.length > 0) {
				roadlineList.value = list.map((item: any) => ({
					value: item.id,
					label: item.line_name || `线路ID:${item.id}`,
				}));
			}
		} catch (error) {
			console.error('加载线路列表失败:', error);
		}
	};

	// 加载营运公司列表
	const loadCompanyList = async () => {
		try {
			const res = await request({
				url: companyApiPrefix,
				method: 'get',
				params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
			});
			const list = getListData(res);
			if (list.length > 0) {
				companyList.value = list.map((item: any) => ({
					value: item.id,
					label: item.company_name || `公司ID:${item.id}`,
				}));
			}
		} catch (error) {
			console.error('加载营运公司列表失败:', error);
		}
	};

	// 加载车辆列表
	const loadVehicleList = async () => {
		try {
			const res = await request({
				url: vehicleApiPrefix,
				method: 'get',
				params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
			});
			const list = getListData(res);
			if (list.length > 0) {
				vehicleList.value = list.map((item: any) => ({
					value: item.id,
					label: `${item.vehicle_plate || ''} ${item.vehicle_no || ''}`.trim() || `车辆ID:${item.id}`,
					vehicle_no: item.vehicle_no || '',
				}));
			}
		} catch (error) {
			console.error('加载车辆列表失败:', error);
		}
	};

	// 加载基础媒体类型列表（is_composite=false）
	const loadBaseMediaTypeList = async () => {
		try {
			const res = await request({
				url: mediaTypeApiPrefix,
				method: 'get',
				params: { limit: 9999, is_composite: false, enabled_mark: 1, delete_mark: 0 },
			});
			const list = getListData(res);
			if (list.length > 0) {
				baseMediaTypeList.value = list.map((item: any) => ({
					value: item.id,
					label: item.media_name || `媒体类型ID:${item.id}`,
					media_name: item.media_name || '',
				}));
			}
		} catch (error) {
			console.error('加载基础媒体类型列表失败:', error);
		}
	};

	// 加载组合媒体类型列表（is_composite=true）
	const loadCompositeMediaTypeList = async () => {
		try {
			const res = await request({
				url: mediaTypeApiPrefix,
				method: 'get',
				params: { limit: 9999, is_composite: true, enabled_mark: 1, delete_mark: 0 },
			});
			const list = getListData(res);
			if (list.length > 0) {
				compositeMediaTypeList.value = list.map((item: any) => ({
					value: item.id,
					label: item.media_name || `媒体类型ID:${item.id}`,
					media_name: item.media_name || '',
				}));
			}
		} catch (error) {
			console.error('加载组合媒体类型列表失败:', error);
		}
	};

	// 获取上刊订单明细列表
	const pageRequest = async (query: any) => {
		return await api.GetList(query);
	};

	// 编辑上刊订单明细
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}
		return await api.UpdateObj(form);
	};

	// 删除上刊订单明细
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加上刊订单明细
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
				labelWidth: '140px',
				wrapper: {
					is: 'el-dialog',
					width: '1000px',
					closeOnClickModal: false,
				},
			},
			actionbar: {
				buttons: {
					export: {
						show: auth('OnAirOrderDetailModelViewSet:Export'),
						text: '导出',
						title: '导出',
						click() {
							return exportRequest(crudExpose.getSearchFormData());
						},
					},
					add: {
						show: auth('OnAirOrderDetailModelViewSet:Create'),
					},
				},
			},
			rowHandle: {
				fixed: 'right',
				width: 150,
				buttons: {
					view: {
						type: 'text',
						order: 1,
						show: auth('OnAirOrderDetailModelViewSet:Retrieve'),
					},
					edit: {
						type: 'text',
						order: 2,
						show: auth('OnAirOrderDetailModelViewSet:Update'),
					},
					remove: {
						type: 'text',
						order: 3,
						show: auth('OnAirOrderDetailModelViewSet:Delete'),
					},
				},
			},
			columns: {
				// 序号列
				_index: getIndexColumnConfig(crudExpose),

				// 上刊订单ID
				order_id: {
					title: '上刊订单',
					type: 'dict-select',
					search: { 
						show: true,
						component: {
							placeholder: '请选择或搜索上刊订单',
						},
					},
					dict: dict({
						value: 'value',
						label: 'label',
						getData: async () => {
							if (onAirOrderList.value.length === 0) {
								await loadOnAirOrderList();
							}
							return onAirOrderList.value;
						},
					}),
					column: {
						minWidth: 180,
						sortable: 'custom',
						align: 'left',
						formatter: (context: any) => {
							const value = context.value;
							if (!value) return '-';
							const order = onAirOrderList.value.find((item: any) => item.value === value);
							return order?.label || `订单ID:${value}`;
						},
					},
					form: {
						rules: [{ required: true, message: '上刊订单必填' }],
						component: {
							placeholder: '请选择上刊订单',
							filterable: true,
							clearable: false,
						},
					},
				},

				// 车位广告ID
				position_id: {
					title: '车位广告',
					type: 'dict-select',
					search: { 
						show: true,
						component: {
							placeholder: '请选择或搜索车位广告',
						},
					},
					dict: dict({
						value: 'value',
						label: 'label',
						getData: async () => {
							if (vehicleAdPositionList.value.length === 0) {
								await loadVehicleAdPositionList();
							}
							return vehicleAdPositionList.value;
						},
					}),
					column: {
						minWidth: 200,
						sortable: 'custom',
						align: 'left',
						formatter: (context: any) => {
							const value = context.value;
							if (!value) return '-';
							const position = vehicleAdPositionList.value.find((item: any) => item.value === value);
							return position?.label || `车位ID:${value}`;
						},
					},
					form: {
						rules: [{ required: true, message: '车位广告必填' }],
						component: {
							placeholder: '请选择车位广告',
							filterable: true,
							clearable: false,
						},
						// 当选择车位广告时，自动填充相关信息
						onChange: ({ form }: any) => {
							const positionId = form.position_id;
							if (positionId) {
								const position = vehicleAdPositionList.value.find((item: any) => item.value === positionId);
								if (position) {
									// 自动填充线路信息
									if (position.roadline_id && !form.roadline_id) {
										form.roadline_id = position.roadline_id;
									}
									if (position.roadline_name && !form.roadline_name) {
										form.roadline_name = position.roadline_name;
									}
									// 自动填充公司信息
									if (position.roadline_company_id && !form.roadline_company_id) {
										form.roadline_company_id = position.roadline_company_id;
									}
									if (position.roadline_company_name && !form.roadline_company_name) {
										form.roadline_company_name = position.roadline_company_name;
									}
									// 自动填充预订车辆信息
									if (position.vehicle_id && !form.plan_vehicle_id) {
										form.plan_vehicle_id = position.vehicle_id;
									}
									if (position.vehicle_no && !form.plan_vehicle_no) {
										form.plan_vehicle_no = position.vehicle_no;
									}
									// 自动填充基础媒体类型
									if (position.base_media_type_id && !form.base_media_type_id) {
										form.base_media_type_id = position.base_media_type_id;
									}
									if (position.base_media_type_name && !form.base_media_type_name) {
										form.base_media_type_name = position.base_media_type_name;
									}
								}
							}
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
						align: 'left',
						show: false, // 隐藏，使用roadline_name显示
					},
					form: {
						rules: [{ required: true, message: '线路必填' }],
						component: {
							placeholder: '请选择线路',
							filterable: true,
						},
					},
				},

				// 线路名称
				roadline_name: {
					title: '线路名称',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 150,
						sortable: 'custom',
						align: 'left',
					},
					form: {
						component: {
							placeholder: '线路名称（自动填充）',
						},
						helper: '线路名称，通常从车位广告自动填充',
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
						align: 'left',
						show: false, // 隐藏，使用roadline_company_name显示
					},
					form: {
						rules: [{ required: true, message: '营运公司必填' }],
						component: {
							placeholder: '请选择营运公司',
							filterable: true,
						},
					},
				},

				// 营运公司名称
				roadline_company_name: {
					title: '营运公司名称',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 150,
						sortable: 'custom',
						align: 'left',
					},
					form: {
						component: {
							placeholder: '营运公司名称（自动填充）',
						},
						helper: '营运公司名称，通常从车位广告自动填充',
					},
				},

				// 预订车辆ID
				plan_vehicle_id: {
					title: '预订车辆',
					type: 'dict-select',
					search: { show: false },
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
						minWidth: 150,
						sortable: 'custom',
						align: 'left',
						show: false, // 隐藏，使用plan_vehicle_no显示
					},
					form: {
						component: {
							placeholder: '请选择预订车辆',
							filterable: true,
						},
						onChange: ({ form }: any) => {
							const vehicleId = form.plan_vehicle_id;
							if (vehicleId) {
								const vehicle = vehicleList.value.find((item: any) => item.value === vehicleId);
								if (vehicle && vehicle.vehicle_no && !form.plan_vehicle_no) {
									form.plan_vehicle_no = vehicle.vehicle_no;
								}
							}
						},
					},
				},

				// 预订车辆自编号
				plan_vehicle_no: {
					title: '预订车辆自编号',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 120,
						sortable: 'custom',
						align: 'left',
					},
					form: {
						component: {
							placeholder: '预订车辆自编号（自动填充）',
						},
					},
				},

				// 实际上刊车辆ID
				act_vehicle_id: {
					title: '实际上刊车辆',
					type: 'dict-select',
					search: { show: false },
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
						minWidth: 150,
						sortable: 'custom',
						align: 'left',
						show: false, // 隐藏，使用act_vehicle_no显示
					},
					form: {
						component: {
							placeholder: '请选择实际上刊车辆',
							filterable: true,
						},
						helper: '实际上刊车辆可能与预订车辆不同',
						onChange: ({ form }: any) => {
							const vehicleId = form.act_vehicle_id;
							if (vehicleId) {
								const vehicle = vehicleList.value.find((item: any) => item.value === vehicleId);
								if (vehicle && vehicle.vehicle_no && !form.act_vehicle_no) {
									form.act_vehicle_no = vehicle.vehicle_no;
								}
							}
						},
					},
				},

				// 实际上刊车辆自编号
				act_vehicle_no: {
					title: '实际上刊车辆自编号',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 120,
						sortable: 'custom',
						align: 'left',
					},
					form: {
						component: {
							placeholder: '实际上刊车辆自编号（自动填充）',
						},
					},
				},

				// 组合媒体类型ID
				composite_media_type_id: {
					title: '组合媒体类型',
					type: 'dict-select',
					search: { show: false },
					dict: dict({
						value: 'value',
						label: 'label',
						getData: async () => {
							if (compositeMediaTypeList.value.length === 0) {
								await loadCompositeMediaTypeList();
							}
							return compositeMediaTypeList.value;
						},
					}),
					column: {
						minWidth: 120,
						sortable: 'custom',
						align: 'left',
						show: false, // 隐藏，使用composite_media_type_name显示
					},
					form: {
						component: {
							placeholder: '请选择组合媒体类型（可选）',
							filterable: true,
						},
						helper: '如"大三侧"、"全车身"等，NULL表示单独预订基础类型',
						onChange: ({ form }: any) => {
							const typeId = form.composite_media_type_id;
							if (typeId) {
								const type = compositeMediaTypeList.value.find((item: any) => item.value === typeId);
								if (type && type.media_name && !form.composite_media_type_name) {
									form.composite_media_type_name = type.media_name;
								}
							}
						},
					},
				},

				// 组合媒体类型名称
				composite_media_type_name: {
					title: '组合媒体类型名称',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: false,
						align: 'left',
					},
					form: {
						component: {
							placeholder: '组合媒体类型名称（自动填充）',
						},
						show: false, // 表单中不显示，自动填充
					},
				},

				// 基础媒体类型ID
				base_media_type_id: {
					title: '基础媒体类型',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						value: 'value',
						label: 'label',
						getData: async () => {
							if (baseMediaTypeList.value.length === 0) {
								await loadBaseMediaTypeList();
							}
							return baseMediaTypeList.value;
						},
					}),
					column: {
						minWidth: 120,
						sortable: 'custom',
						align: 'left',
						show: false, // 隐藏，使用base_media_type_name显示
					},
					form: {
						rules: [{ required: true, message: '基础媒体类型必填' }],
						component: {
							placeholder: '请选择基础媒体类型',
							filterable: true,
						},
						onChange: ({ form }: any) => {
							const typeId = form.base_media_type_id;
							if (typeId) {
								const type = baseMediaTypeList.value.find((item: any) => item.value === typeId);
								if (type && type.media_name && !form.base_media_type_name) {
									form.base_media_type_name = type.media_name;
								}
							}
						},
					},
				},

				// 基础媒体类型名称
				base_media_type_name: {
					title: '基础媒体类型名称',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 120,
						sortable: false,
						align: 'left',
					},
					form: {
						component: {
							placeholder: '基础媒体类型名称（自动填充）',
						},
						show: false, // 表单中不显示，自动填充
					},
				},

				// 实际上刊时间
				act_on_air_datetime: {
					title: '实际上刊时间',
					type: 'datetime',
					search: { show: false },
					column: {
						minWidth: 160,
						sortable: 'custom',
						align: 'left',
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
					},
					form: {
						component: {
							type: 'datetime',
							valueFormat: 'YYYY-MM-DD HH:mm:ss',
							placeholder: '请选择实际上刊时间',
						},
						helper: '实际上刊时间（精确到时分秒）',
					},
				},

				// 执行状态
				execution_status: {
					title: '执行状态',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: 1, label: '待执行', color: 'info' },
							{ value: 2, label: '施工中', color: 'warning' },
							{ value: 3, label: '已完成', color: 'success' },
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
						rules: [{ required: true, message: '执行状态必填' }],
						value: 1, // 默认待执行
						component: {
							placeholder: '请选择执行状态',
						},
					},
				},

				// 执行状态显示字段
				execution_status_display: {
					title: '执行状态',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: false,
						align: 'left',
						show: false, // 隐藏，使用execution_status的字典标签
					},
					form: { show: false },
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
							return value.length > 50 ? value.substring(0, 50) + '...' : value;
						},
					},
					form: {
						col: { span: 24 },
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
						show: false,
						component: {
							name: 'fs-dict-tag',
						},
					},
					form: {
						value: 1,
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
						show: false,
						formatter: (context: any) => {
							const value = context.value;
							if (!value) return '-';
							return value.length > 30 ? value.substring(0, 30) + '...' : value;
						},
					},
					form: {
						col: { span: 24 },
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
						show: false,
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
						show: false,
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
						show: false,
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
						show: false,
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
