import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';
import { ref, Ref, watch, computed } from 'vue';
import { listPageDefMultiLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';

// 代理商API前缀
const agentApiPrefix = '/api/AgentModelViewSet/';
// 线路API前缀
const roadlineApiPrefix = '/api/RoadlineModelViewSet/';
// 车辆API前缀
const vehicleApiPrefix = '/api/VehicleModelViewSet/';
// 媒体类型API前缀
const mediaTypeApiPrefix = '/api/AdMediaTypeModelViewSet/';

//此处为crudOptions配置
export default function ({ crudExpose }: { crudExpose: CrudExpose }): CreateCrudOptionsRet {
	// 代理商列表
	const agentList: Ref<any[]> = ref([]);

	// 线路列表
	const roadlineList: Ref<any[]> = ref([]);

	// 车辆列表
	const vehicleList: Ref<any[]> = ref([]);

	// 媒体类型列表
	const mediaTypeList: Ref<any[]> = ref([]);

	// 当前选中的资源类型（用于动态加载资源列表）
	const currentResourceType: Ref<number | null> = ref(null);

	// 当前资源列表（根据资源类型动态变化）
	const currentResourceList: Ref<any[]> = ref([]);

	// 加载代理商列表
	const loadAgentList = async () => {
		try {
			const res = await request({
				url: agentApiPrefix,
				method: 'get',
				params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
			});
			if (res && res.data && res.data.results && Array.isArray(res.data.results)) {
				agentList.value = res.data.results.map((item: any) => ({
					value: item.id,
					label: `${item.agent_code || ''} ${item.company_name || ''}`.trim() || `代理商ID:${item.id}`,
				}));
			}
		} catch (error) {
			console.error('加载代理商列表失败:', error);
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

	// 加载车辆列表
	const loadVehicleList = async () => {
		try {
			const res = await request({
				url: vehicleApiPrefix,
				method: 'get',
				params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
			});
			if (res && res.data && res.data.results && Array.isArray(res.data.results)) {
				vehicleList.value = res.data.results.map((item: any) => ({
					value: item.id,
					label: `${item.vehicle_plate || ''} ${item.vehicle_no || ''}`.trim() || `车辆ID:${item.id}`,
				}));
			}
		} catch (error) {
			console.error('加载车辆列表失败:', error);
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
				}));
			}
		} catch (error) {
			console.error('加载媒体类型列表失败:', error);
		}
	};

	// 根据资源类型加载并更新资源列表
	const loadResourceListByType = async (resourceType: number) => {
		currentResourceType.value = resourceType;
		if (resourceType === 1) {
			// 线路
			if (roadlineList.value.length === 0) {
				await loadRoadlineList();
			}
			currentResourceList.value = roadlineList.value;
		} else if (resourceType === 2) {
			// 车辆
			if (vehicleList.value.length === 0) {
				await loadVehicleList();
			}
			currentResourceList.value = vehicleList.value;
		} else if (resourceType === 3) {
			// 媒体类型
			if (mediaTypeList.value.length === 0) {
				await loadMediaTypeList();
			}
			currentResourceList.value = mediaTypeList.value;
		} else {
			currentResourceList.value = [];
		}
	};

	// 初始化时加载列表
	loadAgentList();

	// 获取授权列表
	const pageRequest = async (query: any) => {
		return await api.GetList(query);
	};

	// 编辑授权
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}

		// 处理日期字段，确保提交纯日期格式
		if (form.auth_start_date && typeof form.auth_start_date === 'string') {
			form.auth_start_date = form.auth_start_date.split(' ')[0];
		}
		if (form.auth_end_date && typeof form.auth_end_date === 'string') {
			form.auth_end_date = form.auth_end_date.split(' ')[0];
		}

		return await api.UpdateObj(form);
	};

	// 删除授权
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加授权
	const addRequest = async ({ form }: AddReq) => {
		// 处理日期字段
		if (form.auth_start_date && typeof form.auth_start_date === 'string') {
			form.auth_start_date = form.auth_start_date.split(' ')[0];
		}
		if (form.auth_end_date && typeof form.auth_end_date === 'string') {
			form.auth_end_date = form.auth_end_date.split(' ')[0];
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
						show: auth('AgentResourceAuthModelViewSet:Export'),
						text: '导出',
						title: '导出',
						click() {
							return exportRequest(crudExpose.getSearchFormData());
						},
					},
					add: {
						show: auth('AgentResourceAuthModelViewSet:Create'),
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
						show: auth('AgentResourceAuthModelViewSet:Retrieve'),
					},
					edit: {
						type: 'text',
						order: 2,
						show: auth('AgentResourceAuthModelViewSet:Update'),
					},
					remove: {
						type: 'text',
						order: 3,
						show: auth('AgentResourceAuthModelViewSet:Delete'),
					},
				},
			},
			columns: {
				// 序号列
				_index: getIndexColumnConfig(crudExpose),
				
				// 代理商ID（表单使用）
				agent_id: {
					title: '代理商',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						value: 'value',
						label: 'label',
						getData: async () => {
							if (agentList.value.length === 0) {
								await loadAgentList();
							}
							return agentList.value;
						},
					}),
					column: {
						minWidth: 200,
						sortable: 'custom',
						show: false, // 隐藏，使用计算字段agent_code和company_name显示
					},
					form: {
						rules: [{ required: true, message: '代理商必填' }],
						component: {
							placeholder: '请选择代理商',
							filterable: true,
						},
					},
				},

				// 代理商编码（显示字段）
				agent_code: {
					title: '代理商编码',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 150,
						sortable: false,
						show: true, // 显示在列表中
					},
					form: { show: false },
				},

				// 公司名称（显示字段）
				company_name: {
					title: '公司名称',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 200,
						sortable: false,
						show: true, // 显示在列表中
					},
					form: { show: false },
				},

				// 资源类型
				resource_type: {
					title: '资源类型',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: 1, label: '线路' },
							{ value: 2, label: '车辆' },
							{ value: 3, label: '媒体类型' },
						],
					}),
					column: {
						minWidth: 120,
						sortable: 'custom',
						align: 'left',
						show: false, // 隐藏，使用计算字段resource_type_display显示
					},
					form: {
						rules: [{ required: true, message: '资源类型必填' }],
						component: {
							placeholder: '请选择资源类型',
							onChange: async (value: any, form: any) => {
								// 当资源类型改变时，清空资源ID并加载对应的资源列表
								form.resource_id = null;
								if (value) {
									await loadResourceListByType(value);
									// 触发资源ID字段的重新加载
									setTimeout(() => {
										if (crudExpose.getFormComponentRef) {
											const resourceIdRef = crudExpose.getFormComponentRef('resource_id');
											if (resourceIdRef && resourceIdRef.reload) {
												resourceIdRef.reload();
											}
										}
									}, 100);
								}
							},
						},
					},
				},

				// 资源类型显示字段
				resource_type_display: {
					title: '资源类型',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: false,
						align: 'left',
						show: true, // 显示在列表中
					},
					form: { show: false },
				},

				// 资源ID（表单使用，根据资源类型动态加载）
				resource_id: {
					title: '资源',
					type: 'dict-select',
					search: { show: false },
					dict: dict({
						value: 'value',
						label: 'label',
						getData: async (dict: any, context: any) => {
							// 尝试从表单数据中获取资源类型
							let resourceType = currentResourceType.value;
							if (!resourceType && context) {
								const formData = context.getFormData?.() || {};
								resourceType = formData.resource_type;
							}
							
							// 如果有资源类型，加载对应的资源列表
							if (resourceType) {
								await loadResourceListByType(resourceType);
							}
							
							return currentResourceList.value;
						},
					}),
					column: {
						minWidth: 200,
						sortable: 'custom',
						show: false, // 隐藏，使用计算字段resource_name显示
					},
					form: {
						rules: [{ required: true, message: '资源必填' }],
						component: {
							placeholder: '请先选择资源类型，然后选择资源',
							filterable: true,
							disabled: (context: any) => {
								// 如果资源类型未选择，禁用资源ID选择
								const form = context?.form || {};
								return !form.resource_type;
							},
						},
					},
				},

				// 资源名称（显示字段）
				resource_name: {
					title: '资源名称',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 200,
						sortable: false,
						show: true, // 显示在列表中
					},
					form: { show: false },
				},

				// 授权开始日期
				auth_start_date: {
					title: '授权开始日期',
					type: 'date',
					search: { show: false },
					column: {
						align: 'center',
						width: 130,
						show: true, // 显示在列表中
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: {
						component: {
							format: 'YYYY-MM-DD',
							valueFormat: 'YYYY-MM-DD',
							placeholder: '请选择授权开始日期',
						},
					},
				},

				// 授权结束日期
				auth_end_date: {
					title: '授权结束日期',
					type: 'date',
					search: { show: false },
					column: {
						align: 'center',
						width: 130,
						show: true, // 显示在列表中
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: {
						component: {
							format: 'YYYY-MM-DD',
							valueFormat: 'YYYY-MM-DD',
							placeholder: '请选择授权结束日期',
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

