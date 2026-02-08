import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';
import { ref, Ref, nextTick } from 'vue';
// @ts-ignore - defConfig.js 没有类型声明
import { listPageDefSingleLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';

// 车辆API前缀
const vehicleApiPrefix = '/api/VehicleModelViewSet/';
// 媒体类型API前缀
const mediaTypeApiPrefix = '/api/AdMediaTypeModelViewSet/';

//此处为crudOptions配置
export default function ({ crudExpose, context }: { crudExpose: CrudExpose; context?: any }): CreateCrudOptionsRet {
	// 车辆列表
	const vehicleList: Ref<any[]> = ref([]);

	// 基础媒体类型列表（只包含基础类型，is_composite=false）
	const baseMediaTypeList: Ref<any[]> = ref([]);

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

	// 加载基础媒体类型列表（只加载基础类型，is_composite=false）
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
				}));
			}
		} catch (error) {
			console.error('加载基础媒体类型列表失败:', error);
		}
	};

	// 初始化时加载列表
	loadVehicleList();
	loadBaseMediaTypeList();

	// 获取资源位列表（根据 vehicle_id 过滤）
	// 注意：VehicleAdCalendarModelViewSet 需要排除 resource_status=1 的数据
	const pageRequest = async (query: any) => {
		// 合并外部筛选条件（从 context 中获取）
		if (context?.externalFilters) {
			query = {
				...query,
				...context.externalFilters,
			};
		}
		// 添加参数排除 resource_status=1 的数据
		// 使用 exclude_resource_status=1 参数来排除空闲状态的数据
		query.exclude_resource_status = 1;
		return await api.GetList(query);
	};

	// 编辑资源位
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}

		// 处理日期字段，确保提交纯日期格式
		if (form.scheduled_start_date && typeof form.scheduled_start_date === 'string') {
			form.scheduled_start_date = form.scheduled_start_date.split(' ')[0];
		}
		if (form.scheduled_end_date && typeof form.scheduled_end_date === 'string') {
			form.scheduled_end_date = form.scheduled_end_date.split(' ')[0];
		}

		return await api.UpdateObj(form);
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
		// 处理日期字段
		if (form.scheduled_start_date && typeof form.scheduled_start_date === 'string') {
			form.scheduled_start_date = form.scheduled_start_date.split(' ')[0];
		}
		if (form.scheduled_end_date && typeof form.scheduled_end_date === 'string') {
			form.scheduled_end_date = form.scheduled_end_date.split(' ')[0];
		}

		return await api.AddObj(form);
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
			toolbar: {
				show: false, // 隐藏工具栏（包括刷新按钮）
			},
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
				show: false, // 隐藏所有操作栏按钮
			},
			rowHandle: {
				show: false, // 隐藏所有行操作按钮
			},
			columns: {
				// 序号列
				_index: getIndexColumnConfig(crudExpose),
				
				// 资源编码
				resource_code: {
					title: '资源编码',
					type: 'input',
					search: { show: true },
					column: {
						// 前面的字段收窄，给日期列更多空间
						width: 230,
						sortable: 'custom',
						show: true, // 显示在列表中
						showOverflowTooltip: true,
					},
					form: {
						rules: [{ required: true, message: '资源编码必填' }],
						component: {
							placeholder: '请输入资源编码，如：V100-LEFT',
						},
					},
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
						minWidth: 100,
						sortable: 'custom',
						show: false, // 隐藏，使用计算字段vehicle_plate和vehicle_no显示
					},
					form: {
						rules: [{ required: true, message: '车辆必填' }],
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
						width: 180,
						sortable: false,
						align: 'left',
						show: true, // 列表显示车牌号
						showOverflowTooltip: true,
					},
					form: { show: false },
				},

				// 车辆编号（隐藏，使用vehicle_display显示）
				vehicle_no: {
					title: '车辆编号',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 90,
						sortable: false,
						align: 'left',
						show: false, // 隐藏，使用vehicle_display显示
					},
					form: { show: false },
				},

				// 基础媒体类型ID（表单使用）
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
						minWidth: 150,
						sortable: 'custom',
						align: 'left',
						show: false, // 隐藏，使用计算字段media_type_name显示
					},
					form: {
						rules: [{ required: true, message: '基础媒体类型必填' }],
						component: {
							placeholder: '请选择基础媒体类型（必须是基础类型，不能是组合类型）',
							filterable: true,
						},
					},
				},

				// 媒体类型名称（显示字段）
				media_type_name: {
					title: '媒体类型',
					type: 'text',
					search: { show: false },
					column: {
						width: 150,
						sortable: false,
						align: 'left',
						show: true, // 显示在列表中
						showOverflowTooltip: true,
					},
					form: { show: false },
				},

				// 资源状态
				resource_status: {
					title: '资源状态',
					type: 'dict-select',
					search: { show: true },
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
						minWidth: 150,
						sortable: 'custom',
						align: 'left',
						show: false, // 隐藏，使用计算字段resource_status_display显示
					},
					form: {
						rules: [{ required: true, message: '资源状态必填' }],
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
						width: 150,
						sortable: false,
						align: 'center',
						show: true, // 显示在列表中
					},
					form: { show: false },
				},
				// 上刊日期（调整到投放开始日期前面）
				on_air_date: {
					title: '上刊日期',
					type: 'date',
					search: { show: false },
					column: {
						align: 'left',
						width: 200,
						show: true, // 显示在列表中
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: { show: false },
				},
				// 投放开始日期
				scheduled_start_date: {
					title: '投放开始日期',
					type: 'date',
					search: { show: false },
					column: {
						align: 'left',
						width: 200,
						show: true, // 显示在列表中
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: {
						component: {
							format: 'YYYY-MM-DD',
							valueFormat: 'YYYY-MM-DD',
							placeholder: '请选择投放开始日期',
						},
					},
				},

				// 投放结束日期
				scheduled_end_date: {
					title: '投放结束日期',
					type: 'date',
					search: { show: false },
					column: {
						align: 'left',
						width: 200,
						show: true, // 显示在列表中
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: {
						component: {
							format: 'YYYY-MM-DD',
							valueFormat: 'YYYY-MM-DD',
							placeholder: '请选择投放结束日期',
						},
					},
				},

				// 下刊日期
				off_air_date: {
					title: '下刊日期',
					type: 'date',
					search: { show: false },
					column: {
						align: 'left',
						width: 200,
						show: true, // 显示在列表中
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: { show: false },
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
						component: {
							placeholder: '请输入备注',
							rows: 4,
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

