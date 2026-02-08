import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet, compute } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';
import { ref, Ref, nextTick, h } from 'vue';
// @ts-ignore - defConfig.js 没有类型声明
import { listPageDefSingleLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';
import { ElMessage } from 'element-plus';
import MediaTypeDualSelector from './components/MediaTypeDualSelector.vue';

// 车辆API前缀
const vehicleApiPrefix = '/api/VehicleModelViewSet/';
// 媒体类型API前缀
const mediaTypeApiPrefix = '/api/AdMediaTypeModelViewSet/';

//此处为crudOptions配置
export default function ({ crudExpose, context }: { crudExpose: CrudExpose; context?: any }): CreateCrudOptionsRet {
	// 车辆列表
	const vehicleList: Ref<any[]> = ref([]);

	// 媒体类型列表（包含所有类型，包括基础类型和组合类型）
	const mediaTypeList: Ref<any[]> = ref([]);

	// 兼容后端两种列表返回：
	// - 分页：{ code, data: [...] }
	// - 其他历史/个别接口：{ code, data: { results: [...] } }
	const getListData = (resp: any): any[] => {
		const data = resp?.data;
		if (Array.isArray(data)) return data;
		if (data && Array.isArray(data.results)) return data.results;
		return [];
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
				}));
			}
		} catch (error) {
			console.error('加载车辆列表失败:', error);
		}
	};

	// 加载所有媒体类型列表（包括基础类型和组合类型）
	const loadMediaTypeList = async () => {
		try {
			const res = await request({
				url: mediaTypeApiPrefix,
				method: 'get',
				params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
			});
			const list = getListData(res);
			if (list.length > 0) {
				mediaTypeList.value = list.map((item: any) => ({
					value: item.id,
					label: item.media_name || `媒体类型ID:${item.id}`,
				}));
			}
		} catch (error) {
			console.error('加载媒体类型列表失败:', error);
		}
	};

	// 初始化时加载列表
	loadVehicleList();
	loadMediaTypeList();

	// 获取资源位列表（只显示 resource_status=1 的数据，后端已处理过滤）
	const pageRequest = async (query: any) => {
		// 移除可能存在的 resource_status 搜索条件，因为后端强制只返回 resource_status=1 的数据
		const { resource_status, ...restQuery } = query;
		return await api.GetList(restQuery);
	};

	// 编辑资源位
	const editRequest = async ({ form, row }: EditReq) => {
		// 编辑：按“车辆维度”设置媒体类型（支持组合类型拆分/多选并集），不走标准 Update
		const vehicleId = row?.vehicle_id || form?.vehicle_id;
		if (!vehicleId) {
			ElMessage.error('未找到车辆ID，无法编辑媒体类型');
			throw new Error('缺少 vehicle_id');
		}

		const selected = form?.media_type_items || [];
		const ids = Array.isArray(selected) ? selected.map((x: any) => String(x?.id)).filter(Boolean) : [];
		if (ids.length < 1) {
			ElMessage.error('请至少选择 1 个媒体类型');
			throw new Error('缺少 media_type_ids');
		}

		return await api.setVehicleMediaTypesBatch({
			vehicle_id: String(vehicleId),
			media_type_ids: ids,
			remark: form.remark,
		});
	};

	// 删除资源位
	const delRequest = async ({ row }: DelReq) => {
		const result = await api.DelObj(row.id);
		// 删除成功后，清空树形缓存并刷新表格
		const tableRef = crudExpose.getBaseTableRef();
		if (tableRef?.store?.states) {
			// 清空已渲染数据与树结构缓存
			tableRef.store.states.data && (tableRef.store.states.data.value = []);
			tableRef.store.states.treeData && (tableRef.store.states.treeData.value = []);
			tableRef.store.states.lazyTreeNodeMap && (tableRef.store.states.lazyTreeNodeMap.value = {});
		}
		// 使用 nextTick 确保 DOM 更新后再刷新，让树表状态正确恢复
		nextTick(() => {
			// 刷新列表（重新加载根节点）
			crudExpose.doRefresh();
		});
		return result;
	};

	// 添加资源位
	const addRequest = async ({ form }: AddReq) => {
		// 新增支持选择多台车辆（从左侧树多选中取值）
		const selectedVehicleIdsRaw = context?.selectedVehicleIds?.value ?? context?.selectedVehicleIds ?? [];
		const selectedVehicleIds: string[] = Array.isArray(selectedVehicleIdsRaw) ? selectedVehicleIdsRaw : [];
		if (selectedVehicleIds.length < 1) {
			ElMessage.error('请在左侧树中至少勾选 1 台车辆后再新增');
			throw new Error('新增资源位至少需要选择 1 台车辆');
		}
		
		// 从左右分栏选择器获取选中的媒体类型
		const selected = form?.media_type_items || [];
		const mediaTypeIds = Array.isArray(selected) ? selected.map((x: any) => String(x?.id)).filter(Boolean) : [];
		if (mediaTypeIds.length < 1) {
			ElMessage.error('请至少选择 1 个媒体类型');
			throw new Error('媒体类型必填');
		}

		// 为每个媒体类型调用批量创建接口（后端会处理组合类型拆分、resource_status=1、resource_code生成）
		const results = [];
		for (const mediaTypeId of mediaTypeIds) {
			try {
				const result = await api.bulkCreate({
					vehicle_ids: selectedVehicleIds,
					media_type_id: mediaTypeId,
					// 新增时不传备注
				});
				results.push(result);
			} catch (error) {
				console.error(`为媒体类型 ${mediaTypeId} 创建资源位失败:`, error);
				throw error;
			}
		}
		
		// 返回最后一个结果（或合并结果）
		return results[results.length - 1] || { code: 200, msg: '创建成功' };
	};

	// 导出数据
	const exportRequest = async (query: UserPageQuery) => {
		return await api.exportData(query);
	};

	return {
		crudOptions: {
			...listPageDefSingleLineCfg,
			// 根据使用该 crud 的组件控制是否展示搜索栏：
			// - 普通树+表页面（index.vue）需要搜索
			// - 模板页内嵌的列表（list.vue）不需要搜索，由外层模板统一控制筛选
			search: {
				show: context?.componentName !== 'VehicleAdResourceModelViewSetList',
			},
			request: {
				pageRequest,
				addRequest,
				editRequest,
				delRequest,
			},
			form: {
				col: { span: 24 }, // 每个字段占一行（100%宽度）
				// add/edit 模式下使用左右分栏选择器，缩小 label 区域，避免左侧留白过大
				labelWidth: compute(({ mode }: any) => {
					if (mode === 'add' || mode === 'edit' || mode === 'view') return '60px';
					return '120px';
				}),
				// label 左对齐
				labelAlign: 'left',
				wrapper: {
					is: 'el-dialog',
					width: '1000px', // 增加宽度以容纳左右分栏组件
					closeOnClickModal: false,
					async onOpened({ mode, form, row }: any) {
						// 新增模式：初始化空数组
						if (mode === 'add') {
							form.media_type_items = [];
						}
						// 编辑/查看模式：加载该车当前已配置的媒体类型（组合优先折叠后的展示）
						if (mode === 'edit' || mode === 'view') {
							// 顶部信息条：线路 + 车辆
							let roadlineName = row?.roadline_name || row?.roadlineName || '';
							const roadlineId = row?.roadline_id || row?.roadlineId || '';
							let vehiclePlate = row?.vehicle_plate || '';
							let vehicleNo = row?.vehicle_no || '';
							const vehicleIdForDisplay = row?.vehicle_id || form?.vehicle_id;

							// 若列表行未携带线路/车辆展示信息（或车辆数据为空），则兜底拉一次车辆详情
							if ((!roadlineName || (!vehiclePlate && !vehicleNo)) && vehicleIdForDisplay) {
								try {
									const vres: any = await request({
										url: `${vehicleApiPrefix}${String(vehicleIdForDisplay)}/`,
										method: 'get',
									});
									const vdata = vres?.data || {};
									vehiclePlate = vehiclePlate || vdata?.vehicle_plate || '';
									vehicleNo = vehicleNo || vdata?.vehicle_no || '';
									roadlineName = roadlineName || vdata?.roadline_name || '';
								} catch (e) {
									// ignore
								}
							}
							const roadlineDisplay = roadlineName || (roadlineId ? `线路ID:${roadlineId}` : '');
							// 车辆显示格式：车牌号（车辆编号）
							let vehicleDisplay = '';
							if (vehiclePlate && vehicleNo) {
								vehicleDisplay = `${vehiclePlate}（${vehicleNo}）`;
							} else if (vehiclePlate) {
								vehicleDisplay = vehiclePlate;
							} else if (vehicleNo) {
								vehicleDisplay = vehicleNo;
							} else if (vehicleIdForDisplay) {
								vehicleDisplay = `车辆ID:${vehicleIdForDisplay}`;
							}
							form._edit_header_info = { roadlineDisplay, vehicleDisplay };

							const vehicleId = row?.vehicle_id || form?.vehicle_id;
							if (vehicleId) {
								try {
									const res: any = await api.getVehicleMediaTypes(String(vehicleId));
									const composites = (res?.data?.composites || []).map((x: any) => ({
										id: String(x.id),
										media_name: x.name || '',
									}));
									const bases = (res?.data?.bases || []).map((x: any) => ({
										id: String(x.id),
										media_name: x.name || '',
									}));
									// 左侧已选：组合 + 剩余基础
									form.media_type_items = [...composites, ...bases].filter((x: any) => x.id);
								} catch (e) {
									form.media_type_items = [];
								}
							}
						}
					},
				},
				afterSubmit({ mode }: any) {
					const tableRef = crudExpose.getBaseTableRef();
					if (tableRef?.store?.states) {
						// 清空已渲染数据与树结构缓存
						tableRef.store.states.data && (tableRef.store.states.data.value = []);
						tableRef.store.states.treeData && (tableRef.store.states.treeData.value = []);
						tableRef.store.states.lazyTreeNodeMap && (tableRef.store.states.lazyTreeNodeMap.value = {});
					}
					// 使用 nextTick 确保 DOM 更新后再刷新，让树表状态正确恢复
					nextTick(() => {
						// 刷新列表（重新加载根节点）
						crudExpose.doRefresh();
					});
				},
			},
			pagination: { show: true }, // 普通列表需要分页
			actionbar: {
				buttons: {
					export: {
						show: auth('VehicleAdResourceModelViewSet:Export'),
						text: '导出',
						title: '导出',
						click() {
							return exportRequest(crudExpose.getSearchFormData());
						},
					},
					add: {
						show: auth('VehicleAdResourceModelViewSet:Create'),
						text: '设置资源位',
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
						show: auth('VehicleAdResourceModelViewSet:Retrieve'),
					},
					edit: {
						type: 'text',
						order: 2,
						show: auth('VehicleAdResourceModelViewSet:Update'),
					},
					remove: {
						type: 'text',
						order: 3,
						show: auth('VehicleAdResourceModelViewSet:Delete'),
					},
				},
			},
			columns: {
				// 编辑弹窗：顶部信息（线路 + 车辆），新增模式不显示
				_edit_header_info: {
					title: '',
					type: 'component',
					search: { show: false },
					column: { show: false },
					form: {
						show: compute(({ mode }) => mode === 'edit' || mode === 'view'),
						col: { span: 24 },
						component: {
							render: ({ form }: any) => {
								const roadline = form?._edit_header_info?.roadlineDisplay || '-';
								const vehicle = form?._edit_header_info?.vehicleDisplay || '-';
								return h(
									'div',
									{
										style: {
											padding: '8px 12px',
											marginBottom: '8px',
											border: '1px solid #ebeef5',
											borderRadius: '6px',
											background: '#f5f7fa',
											color: '#303133',
											display: 'flex',
											gap: '16px',
											flexWrap: 'wrap',
										},
									},
									[
										h('div', { style: { minWidth: '320px' } }, [`线路：${roadline}`]),
										h('div', { style: { minWidth: '320px' } }, [`车辆：${vehicle}`]),
									]
								);
							},
						},
					},
				},

				// 编辑/新增弹窗：展示左右分栏（左已选/右可选）
				media_type_items: {
					title: '媒体类型',
					type: 'component',
					search: { show: false },
					column: { show: false },
					form: {
						show: compute(({ mode }) => mode === 'add' || mode === 'edit' || mode === 'view'),
						rules: [{ required: true, message: '请至少选择 1 个媒体类型' }],
						component: {
							render: ({ form, mode }: any) => {
								const value = Array.isArray(form.media_type_items) ? form.media_type_items : [];
								return h(MediaTypeDualSelector, {
									modelValue: value,
									disabled: mode === 'view',
									key: `media-type-dual-selector-${form.id || 'new'}-${value.length}`,
									'onUpdate:modelValue': (v: any) => {
										if (mode !== 'view') {
											form.media_type_items = v;
										}
									},
								});
							},
						},
					},
				},
				// 序号列
				_index: getIndexColumnConfig(crudExpose),
				
				// 资源编码
				resource_code: {
					title: '资源编码',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 150,
						sortable: 'custom',
						show: true, // 显示在列表中
					},
					form: {
						show: compute(({ mode }) => mode !== 'add' && mode !== 'edit' && mode !== 'view'),
						rules: compute(({ mode }) => (mode === 'add' ? [] : [{ required: true, message: '资源编码必填' }])),
						component: {
							placeholder: '请输入资源编码，如：V100-LEFT',
						},
					},
				},

				// 线路ID（隐藏，用于树形点击过滤）
				roadline_id: {
					title: '线路ID',
					type: 'text',
					search: { show: false }, // 隐藏，通过树形点击设置
					column: { show: false },
					form: { show: false },
				},

				// 车辆ID列表（隐藏，用于多选过滤）
				vehicle_id__in: {
					title: '车辆ID列表',
					type: 'text',
					search: { show: false }, // 隐藏，通过树形多选设置
					column: { show: false },
					form: { show: false },
				},

				// 车辆ID（表单使用）
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
						minWidth: 150,
						sortable: 'custom',
						show: false, // 隐藏，使用计算字段vehicle_plate和vehicle_no显示
					},
					form: {
						show: compute(({ mode }) => mode !== 'add' && mode !== 'edit' && mode !== 'view'),
						rules: compute(({ mode }) => (mode === 'add' ? [] : [{ required: true, message: '车辆必填' }])),
						component: {
							placeholder: '请选择车辆',
							filterable: true,
						},
					},
				},

				// 车牌号（隐藏，使用vehicle_display显示）
				vehicle_plate: {
					title: '车牌号',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: false,
						align: 'left',
						show: true, // 列表显示车牌号
					},
					form: { show: false },
				},

				// 车辆编号（隐藏，使用vehicle_display显示）
				vehicle_no: {
					title: '车辆编号',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: false,
						align: 'left',
						show: false, // 隐藏，使用vehicle_display显示
					},
					form: { show: false },
				},

				// 媒体类型ID（表单使用，新增模式下已隐藏，改用media_type_items）
				base_media_type_id: {
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
						align: 'left',
						show: false, // 隐藏，使用计算字段media_type_name显示
					},
					form: {
						show: false, // 新增模式已改用media_type_items左右分栏选择器
						col: { span: 24 },
						rules: [{ required: true, message: '媒体类型必填' }],
						component: {
							placeholder: '请选择媒体类型',
							filterable: true,
							style: { width: '100%' },
						},
					},
				},

				// 媒体类型名称（展示字段：组合优先，无组合则基础类型）
				display_media_type_name: {
					title: '媒体类型',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 150,
						sortable: false,
						align: 'left',
						show: true, // 显示在列表中
					},
					form: { show: false },
				},

				// 资源状态
				resource_status: {
					title: '资源状态',
					type: 'dict-select',
					search: { show: false }, // 隐藏搜索，因为只显示空值数据
					dict: dict({
						data: [
							{ value: 1, label: '空闲' },
							{ value: 2, label: '预订' },
							{ value: 3, label: '在刊' },
							{ value: 4, label: '下刊' },
							{ value: 5, label: '维修中' },
							{ value: 6, label: '不可用' },
							{ value: 7, label: '到期未下刊' },
						],
					}),
					column: {
						minWidth: 100,
						sortable: 'custom',
						align: 'left',
						show: false, // 隐藏，使用计算字段resource_status_display显示
					},
					form: {
						show: compute(({ mode }) => mode !== 'add' && mode !== 'edit' && mode !== 'view'),
						rules: compute(({ mode }) => (mode === 'add' ? [] : [{ required: true, message: '资源状态必填' }])),
						value: 1, // 默认值：空闲
						component: {
							placeholder: '请选择资源状态',
						},
					},
				},

				// 资源状态显示字段
				resource_status_display: {
					title: '资源状态',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: false,
						align: 'left',
						show: false, // 隐藏，不在列表中显示
					},
					form: { show: false },
				},

				// 当前订单ID
				current_order_id: {
					title: '当前订单ID',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: 'custom',
						show: false,
					},
					form: {
						show: compute(({ mode }) => mode !== 'add' && mode !== 'edit' && mode !== 'view'), // 编辑/查看弹窗不展示
						component: {
							placeholder: '请输入当前订单ID（如有）',
							precision: 0,
						},
					},
				},

				// 计划投放开始日期
				scheduled_start_date: {
					title: '投放开始日期',
					type: 'date',
					search: { show: false },
					column: {
						align: 'center',
						width: 120,
						show: false, // 隐藏，不在列表中显示
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: {
						show: false,
					},
				},

				// 计划投放结束日期
				scheduled_end_date: {
					title: '投放结束日期',
					type: 'date',
					search: { show: false },
					column: {
						align: 'center',
						width: 120,
						show: false, // 隐藏，不在列表中显示
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: {
						show: false,
					},
				},

				// 上刊日期
				on_air_date: {
					title: '上刊日期',
					type: 'date',
					search: { show: false },
					column: {
						align: 'center',
						width: 120,
						show: false, // 隐藏，不在列表中显示
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: {
						show: compute(({ mode }) => mode !== 'add' && mode !== 'edit' && mode !== 'view'),
						component: {
							format: 'YYYY-MM-DD',
							valueFormat: 'YYYY-MM-DD',
							placeholder: '请选择上刊日期',
						},
					},
				},

				// 下刊日期
				off_air_date: {
					title: '下刊日期',
					type: 'date',
					search: { show: false },
					column: {
						align: 'center',
						width: 120,
						show: false, // 隐藏，不在列表中显示
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: {
						show: compute(({ mode }) => mode !== 'add' && mode !== 'edit' && mode !== 'view'),
						component: {
							format: 'YYYY-MM-DD',
							valueFormat: 'YYYY-MM-DD',
							placeholder: '请选择下刊日期',
						},
					},
				},

				// 备注
				remark: {
					title: '备注',
					type: 'textarea',
					search: { show: false },
					column: {
						minWidth: 150,
						sortable: 'custom',
						show: false,
					},
					form: {
						show: false, // 新增模式下不显示备注
						col: { span: 24 },
						component: {
							placeholder: '请输入备注',
							rows: 4,
							style: { width: '100%' },
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

